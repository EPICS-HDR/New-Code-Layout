'''
Author: Andrew Vu
Date: 2/19/2026
Purpose: Shadehill data source following DANR pulling method pattern.
'''
import requests
import pandas as pd
import sqlite3
import sqlite_utils
import traceback
from datetime import datetime
from services.backend.datasources.config import SHADEHILL_DATASETS, SQL_CONVERSION, DB_PATH

URL = "https://www.usbr.gov/gp-bin/arcread.pl"
LOCATION = "Shadehill"

def _pull(debug=False):
    data = []
    start = datetime(2021, 6, 24).strftime("%Y%m%d")
    end = datetime.now().strftime("%Y%m%d")
    sd = {"year": start[:4], "month": start[4:6], "day": start[6:8]}
    ed = {"year": end[:4], "month": end[4:6], "day": end[6:8]}
    for code, name in SHADEHILL_DATASETS.items():
        try:
            r = requests.post(URL, data={"st": "SHR", "by": sd["year"], "bm": sd["month"], "bd": sd["day"], "ey": ed["year"], "em": ed["month"], "ed": ed["day"], "pa": code})
            data.append({"code": code, "name": name, "raw": r.text})
        except Exception as e:
            print(type(e).__name__ + ", skipping " + name)
            if debug:
                traceback.print_exc()
    return data

def _process(data):
    recs = {}
    for item in data:
        col = SQL_CONVERSION.get(item["name"])
        if not col:
            continue
        for line in item["raw"].splitlines()[3:]:
            parts = line.split()
            if len(parts) >= 2:
                try:
                    y, m, d = parts[0].split("/")[:3]
                    ts = f"{y}-{m}-{d} 00:00:00"
                    val = float(parts[-1])
                    if val <= 900000:
                        recs.setdefault(ts, {"location": LOCATION, "datetime": ts})
                        recs[ts][col] = val
                except (ValueError, IndexError):
                    pass
    db = pd.DataFrame(recs.values()) if recs else pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    db.to_sql("temp_staging", conn, if_exists="replace", index=False)
    conn.close()

def _push():
    files = sqlite_utils.Database(DB_PATH)
    files["shadehill"].upsert_all(files["temp_staging"].rows, alter=True, hash_id="unique_id")

def update():
    data = _pull()
    _process(data)
    _push()
    print("Shadehill data update completed successfully")

if __name__ == "__main__":
    update()
