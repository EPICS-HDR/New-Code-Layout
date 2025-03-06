import pandas as pd
import requests
import os


# Send a POST request and get the response text (dataset name)
def get_dataset_name(url):
    response = requests.post(url)
    if response.status_code == 200 and response.text:
        return response.text.replace('"', '')  # Remove quotes from dataset name
    else:
        print(f"Error: Unable to fetch dataset name from {url}. Status code: {response.status_code}")
        return None


# Fetch station data and filter water chemical data
def fetch_and_filter_data(station_id, water_chemicals):
    waterchem_url = f"https://deq.nd.gov/Webservices_SWDataApp/DownloadStationsData/GetStationsWaterChemData/{station_id}"
    waterchem_dataset_name = get_dataset_name(waterchem_url)

    if waterchem_dataset_name:
        waterchem_data_url = f"https://deq.nd.gov/WQ/3_Watershed_Mgmt/SWDataApp/downloaddata/{waterchem_dataset_name}.csv"
        data = pd.read_csv(waterchem_data_url)

        filtered_dataframes = {}
        for chemical in water_chemicals:
            if chemical in data['Parameter'].values:
                chemical_data = data[data['Parameter'] == chemical]
                numeric_columns = ['Min', 'Max', 'Median', 'Mean', 'Std Dev', 'Pct 10th', 'Pct 25th', 'Pct 75th',
                                   'Pct 90th']
                filtered_data = chemical_data.loc[~(chemical_data[numeric_columns].fillna(0) == 0).all(axis=1)]
                filtered_dataframes[chemical] = filtered_data
                print(f"Filtered data for {chemical} retrieved successfully.")
        return filtered_dataframes
    return None


# Read station IDs from an Excel masterlist
station_ids = []
masterlist_path = r'INSERT THE PATH TO THE MASTERLIST HERE'

try:
    df = pd.read_excel(masterlist_path)
    for id in df.iloc[:, 0]:  # Adjust column index based on where station IDs are stored
        station_ids.append(id)
except FileNotFoundError:
    print(f"Error: Masterlist file not found at {masterlist_path}")
except Exception as e:
    print(f"Error reading masterlist: {e}")

water_chemicals = ['Phosphorus (Total) (P)', 'Phosphorus (Total Kjeldahl) (P)', 'Nitrate + Nitrite (N)',
                   'Nitrate Forms Check', 'Nitrate + Nitrite (N) Dis', 'Nitrogen (Total Kjeldahl)',
                   'Nitrogen (TKN-Dissolved)',
                   'Nitrogen (Total-Dis)', 'E.coli', 'Nitrogen (Total)', 'pH', 'Ammonia (N)', 'Ammonia (N)-Dissolved',
                   'Ammonia Forms Check', 'Diss Ammonia TKN Check', 'Dissolved Phosphorus as P']

for station_id in station_ids:
    fetch_and_filter_data(station_id, water_chemicals)
