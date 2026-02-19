'''NOAA weather source. DANR framework: _pull -> _process (temp_staging) -> _push. Set NOAA_TOKEN env var.'''
import os
import requests
import pandas as pd
import sqlite3
import sqlite_utils
from datetime import datetime, timedelta
from services.backend.datasources.config import DB_PATH

NOAA_STATIONS = [("Bismarck", "GHCND:USW00024011"), ("Williston/Basin", "GHCND:USW00024018"), ("Minot", "GHCND:USW00024021")]
BASE_URL = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
DATATYPES = {"TAVG": "avg_temp", "TMAX": "max_temp", "TMIN": "min_temp", "PRCP": "precipitation"}

def _pull():
    data = []
    end = datetime.now()
    start = end - timedelta(days=365)
    headers = {"token": os.environ.get("NOAA_TOKEN", "")} if os.environ.get("NOAA_TOKEN") else {}
    for location, station_id in NOAA_STATIONS:
        try:
            r = requests.get(BASE_URL, params={"datasetid": "GHCND", "stationid": station_id, "startdate": start.strftime("%Y-%m-%d"), "enddate": end.strftime("%Y-%m-%d"), "limit": 1000}, headers=headers, timeout=30)
            data.append({"location": location, "raw": r.json() if r.ok else {}})
        except Exception:
            pass
    return data

def _process(data):
    groups = {}
    for item in data:
        loc = item["location"]
        for row in item["raw"].get("results") or []:
            try:
                dt = row.get("date")
                typ = row.get("datatype")
                col = DATATYPES.get(typ)
                if not col or not dt:
                    continue
                val = row.get("value")
                if val is None:
                    continue
                val = val / 10.0
                ts = f"{dt} 00:00:00"
                key = (loc, ts)
                groups.setdefault(key, {"location": loc, "datetime": ts})
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
    _process(_pull())
    _push()

if __name__ == "__main__":
    update()
