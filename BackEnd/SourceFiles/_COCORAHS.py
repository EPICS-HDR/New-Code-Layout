'''
Author: Kartik Jariam
Date: 3/05/2026
Purpose: This is the COCORAHS source file.
''' 
import requests
import sqlite_utils
from io import StringIO
import pandas as pd
from config import COCORAHSConfig as config
import sqlite3
from datetime import date
import traceback

def _pull(debug=False):
    data = []
    end = date.today().strftime("%Y%m%d")
    elements = ",".join(config['Elements'])
    for station, (station_id, start_date) in config['stationList'].items():
        try:
            params = f'{{"sid":"{station_id}","sdate":"{start_date}","edate":"{end}","elems":"{elements}"}}'
            searchTerm = f"{config['baseURL']}{params}"            
            data.append(requests.get(searchTerm).json())

        except Exception as e:
            print(type(e).__name__+ ", skipping " + station)
            if debug:
                traceback.print_exc()
    return data

def _process(data):
    conn = sqlite3.connect('database.db')
    db = pd.DataFrame()
    for stationData in data:
        temp = pd.json_normalize(stationData)
        temp = temp.explode('data').reset_index(drop=True)
        temp[['date', 'v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7']] = pd.DataFrame(temp['data'].tolist(), index=temp.index) #TO DO: replace v1 ... v7
        temp = temp.drop(columns='data')
        temp[['latitude', 'longitude']] = pd.DataFrame(temp['meta.ll'].tolist(), index=temp.index) #TO DO: replace v1 ... v7
        temp = temp.drop(columns='meta.ll')
        temp[['sid1', 'sid2']] = pd.DataFrame(temp['meta.sids'].tolist(), index=temp.index) #TO DO: replace v1 ... v7
        temp = temp.drop(columns='meta.sids')
        db = pd.concat([db, temp])

    print(db)
        
    db.to_sql('temp_staging', conn, if_exists='replace', index=False)
    conn.close()

def _push():
    files = sqlite_utils.Database('database.db')
    files["COCORAHS"].upsert_all(files["temp_staging"].rows, alter=True, hash_id="unique_id") #TO DO: Remove hash_id?


def update():
    data = _pull()
    _process(data)
    _push()

if (__name__ == "__main__"):
    update()