import pmdarima as pmd
import pandas as pd
import statsmodels.api as sm
import statsmodels.tsa.arima.model as tsa
import sktime.forecasting.arima as skta
import sktime.datatypes as sktu
import datetime
import random
import numpy as np
import tbats as tb
import matplotlib as mpl
from sqlclasses import dictpull
import time as t
import email.utils as eu
import copy
import re
import pickle
import keras 

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
    out_times = list()


    for time_point in range(len(new_times) - 1):

        current_time = datetime.datetime.fromisoformat(new_times[time_point])
        new_values.append(values[time_point])
        out_times.append(current_time)
        #If there is a gap, fill it.
        while time_point < len(new_times) and ((current_time + time_test) < datetime.datetime.fromisoformat(new_times[time_point + 1])):
            new_values.append(values[time_point])
            current_time = current_time + time_gap
            out_times.append(current_time)
    new_values.append(values[len(new_times)-1])
    out_times.append(current_time+time_gap)

    return new_values,out_times,time_gap
        

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
def ARIMA(times: list, values:list) -> pmd.ARIMA:
    #Figure out orders
    #Cross Validation
    #y_train = pmd.model_selection.train_test_split(train_size=365)
    #model = pmd.auto_arima(values, error_action='ignore', seasonal=True, m=365*24)

    #TODO: make multiple seasonality an if loop
    #Fourier modeling of 2nd sesonality
    #Ripped straight from an article, update for better readability, and personal use case
    exog = pd.DataFrame({'date': times})
    exog = exog.set_index(pd.PeriodIndex(exog['date'], freq='H'))
    exog['sin365'] = np.sin(2 * np.pi * exog.index.dayofyear / 365.25)
    exog['cos365'] = np.cos(2 * np.pi * exog.index.dayofyear / 365.25)
    exog['sin365_2'] = np.sin(4 * np.pi * exog.index.dayofyear / 365.25)
    exog['cos365_2'] = np.cos(4 * np.pi * exog.index.dayofyear / 365.25)
    exog = exog.drop(columns=['date'])
    #exog_to_train = exog.iloc[:(len(values)-365)]
    #exog_to_test = exog.iloc[(len(y)-365):]

    print("Start of Arima Models")
    start_time = datetime.datetime.now()
    
    #arima_exog_model = pmd.auto_arima(y=values, exogenous=exog, seasonal=True, m=24)

    with open('pmdarima.pkl','rb') as pkl:
        arima_exog_model = pickle.load(pkl)
        

    split_1 = datetime.datetime.now()

    print("PMD Arima Model End")
    print(split_1-start_time)



    #params = arima_exog_model.get_params()

    #print(params)

    #final_arima = tsa.ARIMA(endog=values,exog=exog,seasonal_order=params['seasonal_order'])
    #results_arima = final_arima.fit()
    with open('tsaarima.pkl', 'rb') as pkl:
        results_arima = pickle.load(pkl)



    split_2 = datetime.datetime.now()

    print("Statsmodel Arima Model End")
    print(split_2-split_1)

    #Convert series to sktime format 


    skt_auto_model = skta.AutoARIMA()
    SeriesY = pd.DataFrame(values)
    #print(sktu.MTYPE_REGISTER)
    exog.set_index(SeriesY.index)
    sktu.check_raise(SeriesY,mtype='pd.DataFrame')
    sktu.check_raise(exog,mtype='pd.DataFrame')
    #fitted_skt_auto_model = skt_auto_model.fit(y=SeriesY,X=exog)
    

    #with open('sktarima.pkl', 'wb') as pkl:
    #    pickle.dump(fitted_skt_auto_model, pkl)

    split_3 = datetime.datetime.now()
    print("SKTime Arima Model End")

    print(split_3 - split_2)

    return arima_exog_model, results_arima

    #y_arima_exog_forecast = arima_exog_model.predict(n_periods=365, exogenous=exog_to_test)

    #End ripped code

    #model.fit(values)
    

    #Gets the order for the MA term + Intergrated part. Integrate until the the series is largely stationary. 
    #sm.tsa.graphics.plot_acf()
    #Gets the oder for the AR term
    #sm.tsa.graphics.plot_pacf()
    
    #sm.tsa.ARIMA()



