'''
Author: Kartik Jariam & Andrew Vu
Date: 1/29/2026
Purpose: This is the master config for all source files. Everything hardcoded must be present in this file. The host must modify this file to add new
         stations or change how data pulling works.
''' 
import os

# -------------------------------------- General --------------------------------------
# Database path - automatically calculated from project root
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Measurements.db")

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

# --------------------------------------  DANR   --------------------------------------
DANRConfig = {
    'baseURL' : "https://apps.sd.gov/NR92WQMAP/api/station/",
    'stationList' : ["SWLAZZZ2411A", "CAMPPOCP01", "SD_11904"],
    'dateTimeFormat' : "%Y-%m-%dT%H:%M:%S"
}

# --------------------------------------  COCORAHS  --------------------------------------
# Format: "Location Name": ["station_id", "start_date", "display_name"]
# To add a station: Add a new entry like: "City, State": ["STCODE0001", "20200101", "City"]
COCORAHS_STATIONS = {
    "Bison, SD": ["SDFK0006", "20070624", "Bison"],
    "Faulkton, SD": ["SDFK0009", "20230401", "Faulkton"],
    "Bismarck, ND": ["NDBH0034", "20120416", "Bismarck"],
    "Langdon, ND": ["NDCV0004", "20200311", "Langdon"],
}

# --------------------------------------Shadehill--------------------------------------
# Format: "code": "Dataset Name"
# To add a dataset: Add a new entry like: "XX": "Dataset Description"
SHADEHILL_DATASETS = {
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

# --------------------------------------  NDGIS  --------------------------------------
# NDGIS automatically discovers stations from ArcGIS. To limit the number of stations processed,
# modify the limit parameter in New_NDGIS.py's _station_ids() function (default: 10)

# --------------------------------------  NOAA   --------------------------------------
# Format: ("Location Name", "GHCND:station_id")
# To add a station: Add a new entry like: ("City, State", "GHCND:USW00012345")
# Get station IDs from: https://www.ncei.noaa.gov/cdo-web/
NOAA_STATIONS = [
    ("Bismarck", "GHCND:USW00024011"),
    ("Williston/Basin", "GHCND:USW00024018"),
    ("Minot", "GHCND:USW00024021"),
]

# --------------------------------------  USGS   --------------------------------------
# Format: 'Location': ['site_code', category]
# Categories: 1=Elevation+Discharge+GaugeHeight, 2=Elevation+GaugeHeight, 3=All+WaterTemp, 4=Discharge+GaugeHeight
# To add a gauge: Add a new entry like: 'Location': ['06340000', 1]
# Get site codes from: https://waterdata.usgs.gov/nwis
USGS_LOCATIONS = {
    'Hazen': ['06340500', 1],
    'Stanton': ['06340700', 2],
    'Washburn': ['06341000', 2],
    'Price': ['06342020', 2],
    'Bismarck': ['06342500', 3],
    'Schmidt': ['06349700', 2],
    'Judson': ['06348300', 1],
    'Mandan': ['06349000', 1],
    'Breien': ['06354000', 1],
    'Wakpala': ['06354881', 4],
    'Little Eagle': ['06357800', 4],
    'Cash': ['06356500', 4],
    'Whitehorse': ['06360500', 4],
}

# --------------------------------------  USACE  --------------------------------------
# (Not yet implemented in new framework)

# --------------------------------------  NDMES  --------------------------------------
# (Not yet implemented in new framework)
