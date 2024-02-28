import os
import math
import numpy as np
import pandas as pd


def get_data(comid):
    url = 'https://geoglows.ecmwf.int/api/HistoricSimulation/?reach_id={0}&return_format=csv'.format(comid)
    status = False
    while not status:
      try:
        df = pd.read_csv(url, index_col=0) 
        if(df.shape[0]>0):
           status = True
        else:
           raise ValueError("Dataframe has not data.")
      except:
        print("Trying to retrieve data...")
    df.index = pd.to_datetime(df.index)
    df.index = df.index.to_series().dt.strftime("%Y-%m-%d %H:%M:%S")
    df.index = pd.to_datetime(df.index)
    return(df)


def get_historical_simulation(path, comid):
    file_path = f"{path}/{comid}.csv"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, index_col="datetime")
        df.index = pd.to_datetime(df.index)
        df.index = df.index.to_series().dt.strftime("%Y-%m-%d %H:%M:%S")
        df.index = pd.to_datetime(df.index)
    else:
        df = get_data(comid)
        df.to_csv(file_path, index=True)
    return(df)



def gumbel_1(std: float, xbar: float, rp: int) -> float:
  return -math.log(-math.log(1 - (1 / rp))) * std * .7797 + xbar - (.45 * std)


def get_return_periods(comid, data):
    # Stats
    max_annual_flow = data.groupby(data.index.strftime("%Y")).max()
    mean_value = np.mean(max_annual_flow.iloc[:,0].values)
    std_value = np.std(max_annual_flow.iloc[:,0].values)

    # Return periods
    return_periods = [100, 50, 25, 10, 5, 2]
    return_periods_values = []

    # Compute return periods
    for rp in return_periods:
      return_periods_values.append(gumbel_1(std_value, mean_value, rp))

    # Parse to list
    d = {'rivid': [comid], 
         'return_period_100': [return_periods_values[0]], 
         'return_period_50': [return_periods_values[1]], 
         'return_period_25': [return_periods_values[2]], 
         'return_period_10': [return_periods_values[3]], 
         'return_period_5': [return_periods_values[4]], 
         'return_period_2': [return_periods_values[5]]}
    
    # Parse to dataframe
    rperiods_df = pd.DataFrame(data=d)
    rperiods_df.set_index('rivid', inplace=True)

    return(rperiods_df)



