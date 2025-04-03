import requests
import csv
import os
from services.backend.datasources.base import DataSource
from services.backend.datasources.utils import DataParser

class USACEDataSource(DataSource):
    """
    Data source for USACE dam data.
    """
    
    def __init__(self):
        super().__init__("USACE", "dam")
        self.location_dict = {
            'Fort Peck': ['FTPK'],
            'Garrison': ['GARR'],
            'Oahe': ['OAHE'],
            'Big Bend': ['BEND'],
            'Fort Randall': ['FTRA'],
            'Gavins Point': ['GAPT']
        }
        
    def fetch(self, location, dataset, start_date=None, end_date=None):
        """
        Fetch dam data from USACE.
        
        Args:
            location: Location to fetch data for
            dataset: Not used for USACE
            start_date: Not used for USACE
            end_date: Not used for USACE
            
        Returns:
            Raw text data
        """
        location_data = self.location_dict[location]
        location_code = location_data[0]
        
        url = f'https://www.nwd-mr.usace.army.mil/rcc/programs/data/{location_code}'
        
        try:
            response = requests.get(url, verify=False)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching USACE data for {location}: {e}")
            return None
        
        # Create temporary file
        file_name = f"./temp_{location}.txt"
        
        # Write response to file
        with open(file_name, "w") as f:
            writer = csv.writer(f)
            for line in response.text.split("\n"):
                writer.writerow(line.split("\t"))
        
        # Extract relevant data
        count = 0
        alternate = 0
        data = []
        
        with open(file_name, "r") as file:
            for line in file:
                if count == 4:
                    data.append(line)
                elif count > 5:
                    if alternate % 2 == 0:
                        data.append(line.strip('"'))
                    alternate += 1
                count += 1
        
        # Rewrite the file with cleaned data
        with open(file_name, "w") as file:
            for line in data:
                file.write(f"{line}")
        
        # Read the file content
        file_content = ""
        with open(file_name, "r") as file:
            file_content = file.read()
        
        # Clean up
        try:
            os.remove(file_name)
        except Exception as e:
            print(f"Error removing temporary file: {e}")
        
        return file_content
    
    def process(self, raw_data, location, dataset):
        """
        Process the raw USACE data.
        
        Args:
            raw_data: Raw text data
            location: Location the data is for
            dataset: Type of data (e.g., "Elevation")
            
        Returns:
            Tuple of (times, values)
        """
        if not raw_data:
            return [], []
            
        # Parse the raw data
        lines = raw_data.strip().split('\n')
        
        Date = []
        Hour = []
        Elevation = []
        Flow_Spill = []
        Flow_Powerhouse = []
        Flow_Out = []
        Elev_Tailwater = []
        Energy = []
        Temp_Water = []
        Temp_Air = []
        
        for i, line in enumerate(lines):
            if i > 1 and i < 170:  # Skip header and limit data
                parts = line.split()
                if len(parts) >= 10:  # Ensure line has enough columns
                    Date.append(parts[0])
                    Hour.append(parts[1])
                    Elevation.append(parts[2])
                    Flow_Spill.append(parts[3])
                    Flow_Powerhouse.append(parts[4])
                    Flow_Out.append(parts[5])
                    Elev_Tailwater.append(parts[6])
                    Energy.append(parts[7])
                    Temp_Water.append(parts[8])
                    Temp_Air.append(parts[9])
        
        # Parse numeric values
        Elevation = DataParser.parse_numeric_list(Elevation)
        Flow_Spill = DataParser.parse_numeric_list(Flow_Spill)
        Flow_Powerhouse = DataParser.parse_numeric_list(Flow_Powerhouse)
        Flow_Out = DataParser.parse_numeric_list(Flow_Out)
        Elev_Tailwater = DataParser.parse_numeric_list(Elev_Tailwater)
        Energy = DataParser.parse_numeric_list(Energy)
        Temp_Water = DataParser.parse_numeric_list(Temp_Water)
        Temp_Air = DataParser.parse_numeric_list(Temp_Air)
        
        # Combine date and time
        times = []
        for i in range(len(Hour)):
            times.append(Date[i] + " " + Hour[i])
        
        # Map datasets to their values
        datasets = {
            "Elevation": Elevation,
            "Flow Spill": Flow_Spill,
            "Flow Powerhouse": Flow_Powerhouse,
            "Flow Out": Flow_Out,
            "Tailwater Elevation": Elev_Tailwater,
            "Energy": Energy,
            "Water Temperature": Temp_Water,
            "Air Temperature": Temp_Air
        }
        
        # Return the requested dataset
        if dataset in datasets:
            return times, datasets[dataset]
        else:
            return [], []
    
    def pull_all(self, start_date, end_date):
        """
        Pull data for all locations and datasets.
        
        Args:
            start_date: Not used for USACE
            end_date: Not used for USACE
        """
        datasets = [
            "Elevation", "Flow Spill", "Flow Powerhouse", "Flow Out", 
            "Tailwater Elevation", "Energy", "Water Temperature", "Air Temperature"
        ]
        
        for location in self.location_dict.keys():
            print(f"Pulling USACE data for {location}...")
            
            # Fetch the data once
            try:
                raw_data = self.fetch(location, None, start_date, end_date)
                
                # Process and store each dataset
                for dataset in datasets:
                    times, values = self.process(raw_data, location, dataset)
                    if times and values:
                        self.store(times, values, location, dataset)
            except Exception as e:
                print(f"Error processing USACE data for {location}: {e}")