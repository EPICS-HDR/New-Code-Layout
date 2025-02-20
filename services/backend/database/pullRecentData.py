from datetime import datetime, date, timedelta
import requests
import plotly.offline
import csv
import pandas as pd
import plotly.graph_objs as go
import os
import numpy as np
from sqlclasses import updateDictionary
import json
from forecast import forecastdatacall


def getDates():

    # Decides how many days to pull
    numDays = 30

    # Gets the current date
    now = datetime.now()
    end_day = now.strftime("%d")
    end_month = now.strftime("%m")
    end_year = now.strftime("%Y")

    # Uses the timedelta function to choose a date numDays days before current date
    start_date = (date.today() - timedelta(days=numDays)).isoformat()

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


def ParseData(List):

    # Initializes Count Value
    index = 0

    # Iterates through entire length of inputted list
    for item in range(0, len(List)):

        # Reinitializes neg check
        neg = 0

        # Inititalizes all data to string for parsing
        List[index] = str(List[index])

        # Checks if Value is Only a hyphen
        if List[index] == "-":
            List[index] = "0"

        # Checks for Common Error Character (Can add more as issues arise)
        if '"' in List[index]:
            temp = List[index].split('"')

            # Plugs partially parsed data back into list
            List[index] = "".join(temp)

        # Checks for Commas, Removing if Needed
        if "," in List[index]:
            tempList = List[index].split(",")
            Ndata = tempList[0] + tempList[1]

            # Plugs partially parsed data back into list
            List[index] = Ndata

        # Checks if Negative, Makes note
        if "-" in List[index]:
            neg = 1

        # Sets variable for Try test. Removes Issue Characters
        data = List[index].strip('-"')

        # Attempts to make the data a float, assigns value of 0 if not possible
        try:
            data = float(data)
        except:
            data = 0

        # Reapplies negative if needed
        if neg == 1:
            data *= -1

        # Replaces original value with parsed, numerical data
        List[index] = data
        index += 1

    # Returns altered list
    return List


