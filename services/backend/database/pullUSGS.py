import requests
import csv
from backend.database.sqlclasses import updateDictionary
import os

def pullGaugeData(city, start_day, start_month, start_year, end_day, end_month, end_year):
    
    location_dict = {'Hazen':['06340500', 1],
                    'Stanton':['06340700', 2],
                    'Washburn':['06341000', 2],
                    'Price': ['06342020', 2],
                    'Bismarck': ['06342500', 3],
                    'Schmidt': ['06349700', 2],
                    'Judson': ['06348300', 1], 
                    'Mandan': ['06349000', 1],
                    'Breien': ['06354000', 1],
                    'Wakpala': ['06354881', 4],
                    'Little Eagle': ['06357800', 4],
                    'Cash': ['06356500', 4],
                    'Whitehorse': ['06360500', 4]}

    location_data = location_dict[f'{city}']
    code = location_data[0]
    category = location_data[1]

    if category == 1:
        url = f'https://waterdata.usgs.gov/nwis/uv?cb_00060=on&cb_00065=on&cb_63160=on&format=rdb&site_no={code}&legacy=1&period=&begin_date={start_year}-{start_month}-{start_day}&end_date={end_year}-{end_month}-{end_day}'
        num_sets = 3
        linecount = 56
    elif category == 2:
        url = f'https://waterdata.usgs.gov/nwis/uv?cb_00065=on&cb_63160=on&format=rdb&site_no={code}&legacy=1&period=&begin_date={start_year}-{start_month}-{start_day}&end_date={end_year}-{end_month}-{end_day}'
        num_sets = 2
        linecount = 54
    elif category == 3:
        url = f'https://waterdata.usgs.gov/nwis/uv?cb_00010=on&cb_00060=on&cb_00065=on&cb_63160=on&format=rdb&site_no={code}&legacy=1&period=&begin_date={start_year}-{start_month}-{start_day}&end_date={end_year}-{end_month}-{end_day}'
        num_sets = 4
        linecount = 58
    elif category == 4:
        url = f'https://waterdata.usgs.gov/nwis/uv?cb_00060=on&cb_00065=on&format=rdb&site_no={code}&legacy=1&period=&begin_date={start_year}-{start_month}-{start_day}&end_date={end_year}-{end_month}-{end_day}'
        num_sets = 2
        linecount = 54
        
    linecount2 = linecount + 3
        
    response = requests.get(url)

    file_name = f"./services/static/JSON{city}"

    with open('./services/static/JSONdata.txt', "w") as f: # writes text from the website to text
        writer = csv.writer(f)
        for line in response.text.split("\n"):
            writer.writerow(line.split("\t"))

    data = []
    count = 0
    alternate = 0

    with open('./services/static/JSONdata.txt', "r") as file: 
        for line in file:
            if count == linecount:
                data.append(line)
            elif count > linecount2:
                if alternate % 2 == 0:
                    line.strip('\n')
                    data.append(line)
                alternate += 1
            count += 1

    with open (f'{file_name}.csv', "w") as file:
        for line in data:
            file.write(f"{line}")
            
    with open (f'{file_name}.csv', "w") as file:
        for line in data:
            file.write(f"{line}")    
        
    with open ('./services/static/JSONdata.txt', "w") as file:
        for line in data:
            file.write(f"{line}")
        
    with open(f'{file_name}.csv', 'rt') as f:
        reader = csv.reader(f)
        data_matrix = list(reader)

    data_matrix1 = data_matrix[:-1]

    if num_sets == 2:
        length = 8 # when there are two data points, the length of the matrix is 8
    elif num_sets == 3: # length is ten when there are three data points
        length = 10 
    elif num_sets == 4:
        length = 12

    times = []
    dataset1 = []
    dataset2 = []
    dataset3 = []
    dataset4 = []

    for matrixindex in range(4,len(data_matrix1)): # setting the data we need into lists
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
        name1 = 'Stream water level elevation above NAVD'
        name2 = 'Discharge, cubic feet per second'
        name3 = 'Gauge height, feet, [Bubbler]'
        if city == 'Judson':
            discharge = dataset3
            gauge_height = dataset2
            name3 = 'Discharge, cubic feet per second'
            name2 = 'Gauge height, feet, [Bubbler]'
    elif category == 2:
        stream_level = dataset1
        gauge_height = dataset2
        name1 = 'Stream water level elevation above NAVD'
        name2 = 'Gauge height, feet, [Bubbler]'
    elif category == 3:
        stream_level = dataset1
        water_temp = dataset2
        discharge = dataset3
        gauge_height = dataset4
        name1 = 'Stream water level elevation above NAVD'
        name2 = 'Water temperature, Celcius'
        name3 = 'Discharge, cubic feet per second'
        name4 = 'Gauge height, feet, [Bubbler]'
    elif category == 4:
        discharge = dataset1
        gauge_height = dataset2
        name1 = 'Discharge, cubic feet per second'
        name2 = 'Gauge height, feet, [Bubbler]'
    
    if category != 2: # correcting the values that say 'Ice', as they can not be displayed
        for i in range(0, len(discharge)): # correcting these to be 0, so they do not have a 
            if discharge[i] == 'Ice':
                discharge[i] = 0
        
        if category == 1 and city != 'Judson':
            dataset2 = discharge
        elif category == 3 or city == 'Judson':
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
    os.remove(f'./services/static/JSONdata.txt')