from backend.graphgeneration.createCustom import customGraph, makeTable
from backend.database.sqlclasses import dictpull
from backend.database.pullUSACE import pullDamData
from backend.database.pullShadeHill import pullShadeHill
from backend.database.pullUSGS import pullGaugeData
from backend.database.pullNDMES import pullMesonetData
from backend.database.pullUSGS import pullGaugeData
from backend.database.pullNOAA import forecastdatacall
from backend.database.PullCoCoRaHSAPI import pullCoCoRaHSAPI
from datetime import datetime, date, timedelta
import os

def getDates():
    
    """
    Function documentation:
    Establishes date range, used for:
        1. Pulling data from most sources
        2. Accessing stored data in our database
    Change numDays variable to dictate how many days to pull
    """

    # Decides how many days to pull
    numDays = 30

    # Gets the current date
    now = datetime.now()
    end_day = now.strftime("%d")
    end_month = now.strftime("%m")
    end_year = now.strftime("%Y") 
    
    # Uses the timedelta function to choose a date numDays days before current date
    start_date = (date.today()-timedelta(days=numDays)).isoformat()

    # Initializes empty lists to fill with dates
    index = 0
    year = []
    month = []
    day = []

    # Knowing the syntax of the datetime module's outputs, adds necessary characters to appropriate lists
    for character in start_date:
        if index < 4:
            year.append(character)
        elif 4 < index < 7:
            month.append(character)
        elif 7 < index:
            day.append(character)
        index += 1

    # Combines characters from each list into complete words
    start_year = "".join(year)
    start_month = "".join(month)
    start_day = "".join(day)
    
    # Returns pulled current date, and calculated past date
    return start_day, start_month, start_year, end_day, end_month, end_year

# TODO Find out how to reduce run time. Optimize looping structure
# TODO Figure out issue with graph generation
def updateGraphs(start_day, start_month, start_year, end_day, end_month, end_year):

    """
    Function documentation:
    Generates and caches graphs to display on Interactive Map
    Uses looping along with try/except structure to attempt all possible graphs
    Currently generates graphs for:
        1. USGS Gauge locations
        2. USACE Dam locations
        3. North Dakota Mesonet locations
    Note: Splitting up into seperate looping structures by location category sped up
    runtime signifcantly
    """

    start_date = start_year + "-" + start_month + "-" + start_day
    end_date = end_year + "-" + end_month + "-" + end_day

    # TODO @AP - These variables are in a weird place lets move them to a config file or a constants file
    gaugelocations = ["Hazen", "Stanton", "Washburn", "Price", "Bismarck", 
                "Schmidt", "Judson", "Mandan", "Breien", "Wakpala", "Little Eagle",
                "Cash", "Whitehorse"]
    damlocations = ["Fort Peck", "Garrison", "Oahe", "Big Bend", "Fort Randall", "Gavins Point"]
    meslocations = ["Carson", "Fort Yates", "Linton", "Mott"]

    datasets = ["Gauge Height","Elevation", "Discharge", "Water Temperature", 
                "Flow Spill", "Flow Powerhouse", "Flow Out", "Tailwater Elevation", "Energy",
                "Air Temperature", "Average Air Temperature", "Average Relative Humidity", 
                "Average Bare Soil Temperature", "Average Turf Soil Temperature", "Maximum Wind Speed",
                "Average Wind Direction", "Total Solar Radiation", "Total Rainfall",
                "Average Baromatric Pressure", "Average Dew Point", "Average Wind Chill"]

    previousError = None
    # Iterates through each possible location and dataset

    for location in gaugelocations:
        for dataset in datasets:
            title = f"{location} {dataset} Table"
            try:
                # Attempts database pull for location/dataset combination
                times, data = dictpull(location, dataset, start_date, end_date, "gauge")
                # Always completes graph without prescence of None type data
                if None not in data:
                    customGraph(times, [location], [data], dataset, 1)
                    makeTable([data], title)
                # Runs in cases where at least one None type datapoint exists
                else:
                    i = 0
                    # Iterates through each element of the list, generating one graph if at least one numerical data point exists
                    for datapoint in data:
                        if (type(datapoint) == float) and (i == 0):
                            customGraph(times, [location], [data], dataset, 1)
                            makeTable([data], title)
                            i += 1
            except Exception as e:
                if previousError != str(e):  # Compare error messages
                    print(e)
                previousError = str(e)  # Store the current error message for comparison

    for location in damlocations:
        for dataset in datasets:
            title = f"{location} {dataset} Table"
            try:
                # Attempts database pull for location/dataset combination
                times, data = dictpull(location, dataset, start_date, end_date, "dam")
                # Always completes graph without prescence of None type data
                if None not in data:
                    customGraph(times, [location], [data], dataset, 1)
                    makeTable([data], title)
                # Runs in cases where at least one None type datapoint exists
                else:
                    i = 0
                    # Iterates through each element of the list, generating one graph if at least one numerical data point exists
                    for datapoint in data:
                        if (type(datapoint) == float) and (i == 0):
                            customGraph(times, [location], [data], dataset, 1)
                            makeTable([data], title)
                            i += 1
            except Exception as e:
                if previousError != str(e):  # Compare error messages
                    print(e)
                previousError = str(e)  # Store the current error message for comparison

    for location in meslocations:
        for dataset in datasets:
            title = f"{location} {dataset} Table"
            try:
                # Attempts database pull for location/dataset combination
                times, data = dictpull(location, dataset, start_date, end_date, "mesonet")
                # Always completes graph without prescence of None type data
                if None not in data:
                    customGraph(times, [location], [data], dataset, 1)
                    makeTable([data], title)
                # Runs in cases where at least one None type datapoint exists
                else:
                    i = 0
                    # Iterates through each element of the list, generating one graph if at least one numerical data point exists
                    for datapoint in data:
                        if (type(datapoint) == float) and (i == 0):
                            customGraph(times, [location], [data], dataset, 1)
                            makeTable([data], title)
                            i += 1
            except Exception as e:
                if previousError != str(e):  # Compare error messages
                    print(e)
                previousError = str(e)  # Store the current error message for comparison

    # TODO @AP - We should add another one of these codeblocks for the south dakota pipeline