def pullGaugeData(city):

    location_dict = {
        "Hazen": ["06340500", 1],
        "Stanton": ["06340700", 2],
        "Washburn": ["06341000", 2],
        "Price": ["06342020", 2],
        "Bismarck": ["06342500", 3],
        "Schmidt": ["06349700", 2],
        "Judson": ["06348300", 1],
        "Mandan": ["06349000", 1],
        "Breien": ["06354000", 1],
        "Wakpala": ["06354881", 4],
        "Little Eagle": ["06357800", 4],
        "Cash": ["06356500", 4],
        "Whitehorse": ["06360500", 4],
    }

    start_day, start_month, start_year, end_day, end_month, end_year = getDates()

    location_data = location_dict[f"{city}"]
    code = location_data[0]
    category = location_data[1]

    if category == 1:
        url = f"https://waterdata.usgs.gov/nwis/uv?cb_00060=on&cb_00065=on&cb_63160=on&format=rdb&site_no={code}&legacy=1&period=&begin_date={start_year}-{start_month}-{start_day}&end_date={end_year}-{end_month}-{end_day}"
        num_sets = 3
        linecount = 56
    elif category == 2:
        url = f"https://waterdata.usgs.gov/nwis/uv?cb_00065=on&cb_63160=on&format=rdb&site_no={code}&legacy=1&period=&begin_date={start_year}-{start_month}-{start_day}&end_date={end_year}-{end_month}-{end_day}"
        num_sets = 2
        linecount = 54
    elif category == 3:
        url = f"https://waterdata.usgs.gov/nwis/uv?cb_00010=on&cb_00060=on&cb_00065=on&cb_63160=on&format=rdb&site_no={code}&legacy=1&period=&begin_date={start_year}-{start_month}-{start_day}&end_date={end_year}-{end_month}-{end_day}"
        num_sets = 4
        linecount = 58
    elif category == 4:
        url = f"https://waterdata.usgs.gov/nwis/uv?cb_00060=on&cb_00065=on&format=rdb&site_no={code}&legacy=1&period=&begin_date={start_year}-{start_month}-{start_day}&end_date={end_year}-{end_month}-{end_day}"
        num_sets = 2
        linecount = 54

    linecount2 = linecount + 3

    response = requests.get(url)

    file_name = f"./services/static/JSON{city}"

    with open(
        "./services/static/JSONdata.txt", "w"
    ) as f:  # writes text from the website to text
        writer = csv.writer(f)
        for line in response.text.split("\n"):
            writer.writerow(line.split("\t"))

    data = []
    count = 0
    alternate = 0

    with open("./services/static/JSONdata.txt", "r") as file:
        for line in file:
            if count == linecount:
                data.append(line)
            elif count > linecount2:
                if alternate % 2 == 0:
                    line.strip("\n")
                    data.append(line)
                alternate += 1
            count += 1

    # Use of CSV is here (Aditya Pachpande)

    with open(f"{file_name}.csv", "w") as file:
        for line in data:
            file.write(f"{line}")

    with open(f"{file_name}.csv", "w") as file:
        for line in data:
            file.write(f"{line}")

    with open("./services/static/JSONdata.txt", "w") as file:
        for line in data:
            file.write(f"{line}")

    with open(f"{file_name}.csv", "rt") as f:
        reader = csv.reader(f)
        data_matrix = list(reader)

    # Use of CSV is here (Aditya Pachpande)

    data_matrix1 = data_matrix[:-1]

    if num_sets == 2:
        length = 8  # when there are two data points, the length of the matrix is 8
    elif num_sets == 3:  # length is ten when there are three data points
        length = 10
    elif num_sets == 4:
        length = 12

    times = []
    dataset1 = []
    dataset2 = []
    dataset3 = []
    dataset4 = []

    for matrixindex in range(
        4, len(data_matrix1)
    ):  # setting the data we need into lists
        if matrixindex != 0:
            for data in range(0, length):
                if data == 2:
                    times.append(data_matrix1[matrixindex][data])
                elif data == 4:
                    dataset1.append(data_matrix1[matrixindex][data])
                elif data == 6:
                    dataset2.append(data_matrix1[matrixindex][data])
                elif num_sets >= 3 and data == 8:
                    dataset3.append(data_matrix1[matrixindex][data])
                elif num_sets == 4 and data == 10:
                    dataset4.append(data_matrix1[matrixindex][data])

    if category == 1:
        stream_level = dataset1
        discharge = dataset2
        gauge_height = dataset3
        name1 = "Stream water level elevation above NAVD"
        name2 = "Discharge, cubic feet per second"
        name3 = "Gauge height, feet, [Bubbler]"
        if city == "Judson":
            discharge = dataset3
            gauge_height = dataset2
            name3 = "Discharge, cubic feet per second"
            name2 = "Gauge height, feet, [Bubbler]"
    elif category == 2:
        stream_level = dataset1
        gauge_height = dataset2
        name1 = "Stream water level elevation above NAVD"
        name2 = "Gauge height, feet, [Bubbler]"
    elif category == 3:
        stream_level = dataset1
        water_temp = dataset2
        discharge = dataset3
        gauge_height = dataset4
        name1 = "Stream water level elevation above NAVD"
        name2 = "Water temperature, Celcius"
        name3 = "Discharge, cubic feet per second"
        name4 = "Gauge height, feet, [Bubbler]"
    elif category == 4:
        discharge = dataset1
        gauge_height = dataset2
        name1 = "Discharge, cubic feet per second"
        name2 = "Gauge height, feet, [Bubbler]"

    if (
        category != 2
    ):  # correcting the values that say 'Ice', as they can not be displayed
        for i in range(
            0, len(discharge)
        ):  # correcting these to be 0, so they do not have a
            if discharge[i] == "Ice":
                discharge[i] = 0

        if category == 1 and city != "Judson":
            dataset2 = discharge
        elif category == 3 or city == "Judson":
            dataset3 = discharge
        elif category == 4:
            dataset1 = discharge

    if category == 1:
        updateDictionary(times, stream_level, city, "Elevation", "gauge")
        updateDictionary(times, gauge_height, city, "Gauge Height", "gauge")
        updateDictionary(times, discharge, city, "Discharge", "gauge")
    elif category == 2:
        updateDictionary(times, stream_level, city, "Elevation", "gauge")
        updateDictionary(times, gauge_height, city, "Gauge Height", "gauge")
    elif category == 3:
        updateDictionary(times, stream_level, city, "Elevation", "gauge")
        updateDictionary(times, gauge_height, city, "Gauge Height", "gauge")
        updateDictionary(times, discharge, city, "Discharge", "gauge")
        updateDictionary(times, water_temp, city, "Water Temperature", "gauge")
    elif category == 4:
        updateDictionary(times, gauge_height, city, "Gauge Height", "gauge")
        updateDictionary(times, discharge, city, "Discharge", "gauge")

    os.remove(f"./services/static/JSON{city}.csv")
    os.remove(f"./services/static/JSONdata.txt")


