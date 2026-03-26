'''
Author: Kartik Jariam & Andrew Vu
Date: 1/29/2026
Purpose: This is the master config for all source files. Everything hardcoded must be present in this file. The host must modify this file to add new
         stations or change how data pulling works.
''' 

# -------------------------------------- General --------------------------------------


# --------------------------------------  DANR   --------------------------------------
DANRConfig = {
    'baseURL' : "https://apps.sd.gov/NR92WQMAP/api/station/",
    'stationList' : ["SWLAZZZ2411A", "CAMPPOCP01", "SD_11904"],
    'dateTimeFormat' : "%Y-%m-%dT%H:%M:%S"
}

# --------------------------------------  COCORAHS  --------------------------------------
COCORAHSConfig = {
    'baseURL' : "http://data.rcc-acis.org/StnData?params=",
    'stationList' : {
        "Bison, SD": ["SDFK0006", "20070624"],
        "Faulkton, SD": ["SDFK0009", "20230401"],
        "Bismarck, ND": ["NDBH0034", "20120416"],
        "Langdon, ND": ["NDCV0004", "20200311"],
    },
    'Elements' : ['maxt', 'mint', 'avgt', 'obst', 'pcpn', 'snow', 'snwd']
}
# --------------------------------------  USACE  --------------------------------------
USACEConfig = {
    'baseURL' : "https://www.nwd-mr.usace.army.mil/rcc/programs/data/",
    'stationList' : ["GARR"],
    'ColumnNames' : ['DateTime', 'Temp_Air', 'Flow_Out', 'Elev_Tailwater', 'Energy', 'Temp_Water', 'Elev', 'Flow_Spill', 'Flow_Powerhouse']
}