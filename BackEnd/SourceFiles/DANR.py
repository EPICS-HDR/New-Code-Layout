import requests
from datetime import datetime
import pandas as pd
import sqlite3
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
    format_string = DANRConfig['dateTimeFormat']
    count = 0
    for station_index, station in enumerate(data):
        for sample in station['parameters']:           
            EpochTime = datetime.strptime(sample['sampleDate'], format_string)
            if EpochTime<=self.cutoff:
                count +=1


    del self.data[station_index]['parameters'][:count]
    
def _push(data):
    conn = sqlite3.connect('mydatabase.db')
    db = pd.DataFrame()
    for data in self.data:

        meta = [['station', key] for key in list(data['station'].keys())]
        temp = pd.json_normalize(data=data, record_path= 'parameters', meta=meta)
        db = pd.concat([db, temp])

    db.to_sql('mydatabase.db', conn, if_exists='replace', index=False)

    print(db)
    conn.close()

def update():
    data = _pull()
    data = _process(data)
    _push(data)


def main():
    data = _pull(True)
    print(data)

if (__name__ == "__main__"):
    main()
    
