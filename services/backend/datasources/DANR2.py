import requests
import json
from datetime import datetime
import pandas as pd
import sqlite3
import traceback

baseURLS = {"DANR" : "https://apps.sd.gov/NR92WQMAP/api/station/", "NDMES" : ""}
StationList = {"DANR" : ["SWLAZZZ2411A", "CAMPPOCP01", "SD_11904"]}
URL = baseURLS["DANR"]
stations = StationList["DANR"]

def _pull(debug=False):
    data = []
    for station in stations:
        try:
            data.append(requests.get(URL+station).json())

        except Exception as e:
            print(type(e).__name__+ ", skipping " + station)
            if debug:
                traceback.print_exc()

    return data

    
def _process(self):
    format_string = "%Y-%m-%dT%H:%M:%S"
    count = 0
    for station_index, station in enumerate(self.data):
        for sample in station['parameters']:           
            EpochTime = datetime.strptime(sample['sampleDate'], format_string)
            if EpochTime<=self.cutoff:
                count +=1


    del self.data[station_index]['parameters'][:count]
    
def _push(self):
    conn = sqlite3.connect('mydatabase.db')
    db = pd.DataFrame()
    for data in self.data:

        meta = [['station', key] for key in list(data['station'].keys())]
        temp = pd.json_normalize(data=data, record_path= 'parameters', meta=meta)
        db = pd.concat([db, temp])

    db.to_sql('mydatabase.db', conn, if_exists='replace', index=False)

    print(db)
    conn.close()

    
def main():
    data = _pull(True)
    print(data)

if (__name__ == "__main__"):
    main()
    
