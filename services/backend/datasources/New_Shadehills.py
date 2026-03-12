'''Shadehill data source. DANR framework: _pull -> _process (temp_staging) -> _push.'''
import requests
import pandas as pd
import sqlite3
import sqlite_utils
from datetime import datetime
from BackEnd.SourceFiles.config import SHADEHILL_DATASETS, SQL_CONVERSION, DB_PATH

URL = "https://www.usbr.gov/gp-bin/arcread.pl"
LOCATION = "Shadehill"

def _pull():
    data = []
    start = datetime(2021, 6, 24).strftime("%Y%m%d")
    end = datetime.now().strftime("%Y%m%d")
    sd = {"year": start[:4], "month": start[4:6], "day": start[6:8]}
    ed = {"year": end[:4], "month": end[4:6], "day": end[6:8]}
    for code, name in SHADEHILL_DATASETS.items():
        try:
            r = requests.post(URL, data={"st": "SHR", "by": sd["year"], "bm": sd["month"], "bd": sd["day"], "ey": ed["year"], "em": ed["month"], "ed": ed["day"], "pa": code})
            data.append({"name": name, "raw": r.text})
        except Exception:
            pass
    return data

import io

def _process(data):
    db = pd.DataFrame()
    for item in data:
        col = SQL_CONVERSION.get(item["name"])
        if not col:
            continue
        try:
            temp = pd.read_csv(io.StringIO(item["raw"]), skiprows=4, sep=r'\s+', names=["datetime", col], usecols=[0, 1])
            temp[col] = pd.to_numeric(temp[col], errors='coerce')
            temp = temp[temp[col] <= 900000] # preserve the existing filter logic
            temp["datetime"] = pd.to_datetime(temp["datetime"], format="%Y/%m/%d", errors="coerce").astype(str)
            if db.empty:
                db = temp
            else:
                db = db.merge(temp, on="datetime", how="outer")
        except Exception:
            pass
            
    if not db.empty:
        db["location"] = LOCATION
        conn = sqlite3.connect(DB_PATH)
        db.to_sql("temp_staging", conn, if_exists="replace", index=False)
        conn.close()

def _push():
    files = sqlite_utils.Database(DB_PATH)
    files["shadehill"].upsert_all(files["temp_staging"].rows, alter=True, hash_id="unique_id")

def update():
    _process(_pull())
    _push()

if __name__ == "__main__":
    update()