#TBATS Model
def tbats_model(values:list) -> tb.TBATS:
    #Create variable estimator
    estimator = tb.TBATS(seasonal_periods=(24, 24 * 365.25),n_jobs=1)
    #Fit model to data
    start_time = datetime.datetime.now()
    model = estimator.fit(values)
    end_time = datetime.datetime.now()
    print("TBATS Model Time")
    print(end_time-start_time)
    
    #Model Forecast
    m_forecast = model.forecast(steps=24*365)
    return model

def mae(model, test_data: list, time_data:list, time_delta: datetime, arima:bool, update_size:int) -> list:
    print("MAE :)")
    #TODO: Fill in
    #Find out how far in each loop we have data for. 
    day = datetime.timedelta(days=1) / time_delta
    day3 = int(3 * day)
    day7 = int(7 * day)
    day21 = int(21 * day)
    year = int(365 * day)
    year_len = len(test_data) - year
    day21_len = len(test_data) - day21
    day7_len = len(test_data) - day7
    day3_len = len(test_data) - day3



    #Loop that iterates through updates. 
    predict_size = 365 * day
    test_array = np.array(test_data)
    update_time = list()

    day3_mae, day3_mse, day3_points_total, day7_mae, day7_mse, day7_points_total, day21_mae, day21_mse, day21_points_total, year_mae, year_mse, year_points_total = 0,0,0,0,0,0,0,0,0,0,0,0
    
    for point in range(len(test_data)):
        if point % 10 == 0:
            print(point)
        predicts = model.predict(int(predict_size))
        predicts = np.array(predicts)
        if point < day3_len:
            day3_array = test_array[point:point+day3] - predicts[:day3]
            day3_mae += np.sum(np.abs(day3_array))
            day3_mse += np.sum(np.power(day3_array,2))
            day3_points_total += day3
            predict_size = day3
        if point < day7_len:
            day7_array = test_array[point:point+day7] - predicts[:day7]
            day7_mae += np.sum(np.abs(day7_array))
            day7_mse += np.sum(np.power(day7_array,2))
            day7_points_total += day7
            predict_size = day7
        if point < day21_len:
            day21_array = test_array[point:point+day21] - predicts[:day21]
            day21_mae += np.sum(np.abs(day21_array))
            day21_mse += np.sum(np.power(day21_array,2))
            day21_points_total += day21
            predict_size = day21
        if point < year_len:
            year_array = test_array[point:point+year] - predicts[:year]
            year_mae += np.sum(np.abs(year_array))
            year_mse += np.sum(np.power(year_array,2))
            year_points_total += year
            predict_size = year
            
        st = datetime.datetime.now()
        if arima:
            exog = pd.DataFrame({'date': time_data[point:point+1+update_size]})
            exog = exog.set_index(pd.PeriodIndex(exog['date'], freq='D'))
            exog['sin365'] = np.sin(2 * np.pi * exog.index.dayofyear / 365.25)
            exog['cos365'] = np.cos(2 * np.pi * exog.index.dayofyear / 365.25)
            exog['sin365_2'] = np.sin(4 * np.pi * exog.index.dayofyear / 365.25)
            exog['cos365_2'] = np.cos(4 * np.pi * exog.index.dayofyear / 365.25)
            exog = exog.drop(columns=['date'])
            model.append(test_data[point],exog,0)
            model.predict(predict_size)
        else:
            model.update_predict(test_data[point:point+1+update_size], fh=predict_size, update_params=True)
        end = datetime.datetime.now()
        update_time.append(end-st)
        

    out = list()
    out.append(day3_mae/day3_points_total)
    out.append(day3_mse/day3_points_total)
    out.append(day7_mae/day7_points_total)
    out.append(day7_mse/day7_points_total)
    out.append(day21_mae/day21_points_total)
    out.append(day21_mse/day21_points_total)
    #out.append(year_mae/year_points_total)
    #out.append(year_mse/year_points_total)
    out.append(np.average(np.array(update_time)))
    return out



            
    
        
        





# dates1, values1 = dictpull('Carson', 'Average Air Temperature', '2000-01-01', '2024-01-01', 'mesonet')
# dates2, values2 = dictpull('Carson', 'Average Air Temperature', '2024-01-01', '2024-07-01', 'mesonet')
# n_values, n_times, time_gap = fill_in_the_blanks(dates1,values1)
# n_values2, n_times2, time_gap2 = fill_in_the_blanks(dates2, values2)

