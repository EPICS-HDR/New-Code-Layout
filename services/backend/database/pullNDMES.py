import requests
import csv
import pandas as pd
from backend.database.parseData import ParseData
from backend.database.sqlclasses import updateDictionary
import os

def pullMesonetData(location, day1, month1, year1, day2, month2, year2):

    NODAK_dict = {'Fort Yates':['89', 'Fort Yates, ND'],
                'Linton':['35', 'Linton, ND'],
                'Mott':['69', 'Mott, ND'],
                'Carson': ['96', 'Carson, ND']}

    location_dict = NODAK_dict[f'{location}']
    station = location_dict[0]

    file_name = f'./static/JSON{location}.csv'

    url_csv = f'https://ndawn.ndsu.nodak.edu/table.csv?ttype=hourly&station={station}&begin_date={year1}-{month1}-{day1}&end_date={year2}-{month2}-{day2}'

    response = requests.get(url_csv)

    # check if response was successful
    if response.status_code == 200:
        # parse the csv data using the csv modules reader object
        reader = csv.reader(response.text.splitlines())
        with open(file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            # write parsed csv data to file
            writer.writerows(reader)
        file.close()
        
    # list of columns need to delete from dataframe
    list_to_del = ['Avg Air Temp Flag', 'Avg Rel Hum Flag', 'Avg Bare Soil Temp Flag', 'Avg Turf Soil Temp Flag', 'Avg Wind Speed Flag', 'Max Wind Speed Flag', 'Avg Wind Dir Flag', 'Avg Wind Dir SD Flag', 'Avg Dew Point Flag', 'Avg Baro Press Flag', 'Avg Sol Rad Flag', 'Total Rainfall Flag']

    list_to_del_2 = ['Station Name', 'Latitude', 'Longitude', 'Elevation']

    df = pd.read_csv(file_name, skiprows=3) # get rid of first three rows
    df2 = df.iloc[1:] # deleting the second line, which was just units
    for i in list_to_del: # deleting the columns from list
        del df2[i]

    for i in list_to_del_2: # deleting the columns from list
        del df2[i]

    df2.to_csv(file_name, index = False) # writing to a csv file

    years = df2['Year'].tolist()
    months = df2['Month'].tolist()
    days = df2['Day'].tolist()
    hours = df2['Hour'].tolist()

    times = []
    for i in range(0, len(years)):
        month = int(months[i])
        if month < 10:
            month = "0" + str(month)
        else:
            month = str(month)

        day = int(days[i])
        if day < 10:
            day = "0" + str(day)
        else:
            day = str(day)

        hourlist = []
        index = 0
        hour = int(hours[i])
        if hour < 1000:
            hour = str(hour)
            hourlist.append("0")
            for character in hour:
                if index == 1:
                    hourlist.append(":")
                hourlist.append(character)
                index += 1
            hour = "".join(hourlist)
        else:
            hour = str(hour)
            for character in hour:
                if index == 2:
                    hourlist.append(":")
                hourlist.append(character)
                index += 1
            hour = "".join(hourlist)

        times.append(str(int(years[i])) + "-" + month + "-" + day + " " + hour)

    avg_air_temp = df2['Avg Air Temp'].tolist()
    avg_rel_hum = df2['Avg Rel Hum'].tolist()
    avg_bare_soil_temp = df2['Avg Bare Soil Temp'].tolist()
    avg_turf_soil_temp = df2['Avg Turf Soil Temp'].tolist()
    avg_wind_speed = df2['Avg Wind Speed'].tolist()
    avg_wind_dir = df2['Avg Wind Dir'].tolist()
    avg_wind_dir_sd = df2['Avg Wind Dir SD'].tolist()
    tot_sol_rad = df2['Avg Sol Rad'].tolist()
    tot_rainfall = df2['Total Rainfall'].tolist()
    avg_baro_press = df2['Avg Baro Press'].tolist()
    avg_dew_point = df2['Avg Dew Point'].tolist()
    avg_wind_chill = df2['Avg Wind Chill'].tolist()

    # Converts String Data to Numerical, Parsing and Salvaging Bad Data
    avg_air_temp = ParseData(avg_air_temp)
    avg_rel_hum = ParseData(avg_rel_hum)
    avg_bare_soil_temp = ParseData(avg_bare_soil_temp)
    avg_turf_soil_temp = ParseData(avg_turf_soil_temp)
    avg_wind_speed = ParseData(avg_wind_speed)
    avg_wind_dir = ParseData(avg_wind_dir)
    tot_sol_rad = ParseData(tot_sol_rad)
    tot_rainfall = ParseData(tot_rainfall)
    avg_baro_press = ParseData(avg_baro_press)
    avg_dew_point = ParseData(avg_dew_point)
    avg_wind_chill = ParseData(avg_wind_chill)
    
    updateDictionary(times, avg_air_temp, location, "Average Air Temperature", "mesonet")
    updateDictionary(times, avg_rel_hum, location, "Average Relative Humidity", "mesonet")
    updateDictionary(times, avg_bare_soil_temp, location, "Average Bare Soil Temperature", "mesonet")
    updateDictionary(times, avg_turf_soil_temp, location, "Average Turf Soil Temperature", "mesonet")
    updateDictionary(times, avg_wind_speed, location, "Maximum Wind Speed", "mesonet")
    updateDictionary(times, avg_wind_dir, location, "Average Wind Direction", "mesonet")
    updateDictionary(times, tot_sol_rad, location, "Total Solar Radiation", "mesonet")
    updateDictionary(times, tot_rainfall, location, "Total Rainfall", "mesonet")
    updateDictionary(times, avg_baro_press, location, "Average Baromatric Pressure", "mesonet")
    updateDictionary(times, avg_dew_point, location, "Average Dew Point", "mesonet")
    updateDictionary(times, avg_wind_chill, location, "Average Wind Chill", "mesonet")

    os.remove(file_name)