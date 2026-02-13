import requests
import pandas as pd
import sqlite3
import sqlite_utils
import traceback
from config import DANRConfig

def _pull(debug=False):
    data = []
    for station in DANRConfig['stationList']:
        try:
            searchTerm = DANRConfig['baseURL'] + station
            data.append(requests.get(searchTerm).json())
        except Exception as e:
            print(type(e).__name__+ ", skipping " + station)
            if debug:
                traceback.print_exc()
    return data
    
def _process(data):
    conn = sqlite3.connect('mydatabase.db')
    db = pd.DataFrame()
    for dataPoint in data:
        meta = [['station', key] for key in list(dataPoint['station'].keys())]
        temp = pd.json_normalize(data=dataPoint, record_path= 'parameters', meta=meta)
        db = pd.concat([db, temp])
    db.to_sql('temp_staging', conn, if_exists='replace', index=False)
    conn.close()

def _push():
    files = sqlite_utils.Database('mydatabase.db')
    files["DANR"].upsert_all(files["temp_staging"].rows, alter=True, hash_id="unique_id")

def update():
    data = _pull()
    _process(data)
    _push()

if (__name__ == "__main__"):
    update()