# model_list = list()
# print('Got here.')

#year_output = tbats_model(n_values)
#mpl.pyplot.plot(year_output)
#mpl.pyplot.show()
# exog = pd.DataFrame({'date': n_times2[0:1]})
# exog = exog.set_index(pd.PeriodIndex(exog['date'], freq='H'))
# exog['sin365'] = np.sin(2 * np.pi * exog.index.dayofyear / 365.25)
# exog['cos365'] = np.cos(2 * np.pi * exog.index.dayofyear / 365.25)
# exog['sin365_2'] = np.sin(4 * np.pi * exog.index.dayofyear / 365.25)
# exog['cos365_2'] = np.cos(4 * np.pi * exog.index.dayofyear / 365.25)
# exog = exog.drop(columns=['date'])

#print("Near here.")


#model_list.append(ARIMA(n_times,n_values))
# pmda, sttsa =ARIMA(n_times,n_values)

# start_time = datetime.datetime.now()

# pmda.update(n_values[0],exog)

# pmda.predict(10)



# end_time = datetime.datetime.now()

# sttsa = sttsa.append(n_values2[0:1],exog=exog,refit=True)

# exog = pd.DataFrame({'date': n_times2[1:11]})
# exog = exog.set_index(pd.PeriodIndex(exog['date'], freq='H'))
# exog['sin365'] = np.sin(2 * np.pi * exog.index.dayofyear / 365.25)
# exog['cos365'] = np.cos(2 * np.pi * exog.index.dayofyear / 365.25)
# exog['sin365_2'] = np.sin(4 * np.pi * exog.index.dayofyear / 365.25)
# exog['cos365_2'] = np.cos(4 * np.pi * exog.index.dayofyear / 365.25)
# exog = exog.drop(columns=['date'])
# sttsa.forecast(steps=10,exog=exog)

# end_time2= datetime.datetime.now()

# print('Update Check')

# print(end_time-start_time)
# print(end_time2 - end_time)

#out = mae(model_list[0],n_values2,n_times2,time_gap,True)

def wrapper(location:str, variable:str, table:str) -> bool:
    models = list()
    mae_out = list()
    train_times, train_values = dictpull(location, variable, '2000-01-01', '2024-01-01', table)
    filled_train_values, filled_train_times, train_time_gap = fill_in_the_blanks(train_times, train_values)
    test_times, test_values = dictpull(location, variable, '2024-01-01', '2024-07-01', table)
    filled_test_values, filled_train_times, test_time_gap = fill_in_the_blanks(test_times, test_values)
    models.append(tbats_model(filled_train_values))
    models.append(ARIMA(filled_train_values))
    n = 0
    n_model = list()
    for model in models:
        if n == 1:
            mae_out[n] = mae(model,filled_test_values, train_time_gap, True,7)
        else:
            mae_out[n] = mae(model, filled_test_values, train_time_gap, False,7)
        n += 1
    mae_out.append([0,0,0,0,0,0,0,0,0])
    #mae_out = [[43.4,643,5234,9467,124,4.2856,90.23,73,5],[55.3,783,1023,8,126,5.67901,90.23,409,4],[0,0,0,0,0,0,0,0,0]]

    file_name = location.replace(" ", "") + variable.replace(" ", "") + ".txt" 
    with open(file_name, 'w') as f:
        print("-------------------------------------------------------------\n",file=f)
        print("|                  Predictive Model Analysis                 |\n",file=f)
        print("|------------------------------------------------------------|\n",file=f)
        print(f"|         {location:15} {variable:25}          |\n",file=f)
        print("|------------------------------------------------------------|\n",file=f)
        print("|               |     SARIMA     |    TBATS    |     RNN     |\n",file=f)
        print("|------------------------------------------------------------|\n",file=f)
        print(f"|   3-DAY MAE   |    {mae_out[0][0]:7}     |   {mae_out[1][0]:7}  |   {mae_out[2][0]:7}  |\n",file=f)
        print("|------------------------------------------------------------|\n",file=f)
        print(f"|   3-DAY MSE   |    {mae_out[0][1]:7}     |   {mae_out[1][1]:7}   |   {mae_out[2][1]:7}   |\n",file=f)
        print("|------------------------------------------------------------|\n",file=f)
        print(f"|   7-DAY MAE   |    {mae_out[0][2]:7}     |   {mae_out[1][2]:7}   |   {mae_out[2][2]:7}   |\n",file=f)
        print("|------------------------------------------------------------|\n",file=f)
        print(f"|   7-DAY MSE    |    {mae_out[0][3]:7}     |   {mae_out[1][3]:7}   |   {mae_out[2][3]:7}   |\n",file=f)
        print("|------------------------------------------------------------|\n",file=f)
        print(f"|   21-DAY MAE   |    {mae_out[0][4]:7}     |   {mae_out[1][4]:7}   |   {mae_out[2][4]:7}   |\n",file=f)
        print("|------------------------------------------------------------|\n",file=f)
        print(f"|   21-DAY MSE   |    {mae_out[0][5]:7}     |   {mae_out[1][5]:7}   |   {mae_out[2][5]:7}   |\n",file=f)
        print("|------------------------------------------------------------|\n",file=f)
        print(f"|   YEAR MAE    |    {mae_out[0][6]:7}     |   {mae_out[1][6]:7}  |   {mae_out[2][6]:7}   |\n",file=f)
        print("|------------------------------------------------------------|\n",file=f)
        print(f"|   YEAR MSE    |    {mae_out[0][7]:7}     |   {mae_out[1][7]:7}   |   {mae_out[2][7]:7}   |\n",file=f)
        print("|------------------------------------------------------------|\n",file=f)
        print(f"|   CPU TIME    |    {mae_out[0][8]:7}     |   {mae_out[1][8]:7}   |   {mae_out[2][8]:7}   |\n",file=f)
        print("|------------------------------------------------------------|\n",file=f)
        


