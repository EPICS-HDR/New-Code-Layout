'''
Author: Andrew Vu
Date: 2/19/2026
Purpose: NOAA weather data source following DANR pulling method pattern.
NOAA weather source. DANR framework: _pull -> _process (temp_staging) -> _push.
Uses NCEI CDO API. Set your API key in the environment before running:
  export NOAA_TOKEN=your_key
(or add NOAA_TOKEN to a .env file and load it; do not commit the key to git)
'''
import os
import requests
import pandas as pd
import sqlite3
import sqlite_utils
import traceback
from datetime import datetime, timedelta
from services.backend.datasources.config import DB_PATH

# (location_name, NCEI station id). Expand as needed.
NOAA_STATIONS = [
    ("Bismarck", "GHCND:USW00024011"),
    ("Williston/Basin", "GHCND:USW00024018"),
    ("Minot", "GHCND:USW00024021"),
]
BASE_URL = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
DATATYPES = {"TAVG": "avg_temp", "TMAX": "max_temp", "TMIN": "min_temp", "PRCP": "precipitation"}

def _pull(debug=False):
    data = []
    end = datetime.now()
    start = end - timedelta(days=365)
    s = start.strftime("%Y-%m-%d")
    e = end.strftime("%Y-%m-%d")
    token = os.environ.get("NOAA_TOKEN", "")
    headers = {"token": token} if token else {}
    for location, station_id in NOAA_STATIONS:
        try:
            r = requests.get(BASE_URL, params={"datasetid": "GHCND", "stationid": station_id, "startdate": s, "enddate": e, "limit": 1000}, headers=headers, timeout=30)
            data.append({"location": location, "raw": r.json() if r.ok else {}})
        except Exception as ex:
            print(type(ex).__name__ + ", skipping " + location)
            if debug:
                traceback.print_exc()
    return data

def _process(data):
    groups = {}
    for item in data:
        loc = item["location"]
        res = item["raw"].get("results") or []
        for row in res:
            try:
                dt = row.get("date")
                typ = row.get("datatype")
                col = DATATYPES.get(typ)
                if not col or not dt:
                    continue
                val = row.get("value")
                if val is None:
                    continue
                if typ == "PRCP":
                    val = val / 10.0  # tenths mm -> mm
                elif typ.startswith("T"):
                    val = val / 10.0  # tenths C -> C
                ts = f"{dt} 00:00:00"
                key = (loc, ts)
                if key not in groups:
                    groups[key] = {"location": loc, "datetime": ts}
                groups[key][col] = val
            except (TypeError, ValueError, KeyError):
                continue
    db = pd.DataFrame(groups.values()) if groups else pd.DataFrame(columns=["location", "datetime"])
    conn = sqlite3.connect(DB_PATH)
    db.to_sql("temp_staging", conn, if_exists="replace", index=False)
    conn.close()

def _push():
    files = sqlite_utils.Database(DB_PATH)
    files["noaa_weather"].upsert_all(files["temp_staging"].rows, alter=True, hash_id="unique_id")

def update():
    data = _pull()
    _process(data)
    _push()
    print("NOAA weather data update completed successfully")

if __name__ == "__main__":
    update()
