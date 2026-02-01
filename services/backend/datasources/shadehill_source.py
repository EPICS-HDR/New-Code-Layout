"""
================================================================================
FILE: shadehill_source.py
AUTHOR: Andrew Vu
CREATED: 2026-01-29 
PURPOSE: 
    Fetches, processes, and stores data from the Shadehill Reservoir API.
    Uses a function-based approach with pandas to convert data to DataFrame
    and store in SQLite.
    
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
    # Navigate up 4 levels: shadehill_source.py -> datasources -> backend -> services -> project_root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file_path))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

# ============================================================================
# IMPORTS
# ============================================================================
import requests
import json
from datetime import datetime
import pandas as pd
import sqlite3
import traceback
from services.backend.datasources.config import SHADEHILL_DATASETS, SQL_CONVERSION, DB_PATH

# ============================================================================
# CONSTANTS
# ============================================================================
URL = "https://www.usbr.gov/gp-bin/arcread.pl"  # Shadehill API endpoint
LOCATION = "Shadehill"
datasets = SHADEHILL_DATASETS

# ============================================================================
# HELPER FUNCTION: Parse date string
# ============================================================================
def _parse_date_string(date_str):
    """
    Convert date string 'YYYYMMDD' to dict with year, month, day.
    API expects dates in separate fields, not a single string.
    
    Args:
        date_str (str): Date in 'YYYYMMDD' format (e.g., '20210624')
    
    Returns:
        dict: {'year': '2021', 'month': '06', 'day': '24'} or None if invalid
    """
    if len(date_str) == 8:
        return {
            'year': date_str[:4],
            'month': date_str[4:6],
            'day': date_str[6:8]
        }
    return None

# ============================================================================
# FUNCTION: Pull data from API
# ============================================================================
def _pull(start_date_str, end_date_str, debug=False):
    """
    Fetch raw data from Shadehill API for all datasets.
    
    Args:
        start_date_str (str): Start date in 'YYYYMMDD' format
        end_date_str (str): End date in 'YYYYMMDD' format
        debug (bool): If True, print full error tracebacks
    
    Returns:
        list: List of dicts with 'dataset_code', 'dataset_name', 'raw_data'
    """
    data = []
    start_date = _parse_date_string(start_date_str)
    end_date = _parse_date_string(end_date_str)
    
    if not start_date or not end_date:
        print("Invalid date format. Expected YYYYMMDD")
        return data
    
    for dataset_code, dataset_name in datasets.items():
        try:
            form_data = {
                'st': 'SHR',                    # Station code
                'by': start_date['year'],        # Begin year
                'bm': start_date['month'],       # Begin month
                'bd': start_date['day'],         # Begin day
                'ey': end_date['year'],          # End year
                'em': end_date['month'],         # End month
                'ed': end_date['day'],           # End day
                'pa': dataset_code,              # Parameter code
            }
            
            response = requests.post(URL, data=form_data)
            
            if response.status_code == 200:
                data.append({
                    'dataset_code': dataset_code,
                    'dataset_name': dataset_name,
                    'raw_data': response.text
                })
            else:
                print(f"Error fetching {dataset_name}: HTTP {response.status_code}")
                
        except Exception as e:
            print(type(e).__name__ + f", skipping {dataset_name}")
            if debug:
                traceback.print_exc()
    
    return data

# ============================================================================
# FUNCTION: Process raw data into structured format
# ============================================================================
def _process(data, cutoff=None):
    """
    Parse raw text data from API into structured records.
    
    API format: First 3 lines are headers, then each line has date (YYYY/MM/DD) and value.
    Groups all datasets by timestamp (one record per timestamp).
    Filters invalid values (> 900000).
    
    Args:
        data (list): List of dicts from _pull() with 'raw_data', 'dataset_name', etc.
        cutoff (datetime, optional): Skip records with datetime <= cutoff (for incremental updates)
    
    Returns:
        list: List of dicts, one per timestamp with all dataset values
    """
    all_records = {}  # {timestamp: {location, datetime, field1, field2, ...}}
    
    for item in data:
        raw_data = item['raw_data']
        dataset_name = item['dataset_name']
        sql_field = SQL_CONVERSION.get(dataset_name)  # Map to SQL column name
        
        if not sql_field:
            continue
        
        lines = raw_data.splitlines()
        
        for i, line in enumerate(lines):
            if i >= 3:  # Skip header lines
                parts = line.split()
                
                if len(parts) >= 2:
                    date_parts = parts[0].strip().split("/")
                    
                    if len(date_parts) == 3:
                        year, month, day = date_parts[0], date_parts[1], date_parts[2]
                        timestamp = f"{year}-{month}-{day} 00:00"
                        
                        # Skip records before cutoff date (for incremental updates)
                        if cutoff:
                            try:
                                record_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
                                if record_time <= cutoff:
                                    continue
                            except:
                                pass
                        
                        # Initialize record for this timestamp if not exists
                        if timestamp not in all_records:
                            all_records[timestamp] = {
                                'location': LOCATION,
                                'datetime': timestamp
                            }
                        
                        # Parse and store the value
                        try:
                            value = float(parts[-1])
                            # API uses values > 900000 to indicate invalid/missing data
                            if value <= 900000:
                                all_records[timestamp][sql_field] = value
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
    db.to_sql('shadehill', conn, if_exists='replace', index=False)
    
    print(f"Successfully stored {len(db)} records")
    print(db)
    conn.close()

# ============================================================================
# MAIN FUNCTION
# ============================================================================
def main():
    """Orchestrate the data pipeline: pull -> process -> push"""
    start_date = "20210624"
    
    # Use today's date as end date to get most recent data
    today = datetime.now()
    end_date = today.strftime('%Y%m%d')
    
    data = _pull(start_date, end_date, debug=True)
    print(f"Pulled {len(data)} datasets")
    
    records = _process(data)
    print(f"Processed {len(records)} records")
    
    _push(records)

# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    main()