def pullDamData(dam_location):

    DAM_dict = {
        "Fort Peck": ["FTPK"],
        "Garrison": ["GARR"],
        "Oahe": ["OAHE"],
        "Big Bend": ["BEND"],
        "Fort Randall": ["FTRA"],
        "Gavins Point": ["GAPT"],
    }

    # Use of CSV is here (Aditya Pachpande)

    file_name = f"./services/static/JSON{dam_location}.txt"
    file_name_csv = f"./services/static/JSON{dam_location}.csv"

    # Use of CSV is here (Aditya Pachpande)

    location_data = DAM_dict[f"{dam_location}"]
    location_code = location_data[0]

    url = f"https://www.nwd-mr.usace.army.mil/rcc/programs/data/{location_code}"

    response = requests.get(url, verify=False)

    # Use of CSV is here (Aditya Pachpande)
    with open(file_name, "w") as f:
        writer = csv.writer(f)
        for line in response.text.split("\n"):
            writer.writerow(line.split("\t"))

    # Use of CSV is here (Aditya Pachpande)
    count = 0
    alternate = 0
    data = []
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
    index = 0

    # creating text file
    with open(file_name, "r") as file:
        for line in file:
            if count == 4:
                data.append(line)
            elif count > 5:
                if alternate % 2 == 0:
                    data.append(line.strip('"'))
                alternate += 1
            count += 1

    with open(file_name, "w") as file:
        for line in data:
            file.write(f"{line}")

    with open(file_name, "r") as filer:
        for banana in filer:
            if index > 1 and index < 170:
                liney = banana.split()
                Date.append(liney[0])
                Hour.append(liney[1])
                Elevation.append(liney[2])
                Flow_Spill.append(liney[3])
                Flow_Powerhouse.append(liney[4])
                Flow_Out.append(liney[5])
                Elev_Tailwater.append(liney[6])
                Energy.append(liney[7])
                Temp_Water.append(liney[8])
                Temp_Air.append(liney[9])
            index += 1

    lister = [
        Elevation,
        Flow_Spill,
        Flow_Powerhouse,
        Flow_Out,
        Elev_Tailwater,
        Energy,
        Temp_Water,
        Temp_Air,
    ]
    list_data = [
        "Feet",
        "Cubic Feet Per Second",
        "Cubic Feet Per Second",
        "Cubic Feet Per Second",
        "Feet",
        "MWH",
        "Fahrenheit",
        "Fahrenheit",
    ]

    # Converts String Data to Numerical, Parsing and Salvaging Bad Data
    Elevation = ParseData(Elevation)
    Flow_Spill = ParseData(Flow_Spill)
    Flow_Powerhouse = ParseData(Flow_Powerhouse)
    Flow_Out = ParseData(Flow_Out)
    Elev_Tailwater = ParseData(Elev_Tailwater)
    Energy = ParseData(Energy)
    Temp_Water = ParseData(Temp_Water)
    Temp_Air = ParseData(Temp_Air)

    # Removes pulled file from storage once used, and no longer needed
    os.remove(f"./services/static/JSON{dam_location}.txt")

    index = 0
    times = []

    for item in range(0, len(Hour)):
        times.append(Date[index] + " " + Hour[index])
        index += 1

    updateDictionary(times, Elevation, dam_location, "Elevation", "dam")
    updateDictionary(times, Flow_Spill, dam_location, "Flow Spill", "dam")
    updateDictionary(times, Flow_Powerhouse, dam_location, "Flow Powerhouse", "dam")
    updateDictionary(times, Flow_Out, dam_location, "Flow Out", "dam")
    updateDictionary(times, Elev_Tailwater, dam_location, "Tailwater Elevation", "dam")
    updateDictionary(times, Energy, dam_location, "Energy", "dam")
    updateDictionary(times, Temp_Water, dam_location, "Water Temperature", "dam")
    updateDictionary(times, Temp_Air, dam_location, "Air Temperature", "dam")


