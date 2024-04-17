import json
from datetime import date, timedelta
import datetime
from sqlclasses import dictpull as dp

def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)

hours = ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24"]
minutes = ["00", "15", "30", "45"]

def dictpull(location, dataset, startdate, enddate):
    
    start_year = []
    start_month = []
    start_day = []
    end_year = []
    end_month = []
    end_day = []
    
    index = 0
    for character in startdate:
        if index < 4:
            start_year.append(character)
        elif 4 < index < 7:
            start_month.append(character)
        elif index > 7:
            start_day.append(character)
        index += 1
            
    start_year = int("".join(start_year))
    start_month = int("".join(start_month))
    start_day = int("".join(start_day))
    
    index = 0
    for character in enddate:
        if index < 4:
            end_year.append(character)
        elif 4 < index < 7:
            end_month.append(character)
        elif index > 7:
            end_day.append(character)
        index += 1
            
    end_year = int("".join(end_year))
    end_month = int("".join(end_month))
    end_day = int("".join(end_day))
    
    startdate = datetime.date(start_year, start_month, start_day)

    enddate = datetime.date(end_year, end_month, end_day)

    dates = []
    for dt in daterange(startdate, enddate):
        dates.append(dt.strftime("%Y-%m-%d"))

    with open('dictionary.json', 'r') as file:
            existing_data = file.read()
    data_dict = json.loads(existing_data)

    times = []
    data = []

    for date in dates:
        
        # Checks to see if date is in dictionary
        if data_dict[f"{location}"][f"{dataset}"].get(date, 0) != 0:
            
            # Creates temporary dictionary for specific date
            temp_dict = data_dict[f"{location}"][f"{dataset}"][f"{date}"]
            
            # Tries all possible keys
            for hour in hours:
                for minute in minutes:
                    time = hour + ":" + minute

                    # Appends relevant data to lists
                    if temp_dict.get(time, 3.14159265) != 3.14159265:
                        times.append(date + " " + time)
                        try:
                            data.append(float(temp_dict[time]))
                        except:
                            data.append(0)

    del times[-1]
    del data[-1]
    
    return times, data

def updateDictionary(ttimes, data, location, dataset):
    
    # Fix for bug where location number was occassionally being passed
    locationdict = {'6340500':'Hazen',
                    '6340700':'Stanton',
                    '6341000':'Washburn',
                    '6342020':'Price',
                    '6342500':'Bismarck',
                    '6349700':'Schmidt',
                    '6348300':'Judson',
                    '6349000':'Mandan',
                    '6354000':'Breien',
                    '06354881':'Wakpala',
                    '06357800':'Little Eagle',
                    '06356500':'Cash',
                    '06360500':'Whitehorse'
    }
    
    location = str(location)
    if locationdict.get(location, 0) != 0:
        location = locationdict[location]

    dates = []
    times = []
    for string in ttimes:
        temp = string.split()
        if len(temp) == 2:
            dates.append(temp[0])
            times.append(temp[1])

    # Load existing data from file
    with open('dictionary.json', 'r') as file:
        existing_data = file.read()
    data_dict = json.loads(existing_data)

    # Create nested dictionary for the new datapoints
    datapoints = {}
    
    length = len(data) - 1
    for i in range(0, len(dates)):
        if dates[i] not in datapoints:
            datapoints[dates[i]] = {}
        datapoints[dates[i]][times[i]] = data[i]
        if i >= length:
            break

    # Create nested dictionary for the new dataset
    if dataset not in data_dict.get(location, {}):
        data_dict.setdefault(location, {})[dataset] = {}

    # Update nested dictionary for the new datapoints
    data_dict[location][dataset].update(datapoints)

    # Save updated data to file
    with open('dictionary.json', 'w') as file:
        file.write(json.dumps(data_dict))

def createMonthJson(location, datasets):

    # Gets the current date and month ago
    start_date = (date.today()-timedelta(days=30)).isoformat()
    end_date = date.today().isoformat()

    if len(datasets) == 2 or len(datasets) == 3 or len(datasets) == 4:
        datalists = []

        for dataset in datasets:
            times, data = dp(location, dataset, start_date, end_date)
            
            datalists.append(times)
            datalists.append(data)
    
    else:
        datalists = []

        index = 0
        for dataset in datasets:

            times, data = dp(location, dataset, start_date, end_date)
            if index == 0: 
                del times[-1]
                datalists.append(times)
            del data[-1]
            datalists.append(data)
            index += 1

    json_str = json.dumps(datalists)

    # Write the JSON string to a text file
    with open(f'./services/static/JSON/{location.lower()}graphs.json', 'w') as f:
        f.write(json_str)

def deleteDatasetEntries(dataset):
    # This code will run through every existing dataset in the dictionary and remove all entires for a specific dataset
    # Only run IF ABSOLUTELY sure
    with open('dictionary.json', 'r') as file:
        existing_data = file.read()
    data_dict = json.loads(existing_data)
    for location in data_dict:
        if dataset in data_dict[location]:
            data_dict[location].pop(dataset)
    with open('dictionary.json', 'w') as file:
        file.write(json.dumps(data_dict))

def createForecastJson(location, datasets):

    # Gets the current date and month ago
    end_date = (date.today()+timedelta(days=30)).isoformat()
    start_date = date.today().isoformat()

    if len(datasets) == 2 or len(datasets) == 3 or len(datasets) == 4:
        datalists = []

        for dataset in datasets:
            times, data = dictpull(location, dataset, start_date, end_date)
            datalists.append(times)
            datalists.append(data)
    
    else:
        datalists = []

        index = 0
        for dataset in datasets:

            times, data = dictpull(location, dataset, start_date, end_date)
            if index == 0: 
                del times[-1]
                datalists.append(times)
            del data[-1]
            datalists.append(data)
            index += 1

    json_str = json.dumps(datalists)

    # Write the JSON string to a text file
    with open(f'./services/static/JSON/{location.lower()}.json', 'w') as f:
        f.write(json_str)