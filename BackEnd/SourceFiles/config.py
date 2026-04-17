'''
Author: Kartik Jariam & Andrew Vu
Date: 1/29/2026
Purpose: This is the master config for all source files. Everything hardcoded must be present in this file. The host must modify this file to add new
         stations or change how data pulling works.
'''
import os

# -------------------------------------- General --------------------------------------

DB_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'database.db'))

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
    'stationList' : ["SWLAZZZ2411A", "CAMPPOCP01", "SD_11904", "SWLAZZZ2006", "460740", "460702", "460703", "460755", "460745", "460805", "460707", "460761", "460815", "460835", "460825", "460840", "460875", "460865", "468860", "460905", "460910", "460880", "460900", "460895", "460955", "460710", "460700", "460850", "460925", "460831", "460832", "460733", "460734", "460735", "460736", "460737", "460039", "460640", "460842", "460645", "460646", "460647", "460649", "460650", "460651", "460652", "460653", "460654", "460655", "460657", "460661", "460662", "460664", "460665", "460666", "460667", "460669", "460670", "460671", "460672", "460673", "460674", "460676", "460677", "460678", "460679", "460681", "460682", "460684", "460685", "460687", "460688", "460689", "460690", "460691", "460692", "460695", "460102", "460103", "460110", "460111", "460117", "460118", "460121", "460122", "460123", "460124", "460127", "460128", "460131", "460132", "460133", "460134", "460135", "460136", "460137", "460138", "460139", "460140", "460141", "460142", "460143", "460144", "460145", "460146", "460150", "460151", "460152", "460154", "460155", "460157", "460160", "460161", "460162", "460164", "460171", "460172", "460173", "460174", "460175", "460176", "460177", "460178", "460179", "460180", "460181", "460182", "460183", "460184", "460185", "460186", "460187", "460188", "460189", "460190", "460191", "460192", "460193", "460194", "460195", "460196", "460197", "460198", "460199", "460200", "46BSA1", "46BS08", "46BS18", "46BS23", "46BS29", "46BS49", "46MN31", "46MN32", "46MN33", "46MN35", "46MN38", "46MN39", "SWLABAC9508", "SWLAZZZ9508", "SWLAZZZ9508A", "SWLAZZZ9508B", "SWLAZZZ9508C", "SWLABAC9517", "SWLAZZZ9517", "SWLAZZZ9517A", "SWLAZZZ9517B", "SWLAZZZ9517C", "SWLABAC2205", "SWLAZZZ2205", "SWLAZZZ2205A", "SWLAZZZ2205B", "SWLAZZZ2205C", "SWLABAC2209", "SWLAZZZ2209", "SWLAZZZ2209A", "SWLAZZZ2209B", "SWLAZZZ2209C", "SWLABAC2219", "SWLAZZZ2219", "SWLAZZZ2219A", "SWLAZZZ2219B", "SWLAZZZ2219C", "SWLABAC2226", "SWLAZZZ2226", "SWLAZZZ2226A", "SWLAZZZ2226B", "SWLAZZZ2226C", "SWLABAC2305", "SWLAZZZ2305", "SWLAZZZ2305A", "SWLAZZZ2305B", "SWLAZZZ2305C", "SWLABAC3201", "SWLAZZZ3201", "SWLAZZZ3201A", "SWLAZZZ3201B", "SWLAZZZ3201C", "SWLABAC4302", "SWLAZZZ4302", "SWLAZZZ4302A", "SWLAZZZ4302B", "SWLAZZZ4302C", "SWLABAC4306", "SWLAZZZ4306", "SWLAZZZ4306A", "SWLAZZZ4306B", "SWLAZZZ4306C", "SWLABAC4309", "SWLAZZZ4309", "SWLAZZZ4309A", "SWLAZZZ4309B", "SWLAZZZ4309C", "SWLABAC4401", "SWLAZZZ4401", "SWLAZZZ4401A", "SWLAZZZ4401B", "SWLAZZZ4401C", "SWLABAC4807", "SWLAZZZ4807", "SWLAZZZ4807A", "SWLAZZZ4807B", "SWLAZZZ4807C", "SWLABAC9118", "SWLAZZZ9118", "SWLAZZZ9118A", "SWLAZZZ9118B", "SWLAZZZ9118C", "SWLABAC5315", "SWLAZZZ5315", "SWLAZZZ5315A", "SWLAZZZ5315B", "SWLAZZZ5315C", "SWLABAC9613", "SWLAZZZ9613", "SWLAZZZ9613A", "SWLAZZZ9613B", "SWLAZZZ9613C", "SWLABAC9608", "SWLAZZZ9608", "SWLAZZZ9608A", "SWLAZZZ9608B", "SWLAZZZ9608C", "SWLABAC9612", "SWLAZZZ9612", "SWLAZZZ9612A", "SWLAZZZ9612B", "SWLAZZZ9612C", "SWLABAC1812", "SWLAZZZ1812", "SWLAZZZ1812A", "SWLAZZZ1812B", "SWLAZZZ1812C", "SWLABAC2203", "SWLAZZZ2203", "SWLAZZZ2203A", "SWLAZZZ2203B", "SWLAZZZ2203C", "SWLABAC2303", "SWLAZZZ2303", "SWLAZZZ2303A", "SWLAZZZ2303B", "SWLAZZZ2303C", "SWLABAC2319", "SWLAZZZ2319", "SWLAZZZ2319A", "SWLAZZZ2319B", "SWLAZZZ2319C", "SWLABAC2301", "SWLAZZZ2301", "SWLAZZZ2301A", "SWLAZZZ2301B", "SWLAZZZ2301C", "SWLABAC2310", "SWLAZZZ2310", "SWLAZZZ2310A", "SWLAZZZ2310B", "SWLAZZZ2310C", "SWLABAC2315", "SWLAZZZ2315", "SWLAZZZ2315A", "SWLAZZZ2315B", "SWLAZZZ2315C", "SWLABAC2408", "SWLAZZZ2408", "SWLAZZZ2408A", "SWLAZZZ2408B", "SWLAZZZ2408C", "SWLABAC2411", "SWLAZZZ2411", "SWLAZZZ2411A", "SWLAZZZ2411B", "SWLAZZZ2411C", "SWLABAC3304", "SWLAZZZ3304", "SWLAZZZ3304A", "SWLAZZZ3304B", "SWLAZZZ3304C", "SWLABAC4843", "SWLAZZZ4843", "SWLAZZZ4843A", "SWLAZZZ4843B", "SWLAZZZ4843C", "SWLABAC4806", "SWLAZZZ4806", "SWLAZZZ4806A", "SWLAZZZ4806B", "SWLAZZZ4806C", "SWLABAC5103", "SWLAZZZ5103", "SWLAZZZ5103A", "SWLAZZZ5103B", "SWLAZZZ5103C", "SWLABAC9105", "SWLAZZZ9105", "SWLAZZZ9105A", "SWLAZZZ9105B", "SWLAZZZ9105C", "SWLABAC3305", "SWLAZZZ3305", "SWLAZZZ3305A", "SWLAZZZ3305B", "SWLAZZZ3305C", "SWLABAC9504", "SWLAZZZ9504", "SWLAZZZ9504A", "SWLAZZZ9504B", "SWLAZZZ9504C", "SWLABAC4834", "SWLAZZZ4834", "SWLAZZZ4834A", "SWLAZZZ4834B", "SWLAZZZ4834C"],
    'dateTimeFormat' : "%Y-%m-%dT%H:%M:%S"
}