#wrapper('Carson', 'Average Air Temperature', 'mesonet')
#wrapper('Carson', 'Average Baromatric Pressure', 'mesonet')




#ARIMA(dates1,values1,True)






#RNN Model



def rnn_shape(time_gap: datetime.timedelta, how_far: int) -> list:
    """Creates the input and output shapes for a Keras RNN."""

    shapes = list()
    input_days = 21
    if time_gap == hour:
        input_size = input_days*24 + 1
        shapes[0] = (input_size, 1)
        output_size = how_far*24
        shapes[1] = (output_size, 1)


    elif time_gap == day:
        input_size = input_days + 1
        shapes[0] = (input_size, 1)
        output_size = how_far
        shapes[1] = (output_size, 1)
    

    return shapes

def rnn_training_data(times:list, values:list, shapes:list) -> list:
    "Create training data based on the shape of the input and output."
    input_size = shapes[0][0] - 1
    output_size = shapes[1][0]
    window_size = (shapes[0][0] - 1) + shapes[1][0]
    training_data = list()

    for time in range(times.len - window_size):
        input = values[time:time+input_size]
        input.append(times[time+input_size+1])
        output = values[time+input_size+1:time+window_size]
        training_data.append((input,output))
    return training_data


def RNN_Cr(times:list, values:list,time_gap:datetime.timedelta,how_far:int):
    shapes = rnn_shape(time_gap,how_far)
    training_data = rnn_training_data(times,values,shapes)

    model = keras.models.Sequential()
    model.add(keras.layers.SimpleRNN(2,input_shape=shapes[0],activation=['linear','linear']))
    model.compile(loss='mean_squared_error', optimizer='adam')

    with open('RNN.pkl','Wb') as pkl:
        pickle.dump(model, pkl)
    
    return model

    

#TEST STRUCTURE

    #TEST MAE/UPDATE FREQ
wrapper('Carson', 'Average Air Temperature','Mesonet')



    #TEST RNN SHAPE
#dates1, values1 = dictpull('Carson', 'Average Air Temperature', '2000-01-01', '2024-01-01', 'mesonet')
#dates2, values2 = dictpull('Carson', 'Average Air Temperature', '2024-01-01', '2024-07-01', 'mesonet')
#n_values, n_times, time_gap = fill_in_the_blanks(dates1,values1)
#n_values2, n_times2, time_gap2 = fill_in_the_blanks(dates2, values2)

#shapes = rnn_shape(time_gap,21)

    #TEST RNN TRAINING VALUES
#training_data = rnn_training_data(n_times,n_values,shapes=shapes)

    #TEST RNN
#RNN_Cr()
    
    