def pullMesonetData(location):

    NODAK_dict = {
        "Fort Yates": ["89", "Fort Yates, ND"],
        "Linton": ["35", "Linton, ND"],
        "Mott": ["69", "Mott, ND"],
        "Carson": ["96", "Carson, ND"],
    }

    day1, month1, year1, day2, month2, year2 = getDates()

    location_dict = NODAK_dict[f"{location}"]
    station = location_dict[0]

    file_name = f"./services/static/JSON{location}.csv"

    url_csv = f"https://ndawn.ndsu.nodak.edu/table.csv?ttype=hourly&station={station}&begin_date={year1}-{month1}-{day1}&end_date={year2}-{month2}-{day2}"

    response = requests.get(url_csv)

    # check if response was successful
    if response.status_code == 200:
        # parse the csv data using the csv modules reader object
        reader = csv.reader(response.text.splitlines())
        with open(file_name, "w", newline="") as file:
            writer = csv.writer(file)
            # write parsed csv data to file
            writer.writerows(reader)
        file.close()

    # list of columns need to delete from dataframe
    list_to_del = [
        "Avg Air Temp Flag",
        "Avg Rel Hum Flag",
        "Avg Bare Soil Temp Flag",
        "Avg Turf Soil Temp Flag",
        "Avg Wind Speed Flag",
        "Max Wind Speed Flag",
        "Avg Wind Dir Flag",
        "Avg Wind Dir SD Flag",
        "Avg Dew Point Flag",
        "Avg Baro Press Flag",
        "Avg Sol Rad Flag",
        "Total Rainfall Flag",
    ]

    list_to_del_2 = ["Station Name", "Latitude", "Longitude", "Elevation"]

    df = pd.read_csv(file_name, skiprows=3)  # get rid of first three rows
    df2 = df.iloc[1:]  # deleting the second line, which was just units
    for i in list_to_del:  # deleting the columns from list
        del df2[i]

    for i in list_to_del_2:  # deleting the columns from list
        del df2[i]

    df2.to_csv(file_name, index=False)  # writing to a csv file

    years = df2["Year"].tolist()
    months = df2["Month"].tolist()
    days = df2["Day"].tolist()
    hours = df2["Hour"].tolist()

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

    avg_air_temp = df2["Avg Air Temp"].tolist()
    avg_rel_hum = df2["Avg Rel Hum"].tolist()
    avg_bare_soil_temp = df2["Avg Bare Soil Temp"].tolist()
    avg_turf_soil_temp = df2["Avg Turf Soil Temp"].tolist()
    avg_wind_speed = df2["Avg Wind Speed"].tolist()
    avg_wind_dir = df2["Avg Wind Dir"].tolist()
    avg_wind_dir_sd = df2["Avg Wind Dir SD"].tolist()
    tot_sol_rad = df2["Avg Sol Rad"].tolist()
    tot_rainfall = df2["Total Rainfall"].tolist()
    avg_baro_press = df2["Avg Baro Press"].tolist()
    avg_dew_point = df2["Avg Dew Point"].tolist()
    avg_wind_chill = df2["Avg Wind Chill"].tolist()

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

    updateDictionary(
        times, avg_air_temp, location, "Average Air Temperature", "mesonet"
    )
    updateDictionary(
        times, avg_rel_hum, location, "Average Relative Humidity", "mesonet"
    )
    updateDictionary(
        times, avg_bare_soil_temp, location, "Average Bare Soil Temperature", "mesonet"
    )
    updateDictionary(
        times, avg_turf_soil_temp, location, "Average Turf Soil Temperature", "mesonet"
    )
    updateDictionary(times, avg_wind_speed, location, "Maximum Wind Speed", "mesonet")
    updateDictionary(times, avg_wind_dir, location, "Average Wind Direction", "mesonet")
    updateDictionary(times, tot_sol_rad, location, "Total Solar Radiation", "mesonet")
    updateDictionary(times, tot_rainfall, location, "Total Rainfall", "mesonet")
    updateDictionary(
        times, avg_baro_press, location, "Average Baromatric Pressure", "mesonet"
    )
    updateDictionary(times, avg_dew_point, location, "Average Dew Point", "mesonet")
    updateDictionary(times, avg_wind_chill, location, "Average Wind Chill", "mesonet")

    os.remove(file_name)


