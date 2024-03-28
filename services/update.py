from backend.graphgeneration.createCustom import customGraph, makeTable
from backend.database.sqlclasses import dictpull

start_date = "2024-02-26"
end_date = "2024-03-26"

locations = ["Hazen", "Stanton", "Washburn", "Price", "Bismarck", 
            "Schmidt", "Judson", "Mandan", "Breien", "Wakpala", "Little Eagle",
            "Cash", "Whitehorse", "Fort Peck", "Garrison", "Oahe", "Big Bend", 
            "Fort Randall", "Gavins Point", "Carson", "Fort Yates", "Linton", 
            "Mott"]

datasets = ["Gauge Height","Elevation", "Discharge", "Water Temperature", 
            "Flow Spill", "Flow Powerhouse", "Flow Out", "Tailwater Elevation", "Energy",
            "Air Temperature", "Average Air Temperature", "Average Relative Humidity", 
            "Average Bare Soil Temperature", "Average Turf Soil Temperature", "Maximum Wind Speed",
            "Average Wind Direction", "Total Solar Raditation", "Total Rainfall",
            "Average Baromatric Pressure", "Average Dew Point", "Average Wind Chill"]

#TODO Figure out issue wherein gauge locations graph all four gauge datasets regardless of data being present
# Iterates through each possible .location and dataset
for location in locations:
    for dataset in datasets:
        title = f"{location} {dataset} Table"
        try:
            # Attempts database pull for location/dataset combination
            times, data = dictpull(location, dataset, start_date, end_date)
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
        except:
            pass
