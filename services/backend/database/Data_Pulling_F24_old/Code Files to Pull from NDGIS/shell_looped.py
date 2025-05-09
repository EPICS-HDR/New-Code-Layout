import pandas as pd
import requests
import os


# import time
# TODO: @AP - this code needs to be refined

# Send a POST request and get the response text (dataset name)

def get_dataset_name(url):
    response = requests.post(url)
    return response.text.replace('"', '')  # Take out quotes


# Creates the urls needed to get the field and water chem data

# TODO: Remove this and directly send it to the sqlclasses file
# Download the data
def download_file(url, filename):
    download_folder = os.path.expanduser("~/Downloads")  # Adds the files to my downloads folder
    file_path = os.path.join(download_folder, filename)

    # print(f"Saving file to: {file_path}")  #Print the file path

    response = requests.get(url)  # Sends a GET request to the urls to retrieve file content

    if response.status_code == 200:  # Error check, if response code isn't 200 then an error occured with the request
        # Check if anything is recieved (makes sure file isn't empty)
        if response.content:
            with open(file_path, 'wb') as file:
                file.write(response.content)
                # print(f"Downloaded {filename} successfully.")
            print(f"File saved at: {file_path}")
        else:
            print(f"No content received for {filename}.")
    else:
        print(f"Failed to download {filename}. Status code: {response.status_code}")  # Error if the request failed


# Timing the execution
# start_time = time.time()  #Start the timer

# Creates the urls the download_file function will go to to get the csv files


# TEST DATA
station_id = 385551
waterchem_url = f"https://deq.nd.gov/Webservices_SWDataApp/DownloadStationsData/GetStationsWaterChemData/{station_id}"

waterchem_dataset_name = get_dataset_name(waterchem_url)
print("Dataset Name:", waterchem_dataset_name)

waterchem_data_url = f"https://deq.nd.gov/WQ/3_Watershed_Mgmt/SWDataApp/downloaddata/{waterchem_dataset_name}.csv"

download_file(waterchem_data_url, f"Water_Chemistry_Summary_{station_id}.csv")

# TIMER
# end_time = time.time()  #End the timer
# execution_time = end_time - start_time  #Calculate the execution time
# print(f"Total execution time: {execution_time:.2f} seconds")





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


