'''USGS gauge source. DANR framework: _pull -> _process (temp_staging) -> _push.'''
import requests
import pandas as pd
import sqlite3
import sqlite_utils
from datetime import date, timedelta
from BackEnd.SourceFiles.config import SQL_CONVERSION, DB_PATH, USGS_LOCATIONS as LOCATIONS

QUERIES = {1: ('cb_00060=on&cb_00065=on&cb_63160=on', 56), 2: ('cb_00065=on&cb_63160=on', 54), 3: ('cb_00010=on&cb_00060=on&cb_00065=on&cb_63160=on', 58), 4: ('cb_00060=on&cb_00065=on', 54)}
DS_MAP = {1: {4: "Elevation", 6: "Discharge", 8: "Gauge Height"}, 2: {4: "Elevation", 6: "Gauge Height"}, 3: {4: "Elevation", 6: "Water Temperature", 8: "Discharge", 10: "Gauge Height"}, 4: {4: "Discharge", 6: "Gauge Height"}}
JUDSON_MAP = {4: "Elevation", 6: "Gauge Height", 8: "Discharge"}

def _pull():
    data = []
    end = date.today()
    start = end - timedelta(days=365)
    for loc, (code, cat) in LOCATIONS.items():
        query, lc = QUERIES[cat]
        matrix = []
        chunk_start = start
        while chunk_start <= end:
            chunk_end = min(chunk_start + timedelta(days=60), end)
            try:
                url = f'https://waterdata.usgs.gov/nwis/uv?{query}&format=rdb&site_no={code}&legacy=1&begin_date={chunk_start.strftime("%Y-%m-%d")}&end_date={chunk_end.strftime("%Y-%m-%d")}'
                r = requests.get(url, timeout=30)
                lines = r.text.split("\n")
                if len(lines) > lc:
                    matrix.append(lines[lc].split("\t"))
                for i, line in enumerate(lines[lc+3:]):
                    if i % 2 == 0:
                        matrix.append(line.strip().split("\t"))
            except Exception:
                pass
            chunk_start = chunk_end + timedelta(days=1)
        if matrix:
            data.append({"location": loc, "category": cat, "matrix": matrix})
    return data

def _process(data):
    groups = {}
    for entry in data:
        loc, cat, mat = entry["location"], entry["category"], entry["matrix"]
        if len(mat) < 5:
            continue
        ds_map = JUDSON_MAP if (cat == 1 and loc == 'Judson') else DS_MAP[cat]
        for row in mat[4:]:
            if len(row) < max(ds_map.keys()) + 1:
                continue
            try:
                ts = row[2].strip() if len(row) > 2 and row[2].strip() else None
                if not ts:
                    continue
                key = (loc, ts)
                groups.setdefault(key, {"location": loc, "datetime": ts})
                for idx, ds_name in ds_map.items():
                    if len(row) > idx:
                        val = row[idx].strip()
                        if val and val != 'Ice':
                            try:
                                col = SQL_CONVERSION.get(ds_name)
                                if col:
                                    groups[key][col] = float(val)
                            except (ValueError, TypeError):
                                pass
            except (IndexError, KeyError):
                continue
    db = pd.DataFrame(groups.values()) if groups else pd.DataFrame(columns=["location", "datetime"])
    conn = sqlite3.connect(DB_PATH)
    db.to_sql("temp_staging", conn, if_exists="replace", index=False)
    conn.close()

def _push():
    files = sqlite_utils.Database(DB_PATH)
    files["usgs"].upsert_all(files["temp_staging"].rows, alter=True, hash_id="unique_id")

def update():
    _process(_pull())
    _push()

if __name__ == "__main__":
    update()
