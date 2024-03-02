import os
import math
import numpy as np
import pandas as pd


def get_data(comid):
    """
    Retrieves historical data from GeoGLOWS API based on the reach identifier.

    Parameters:
        comid (int): Identifier of the river reach for which historical data 
                     is requested.

    Returns:
        DataFrame: A pandas DataFrame containing historical data retrieved from 
                   the GeoGLOWS API. The DataFrame has a datetime index.
    """
    # Construct URL for API request
    url = "https://geoglows.ecmwf.int/api/HistoricSimulation"
    url = '{url}/?reach_id={comid}&return_format=csv'.format(url=url, comid=comid)
    
    # Variable to track if data retrieval was successful
    status = False
    
    # Retry until data retrieval is successful
    while not status:
        try:
            # Attempt to read data from the API URL into a DataFrame
            df = pd.read_csv(url, index_col=0)
            
            # Check if the DataFrame contains data
            if df.shape[0] > 0:
                status = True
            else:
                # Raise an error if the DataFrame is empty
                raise ValueError("DataFrame has no data.")
        except Exception as e:
            # Print error message and continue retrying
            print("Error occurred:", e)
            print("Trying to retrieve data...")
    
    # Convert index to datetime format
    df.index = pd.to_datetime(df.index)
    
    # Convert index to string format with specific datetime format
    df.index = df.index.to_series().dt.strftime("%Y-%m-%d %H:%M:%S")
    
    # Convert index back to datetime format
    df.index = pd.to_datetime(df.index)
    return df




def get_historical_simulation(path, comid):
    """
    Retrieves historical simulation data either from a local CSV file or from 
    the GeoGLOWS API based on the reach identifier (comid).

    Parameters:
        path (str): Path to the directory where the historical simulation data 
                    is stored or should be stored.
        comid (int): Identifier of the river reach for which historical simulation 
                     data is requested.

    Returns:
        DataFrame: A pandas DataFrame containing historical simulation data.
                   The DataFrame has a datetime index.
    """
    # Construct file path for the local CSV file
    file_path = f"{path}/{comid}.csv"
    
    # Check if the local CSV file exists
    if os.path.exists(file_path):
        # If the file exists, read data from the CSV file into a DataFrame
        df = pd.read_csv(file_path, index_col="datetime")
        
        # Convert index to datetime format
        df.index = pd.to_datetime(df.index)
        
        # Convert index to string format with specific datetime format
        df.index = df.index.to_series().dt.strftime("%Y-%m-%d %H:%M:%S")
        
        # Convert index back to datetime format
        df.index = pd.to_datetime(df.index)
    else:
        # If the file does not exist, retrieve data from the GeoGLOWS API
        df = get_data(comid)
        
        # Save retrieved data to the local CSV file
        df.to_csv(file_path, index=True)
    
    return df




def gumbel_1(std: float, xbar: float, rp: int) -> float:
    """
    Calculates the Gumbel distribution parameter for a given return period.

    Parameters:
        std (float): Standard deviation of the data.
        xbar (float): Mean of the data.
        rp (int): Return period for which to calculate the Gumbel parameter.

    Returns:
        float: The Gumbel distribution parameter corresponding to the specified 
        return period.
    """
    return -math.log(-math.log(1 - (1 / rp))) * std * .7797 + xbar - (.45 * std)




def get_return_periods(comid, data):
    """
    Calculates return periods for maximum annual streamflow data based on the 
    Gumbel distribution.

    Parameters:
        comid (int): Reach id for which return periods are calculated.
        data (DataFrame): DataFrame containing streamflow data

    Returns:
        DataFrame: A pandas DataFrame containing return periods for the specified 
                   reach id.The DataFrame has columns for different return periods.
                   Each row corresponds to the return periods for the specified 
                   reach id.
    """
    # Compute maximum annual flow for each year
    max_annual_flow = data.groupby(data.index.strftime("%Y")).max()
    
    # Calculate mean and standard deviation of maximum annual flow data
    mean_value = np.mean(max_annual_flow.iloc[:,0].values)
    std_value = np.std(max_annual_flow.iloc[:,0].values)

    # Specify return periods
    return_periods = [100, 50, 25, 10, 5, 2]
    return_periods_values = []

    # Compute return periods based on the Gumbel distribution
    for rp in return_periods:
        return_periods_values.append(gumbel_1(std_value, mean_value, rp))

    # Create dictionary for return periods data
    d = {'rivid': [comid], 
         'return_period_100': [return_periods_values[0]], 
         'return_period_50': [return_periods_values[1]], 
         'return_period_25': [return_periods_values[2]], 
         'return_period_10': [return_periods_values[3]], 
         'return_period_5': [return_periods_values[4]], 
         'return_period_2': [return_periods_values[5]]}
    
    # Create DataFrame from dictionary
    rperiods_df = pd.DataFrame(data=d)
    rperiods_df.set_index('rivid', inplace=True)

    return rperiods_df

