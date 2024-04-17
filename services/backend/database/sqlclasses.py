import sqlite3 as sql
import json
import datetime

# TODO Add new global lists, add sql conversions
gauges = ("Hazen", "Stanton", "Washburn", "Price", "Bismarck", "Schmidt", "Judson", "Breien", "Mandan", "Cash", "Wakpala", "Whitehorse", "Little Eagle")
dams = ("Fort Peck", "Garrison", "Oahe", "Big Bend", "Fort Randall", "Gavins Point")
mesonets = ("Carson", "Fort Yates", "Linton", "Mott")

sql_conversion = {"Elevation" : "elevation", "Air Temperature": "air_temp", "Water Temperature" : "water_temp", \
                  "Flow Spill" : "flow_spill", "Flow Powerhouse" : "flow_power", "Flow Out" : "flow_out", \
                  "Tailwater Elevation" : "tail_ele", "Energy" : "energy", \
                  "Discharge" : "discharge", "Gauge Height" : "gauge_height", \
                  "Average Air Temperature" : "avg_air_temp", "Average Relative Humidity" : "avg_rel_hum", \
                  "Average Bare Soil Temperature" : "avg_bare_soil_temp", "Average Turf Soil Temperature" : "avg_turf_soil_temp", \
                  "Maximum Wind Speed" : "max_wind_speed", "Average Wind Direction" : "avg_wind_dir", \
                  "Total Solar Radiation" : "total_solar_rad", "Total Rainfall" : "total_rainfall", \
                  "Average Baromatric Pressure" : "avg_bar_pressure", "Average Dew Point" : "avg_dew_point", \
                  "Average Dew Point" : "avg_dew_point", "Average Wind Chill" : "avg_wind_chill" \
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

class SQLHandle:
    sqlpointer = sql.connect("Measurements.db")
    def __init__(self):
        pass
    def create_table(self):
        pass
    def add_row(self, values: list) -> None:
        for value in values:
            strv = strv + str(value) + ", "
        strv = strv(0, len(strv)- 3)
        self.sqlpointer.c("INSERT INTO " + self.table + "(" + self.columns + ") VALUES (" + strv + ")")
    def get_date_data(self, start_date: str, end_date: str) -> None:
        self.sqlpointer.c("SELECT * FROM " + self.table + " WHERE date BETWEEN " + start_date + " AND " + end_date)
    def update_old_data(self):
        pass
        
# UNUSED
class Mesonet(SQLHandle):
    def __init__(self):
        super().__init__()
        self.table = "mesonet"
        self.columns = ""

class Dams(SQLHandle):
    def __init__(self):
        super().__init__()
        self.table = "dams"
        self.columns = ""
    

class Gauge(SQLHandle):
    def __init__(self):
        super().__init__()
        self.table = "gauge"
        self.columns = ""
# UNUSED
    
# Running this would overwrite current data
# Creates each table with specified names and headers
# TODO Run a single cur.execute with desired table and headers
def create_tables() -> None:
    conn = sql.connect("./Measurements.db")
    cur = conn.cursor()

    cur.execute("CREATE TABLE mesonet( location TEXT, datetime TEXT, \
                avg_air_temp REAL, avg_rel_hum REAL, \
                avg_bare_soil_temp REAL, avg_turf_soil_temp REAL, \
                max_wind_speed REAL, avg_wind_dir REAL, \
                total_solar_rad REAL, total_rainfall REAL, \
                avg_bar_pressure REAL, avg_dew_point REAL, \
                avg_wind_chill REAL, PRIMARY KEY(location, datetime) \
    )")

    cur.execute("CREATE TABLE gauge (location TEXT, datetime TEXT, \
                elevation REAL, gauge_height REAL, discharge REAL, water_temp REAL, \
                PRIMARY KEY(location, datetime))")
    

    cur.execute("CREATE TABLE dam(location TEXT, datetime TEXT, \
                elevation REAL, flow_spill REAL, flow_power REAL, \
                flow_out REAL, tail_ele REAL, energy REAL, water_temp REAL,\
                air_temp REAL, PRIMARY KEY(location, datetime))")


    

def clear_db():
    #COMPLETELY RESETS DATABASE USE WITH CAUTION: MAKE SURE BACKUP DATA IS AVAILABLE
    conn = sql.connect("./Measurements.db")
    cur = conn.cursor()
    tables = ("mesonet", "dam", "gauge")
    for table_name in tables:
        cur.execute("DROP TABLE ? ", table_name)
    
    
# Was used previouly to convert the old JSON dictionary into SQL
def fill_sql_tables(full_dict: dict) -> None:
    conn = sql.connect("./Measurements.db")
    cur = conn.cursor()

    
    for location in full_dict:
        for variable in full_dict[location]:
            for day in full_dict[location][variable]:
                for time in full_dict[location][variable][day]:
                    value = full_dict[location][variable][day][time]
                    table = "misc"
                    # Checks locations from global variable lists
                    # Currently relies on no overlap
                    if(location in gauges):
                        table = "gauge"
                    if(location in dams):
                        table = "dam"
                    if(location in mesonets):
                        table = "mesonet"
                    data_packet = [table, sql_conversion[variable], value, day + " " + time + ":00.000"]
                    dt = day + " " + time + ":00"
                    update_string = f"UPDATE {table} SET {sql_conversion[variable]} = {value} WHERE location = '{location}' AND datetime = '{dt}'"
                    try: 
                        h = cur.execute(update_string)
                        insert_string = f"INSERT INTO {table} (location, datetime, {sql_conversion[variable]}) VALUES ('{location}', '{dt}', {value})"
                        if(h.rowcount == 0):
                            cur.execute(insert_string)
                    except sql.Error as e: 
                        print(f"Help. {e}")

    conn.commit() #SHIT WILL NOT SAVE WITHOUT COMMIT REMEMBER

    return

# TODO Going to need to add new tables here
def get_table_name(location:str) -> str:
    table = "error"
    if(location in gauges):
        table = "gauge"
    if(location in dams):
        table = "dam"
    if(location in mesonets):
        table = "mesonet"
    return table

# Might not be in use
def fill_dict(db_name: str) ->dict:
    conn = sql.connect("./Measurements.db")
    cur = conn.cursor()
    partical_dict = dict()
    rows = cur.execute("SELECT * FROM ? WHERE location = ? ORDER by datetime")
    for row in rows:
        for variable in variables:
            datetime = row['datetime']
            partical_dict[variable][datetime] = row[variable]
    pass

    
# Taking SQL data and putting it into a graphable format
def create_lists(db_name: str, location: str, variable:str, start_date: str, end_date: str) -> list:
    conn = sql.connect("./Measurements.db")
    cur = conn.cursor()
    list_of_lists = []
    date_list = []
    variable_list = []
    index = 0

    rows = cur.execute(f"SELECT * FROM {table_name} WHERE location = {location} AND {variable} IS NOT NULL AND datetime BETWEEN {start_date} AND {end_date} ORDER by datetime")
    for row in rows:
        date_list[index] = row['datetime']
        variable_list[index] = row[variable]
        index += 1
    
    list_of_lists.append(date_list)
    list_of_lists.append(variable_list)
    return list_of_lists

# TODO call this function elsewhere
def updateDictionary(times: list, data: list, location: str, variable: str) -> None:
    conn = sql.connect("./Measurements.db")
    cur = conn.cursor()
    table = get_table_name(location)
    if(location in locationdict):
        location = locationdict[location] 
    for i in range(len(times)):
        if(data[i]): #Checks to see if the string is empty. Empty strings return false.
            try:    
                update_string = f"UPDATE {table} SET {sql_conversion[variable]} = {data[i]} WHERE location = '{location}' AND datetime = '{times[i]}'"
                h = cur.execute(update_string)
                insert_string = f"INSERT INTO {table} (location, datetime, {sql_conversion[variable]}) VALUES ('{location}', '{times[i]}', {data[i]})"
                if (h.rowcount == 0): 
                    try:
                        cur.execute(insert_string)
                    except sql.Error as e: 
                        print(f"Ohgod. {e}")
            except:
                print("Ruh Roh")
            
    conn.commit()

def dictpull(location: str, variable: str, start_date: str, end_date: str) -> tuple:
    conn = sql.connect("Measurements.db")
    conn.row_factory = sql.Row
    cur = conn.cursor()
    date_list = []
    variable_list = []
    index = 0

    table_name = get_table_name(location)
    variable = sql_conversion[variable]
    rows = cur.execute(f"SELECT * FROM {table_name} WHERE location = '{location}' AND '{variable}' IS NOT NULL AND datetime BETWEEN '{start_date}' AND '{end_date}' ORDER by datetime")
    for row in rows:
        date_list.append(row['datetime'])
        variable_list.append(row[variable])
        index += 1
    

    return date_list, variable_list

def find_data(location: str, start_date: str, end_date: str) -> list:
    conn = sql.connect("Measurements.db")
    conn.row_factory = sql.Row
    cur = conn.cursor()
    datalist = []

    table_name = get_table_name(location)
    if table_name == "error":
        return datalist
    
    rows = cur.execute(f"SELECT * FROM {table_name} WHERE location = '{location}' AND datetime BETWEEN '{start_date}' AND '{end_date}' ORDER by datetime")
    for row in rows:
        datalist.append(row)

    return datalist

def find_data2(location: str, start_date: str, end_date: str,fields:list) -> list:
    conn = sql.connect("Measurements.db")
    conn.row_factory = sql.Row
    cur = conn.cursor()
    datalist = []

    table_name = get_table_name(location)
    if table_name == "error":
        return datalist
    
    rows = cur.execute(f"SELECT {','.join(fields)} FROM {table_name} WHERE location = '{location}' AND datetime BETWEEN '{start_date}' AND '{end_date}' ORDER by datetime")
    for row in rows:
        datalist.append(row)

    return datalist
#create_tables()


#with open('project/dictionary.json', 'r') as file:
#        existing_data = file.read()
#data_dict = json.loads(existing_data)

#fill_sql_tables(data_dict)

class moving_average:
    def __moving_avg(self, times, data, size) -> tuple:
        previous_date = datetime.datetime.fromisoformat(times[0])
        daily_avg_dates = []
        daily_avg_data = []
        index = 0
        total = 0 
        parts = 0
        for i in range(len(times)):
            d = datetime.datetime.fromisoformat(times[i])
            if (d.day != previous_date.day) :
                daily_avg_dates.append(previous_date.isoformat())
                daily_avg_data.append(total/parts)
                previous_date = d
                index += 1
                total = 0
                parts = 0
            else :
                total += data[i]
                parts += 1
        
        s_index = 0
        output_dates = []
        output_data = []
        output = 0
        # CHECK TO MAKE SURE YOUR -1'S AND INDEXES LINE UP
        for k in range(size):
            output += daily_avg_data[k]

        output_dates.append(daily_avg_dates[size-1]) 
        output_data.append(output)
        for j in range(size, len(daily_avg_dates)):

            s_index += 1
            output -= daily_avg_data[j - size]
            output += daily_avg_data[j]
            output_dates.append(daily_avg_dates[j])
            output_data.append(output)
        
        return output_dates, output_data
    
        pass
    def one_day_ma(self,times, data) -> tuple:
        output = self.__moving_avg(times, data, 1)
        return output
    def five_day_ma(self,times, data) -> tuple:
        output = self.__moving_avg(times,data, 5)
        return output
    def ten_day_ma(self,times, data) -> tuple:
        output = self.__moving_avg(times,data, 10)
        return output
    def one_month_ma(self,times, data) -> tuple:
        output = self.__moving_avg(times,data, 30)
        return output

ma_time, ma_data = dictpull("Bismarck", "Elevation", "2023-06-05 00:00:00", "2023-07-05 00:00:00")
ma = moving_average()
da_t, da_a = ma.one_day_ma(ma_time, ma_data)
