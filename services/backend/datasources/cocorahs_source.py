"""
================================================================================
FILE: cocorahs_source.py
AUTHOR: Andrew Vu
CREATED: 2026-01-29 
PURPOSE: 
    Fetches, processes, and stores CoCoRaHS (Community Collaborative Rain, 
    Hail & Snow Network) precipitation and snow data. Uses a function-based 
    approach with pandas to convert data to DataFrame and store in SQLite.
    
    Workflow: _pull() -> _process() -> _push()
================================================================================
"""

# ============================================================================
# PATH SETUP - Handle imports when file is run directly
# ============================================================================
import sys
import os

# Add project root to path when run directly (so it can find 'services' module)
if __name__ == "__main__":
    current_file_path = os.path.abspath(__file__)
    # Navigate up 4 levels: cocorahs_source.py -> datasources -> backend -> services -> project_root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file_path))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

# ============================================================================
# IMPORTS
# ============================================================================
import requests
import json
from datetime import datetime, date
import pandas as pd
import sqlite3
import traceback
from services.backend.datasources.config import COCORAHS_STATIONS, SQL_CONVERSION, DB_PATH

# ============================================================================
# CONSTANTS
# ============================================================================
BASE_URL = "http://data.rcc-acis.org/StnData"
stations = COCORAHS_STATIONS

# Dataset mapping: name -> index in API response array
# API returns: [date, precipitation, snowfall, snow_depth]
DATASETS = {
    'Precipitation': 1,
    'Snowfall': 2,
    'Snow Depth': 3,
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def _build_api_url(station_id, start_date, end_date):
    """
    Build CoCoRaHS API URL with parameters.
    
    Args:
        station_id (str): CoCoRaHS station ID (e.g., 'SDFK0006')
        start_date (str): Start date in 'YYYYMMDD' format
        end_date (str): End date in 'YYYYMMDD' format
    
    Returns:
        str: Complete API URL
    """
    params = f'{{"sid":"{station_id}","sdate":"{start_date}","edate":"{end_date}","elems":"pcpn,snow,snwd"}}'
    return f"{BASE_URL}?params={params}"

def _format_timestamp(date_str):
    """
    Convert date string from 'YYYY-MM-DD' to 'YYYY-MM-DD HH:MM:SS' format.
    
    Args:
        date_str (str): Date in 'YYYY-MM-DD' format
    
    Returns:
        str: Formatted datetime string
    """
    year, month, day = date_str.split("-")
    return f"{year}-{month}-{day} 00:00:00"

# ============================================================================
# FUNCTION: Pull data from API
# ============================================================================
def _pull(debug=False):
    """
    Fetch raw data from CoCoRaHS API for all configured stations.
    
    Args:
        debug (bool): If True, print full error tracebacks
    
    Returns:
        list: List of dicts with 'location', 'dict_location', 'raw' (JSON data)
    """
    data = []
    end_date_str = date.today().strftime("%Y%m%d")
    
    for location, station_info in stations.items():
        station_id = station_info[0]      # Station ID (e.g., 'SDFK0006')
        start_date_str = station_info[1]  # Start date for this station
        dict_location = station_info[2] if len(station_info) > 2 else location  # DB location name
        
        url = _build_api_url(station_id, start_date_str, end_date_str)
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            results_dict = json.loads(response.text)
        except Exception as e:
            print(type(e).__name__ + f", skipping {location}")
            if debug:
                traceback.print_exc()
            results_dict = None
        
        data.append({
            'location': location,
            'dict_location': dict_location,
            'raw': results_dict
        })
    
    return data

# ============================================================================
# FUNCTION: Process raw data into structured format
# ============================================================================
def _process(data, cutoff=None):
    """
    Parse raw JSON data from API into structured records.
    
    API returns JSON with 'data' array: [[date, precipitation, snowfall, snow_depth], ...]
    Groups all datasets by location and timestamp (one record per location/timestamp).
    
    Args:
        data (list): List of dicts from _pull() with 'raw', 'location', 'dict_location'
        cutoff (datetime, optional): Skip records with datetime <= cutoff
    
    Returns:
        list: List of dicts, one per location/timestamp with all dataset values
    """
    all_records = {}  # {(location, timestamp): {location, datetime, precipitation, snowfall, snow_depth}}
    
    for entry in data:
        raw = entry.get('raw') or {}
        data_list = raw.get('data') or []  # API data array
        location = entry.get('dict_location')  # Use dict_location for DB
        
        if not data_list:
            continue
        
        for row in data_list:
            if not row or len(row) < 2:
                continue
            
            date_str = row[0]  # First element is date
            timestamp = _format_timestamp(date_str)
            
            # Skip records before cutoff date (for incremental updates)
            if cutoff:
                try:
                    record_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    if record_time <= cutoff:
                        continue
                except:
                    pass
            
            # Create unique key for location + timestamp
            key = (location, timestamp)
            
            # Initialize record for this location/timestamp if not exists
            if key not in all_records:
                all_records[key] = {
                    'location': location,
                    'datetime': timestamp
                }
            
            # Extract values for each dataset
            for ds_name, idx in DATASETS.items():
                if len(row) > idx:
                    val = row[idx]
                    try:
                        value = float(val) if val not in (None, "") else None
                        if value is not None:
                            sql_field = SQL_CONVERSION.get(ds_name)
                            if sql_field:
                                all_records[key][sql_field] = value
                    except:
                        pass  # Skip invalid values
    
    return list(all_records.values())

# ============================================================================
# FUNCTION: Push data to SQLite database
# ============================================================================
def _push(records):
    """
    Store processed records in SQLite using pandas.
    
    Args:
        records (list): List of dicts from _process()
    """
    if not records:
        print("No records to push")
        return
    
    # Use DB_PATH from config to ensure correct database location
    conn = sqlite3.connect(DB_PATH)
    
    # Convert to DataFrame and write to database
    db = pd.DataFrame(records)
    db.to_sql('cocorahs', conn, if_exists='replace', index=False)
    
    print(f"Successfully stored {len(db)} records")
    print(db)
    conn.close()

# ============================================================================
# MAIN FUNCTION
# ============================================================================
def main():
    """Orchestrate the data pipeline: pull -> process -> push"""
    data = _pull(debug=True)
    print(f"Pulled {len(data)} stations")
    
    records = _process(data)
    print(f"Processed {len(records)} records")
    
    _push(records)

# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    main()
