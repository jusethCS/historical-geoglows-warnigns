import os
import xarray as xr
import pandas as pd
import datetime as dt


def get_ensemble_forecast_ncfiles(forecast_path:str, date:dt.datetime) -> tuple:
    """
    Reads NetCDF files (.nc) from a specified folder corresponding to a given date and 
    returns them as a list of datasets along with their indices.
    
    Parameters:
        forecast_path (str): Path to the directory containing forecast data.
        date (datetime): Date for which the forecast data needs to be retrieved.
        
    Returns:
        tuple: A tuple containing two elements:
            - datasets: List of datasets loaded from the NetCDF files.
            - ensemble_index: List of indices corresponding to each dataset, extracted 
              from the filenames.
    """
    # Construct folder path based on forecast_path and date
    folder = "{dir}/{date:%Y%m%d.00}".format(dir=forecast_path, date=date)
    
    # Get a list of all NetCDF files in the folder
    ncfiles = [os.path.join(folder, ncfile) for ncfile in os.listdir(folder)]
    
    # Load each NetCDF file as a dataset and Extract ensemble indices from filenames
    dataset = []
    ensemble_index = []
    for ncfile in ncfiles:
        try:
            dataset.append(xr.load_dataset(ncfile))
            ensemble_index.append(os.path.basename(ncfile)[:-3].split("_")[-1])
        except Exception as err:
            print(err)
    return dataset, ensemble_index




def get_ensemble_forecast(dataset:list, ensemble_index:list, reach_id:int) -> pd.DataFrame:
    """
    Extracts ensemble forecast data for a specific river reach ID from a list of 
    datasets.
    
    Parameters:
        - dataset (list): 
            List of xarray datasets containing forecast data.
        - ensemble_index (list): 
            List of indices corresponding to each dataset, identifying the forecast 
            ensemble.
        - reach_id (int): 
            Identifier of the river reach for which the ensemble forecast is required.
        
    Returns:
        DataFrame: 
            A pandas DataFrame containing the ensemble forecast data for the specified 
            river reach. The DataFrame has 52 columns, each representing a member of 
            the ensemble forecast.
    """
    # Determine the number of datasets
    n = len(dataset)
    
    # Initialize an empty DataFrame to store ensemble forecast data
    df_ensemble = pd.DataFrame()
    
    # Iterate over each dataset
    for i in range(n):
        # Extract the ensemble index from ensemble_index list
        ensemble = int(ensemble_index[i])
        
        # Extract forecast data for the specified river reach from the current dataset
        df = dataset[i]['Qout'].sel(rivid=reach_id).to_dataframe()["Qout"]
        
        # Add forecast data to the DataFrame with appropriate column names
        df_ensemble[f"ensemble_{ensemble:02d}"] = df
    
    return df_ensemble


def ensemble_quantile(ensemble:pd.DataFrame, quantile: float, label:str):
    """
    Calculates the specified quantile from an ensemble forecast and returns it 
    as a DataFrame.
    
    Parameters:
        - ensemble (DataFrame): DataFrame containing ensemble forecast data.
        - quantile (float): Quantile value to calculate (e.g., 0.5 for median).
        - label (str): Label to assign to the column containing the quantile 
                       values in the output DataFrame.
        
    Returns:
        DataFrame: A pandas DataFrame containing the calculated quantile values.
                   The DataFrame has a single column with the specified label.
    """
    # Calculate the specified quantile along the columns (axis=1) of the ensemble
    df = ensemble.quantile(quantile, axis=1).to_frame()
    
    # Rename the column to the specified label
    df.rename(columns={quantile: label}, inplace=True)
    
    return df



def get_ensemble_stats(ensemble:pd.DataFrame) -> pd.DataFrame:
    """
    Computes statistical summary measures from an ensemble forecast and returns 
    them as a DataFrame.
    
    Parameters:
        ensemble (DataFrame): DataFrame containing ensemble forecast data.
        
    Returns:
        DataFrame: A pandas DataFrame containing statistical summary measures 
                   computed from the ensemble forecast. The DataFrame includes 
                   columns for maximum, 75th percentile, median, 25th percentile, 
                   and minimum flows, as well as a column for high-resolution 
                   forecast.
    """
    # Extract high-resolution forecast
    high_res_df = ensemble['ensemble_52'].to_frame()
    
    # Remove high-resolution forecast from the ensemble DataFrame
    ensemble.drop(columns=['ensemble_52'], inplace=True)
    
    # Drop rows with missing values from both ensemble and high-resolution forecast
    ensemble.dropna(inplace=True)
    high_res_df.dropna(inplace=True)
    
    # Rename the column containing high-resolution forecast
    high_res_df.rename(columns={'ensemble_52': 'high_res_m^3/s'}, inplace=True)
    
    # Compute ensemble statistics
    stats_df = pd.concat([
        ensemble_quantile(ensemble, 1.00, 'flow_max_m^3/s'),
        ensemble_quantile(ensemble, 0.75, 'flow_75%_m^3/s'),
        ensemble_quantile(ensemble, 0.50, 'flow_avg_m^3/s'),
        ensemble_quantile(ensemble, 0.25, 'flow_25%_m^3/s'),
        ensemble_quantile(ensemble, 0.00, 'flow_min_m^3/s'),
        high_res_df
    ], axis=1)
    
    return stats_df

