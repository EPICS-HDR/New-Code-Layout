'''
Author: Andrew Vu
Date: 2/19/2026
Purpose: NDGIS water quality data source following DANR pulling method pattern.
'''
import requests
import pandas as pd
import io
import sqlite3
import sqlite_utils
import traceback
from services.backend.datasources.config import SQL_CONVERSION, DB_PATH

ARCGIS_URL = "https://ndgishub.nd.gov/arcgis/rest/services/Applications/DOH_SurfaceWaterSamplingSites/MapServer/0/query"
WATERCHEM_URL = "https://deq.nd.gov/Webservices_SWDataApp/DownloadStationsData/GetStationsWaterChemData/{}"
CSV_BASE = "https://deq.nd.gov/WQ/3_Watershed_Mgmt/SWDataApp/downloaddata/{}.csv"
WQ_COLS = [k for k, v in SQL_CONVERSION.items() if v.startswith("total_phosphorus") or v.startswith("nitrate") or v.startswith("nitrogen") or v in ("e_coli", "ph", "ammonia", "dissolved_phosphorus") or "dissolved" in v or "tkn" in v or "forms_check" in v]
PARAM_TO_COL = {k: SQL_CONVERSION[k] for k in SQL_CONVERSION if SQL_CONVERSION[k] in ["total_phosphorus", "total_kjeldahl_phosphorus", "nitrate_nitrite", "nitrate_forms_check", "nitrate_nitrite_dissolved", "total_kjeldahl_nitrogen", "tkn_dissolved", "total_nitrogen_dissolved", "e_coli", "total_nitrogen", "ph", "ammonia_nitrogen", "ammonia_nitrogen_dissolved", "ammonia_forms_check", "diss_ammonia_tkn_check", "dissolved_phosphorus"]}

def _station_ids():
    out = []
    off = 0
    while True:
        r = requests.get(ARCGIS_URL, params={"where": "1=1", "outFields": "SITE_ID", "returnGeometry": "false", "f": "json", "resultOffset": off, "resultRecordCount": 2000}, timeout=30)
        r.raise_for_status()
        feats = r.json().get("features", [])
        if not feats:
            break
        for f in feats:
            sid = f.get("attributes", {}).get("SITE_ID")
            if sid and str(sid).strip():
                out.append(str(sid).strip())
        if len(feats) < 2000:
            break
        off += 2000
    return list(dict.fromkeys(out))

def _pull(debug=False):
    data = []
    for sid in _station_ids():
        try:
            name_r = requests.post(WATERCHEM_URL.format(sid))
            if name_r.status_code != 200 or not name_r.text:
                continue
            name = name_r.text.replace('"', '').strip()
            csv_r = requests.get(CSV_BASE.format(name))
            csv_r.raise_for_status()
            txt = csv_r.text
            if txt.startswith("sep="):
                txt = "\n".join(txt.split("\n")[1:])
            try:
                df = pd.read_csv(io.StringIO(txt), sep=";")
            except Exception:
                df = pd.read_csv(io.StringIO(txt))
            if "DATE_COLL" in df.columns and "Parameter" in df.columns and "Result" in df.columns:
                data.append({"station_id": sid, "rows": df.to_dict("records")})
        except Exception as e:
            print(type(e).__name__ + ", skipping " + str(sid))
            if debug:
                traceback.print_exc()
    return data

def _process(data):
    groups = {}
    for blob in data:
        sid = blob["station_id"]
        for r in blob["rows"]:
            try:
                dt = pd.to_datetime(r["DATE_COLL"]).strftime("%Y-%m-%d %H:%M:%S")
                param = r.get("Parameter")
                col = PARAM_TO_COL.get(param)
                if not col:
                    continue
                val = r.get("Result")
                if val == "*NON-DETECT" or val is None:
                    continue
                val = float(val)
            except (KeyError, ValueError, TypeError):
                continue
            key = (sid, dt)
            if key not in groups:
                groups[key] = {"location": sid, "datetime": dt}
            groups[key][col] = val
    db = pd.DataFrame(groups.values()) if groups else pd.DataFrame(columns=["location", "datetime"])
    conn = sqlite3.connect(DB_PATH)
    db.to_sql("temp_staging", conn, if_exists="replace", index=False)
    conn.close()

def _push():
    files = sqlite_utils.Database(DB_PATH)
    files["water_quality"].upsert_all(files["temp_staging"].rows, alter=True, hash_id="unique_id")

def update():
    data = _pull()
    _process(data)
    _push()
    print("NDGIS water quality data update completed successfully")

if __name__ == "__main__":
    update()
