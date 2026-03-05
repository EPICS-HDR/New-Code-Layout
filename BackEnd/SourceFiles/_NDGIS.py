'''
Author: Kartik Jariam
Date: 3/05/2026
Purpose: This is the NDGIS source file.
''' 
import subprocess
import sqlite_utils
from io import StringIO
import pandas as pd
from config import USACEConfig as config
import sqlite3
import traceback

def _pull(debug=False):
    data = []
    for station in config['stationList']:
        try:
            searchTerm = config['baseURL'] + station
            dataPoint = subprocess.run(['curl', searchTerm], text=True, capture_output=True)
            data.append([dataPoint, station])
        except Exception as e:
            print(type(e).__name__+ ", skipping " + station)
            if debug:
                traceback.print_exc()
    return data

def _process(data):
    conn = sqlite3.connect('mydatabase.db')
    db = pd.DataFrame()
    for dataPoint in data:
        io = StringIO(dataPoint[0].stdout)
        temp = pd.read_csv(io, skiprows=4, sep=r'\s{2,}', thousands=',', names=config['ColumnNames'], engine='python')
        metaData = dataPoint[1]
        temp['Station'] = metaData
        db = pd.concat([db, temp])
    db.to_sql('temp_staging', conn, if_exists='replace', index=False)
    conn.close()

def _push():
    files = sqlite_utils.Database('mydatabase.db')
    files["USACE"].upsert_all(files["temp_staging"].rows, alter=True, hash_id="unique_id")


def update():
    data = _pull()
    _process(data)
    _push()

if (__name__ == "__main__"):
    data= _pull(True)
    _process(data)