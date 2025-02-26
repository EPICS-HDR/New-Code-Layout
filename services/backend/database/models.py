import pmdarima as pmd
import pandas as pd
import statsmodels.api as sm
import datetime
import random
import numpy as np
import tbats as tb
import matplotlib as mpl
from sqlclasses import dictpull
import time as t
import email.utils as eu
import re

#Function to get all data for a variable, returned as two lists, a time and a value.
def getData(location: str, variable: str, table: str) -> tuple:
    start = datetime.date.fromtisoformat('1900-01-01').isoformat()
    return dictpull(location,variable,table,start,datetime.today())


    

#Fills in gaps by repeating last known value.
def fill_in_the_blanks(times:list, values:list) -> list:
    new_times = list()
    #TODO: Make the time gap more robust
    for time in range(len(times)):
        if re.search('24:00',times[time]) is not None:
            temp_date = datetime.datetime.fromisoformat(re.sub('24:00','00:00', times[time])) + datetime.timedelta(days=1)
            new_times.append(datetime.datetime.isoformat(temp_date))
        else:
            new_times.append(times[time])
        

    time_gap = datetime.datetime.fromisoformat(new_times[1]) - datetime.datetime.fromisoformat(new_times[0])

    #Give some gap, so that minor variations in time gap don't create unnecisary fill
    time_test = time_gap * 1.05
    new_values = list()


    for time_point in range(len(new_times) - 1):
        current_time = datetime.datetime.fromisoformat(new_times[time_point])
        new_values.append(values[time_point])
        #If there is a gap, fill it.
        while time_point < len(new_times) and ((current_time + time_test) < datetime.datetime.fromisoformat(new_times[time_point + 1])):
            new_values.append(values[time_point])
            current_time = current_time + time_gap
            
    new_values.append(values[len(new_times)-1])

    return new_values
        

#Function to break up the data into training and testing portions. With a set max length, nominally 21.
#Return tuple is 2 lists of start and end dates. They represent the start and end dates of the  
def trainTest(table:str, location:str, variable:str) -> tuple:
    #TODO: Make sure you don't need to floor/ceiling a variable. 
    dates, data = getData(location, variable, table)
    duration = datetime.timedelta(dates[0], dates[-1])
    slices = duration.days / 21
    test_s = int(slices * .2)
    test_sections = random.sample(range(slices), k=test_s)
    #Take test_sections and turn it into dates
    


    
    


#ARIMA Model
def ARIMA(times: list, values:list, multipleSeasonality:bool) -> None:
    #Figure out orders
    #Cross Validation
    y_train = pmd.model_selection.train_test_split(train_size=365)
    model = pmd.auto_arima(y_train, error_action='ignore', seasonal=True, m=365)

    #TODO: make multiple seasonality an if loop
    #Fourier modeling of 2nd sesonality
    #Ripped straight from an article, update for better readability, and personal use case
    exog = pd.DataFrame({'date': y.index})
    exog = exog.set_index(pd.PeriodIndex(exog['date'], freq='D'))
    exog['sin365'] = np.sin(2 * np.pi * exog.index.dayofyear / 365.25)
    exog['cos365'] = np.cos(2 * np.pi * exog.index.dayofyear / 365.25)
    exog['sin365_2'] = np.sin(4 * np.pi * exog.index.dayofyear / 365.25)
    exog['cos365_2'] = np.cos(4 * np.pi * exog.index.dayofyear / 365.25)
    exog = exog.drop(columns=['date'])
    exog_to_train = exog.iloc[:(len(y)-365)]
    exog_to_test = exog.iloc[(len(y)-365):]
    
    arima_exog_model = pmd.auto_arima(y=y_train, exogenous=exog_to_train, seasonal=True, m=7)

    y_arima_exog_forecast = arima_exog_model.predict(n_periods=365, exogenous=exog_to_test)

    #End ripped code

    model.fit(values)

    #Gets the order for the MA term + Intergrated part. Integrate until the the series is largely stationary. 
    sm.tsa.graphics.plot_acf()
    #Gets the oder for the AR term
    sm.tsa.graphics.plot_pacf()
    
    sm.tsa.ARIMA()



#TBATS Model
def tbats_model(values:list) -> list:
    #Create variable estimator
    estimator = tb.TBATS(seasonal_periods=(24, 24 * 365.25),n_jobs=2)
    #Fit model to data
    model = estimator.fit(values)
    
    #Model Forecast
    m_forecast = model.forecast(steps=24*365)
    return m_forecast



dates1, values1 = dictpull('Carson', 'Average Air Temperature', '2000-01-01', '2024-01-01', 'mesonet')
n_values = fill_in_the_blanks(dates1,values1)

print('Got here.')

year_output = tbats_model(n_values)
mpl.pyplot.plot(year_output)
mpl.pyplot.show()

#ARIMA(dates1,values1,True)






#RNN Model






#