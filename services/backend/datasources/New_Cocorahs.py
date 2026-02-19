'''
Author: Andrew Vu
Date: 2/19/2026
Purpose: CoCoRaHS data source following DANR pulling method pattern.
'''
import requests
import pandas as pd
import sqlite3
import sqlite_utils
import json
import traceback
from datetime import date
from services.backend.datasources.config import COCORAHS_STATIONS, SQL_CONVERSION, DB_PATH

BASE_URL = "http://data.rcc-acis.org/StnData"
DATASETS = {'Precipitation': 1, 'Snowfall': 2, 'Snow Depth': 3}

def _build_api_url(station_id, start_date, end_date):
    params = f'{{"sid":"{station_id}","sdate":"{start_date}","edate":"{end_date}","elems":"pcpn,snow,snwd"}}'
    return f"{BASE_URL}?params={params}"

def _format_timestamp(date_str):
    year, month, day = date_str.split("-")
    return f"{year}-{month}-{day} 00:00:00"

def _pull(debug=False):
    data = []
    end_date_str = date.today().strftime("%Y%m%d")
    for location, station_info in COCORAHS_STATIONS.items():
        station_id = station_info[0]
        start_date_str = station_info[1]
        try:
            url = _build_api_url(station_id, start_date_str, end_date_str)
            data.append(requests.get(url).json())
        except Exception as e:
            print(type(e).__name__ + ", skipping " + location)
            if debug:
                traceback.print_exc()
    return data

def _process(data):
    conn = sqlite3.connect(DB_PATH)
    db = pd.DataFrame()
    for idx, entry in enumerate(data):
        if not entry or 'data' not in entry:
            continue
        location = list(COCORAHS_STATIONS.keys())[idx]
        dict_location = COCORAHS_STATIONS[location][2] if len(COCORAHS_STATIONS[location]) > 2 else location
        for row in entry.get('data', []):
            if not row or len(row) < 2:
                continue
            record = {'location': dict_location, 'datetime': _format_timestamp(row[0])}
            for ds_name, idx_val in DATASETS.items():
                if len(row) > idx_val:
                    val = row[idx_val]
                    try:
                        value = float(val) if val not in (None, "") else None
                        if value is not None:
                            sql_field = SQL_CONVERSION.get(ds_name)
                            if sql_field:
                                record[sql_field] = value
                    except:
                        pass
            if len(record) > 2:  # Has data beyond location and datetime
                db = pd.concat([db, pd.DataFrame([record])], ignore_index=True)
    db.to_sql('temp_staging', conn, if_exists='replace', index=False)
    conn.close()

def _push():
    files = sqlite_utils.Database(DB_PATH)
    files["cocorahs"].upsert_all(files["temp_staging"].rows, alter=True, hash_id="unique_id")

def update():
    data = _pull()
    _process(data)
    _push()
    print("CoCoRaHS data update completed successfully")

if __name__ == "__main__":
    update()
