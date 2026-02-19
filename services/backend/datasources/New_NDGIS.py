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
PARAM_TO_COL = {k: SQL_CONVERSION[k] for k in SQL_CONVERSION if SQL_CONVERSION[k] in ["total_phosphorus", "total_kjeldahl_phosphorus", "nitrate_nitrite", "nitrate_forms_check", "nitrate_nitrite_dissolved", "total_kjeldahl_nitrogen", "tkn_dissolved", "total_nitrogen_dissolved", "e_coli", "total_nitrogen", "ph", "ammonia_nitrogen", "ammonia_nitrogen_dissolved", "ammonia_forms_check", "diss_ammonia_tkn_check", "dissolved_phosphorus"]}


def _station_ids(limit: int = 10):
    """
    Fetch a small set of NDGIS station IDs from ArcGIS.
    We only take the first `limit` IDs to keep runtime reasonable.
    """
    try:
        r = requests.get(
            ARCGIS_URL,
            params={
                "where": "1=1",
                "outFields": "SITE_ID",
                "returnGeometry": "false",
                "f": "json",
                "resultRecordCount": limit,
            },
            timeout=30,
        )
        r.raise_for_status()
        feats = r.json().get("features", [])
        ids = []
        for f in feats:
            sid = f.get("attributes", {}).get("SITE_ID")
            if sid and str(sid).strip():
                ids.append(str(sid).strip())
        # Deduplicate and cap to limit
        seen = set()
        out = []
        for sid in ids:
            if sid not in seen:
                seen.add(sid)
                out.append(sid)
            if len(out) >= limit:
                break
        return out
    except Exception:
        return []


def _pull(debug: bool = False):
    data = []
    station_ids = _station_ids(limit=10)
    if debug:
        print(f"Found {len(station_ids)} NDGIS stations: {station_ids}")
    for sid in station_ids:
        try:
            name_r = requests.post(WATERCHEM_URL.format(sid), timeout=30)
            if name_r.status_code != 200 or not name_r.text:
                if debug:
                    print(f"Station {sid}: HTTP {name_r.status_code} or empty response")
                continue
            name = name_r.text.replace('"', '').strip()
            if not name:
                if debug:
                    print(f"Station {sid}: Empty dataset name")
                continue
            csv_r = requests.get(CSV_BASE.format(name), timeout=30)
            csv_r.raise_for_status()
            txt = csv_r.text
            if txt.startswith("sep="):
                txt = "\n".join(txt.split("\n")[1:])
            try:
                df = pd.read_csv(io.StringIO(txt), sep=";")
            except Exception:
                df = pd.read_csv(io.StringIO(txt))
            if "DATE_COLL" in df.columns and "Parameter" in df.columns and "Result" in df.columns:
                if len(df) > 0:
                    data.append({"station_id": sid, "rows": df.to_dict("records")})
                    if debug:
                        print(f"Station {sid}: Loaded {len(df)} rows")
                elif debug:
                    print(f"Station {sid}: CSV has correct columns but no data rows")
            elif debug:
                print(f"Station {sid}: Missing required columns in CSV")
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
    data = _pull(debug=True)
    print(f"Pulled data from {len(data)} stations")
    _process(data)
    _push()
    print("NDGIS water quality data update completed successfully")

if __name__ == "__main__":
    update()
