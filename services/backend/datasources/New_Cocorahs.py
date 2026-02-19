'''CoCoRaHS data source. DANR framework: _pull -> _process (temp_staging) -> _push.'''
import requests
import pandas as pd
import sqlite3
import sqlite_utils
from datetime import date
from services.backend.datasources.config import COCORAHS_STATIONS, SQL_CONVERSION, DB_PATH

BASE_URL = "http://data.rcc-acis.org/StnData"
DATASETS = {'Precipitation': 1, 'Snowfall': 2, 'Snow Depth': 3}

def _pull():
    data = []
    end = date.today().strftime("%Y%m%d")
    for location, (station_id, start_date, *rest) in COCORAHS_STATIONS.items():
        try:
            params = f'{{"sid":"{station_id}","sdate":"{start_date}","edate":"{end}","elems":"pcpn,snow,snwd"}}'
            data.append(requests.get(f"{BASE_URL}?params={params}").json())
        except Exception:
            pass
    return data

def _process(data):
    recs = {}
    locations = list(COCORAHS_STATIONS.keys())
    for idx, entry in enumerate(data):
        if not entry or 'data' not in entry:
            continue
        loc = COCORAHS_STATIONS[locations[idx]][2] if len(COCORAHS_STATIONS[locations[idx]]) > 2 else locations[idx]
        for row in entry.get('data', []):
            if len(row) < 2:
                continue
            ts = f"{row[0]} 00:00:00"
            recs.setdefault(ts, {"location": loc, "datetime": ts})
            for ds_name, idx_val in DATASETS.items():
                if len(row) > idx_val and row[idx_val] not in (None, ""):
                    try:
                        val = float(row[idx_val])
                        col = SQL_CONVERSION.get(ds_name)
                        if col:
                            recs[ts][col] = val
                    except (ValueError, TypeError):
                        pass
    db = pd.DataFrame(recs.values()) if recs else pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    db.to_sql('temp_staging', conn, if_exists='replace', index=False)
    conn.close()

def _push():
    files = sqlite_utils.Database(DB_PATH)
    files["cocorahs"].upsert_all(files["temp_staging"].rows, alter=True, hash_id="unique_id")

def update():
    _process(_pull())
    _push()

if __name__ == "__main__":
    update()
