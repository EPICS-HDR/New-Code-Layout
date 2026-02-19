'''
USGS gauge data source. DANR framework: _pull -> _process (temp_staging) -> _push.
'''
import requests
import pandas as pd
import sqlite3
import sqlite_utils
import traceback
from datetime import datetime, date, timedelta
from services.backend.datasources.config import SQL_CONVERSION, DB_PATH

LOCATIONS = {
    'Hazen': ['06340500', 1], 'Stanton': ['06340700', 2], 'Washburn': ['06341000', 2],
    'Price': ['06342020', 2], 'Bismarck': ['06342500', 3], 'Schmidt': ['06349700', 2],
    'Judson': ['06348300', 1], 'Mandan': ['06349000', 1], 'Breien': ['06354000', 1],
    'Wakpala': ['06354881', 4], 'Little Eagle': ['06357800', 4], 'Cash': ['06356500', 4],
    'Whitehorse': ['06360500', 4]
}
QUERIES = {1: ('cb_00060=on&cb_00065=on&cb_63160=on', 56, 3), 2: ('cb_00065=on&cb_63160=on', 54, 2),
           3: ('cb_00010=on&cb_00060=on&cb_00065=on&cb_63160=on', 58, 4), 4: ('cb_00060=on&cb_00065=on', 54, 2)}
DS_MAP = {1: {4: "Elevation", 6: "Discharge", 8: "Gauge Height"},
          2: {4: "Elevation", 6: "Gauge Height"},
          3: {4: "Elevation", 6: "Water Temperature", 8: "Discharge", 10: "Gauge Height"},
          4: {4: "Discharge", 6: "Gauge Height"}}
JUDSON_MAP = {4: "Elevation", 6: "Gauge Height", 8: "Discharge"}

def _pull(debug=False):
    data = []
    end = date.today()
    start = end - timedelta(days=365)
    for loc, (code, cat) in LOCATIONS.items():
        query, lc, ns = QUERIES[cat]
        matrix = []
        chunk_start = start
        while chunk_start <= end:
            chunk_end = min(chunk_start + timedelta(days=60), end)
            url = f'https://waterdata.usgs.gov/nwis/uv?{query}&format=rdb&site_no={code}&legacy=1&begin_date={chunk_start.strftime("%Y-%m-%d")}&end_date={chunk_end.strftime("%Y-%m-%d")}'
            try:
                r = requests.get(url, timeout=30)
                lines = r.text.split("\n")
                if len(lines) > lc:
                    matrix.append(lines[lc].split("\t"))
                alt = 0
                for line in lines[lc+3:]:
                    if alt % 2 == 0:
                        matrix.append(line.strip().split("\t"))
                    alt += 1
            except Exception as e:
                print(type(e).__name__ + ", skipping " + loc)
                if debug:
                    traceback.print_exc()
            chunk_start = chunk_end + timedelta(days=1)
        if matrix:
            data.append({"location": loc, "category": cat, "matrix": matrix})
    return data

def _process(data):
    groups = {}
    for entry in data:
        loc, cat, mat = entry["location"], entry["category"], entry["matrix"]
        if not mat or len(mat) < 5:
            continue
        ds_map = JUDSON_MAP if (cat == 1 and loc == 'Judson') else DS_MAP[cat]
        for row in mat[4:]:
            if len(row) < max(ds_map.keys()) + 1:
                continue
            try:
                ts = row[2] if len(row) > 2 else None
                if not ts or len(ts.strip()) == 0:
                    continue
                ts = ts.strip()
                key = (loc, ts)
                if key not in groups:
                    groups[key] = {"location": loc, "datetime": ts}
                for idx, ds_name in ds_map.items():
                    if len(row) > idx:
                        val = row[idx].strip()
                        if val and val != 'Ice':
                            try:
                                v = float(val)
                                col = SQL_CONVERSION.get(ds_name)
                                if col:
                                    groups[key][col] = v
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
    data = _pull()
    _process(data)
    _push()
    print("USGS gauge data update completed successfully")

if __name__ == "__main__":
    update()
