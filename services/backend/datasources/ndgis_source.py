# ndgis_source.py
from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
import os
import requests
from typing import Dict, List, Tuple, Any, Optional, Union
import pandas as pd
import io
from base import DataSource  # Import the base class
# from services.backend.datasources.utils import DataParser # Not directly used in your original pullNDGIS
# from services.backend.datasources.utils import DateHelper # Not directly used in your original pullNDGIS


class NDGISWaterChem(DataSource):
    def __init__(self, name="NDGIS Water Chemistry", data_type="water_quality"):
        super().__init__(name, data_type)
        self.masterlist_path = r'INSERT THE PATH TO THE MASTERLIST HERE'  # Path to your Excel masterlist

    def _get_dataset_name(self, url):
        """Sends a POST request and gets the response text (dataset name)."""
        response = requests.post(url)
        if response.status_code == 200 and response.text:
            return response.text.replace('"', '')  # Remove quotes from dataset name
        else:
            print(f"Error: Unable to fetch dataset name from {url}. Status code: {response.status_code}")
            return None

    def fetch(self, location=None, dataset=None, start_date=None, end_date=None):
        """
        Fetches water chemical data for specified station IDs and chemicals.

        Args:
            location (list, optional): A list of station IDs to fetch data for. Defaults to None (fetches all from masterlist).
            dataset (list, optional): A list of water chemical parameters to fetch. Defaults to a predefined list.
            start_date (datetime.date, optional): Not used in this implementation. Defaults to None.
            end_date (datetime.date, optional): Not used in this implementation. Defaults to None.

        Returns:
            dict: A dictionary where keys are station IDs and values are dictionaries of
                  chemical parameters and their corresponding DataFrames. Returns None on error.
        """
        station_ids = []
        if location:
            station_ids = location
        else:
            try:
                df = pd.read_excel(self.masterlist_path)
                # Assuming station IDs are in the first column (index 0)
                if not df.empty:
                    station_ids = df.iloc[:, 0].astype(str).tolist()
                else:
                    print(f"Warning: No station IDs found in the masterlist at {self.masterlist_path}")
                    return None
            except FileNotFoundError:
                print(f"Error: Masterlist file not found at {self.masterlist_path}")
                return None
            except Exception as e:
                print(f"Error reading masterlist: {e}")
                return None

        water_chemicals = dataset if dataset else [
            'Phosphorus (Total) (P)', 'Phosphorus (Total Kjeldahl) (P)', 'Nitrate + Nitrite (N)',
            'Nitrate Forms Check', 'Nitrate + Nitrite (N) Dis', 'Nitrogen (Total Kjeldahl)',
            'Nitrogen (TKN-Dissolved)',
            'Nitrogen (Total-Dis)', 'E.coli', 'Nitrogen (Total)', 'pH', 'Ammonia (N)', 'Ammonia (N)-Dissolved',
            'Ammonia Forms Check', 'Diss Ammonia TKN Check', 'Dissolved Phosphorus as P'
        ]

        all_station_data = {}
        for station_id in station_ids:
            print(f"Fetching data for station ID: {station_id}")
            waterchem_url = f"https://deq.nd.gov/Webservices_SWDataApp/DownloadStationsData/GetStationsWaterChemData/{station_id}"
            waterchem_dataset_name = self._get_dataset_name(waterchem_url)

            if waterchem_dataset_name:
                waterchem_data_url = f"https://deq.nd.gov/WQ/3_Watershed_Mgmt/SWDataApp/downloaddata/{waterchem_dataset_name}.csv"
                try:
                    response = requests.get(waterchem_data_url)
                    response.raise_for_status()  # Raise an exception for bad status codes
                    data = pd.read_csv(io.StringIO(response.text))
                    filtered_dataframes = {}
                    for chemical in water_chemicals:
                        if chemical in data['Parameter'].values:
                            chemical_data = data[data['Parameter'] == chemical]
                            numeric_columns = ['Min', 'Max', 'Median', 'Mean', 'Std Dev', 'Pct 10th', 'Pct 25th', 'Pct 75th',
                                               'Pct 90th']
                            filtered_data = chemical_data.loc[~(chemical_data[numeric_columns].fillna(0) == 0).all(axis=1)]
                            filtered_dataframes[chemical] = filtered_data
                            print(f"  Filtered data for {chemical} retrieved successfully for station {station_id}.")
                    if filtered_dataframes:
                        all_station_data[station_id] = filtered_dataframes
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching CSV data for station {station_id}: {e}")
                except pd.errors.EmptyDataError:
                    print(f"Warning: No data found in the CSV file for station {station_id}.")
                except Exception as e:
                    print(f"An unexpected error occurred while processing data for station {station_id}: {e}")
            else:
                print(f"Skipping station {station_id} due to missing dataset name.")

        return all_station_data

    def process(self, raw_data=None, location=None, dataset=None):
        """
        Processes the raw data (DataFrames) into a standardized format of times and values.

        Args:
            raw_data (dict): A dictionary where keys are station IDs and values are dictionaries
                             of chemical parameters and their corresponding DataFrames.
            location (list, optional): Not directly used here as location info is within raw_data. Defaults to None.
            dataset (list, optional): Not directly used here as dataset info is within raw_data. Defaults to None.

        Returns:
            tuple: A tuple containing two dictionaries:
                   - times: A dictionary where keys are (station_id, chemical) tuples and values are lists of timestamps.
                   - values: A dictionary where keys are (station_id, chemical) tuples and values are lists of corresponding values.
        """
        if raw_data is None:
            return {}, {}

        processed_times = {}
        processed_values = {}

        for station_id, chemical_data in raw_data.items():
            for chemical, df in chemical_data.items():
                if not df.empty:
                    # Assuming 'SampleDate' is the timestamp column and a relevant value column exists.
                    # You'll need to identify the appropriate value column(s) for each chemical.
                    # For now, we'll just include all numeric columns. You might need to be more specific.
                    time_col = 'SampleDate'
                    numeric_value_cols = ['Min', 'Max', 'Median', 'Mean', 'Std Dev', 'Pct 10th', 'Pct 25th', 'Pct 75th',
                                          'Pct 90th']

                    if time_col in df.columns:
                        # Convert 'SampleDate' to datetime objects
                        try:
                            times = pd.to_datetime(df[time_col]).tolist()
                            key = (str(station_id), chemical)  # Ensure station_id is a string for consistency
                            processed_times[key] = times

                            # Extract all numeric values for the chemical
                            values_list = []
                            for col in numeric_value_cols:
                                if col in df.columns:
                                    values_list.extend(df[col].tolist())
                            processed_values[key] = values_list

                        except KeyError:
                            print(f"Warning: '{time_col}' column not found in data for station {station_id}, chemical {chemical}.")
                        except Exception as e:
                            print(f"Error processing time/value columns for station {station_id}, chemical {chemical}: {e}")
                    else:
                        print(f"Warning: Required column ('{time_col}') not found in data for station {station_id}, chemical {chemical}.")

        return processed_times, processed_values

    def pull(self, location=None, dataset=None, start_date=None, end_date=None):
        """
        Main method to pull and store data from NDGIS for specified locations and datasets.

        Args:
            location (list, optional): A list of station IDs to fetch data for. Defaults to None (fetches all from masterlist).
            dataset (list, optional): A list of water chemical parameters to fetch. Defaults to a predefined list.
            start_date (datetime.date, optional): Not used in this implementation. Defaults to None.
            end_date (datetime.date, optional): Not used in this implementation. Defaults to None.

        Returns:
            tuple: A tuple containing two dictionaries:
                   - times: A dictionary where keys are (station_id, chemical) tuples and values are lists of timestamps.
                   - values: A dictionary where keys are (station_id, chemical) tuples and values are lists of corresponding values.
        """
        raw_data = self.fetch(location, dataset, start_date, end_date)
        if raw_data:
            times, values = self.process(raw_data)
            # The 'store' method from the base class will need to be adapted to handle the
            # (station_id, chemical) keys and potentially multiple time/value lists.
            # You might need to iterate through the processed data and call store for each.
            for (loc, data_set), time_list in times.items():
                value_list = values.get((loc, data_set))
                if value_list:
                    super().store(time_list, value_list, loc, data_set)
            return times, values
        return {}, {}

if __name__ == '__main__':
    # Example usage:
    ndgis_source = NDGISWaterChem()

    # Pull data for specific station IDs and a subset of chemicals
    station_list = ['380359', '460147']  # Replace with actual station IDs
    chemical_list = ['Phosphorus (Total) (P)', 'Nitrate + Nitrite (N)']
    times, values = ndgis_source.pull(location=station_list, dataset=chemical_list)

    if times and values:
        print("\nSuccessfully pulled and processed data:")
        for key, time_data in times.items():
            print(f"\nStation: {key[0]}, Chemical: {key[1]}")
            print("Times:", time_data)
            print("Values:", values.get(key))
    else:
        print("\nNo data pulled or an error occurred.")

    # To pull data for all stations in the masterlist and the default chemicals:
    # all_times, all_values = ndgis_source.pull()
    # if all_times and all_values:
    #     print("\nSuccessfully pulled and processed data for all stations (default chemicals):")
    #     # Print some sample data or further process it
    # else:
    #     print("\nNo data pulled for all stations (default chemicals) or an error occurred.")
