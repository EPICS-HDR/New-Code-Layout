from shell_pull import get_dataset_name, download_file
import pandas as pd

#Reads the csv with the masterlist and puts all the ids into an empty list
station_ids = []

# TODO @AP - What is the masterlist?
df = pd.read_excel(r'INSERT THE PATH TO THE MASTERLIST HERE')
for id in df.iloc[:,0]: #Change out the 0 after the comma depending on which column the station ids are in
    station_ids.append(id) 


for station_id in station_ids:
    #Creates the urls needed to get the field and water chem data
    waterchem_url = f"https://deq.nd.gov/Webservices_SWDataApp/DownloadStationsData/GetStationsWaterChemData/{station_id}"

    waterchem_dataset_name = get_dataset_name(waterchem_url)  #Runs function to get the name of the dataset
    print("Dataset Names:", waterchem_dataset_name)

    #Creates the urls the download_file function will go to to get the csv files using the dataset name
    waterchem_data_url = f"https://deq.nd.gov/WQ/3_Watershed_Mgmt/SWDataApp/downloaddata/{waterchem_dataset_name}.csv"

    download_file(waterchem_data_url, f"Water_Chemistry_Summary_{station_id}.csv")