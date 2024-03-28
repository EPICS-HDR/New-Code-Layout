import requests
from json import loads
'''
THIS RETURNS THE DATA IN THE FOLLOWING FORM
[date, precipitation, snowfall, snow depth]
'''

# RETURNS THE ACIS LINK TO PULL THE DATA FROM AN API WITH
def get_link(station_ID, start_date, end_date):
    #variables = precipitation, snowfall, snow depth
    params=f'{{"sid":"{station_ID}","sdate":"{start_date}","edate":"{end_date}","elems":"pcpn,snow,snwd"}}' #This establishes the parameters string used in the query 
    url = f'http://data.rcc-acis.org/StnData?params={params}' #This string establishes the URL to be called for the query
    return url

# CREATES A NEW DATE STRING TO MAKE IT SO WE PUT INTO DATABASE
def change_time_string_ACIS(date_str): 
    year, month, day = date_str.split('-') # splitting the date string into year, month, day
    new_time = f'{year}-{month}-{day} 00:00:00' # creating new string to match database
    return new_time

def pullCoCoRaHSAPI(location, end_date):
    # This dictionary has the name of the location as the key and the station Ids and first possible starting dates as the 
    reversed_station_dict = {"Bison, SD" : ["SDFK0006", "20070624"], "Faulkton, SD": ["SDFK0009", "20230401"], "Bismarck, ND": ["NDBH0034", "20120416"], "Langdon, ND": ["NDCV0004", "20200311"]}
    
    station_ID = reversed_station_dict[location][0]
    start_date = reversed_station_dict[location][1]
    # start_date = 20240207

    url = get_link(station_ID, start_date, end_date)

    results = requests.get(url).text  # Make the query
    # Convert the string into a series of nested dictionaries and lists usable in Python:
    results_dict = loads(results)  #Convert JSON object to a dictionary

    for i in range(len(results_dict['data'])): # replaces old time string with the new time string
        results_dict['data'][i][0] = change_time_string_ACIS(results_dict['data'][i][0]) 

    return results_dict#['data']

#  DETERMINED BY USER ON WEBSITE
location = 'Bismarck, ND'
end_date = "20120601"

print(pullCoCoRaHSAPI(location, end_date))
