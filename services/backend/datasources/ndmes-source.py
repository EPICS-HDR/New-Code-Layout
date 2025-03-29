import requests
import csv
import pandas as pd
import os
from backend.datasources.base import DataSource
from backend.datasources.utils import DataParser

class NDMESDataSource(DataSource):
    """
    Data source for North Dakota Mesonet data.
    """
    
    def __init__(self):
        super().__init__("NDMES", "mesonet")
        self.location_dict = {
            "Fort Yates": ["89", "Fort Yates, ND"],
            "Linton": ["35", "Linton, ND"],
            "Mott": ["69", "Mott, ND"],
            "Carson": ["96", "Carson, ND"],
        }
        
    def fetch(self, location, dataset, start_date, end_date):
        """
        Fetch mesonet data from NDSU NDAWN.
        """

        location_data = self.location_dict[location]
        station = location_data[0]
        
        s_year, s_month, s_day = start_date['year'], start_date['month'], start_date['day']
        e_year, e_month, e_day = end_date['year'], end_date['month'], end_date['day']
        
        url_csv = f"https://ndawn.ndsu.nodak.edu/table.csv?ttype=hourly&station={station}&begin_date={s_year}-{s_month}-{s_day}&end_date={e_year}-{e_month}-{e_day}"

        try:
            response = requests.get(url_csv)
            
            if response.status_code != 200:
                print(f"Error fetching NDMES data for {location}: HTTP {response.status_code}")
                return None

            file_name = f"./temp_{location}.csv"

            reader = csv.reader(response.text.splitlines())
            with open(file_name, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerows(reader)
                
            return file_name
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching NDMES data for {location}: {e}")
            return None
    
    def process(self, raw_data, location, dataset):
        """
        Process the raw NDMES data.
        """
        if not raw_data:
            return [], []
            
        file_name = raw_data
        
        try:
            list_to_del = [
                "Avg Air Temp Flag", "Avg Rel Hum Flag", "Avg Bare Soil Temp Flag",
                "Avg Turf Soil Temp Flag", "Avg Wind Speed Flag", "Max Wind Speed Flag",
                "Avg Wind Dir Flag", "Avg Wind Dir SD Flag", "Avg Dew Point Flag",
                "Avg Baro Press Flag", "Avg Sol Rad Flag", "Total Rainfall Flag",
            ]
            
            list_to_del_2 = ["Station Name", "Latitude", "Longitude", "Elevation"]

            df = pd.read_csv(file_name, skiprows=3)

            df2 = df.iloc[1:]

            for i in list_to_del:
                if i in df2.columns:
                    del df2[i]
                    
            for i in list_to_del_2:
                if i in df2.columns:
                    del df2[i]

            years = df2["Year"].tolist()
            months = df2["Month"].tolist()
            days = df2["Day"].tolist()
            hours = df2["Hour"].tolist()

            times = []
            for i in range(0, len(years)):
                month = int(months[i])
                month_str = f"0{month}" if month < 10 else str(month)
                
                day = int(days[i])
                day_str = f"0{day}" if day < 10 else str(day)
                
                hour_int = int(hours[i])
                if hour_int < 1000:
                    hour_str = f"0{hour_int//100}:{hour_int%100}"
                else:
                    hour_str = f"{hour_int//100}:{hour_int%100}"
                
                times.append(f"{int(years[i])}-{month_str}-{day_str} {hour_str}")

            datasets = {
                "Average Air Temperature": df2["Avg Air Temp"].tolist(),
                "Average Relative Humidity": df2["Avg Rel Hum"].tolist(),
                "Average Bare Soil Temperature": df2["Avg Bare Soil Temp"].tolist(),
                "Average Turf Soil Temperature": df2["Avg Turf Soil Temp"].tolist(),
                "Maximum Wind Speed": df2["Avg Wind Speed"].tolist(),
                "Average Wind Direction": df2["Avg Wind Dir"].tolist(),
                "Total Solar Radiation": df2["Avg Sol Rad"].tolist(),
                "Total Rainfall": df2["Total Rainfall"].tolist(),
                "Average Baromatric Pressure": df2["Avg Baro Press"].tolist(),
                "Average Dew Point": df2["Avg Dew Point"].tolist(),
                "Average Wind Chill": df2["Avg Wind Chill"].tolist()
            }

            if dataset in datasets:
                values = DataParser.parse_numeric_list(datasets[dataset])
                os.remove(file_name)
                return times, values

            else:
                os.remove(file_name)
                return [], []
                
        except Exception as e:
            print(f"Error processing NDMES data for {location}: {e}")

            try:
                os.remove(file_name)
            except:
                pass
            return [], []
    
    def pull_all(self, start_date, end_date):
        """
        Pull data for all locations and datasets.
        
        Args:
            start_date: Start date dictionary with year, month, day
            end_date: End date dictionary with year, month, day
        """
        datasets = [
            "Average Air Temperature", "Average Relative Humidity",
            "Average Bare Soil Temperature", "Average Turf Soil Temperature",
            "Maximum Wind Speed", "Average Wind Direction",
            "Total Solar Radiation", "Total Rainfall",
            "Average Baromatric Pressure", "Average Dew Point",
            "Average Wind Chill"
        ]
        
        for location in self.location_dict.keys():
            print(f"Pulling NDMES data for {location}...")
            
            try:
                # Fetch the data once
                raw_data = self.fetch(location, None, start_date, end_date)
                
                if raw_data:
                    # Process and store each dataset
                    for dataset in datasets:
                        times, values = self.process(raw_data, location, dataset)
                        if times and values:
                            self.store(times, values, location, dataset)
            except Exception as e:
                print(f"Error processing NDMES data for {location}: {e}")