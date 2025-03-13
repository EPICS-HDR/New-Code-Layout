gauges = ("Hazen", "Stanton", "Washburn", "Price", "Bismarck", "Schmidt", "Judson", "Breien", "Mandan", "Cash", "Wakpala", "Whitehorse", "Little Eagle")

dams = ("Fort Peck", "Garrison", "Oahe", "Big Bend", "Fort Randall", "Gavins Point")

mesonets = ("Carson", "Fort Yates", "Linton", "Mott")

CoCoRaHs = ("Bison", "Faulkton", "Bismarck", "Langdon")

NOAA = ("Williston/Basin", "Tioga", "Stanley", "Minot", "Sidney/Richland", "Watford City", "Garrison", "Glendive/Dawson", "Hazen/Mercer", \
        "Beach", "Dickinson/Roosevelt", "Glen", "Bismarck", "Miles City/Wiley", "Baker", "Bowman", "Hettinger", "Linton", "Buffalo/Harding", \
        "Mobridge", "Faith", "Spearfish/Clyde", "Pierre", "Custer", "Rapid City", "Philip")

#South Dakota Data Sources



# UNUSED
Shadehill = ("Shadehill")


# SQL Keys
sql_conversion = {"Elevation" : "elevation", "Air Temperature": "air_temp", "Water Temperature" : "water_temp", \
                  "Flow Spill" : "flow_spill", "Flow Powerhouse" : "flow_power", "Flow Out" : "flow_out", \
                  "Tailwater Elevation" : "tail_ele", "Energy" : "energy", \
                  "Discharge" : "discharge", "Gauge Height" : "gauge_height", \
                  "Average Air Temperature" : "avg_air_temp", "Average Relative Humidity" : "avg_rel_hum", \
                  "Average Bare Soil Temperature" : "avg_bare_soil_temp", "Average Turf Soil Temperature" : "avg_turf_soil_temp", \
                  "Maximum Wind Speed" : "max_wind_speed", "Average Wind Direction" : "avg_wind_dir", \
                  "Total Solar Radiation" : "total_solar_rad", "Total Rainfall" : "total_rainfall", \
                  "Average Baromatric Pressure" : "avg_bar_pressure", "Average Dew Point" : "avg_dew_point", \
                  "Average Dew Point" : "avg_dew_point", "Average Wind Chill" : "avg_wind_chill", "Precipitation" : "precipitation", \
                  "Snowfall" : "snowfall", "Snow Depth" : "snow_depth", "Reservoir Storage Content" : "res_stor_content", \
                  "Reservoir Forebay Elevation" : "res_forebay_elev", "Daily Mean Computed Inflow" : "daily_mean_comp_inflow", \
                  "Daily Mean Air Temperature" : "daily_mean_air_temp", "Daily Minimum Air Temperature" : "daily_min_air_temp", \
                  "Daily Maximum Air Temperature" : "daily_max_air_temp", "Total Precipitation (inches per day)" : "tot_precip_daily", \
                  "Total Water Year Precipitation" : "tot_year_precip", "Daily Mean Total Discharge" : "daily_mean_tot_dis", \
                  "Daily Mean River Discharge" : "daily_mean_river_dis", "Daily Mean Spillway Discharge" : "daily_mean_spill_dis", \
                  "Daily Mean Gate One Opening" : "daily_mean_gate_opening", "temperature" : "temperature", \
                  "dewpoint" : "dew_point", "relativeHumidity" : "rel_humidity" , "windChill" : "wind_chill", \
}

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
                    '06360500':'Whitehorse'}

sql_conversion = {"Elevation" : "elevation", "Air Temperature": "air_temp", "Water Temperature" : "water_temp", \
                  "Flow Spill" : "flow_spill", "Flow Powerhouse" : "flow_power", "Flow Out" : "flow_out", \
                  "Tailwater Elevation" : "tail_ele", "Energy" : "energy", \
                  "Discharge" : "discharge", "Gauge Height" : "gauge_height", \
                  "Average Air Temperature" : "avg_air_temp", "Average Relative Humidity" : "avg_rel_hum", \
                  "Average Bare Soil Temperature" : "avg_bare_soil_temp", "Average Turf Soil Temperature" : "avg_turf_soil_temp", \
                  "Maximum Wind Speed" : "max_wind_speed", "Average Wind Direction" : "avg_wind_dir", \
                  "Total Solar Radiation" : "total_solar_rad", "Total Rainfall" : "total_rainfall", \
                  "Average Baromatric Pressure" : "avg_bar_pressure", "Average Dew Point" : "avg_dew_point", \
                  "Average Dew Point" : "avg_dew_point", "Average Wind Chill" : "avg_wind_chill", "Precipitation" : "precipitation", \
                  "Snowfall" : "snowfall", "Snow Depth" : "snow_depth", "Reservoir Storage Content" : "res_stor_content", \
                  "Reservoir Forebay Elevation" : "res_forebay_elev", "Daily Mean Computed Inflow" : "daily_mean_comp_inflow", \
                  "Daily Mean Air Temperature" : "daily_mean_air_temp", "Daily Minimum Air Temperature" : "daily_min_air_temp", \
                  "Daily Maximum Air Temperature" : "daily_max_air_temp", "Total Precipitation (inches per day)" : "tot_precip_daily", \
                  "Total Water Year Precipitation" : "tot_year_precip", "Daily Mean Total Discharge" : "daily_mean_tot_dis", \
                  "Daily Mean River Discharge" : "daily_mean_river_dis", "Daily Mean Spillway Discharge" : "daily_mean_spill_dis", \
                  "Daily Mean Gate One Opening" : "daily_mean_gate_opening", "temperature" : "temperature", \
                  "dewpoint" : "dew_point", "relativeHumidity" : "rel_humidity" , "windChill" : "wind_chill", \
}

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

water_chemicals = ['Phosphorus (Total) (P)', 'Phosphorus (Total Kjeldahl) (P)', 'Nitrate + Nitrite (N)',
                       'Nitrate Forms Check', 'Nitrate + Nitrite (N) Dis', 'Nitrogen (Total Kjeldahl)',
                       'Nitrogen (TKN-Dissolved)',
                       'Nitrogen (Total-Dis)', 'E.coli', 'Nitrogen (Total)', 'pH', 'Ammonia (N)',
                       'Ammonia (N)-Dissolved',
                       'Ammonia Forms Check', 'Diss Ammonia TKN Check', 'Dissolved Phosphorus as P']
