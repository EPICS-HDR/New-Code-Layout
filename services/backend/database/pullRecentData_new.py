from datetime import datetime, date, timedelta
# FIXME: requests, forecast are these imports not listed in requirements.txt?
# FIXME: forecast file does not exist.
import requests
import pandas as pd
import os
import numpy as np
from sqlclasses import updateDictionary
from forecast import forecastdatacall
import io


def getDates():
    numDays = 30
    now = datetime.now()
    end_day = now.strftime("%d")
    end_month = now.strftime("%m")
    end_year = now.strftime("%Y")
    start_date = (date.today() - timedelta(days=numDays)).isoformat()

    index = 0
    year, month, day = [], [], []
    for character in start_date:
        if index < 4:
            year.append(character)
        elif 4 < index < 7:
            month.append(character)
        elif 7 < index:
            day.append(character)
        index += 1

    return ("".join(day), "".join(month), "".join(year), end_day, end_month, end_year)


def ParseData(List):
    for index in range(len(List)):
        item = str(List[index])
        neg = 0

        if item == "-":
            item = "0"
        if '"' in item:
            item = item.replace('"', "")
        if "," in item:
            item = item.replace(",", "")
        if "-" in item:
            neg = 1
            item = item.strip("-")

        try:
            data = float(item)
        except:
            data = 0

        List[index] = data * (-1 if neg else 1)
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
    code, category = location_dict[city]

    url_config = {
        1: f"uv?cb_00060=on&cb_00065=on&cb_63160=on&linecount=56",
        2: f"uv?cb_00065=on&cb_63160=on&linecount=54",
        3: f"uv?cb_00010=on&cb_00060=on&cb_00065=on&cb_63160=on&linecount=58",
        4: f"uv?cb_00060=on&cb_00065=on&linecount=54",
    }
    url = (
        f"https://waterdata.usgs.gov/nwis/{url_config[category]}"
        f"&format=rdb&site_no={code}&legacy=1&period="
        f"&begin_date={start_year}-{start_month}-{start_day}"
        f"&end_date={end_year}-{end_month}-{end_day}"
    )

    response = requests.get(url)
    lines = response.text.split("\n")

    # Process data directly from response
    data_lines = []
    for line in lines[linecount + 1 :]:  # Skip header lines
        if line.strip() and not line.startswith("#"):
            data_lines.append(line.split("\t"))

    # Extract columns directly
    times, datasets = [], [[] for _ in range(num_sets)]
    for row in data_lines:
        if len(row) > max_col:
            times.append(row[2])
            for i in range(num_sets):
                datasets[i].append(row[4 + i * 2])

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


def pullDamData(dam_location):
    DAM_codes = {
        "Fort Peck": "FTPK",
        "Garrison": "GARR",
        "Oahe": "OAHE",
        "Big Bend": "BEND",
        "Fort Randall": "FTRA",
        "Gavins Point": "GAPT",
    }

    response = requests.get(
        f"https://www.nwd-mr.usace.army.mil/rcc/programs/data/{DAM_codes[dam_location]}",
        verify=False,
    )

    # Process text response directly
    lines = [line.split() for line in response.text.split("\n") if line.strip()]
    data = lines[4:-1]  # Skip headers and footers

    # Extract columns directly
    Date, Hour = [], []
    metrics = [[] for _ in range(8)]
    for row in data:
        Date.append(row[0])
        Hour.append(row[1])
        for i in range(8):
            metrics[i].append(row[2 + i])

    # Parse and update database
    times = [f"{Date[i]} {Hour[i]}" for i in range(len(Date))]
    for i, name in enumerate(
        [
            "Elevation",
            "Flow Spill",
            "Flow Powerhouse",
            "Flow Out",
            "Tailwater Elevation",
            "Energy",
            "Water Temperature",
            "Air Temperature",
        ]
    ):
        updateDictionary(times, ParseData(metrics[i]), dam_location, name, "dam")


def pullMesonetData(location):
    station_map = {"Fort Yates": "89", "Linton": "35", "Mott": "69", "Carson": "96"}

    # Get data directly from URL
    response = requests.get(
        f"https://ndawn.ndsu.nodak.edu/table.csv?"
        f"ttype=hourly&station={station_map[location]}&"
        f"begin_date={year1}-{month1}-{day1}&end_date={year2}-{month2}-{day2}"
    )

    # Process CSV data in memory
    df = pd.read_csv(io.StringIO(response.text), skiprows=3)
    df = df.iloc[1:].drop(
        columns=[
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
            "Station Name",
            "Latitude",
            "Longitude",
            "Elevation",
        ]
    )

    # Process timestamps
    times = []
    for _, row in df.iterrows():
        month = f"{row['Month']:02d}"
        day = f"{row['Day']:02d}"
        hour = f"{row['Hour']:04d}"
        times.append(f"{row['Year']}-{month}-{day} {hour[:2]}:{hour[2:]}")

    # Update database with parsed data
    for col in df.columns:
        if col not in ["Year", "Month", "Day", "Hour"]:
            updateDictionary(
                times, ParseData(df[col].tolist()), location, col, "mesonet"
            )


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
    # Gauge locations
    for city in [
        "Hazen",
        "Stanton",
        "Washburn",
        "Price",
        "Bismarck",
        "Schmidt",
        "Judson",
        "Mandan",
        "Breien",
        "Wakpala",
        "Little Eagle",
        "Cash",
        "Whitehorse",
    ]:
        pullGaugeData(city)

    # Dam locations
    for dam in [
        "Fort Peck",
        "Garrison",
        "Oahe",
        "Big Bend",
        "Fort Randall",
        "Gavins Point",
    ]:
        pullDamData(dam)

    # Mesonet stations
    for station in ["Carson", "Fort Yates", "Linton", "Mott"]:
        pullMesonetData(station)

    # Forecast data
    for param in ["temperature", "dewpoint", "relativeHumidity", "windChill"]:
        forecastdatacall(param)

    pullShadeHill()


if __name__ == "__main__":
    pull()