def pullShadeHill():

    start_day, start_month, start_year, end_day, end_month, end_year = getDates()
    datasets = [
        "AF",
        "FB",
        "IN",
        "MM",
        "MN",
        "MX",
        "PP",
        "PU",
        "QD",
        "QRD",
        "QSD",
        "RAD",
    ]

    for dataset in datasets:
        shadehillrequest(
            start_year, start_month, start_day, end_year, end_month, end_day, dataset
        )


def shadehillrequest(
    startyear, startmonth, startday, endyear, endmonth, endday, dataset
):

    # URL of the form action
    url = "https://www.usbr.gov/gp-bin/arcread.pl"

    # Form data to be submitted
    form_data = {
        "st": "SHR",
        "by": startyear,
        "bm": startmonth,
        "bd": startday,
        "ey": endyear,
        "em": endmonth,
        "ed": endday,
        "pa": dataset,
        # Data options: AF, FB, IN, MM, MN, PP, PU, QD, QRD, QSD, RAD
    }

    datasets = {
        "AF": "Reservoir Storage Content",
        "FB": "Reservoir Forebay Elevation",
        "IN": "Daily Mean Computed Inflow",
        "MM": "Daily Mean Air Temperature",
        "MN": "Daily Minimum Air Temperature",
        "MX": "Daily Maximum Air Temperature",
        "PP": "Total Precipitation (inches per day)",
        "PU": "Total Water Year Precipitation",
        "QD": "Daily Mean Total Discharge",
        "QRD": "Daily Mean River Discharge",
        "QSD": "Daily Mean Spillway Discharge",
        "RAD": "Daily Mean Gate One Opening",
    }

    dataname = datasets[dataset]

    # Sending the POST request
    response = requests.post(url, data=form_data)

    # Split the text into lines
    lines = response.text.strip().split("\r")

    count = 0
    times = []
    datas = []

    for line in lines:
        if count >= 3:

            date = line.split(" ")[0]
            year = (date.split("/")[0]).strip("\n")
            month = date.split("/")[1]
            day = date.split("/")[2]

            # Accumulates data
            datas.append(line.split(" ")[-1])

            # Assumes midnight for every day, since time isn't provided
            times.append(year + "-" + month + "-" + day + " " + "00:00")

        count += 1

    del times[-1]
    del datas[-1]


def pull():

    # Pulls and stores all gauge data by location
    pullGaugeData("Hazen")
    pullGaugeData("Stanton")
    pullGaugeData("Washburn")
    pullGaugeData("Price")
    pullGaugeData("Bismarck")
    pullGaugeData("Schmidt")
    pullGaugeData("Judson")
    pullGaugeData("Mandan")
    pullGaugeData("Breien")
    pullGaugeData("Wakpala")
    pullGaugeData("Little Eagle")
    pullGaugeData("Cash")
    pullGaugeData("Whitehorse")

    # Pulls and stores all dam data by location
    pullDamData("Fort Peck")
    pullDamData("Garrison")
    pullDamData("Oahe")
    pullDamData("Big Bend")
    pullDamData("Fort Randall")
    pullDamData("Gavins Point")

    # Pulls and stores all North Dakota mesonet data by location
    pullMesonetData("Carson")
    pullMesonetData("Fort Yates")
    pullMesonetData("Linton")
    pullMesonetData("Mott")

    # Pulls and stores all forecast data given a certain dataset, also creates JSON files
    # STILL HAVE TO FIGURE OUT WHICH DATASETS WE WANT
    forecastdatacall("temperature")
    forecastdatacall("dewpoint")
    forecastdatacall("relativeHumidity")
    forecastdatacall("windChill")
    # createForecastJson("Stanley", ["temperature", "dewpoint", "windChill"])
    # Pulls all Shadehill data, takes a long time to run. Recommend running separately
    pullShadeHill()


pull()