# --------------------------------------  COCORAHS  --------------------------------------
COCORAHSConfig = {
    'baseURL' : "http://data.rcc-acis.org/StnData?params=",
    'stationList' : {
        "Aberdeen, SD": ["SDBR0005", "20070710"],
        "Alexandria, SD": ["SDHN0020", "20250424"],
        "Billings, MT": ["MTYL0012", "20080115"],
        "Bismarck, ND": ["NDBH0034", "20120416"],
        "Bison, SD": ["SDFK0006", "20070624"],
        "Bowman, ND": ["NDBW0001", "20080320"],
        "Bozeman, MT": ["MTGA0008", "20080310"],
        "Brookings, SD": ["SDBK0057", "20101115"],
        "Butte, MT": ["MTSB0002", "20090601"],
        "Custer, SD": ["SDCU0008", "20080415"],
        "Deadwood, SD": ["SDLA0015", "20090520"],
        "Devils Lake, ND": ["NDRY0006", "20140214"],
        "Dickinson, ND": ["NDSK0003", "20090810"],
        "Dillon, MT": ["MTBE0011", "20120514"],
        "Fargo, ND": ["NDCS0012", "20090325"],
        "Faulkton, SD": ["SDFK0009", "20230401"],
        "Fort Pierre, SD": ["SDST0007", "20170807"],
        "Glasgow, MT": ["MTVY0003", "20080610"],
        "Glendive, MT": ["MTDW0001", "20080318"],
        "Grand Forks, ND": ["NDGF0002", "20080401"],
        "Great Falls, MT": ["MTCS0005", "20080505"],
        "Hamilton, MT": ["MTRV0005", "20080305"],
        "Havre, MT": ["MTHL0006", "20091130"],
        "Helena, MT": ["MTLC0002", "20080220"],
        "Hot Springs, SD": ["SDFR0043", "20241019"],
        "Jamestown, ND": ["NDST0008", "20130522"],
        "Kalispell, MT": ["MTFH0003", "20080412"],
        "Langdon, ND": ["NDCV0004", "20200311"],
        "Lewistown, MT": ["MTFR0002", "20080530"],
        "Libby, MT": ["MTLN0005", "20090815"],
        "Livingston, MT": ["MTPR0004", "20080408"],
        "Madison, SD": ["SDLC0003", "20091001"],
        "Mandaree, ND": ["NDMK0007", "20160718"],
        "Miles City, MT": ["MTCU0004", "20080722"],
        "Minot, ND": ["NDWD0014", "20111201"],
        "Missoula, MT": ["MTMS0001", "20080201"],
        "Mitchell, SD": ["SDDV0038", "20150920"],
        "Mobridge, SD": ["SDWL0002", "20080630"],
        "Pierre, SD": ["SDHG0014", "20081112"],
        "Polson, MT": ["MTLK0001", "20080228"],
        "Rapid City, SD": ["SDPN0038", "20080512"],
        "Red Lodge, MT": ["MTCB0007", "20080612"],
        "Sidney, MT": ["MTRC0003", "20080425"],
        "Sioux Falls, SD": ["SDMH0001", "20070601"],
        "Spearfish, SD": ["SDLA0004", "20080601"],
        "Sturgis, SD": ["SDMD0022", "20100518"],
        "Valley City, ND": ["NDBN0003", "20100420"],
        "Vermillion, SD": ["SDCY0010", "20090614"],
        "Wahpeton, ND": ["NDRC0002", "20091105"],
        "Watertown, SD": ["SDCD0015", "20110330"],
        "Whitefish, MT": ["MTFH0018", "20100525"],
        "Williston, ND": ["NDWI0005", "20100615"],
        "Winner, SD": ["SDTP0002", "20080312"],
        "Yankton, SD": ["SDYN0023", "20121005"]
    },
    'Elements' : ['maxt', 'mint', 'avgt', 'obst', 'pcpn', 'snow', 'snwd']
}
# --------------------------------------  USACE  --------------------------------------
USACEConfig = {
    'baseURL' : "https://www.nwd-mr.usace.army.mil/rcc/programs/data/",
    'stationList' : ["GARR"],
    'ColumnNames' : ['DateTime', 'Temp_Air', 'Flow_Out', 'Elev_Tailwater', 'Energy', 'Temp_Water', 'Elev', 'Flow_Spill', 'Flow_Powerhouse']
}