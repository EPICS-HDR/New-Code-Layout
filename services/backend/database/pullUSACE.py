import requests
import csv
from backend.database.parseData import ParseData
import os
from backend.database.sqlclasses import updateDictionary

def pullDamData(dam_location):

    DAM_dict = {'Fort Peck':['FTPK'],
                'Garrison':['GARR'],
                'Oahe':['OAHE'],
                'Big Bend': ['BEND'],
                'Fort Randall': ['FTRA'],
                'Gavins Point': ['GAPT']}

    file_name = f'./static/JSON{dam_location}.txt'
    file_name_csv = f'./static/JSON{dam_location}.csv'
    location_data = DAM_dict[f'{dam_location}']
    location_code = location_data[0]

    url = f'https://www.nwd-mr.usace.army.mil/rcc/programs/data/{location_code}'

    response = requests.get(url, verify=False) 

    with open(file_name, "w") as f:
        writer = csv.writer(f)
        for line in response.text.split("\n"):
            writer.writerow(line.split("\t"))

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

    with open(file_name,'r') as filer: 
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

    lister = [Elevation, Flow_Spill, Flow_Powerhouse, Flow_Out, Elev_Tailwater, Energy, Temp_Water, Temp_Air]
    list_data = ['Feet', 'Cubic Feet Per Second', 'Cubic Feet Per Second', 'Cubic Feet Per Second', 'Feet', 'MWH', 'Fahrenheit', 'Fahrenheit']
    
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
    os.remove(f'./static/JSON{dam_location}.txt')

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