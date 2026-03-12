'''NDMES (NDAWN) mesonet source. DANR framework: _pull -> _process (temp_staging) -> _push.'''
import io
import requests
import pandas as pd
import sqlite3
import sqlite_utils
from datetime import datetime, timedelta
from BackEnd.SourceFiles.config import NDMES_STATIONS, DB_PATH

BASE_URL = "https://ndawn.ndsu.nodak.edu/table.csv"
# CSV column -> mesonet table column
COL_MAP = {
    "Avg Air Temp": "avg_air_temp",
    "Avg Rel Hum": "avg_rel_hum",
    "Avg Bare Soil Temp": "avg_bare_soil_temp",
    "Avg Turf Soil Temp": "avg_turf_soil_temp",
    "Max Wind Speed": "max_wind_speed",
    "Avg Wind Speed": "max_wind_speed",
    "Avg Wind Dir": "avg_wind_dir",
    "Avg Sol Rad": "total_solar_rad",
    "Total Rainfall": "total_rainfall",
    "Avg Baro Press": "avg_bar_pressure",
    "Avg Dew Point": "avg_dew_point",
    "Avg Wind Chill": "avg_wind_chill",
}

def _pull():
    data = []
    end = datetime.now()
    start = end - timedelta(days=365)
    s, e = start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
    for location, (station, _) in NDMES_STATIONS.items():
        try:
            r = requests.get(BASE_URL, params={"ttype": "hourly", "station": station, "begin_date": s, "end_date": e}, timeout=60)
            if r.ok:
                data.append({"location": location, "raw": r.text})
        except Exception:
            pass
    return data

def _process(data):
    db = pd.DataFrame()
    for item in data:
        try:
            temp = pd.read_csv(io.StringIO(item["raw"]), skiprows=[0, 1, 2, 4])
            temp["datetime"] = pd.to_datetime(temp[["Year", "Month", "Day", "Hour"]].rename(columns={"Hour": "hour"}), format="%Y-%m-%d %H", errors="coerce").astype(str)
            temp["location"] = item["location"]
            if "Avg Wind Speed" in temp.columns: temp = temp.drop(columns=["Avg Wind Speed"])
            temp = temp.rename(columns=COL_MAP)
            
            cols_to_keep = list(set(COL_MAP.values())) + ["location", "datetime"]
            temp = temp[[c for c in cols_to_keep if c in temp.columns]]
            
            db = pd.concat([db, temp], ignore_index=True)
        except Exception:
            continue
    conn = sqlite3.connect(DB_PATH)
    db.to_sql("temp_staging", conn, if_exists="replace", index=False)
    conn.close()

def _push():
    files = sqlite_utils.Database(DB_PATH)
    files["mesonet"].upsert_all(files["temp_staging"].rows, alter=True, hash_id="unique_id")

def update():
    _process(_pull())
    _push()

if __name__ == "__main__":
    update()