# TODO Figure out if we need to be storing graphs in both static folders, increases runtime significantly
def main():
    #TODO @AP - The documentation is not complete
    """
    Function documentation:
    Coordinates all function calls associated with:
        1. Pulling Data
        2. Storing Data
        3. Cacheing Graphs
    Currently completely processes data for:
        1.
    """
    
    # Establishes date ranges for use
    start_day, start_month, start_year, end_day, end_month, end_year = getDates()

     # Pulls and stores all USACE data available
    damList = ["Fort Peck", "Garrison", "Oahe", "Big Bend", "Fort Randall", "Gavins Point"]
    for dam in damList:
        pullDamData(dam)

    # TODO @AP gaugeList is redudant it is the same list as gaugelocations (some more lists are redundant in different functions)
    # TODO @AP - I think we should move them to a constants file

    # Pulls and stores all USGS data available
    gaugeList = ["Hazen", "Stanton", "Washburn", "Price", "Bismarck", 
                "Schmidt", "Judson", "Mandan", "Breien", "Wakpala", "Little Eagle",
                "Cash", "Whitehorse"]
    for gauge in gaugeList:
        pullGaugeData(gauge, start_day, start_month, start_year, end_day, end_month, end_year)

    # Pulls and stores all NDMES data available
    ndmesList = ["Carson", "Fort Yates", "Linton", "Mott"]
    for mes in ndmesList:
        pullMesonetData(mes, start_day, start_month, start_year, end_day, end_month, end_year)

    # Pulls all data available from NOAA
    noaaKeyList = ["temperature", "dewpoint", "relativeHumidity", "windChill"]
    for key in noaaKeyList:
        forecastdatacall(key)

    # Pulls all data available from ShadeHill dam
    pullShadeHill(start_day, start_month, start_year, end_day, end_month, end_year)

    # Pulls and stores all data available from CoCoRaHS
    cocoList = ["Bison, SD", "Faulkton, SD", "Bismarck, ND", "Langdon, ND"]
    cocoLocList = ["Bison", "Faulkton", "Bismarck", "Langdon"]
    cocoStart = start_year + start_month + start_day
    cocoEnd = end_year + end_month + end_day
    for i in range(0,4):
        pullCoCoRaHSAPI(cocoList[i], cocoLocList[i], cocoStart, cocoEnd)

    # Removes existing cached graphs
    folder_path = "./static/graphs"
    # Empty current contents of folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        os.unlink(file_path)

    # Creates and Caches graphs
    updateGraphs(start_day, start_month, start_year, end_day, end_month, end_year)

main()