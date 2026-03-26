'''
Author: Kartik Jariam & Andrew Vu
Date: 1/29/2026
Purpose: This is the master config for all source files. Everything hardcoded must be present in this file. The host must modify this file to add new
         stations or change how data pulling works.
''' 

# -------------------------------------- General --------------------------------------

<<<<<<< HEAD
LOCATION_TO_TABLE = {
    "Big Bend": "dam",
    "Fort Randall": "dam",
    "Gavins Point": "dam",
    "Garrison": "dam",
    "Fort Peck": "dam",
    "Bison": "cocorahs",
    "Faulkton": "cocorahs",
    "Langdon": "cocorahs",
    "Shadehill": "shadehill",
    "Bismarck": "noaa_weather",
    "Williston/Basin": "noaa_weather",
    "Minot": "noaa_weather",
    "Fort Yates": "mesonet",
    "Linton": "mesonet",
    "Mott": "mesonet",
    "Carson": "mesonet",
}

# SQL field mappings for variable names
SQL_CONVERSION = {
    "Elevation": "elevation",
    "Air Temperature": "air_temp",
    "Water Temperature": "water_temp",
    "Flow Spill": "flow_spill",
    "Flow Powerhouse": "flow_power",
    "Flow Out": "flow_out",
    "Tailwater Elevation": "tail_ele",
    "Energy": "energy",
    "Discharge": "discharge",
    "Gauge Height": "gauge_height",
    "Average Air Temperature": "avg_air_temp",
    "Average Relative Humidity": "avg_rel_hum",
    "Average Bare Soil Temperature": "avg_bare_soil_temp",
    "Average Turf Soil Temperature": "avg_turf_soil_temp",
    "Maximum Wind Speed": "max_wind_speed",
    "Average Wind Direction": "avg_wind_dir",
    "Total Solar Radiation": "total_solar_rad",
    "Total Rainfall": "total_rainfall",
    "Average Baromatric Pressure": "avg_bar_pressure",
    "Average Dew Point": "avg_dew_point",
    "Average Wind Chill": "avg_wind_chill",
    "Precipitation": "precipitation",
    "Snowfall": "snowfall",
    "Snow Depth": "snow_depth",
    "Reservoir Storage Content": "res_stor_content",
    "Reservoir Forebay Elevation": "res_forebay_elev",
    "Daily Mean Computed Inflow": "daily_mean_comp_inflow",
    "Daily Mean Air Temperature": "daily_mean_air_temp",
    "Daily Minimum Air Temperature": "daily_min_air_temp",
    "Daily Maximum Air Temperature": "daily_max_air_temp",
    "Total Precipitation (inches per day)": "tot_precip_daily",
    "Total Water Year Precipitation": "tot_year_precip",
    "Daily Mean Total Discharge": "daily_mean_tot_dis",
    "Daily Mean River Discharge": "daily_mean_river_dis",
    "Daily Mean Spillway Discharge": "daily_mean_spill_dis",
    "Daily Mean Gate One Opening": "daily_mean_gate_opening",
    "temperature": "temperature",
    "dewpoint": "dew_point",
    "relativeHumidity": "rel_humidity",
    "windChill": "wind_chill",
    "Average Temperature": "avg_temp",
    "Max Temperature": "max_temp",
    "Min Temperature": "min_temp",
    # Water Quality Parameters
    "Phosphorus (Total) (P)": "total_phosphorus",
    "Phosphorus (Total Kjeldahl) (P)": "total_kjeldahl_phosphorus",
    "Nitrate + Nitrite (N)": "nitrate_nitrite",
    "Nitrate Forms Check": "nitrate_forms_check",
    "Nitrate + Nitrite (N) Dis": "nitrate_nitrite_dissolved",
    "Nitrogen (Total Kjeldahl)": "total_kjeldahl_nitrogen",
    "Nitrogen (TKN-Dissolved)": "tkn_dissolved",
    "Nitrogen (Total-Dis)": "total_nitrogen_dissolved",
    "E.coli": "e_coli",
    "Nitrogen (Total)": "total_nitrogen",
    "pH": "ph",
    "Ammonia (N)": "ammonia_nitrogen",
    "Ammonia (N)-Dissolved": "ammonia_nitrogen_dissolved",
    "Ammonia Forms Check": "ammonia_forms_check",
    "Diss Ammonia TKN Check": "diss_ammonia_tkn_check",
    "Dissolved Phosphorus as P": "dissolved_phosphorus",
}
=======
>>>>>>> 3d612f71973f7c18bfbf05a6e5867b2a94f7e90d

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