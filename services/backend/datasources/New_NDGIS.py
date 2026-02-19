'''NDGIS water quality source. DANR framework: _pull -> _process (temp_staging) -> _push.'''
import requests
import pandas as pd
import io
import sqlite3
import sqlite_utils
from BackEnd.SourceFiles.config import SQL_CONVERSION, DB_PATH

ARCGIS_URL = "https://ndgishub.nd.gov/arcgis/rest/services/Applications/DOH_SurfaceWaterSamplingSites/MapServer/0/query"
WATERCHEM_URL = "https://deq.nd.gov/Webservices_SWDataApp/DownloadStationsData/GetStationsWaterChemData/{}"
CSV_BASE = "https://deq.nd.gov/WQ/3_Watershed_Mgmt/SWDataApp/downloaddata/{}.csv"
WQ_COLS = ["total_phosphorus", "total_kjeldahl_phosphorus", "nitrate_nitrite", "nitrate_forms_check", "nitrate_nitrite_dissolved", "total_kjeldahl_nitrogen", "tkn_dissolved", "total_nitrogen_dissolved", "e_coli", "total_nitrogen", "ph", "ammonia_nitrogen", "ammonia_nitrogen_dissolved", "ammonia_forms_check", "diss_ammonia_tkn_check", "dissolved_phosphorus"]
PARAM_TO_COL = {k: SQL_CONVERSION[k] for k in SQL_CONVERSION if SQL_CONVERSION[k] in WQ_COLS}

def _station_ids(limit=10):
    try:
        params = {"where": "1=1", "outFields": "SITE_ID", "returnGeometry": "false", "f": "json", "resultRecordCount": limit}
        r = requests.get(ARCGIS_URL, params=params, timeout=30)
        return [str(f["attributes"]["SITE_ID"]).strip() for f in r.json().get("features", []) if f.get("attributes", {}).get("SITE_ID")]
    except Exception:
        return []

def _pull():
    data = []
    for sid in _station_ids():
        try:
            name_r = requests.post(WATERCHEM_URL.format(sid), timeout=30)
            if name_r.status_code != 200 or not name_r.text:
                continue
            name = name_r.text.replace('"', '').strip()
            csv_r = requests.get(CSV_BASE.format(name), timeout=30)
            csv_r.raise_for_status()
            txt = csv_r.text
            if txt.startswith("sep="):
                txt = "\n".join(txt.split("\n")[1:])
            try:
                df = pd.read_csv(io.StringIO(txt), sep=";")
            except Exception:
                df = pd.read_csv(io.StringIO(txt))
            if "DATE_COLL" in df.columns and "Parameter" in df.columns and "Result" in df.columns and len(df) > 0:
                data.append({"station_id": sid, "rows": df.to_dict("records")})
        except Exception:
            pass
    return data

def _process(data):
    groups = {}
    for station_data in data:
        sid = station_data["station_id"]
        for row in station_data["rows"]:
            try:
                dt = pd.to_datetime(row["DATE_COLL"]).strftime("%Y-%m-%d %H:%M:%S")
                param = row.get("Parameter")
                col = PARAM_TO_COL.get(param)
                if not col:
                    continue
                val = row.get("Result")
                if val == "*NON-DETECT" or val is None:
                    continue
                val = float(val)
                key = (sid, dt)
                groups.setdefault(key, {"location": sid, "datetime": dt})
                groups[key][col] = val
            except (KeyError, ValueError, TypeError):
                continue
    db = pd.DataFrame(groups.values()) if groups else pd.DataFrame(columns=["location", "datetime"])
    conn = sqlite3.connect(DB_PATH)
    db.to_sql("temp_staging", conn, if_exists="replace", index=False)
    conn.close()

def _push():
    files = sqlite_utils.Database(DB_PATH)
    files["water_quality"].upsert_all(files["temp_staging"].rows, alter=True, hash_id="unique_id")

def update():
    _process(_pull())
    _push()

if __name__ == "__main__":
    update()
