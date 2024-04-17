import requests
import pandas as pd
import calendar
from datetime import datetime
import json
from datadict import updateDictionary

def getForecasts(location, dataset):
    """
    Function documentation:
    """

    # Get Points: https://aviationweather.gov/gfa/#obs
    # Get Gridpoints: https://api.weather.gov/points/x,y

    dictionary = {
    "Williston/Basin": "BIS/18,121", # 48.248, -103.749
    "Tioga": "BIS/46,125", # 48.382, -102.898
    "Stanley": "BIS/62,120", # 48.305, -102.415
    "Minot": "BIS/99,116", # 48.247, -101.283
    "Sidney/Richland": "GGW/185,81", # 47.688, -104.183
    "Watford City": "BIS/33,97", # 47.809, -103.255
    "Garrison": "BIS/91,88", # 47.658, -101.448
    "Glendive/Dawson": "GGW/162,56", # 47.137, -104.859
    "Hazen/Mercer": "BIS/85,70", # 47.279, -101.585
    "Beach": "BIS/7,58", # 46.921, -103.996
    "Dickinson/Roosevelt": "BIS/45,50", # 46.798, -102.804
    "Glen": "BIS/75,48", # 46.805, -101.862
    "Bismarck" : "BIS/111,45", # 46.773, -100.749
    "Miles City/Wiley": "BYZ/190,114", # 46.430, -105.894
    "Baker": "BYZ/243,107", # 46.351, -104.264
    "Bowman": "BIS/27,21", # 46.159, -103.303
    "Hettinger": "BIS/48,12", # 46.012, -102.643
    "Linton": "BIS/127,18", # 46.220, -100.241
    "Buffalo/Harding": "UNR/91,130", # 45.599, -103.557
    "Mobridge": "ABR/55,99", # 45.538, -100.402
    "Faith": "UNR/139,100", # 45.031, -102.042
    "Spearfish/Clyde": "UNR/80,77", # 44.463, -103.793
    "Pierre": "ABR/57,44", # 44.371, -100.282
    "Custer": "UNR/84,43", # 43.740, -103.613
    "Rapid City": "UNR/103,56", # 44.030, -103.049
    "Philip": "UNR/151,53" # 44.025, -101.608
    }

    code = dictionary[location]

    # generate url
    url = f'https://api.weather.gov/gridpoints/{code}'
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the JSON data into a Python dictionary
        data_dict = response.json()

        # Display the dictionary (or use it as needed)
        # print(data_dict)

        #initializing of the list
        listy = data_dict['properties'][dataset]['values']
        
        for w in range(0, len(listy)):
            z = listy[w]
            year, month, day, hour = split_validTime(z['validTime']) 
            new_validTime = change_datetime(year, month, day, hour)
            z['validTime'] = new_validTime

    except requests.exceptions.RequestException as e:
        print(f"Error: {location}")
        listy = 0

    return listy

def change_datetime(year, month, day, hour):
    # Create a datetime object
    dt = datetime(year, month, day, hour)
    
    # Format the datetime as a string
    datetime_string = dt.strftime('%Y-%m-%d %H:%M:%S')
    return datetime_string

def pull_forecast(response, data_sets):
    # df = pd.DataFrame()
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON data
        data = response.json()
        for i in data_sets[1:]:
            new_data = data['properties'][data_sets[i]]['values']
        
            # Convert the temperature data into a DataFrame
            df = pd.DataFrame(new_data)
        df.columns = data_sets
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
    
    return df


# splitting the time value into the year, month, day, hour, and interval
def split_validTime(validTime):
    split1 = validTime.split("-")

    year = int(split1[0])
    month = int(split1[1])

    split2 = split1[2].split("T")

    day = int(split2[0])

    # split3 = split2[-1].split("H")
    # interval = int(split3[0])

    split4 = split2[1].split(":")
    hour = int(split4[0])
    
    return year, month, day, hour

def days_in_month(year, month):
    # Check if the provided year and month are valid
    if 1 <= month <= 12 and year >= 0:
        # Use the calendar module to get the number of days in the month
        return calendar.monthrange(year, month)[1]
    else:
        return "Invalid year or month"

def forecastdatacall(dataset):
  
    # All possible locations, to be iterated through. The data will be stored in an order matching these
    locationKeys = ["Williston/Basin", "Tioga", "Stanley", "Minot", "Sidney/Richland", "Watford City", "Garrison", "Glendive/Dawson", "Hazen/Mercer",
                        "Beach", "Dickinson/Roosevelt", "Glen", "Bismarck", "Miles City/Wiley", "Baker", "Bowman", "Hettinger", "Linton", "Buffalo/Harding",
                        "Mobridge", "Faith", "Spearfish/Clyde", "Pierre", "Custer", "Rapid City", "Philip"]

    # List to contain all data for the chosen dataset
    dataList = []

    for location in locationKeys:

        data = 0
        count = 0
        
        # Tries pulling data for this location, giving the except three tries at most
        while data == 0 and count < 3:
            data = getForecasts(location, dataset)
            count += 1

        # Catch statement skipping data processessing just in case data pull still unsuccessful after three tries
        if data != 0:
            # Resetting list for individual data/location
            timeList = []
            valueList = []
            
            for item in data:
                # Compiles all times and writes them to the main list
                timestemp = item["validTime"].split(":")
                time = timestemp[0] + ":" + timestemp[1]
                timeList.append(time)

                # Compiles all data points, in a new list, with matching indexes to their times
                valueList.append(item["value"])

            # After compiling all data, adds to running data list
            dataList.append(timeList)
            dataList.append(valueList)

            # Updates dictionary for each location
            # updateDictionary(timeList, valueList, location, dataset)

    # After all iterations, dumps all data pulled        
    with open(f'./services/static/JSON/{dataset}.json', 'w') as file:
        file.write(json.dumps(dataList))