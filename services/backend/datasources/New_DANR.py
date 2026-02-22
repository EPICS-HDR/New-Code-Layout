'''DANR source. DANR framework: _pull -> _process (temp_staging) -> _push.'''
import requests
import pandas as pd
import sqlite3
import sqlite_utils
from BackEnd.SourceFiles.config import DANRConfig, DB_PATH

def _pull():
    data = []
    for station in DANRConfig['stationList']:
        try:
            r = requests.get(DANRConfig['baseURL'] + station, timeout=30)
            data.append(r.json())
        except Exception as e:
            print(type(e).__name__ + ", skipping " + station)
    return data

def _process(data):
    db = pd.DataFrame()
    for dataPoint in data:
        meta = [['station', key] for key in list(dataPoint['station'].keys())]
        temp = pd.json_normalize(data=dataPoint, record_path='parameters', meta=meta)
        db = pd.concat([db, temp])
    conn = sqlite3.connect(DB_PATH)
    db.to_sql('temp_staging', conn, if_exists='replace', index=False)
    conn.close()

def _push():
    files = sqlite_utils.Database(DB_PATH)
    files["DANR"].upsert_all(files["temp_staging"].rows, alter=True, hash_id="unique_id")

def update():
    _process(_pull())
    _push()

if __name__ == "__main__":
    update()
