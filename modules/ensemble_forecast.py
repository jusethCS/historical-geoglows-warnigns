import xarray as xr
import datetime as dt
import pandas as pd

def get_ensemble_forecast(path:str, reach_id:int, date:dt.datetime) -> pd.DataFrame:
    """
    This function retrieves a set of streamflow forecasts for a specific reach and date. 
    It utilizes GeoGloWS NetCDF files to obtain forecast data. Forecasts are available in 
    52 members (ensembles) for a given date. The function returns a pandas DataFrame 
    containing all the streamflow forecasts for the 52 ensembles for the specified date 
    and reference point.

    Parameters:
    - reach_id: int
        The identifier of the reach for which streamflow forecast is desired.
    - date: datetime
        The date for which streamflow forecasts are desired.

    Returns:
    - pandas.DataFrame
        A DataFrame containing the streamflow forecasts for the 52 ensembles on the specified 
        date and for the given reach. Each column of the DataFrame corresponds to an ensemble 
        member, labeled as 'ensemble_01', 'ensemble_02', ..., 'ensemble_52'.
    """
    # Define the file path template
    template = "{path}/{date}/{file_name}"

    # Initialize an empty DataFrame to store ensemble forecasts
    df_ensemble = pd.DataFrame()

    # Iterate over ensemble forecasts
    for ensemble in range(1, 53):
        # Construct file path
        file_date = date.strftime("%Y%m%d.00")
        file_name = f"Qout_south_america_geoglows_{ensemble}.nc"
        file_path = template.format(path=path, date=file_date, file_name=file_name)

        try:
            # Read data from NC file
            ds = xr.load_dataset(file_path)
            df = ds['Qout'].sel(rivid=reach_id).to_dataframe()["Qout"]

            # Add forecast data to ensemble DataFrame
            df_ensemble[f"ensemble_{ensemble:02d}"] = df
        except:
            print(f"Ensemble {ensemble} is unavailable for reach {reach_id} on {date}.")

    return df_ensemble



def ensemble_quantile(ensemble, quantile, label):
    df = ensemble.quantile(quantile, axis=1).to_frame()
    df.rename(columns = {quantile: label}, inplace = True)
    return(df)


def get_ensemble_stats(ensemble):
    high_res_df = ensemble['ensemble_52'].to_frame()
    ensemble.drop(columns=['ensemble_52'], inplace=True)
    ensemble.dropna(inplace= True)
    high_res_df.dropna(inplace= True)
    high_res_df.rename(columns = {'ensemble_52':'high_res_m^3/s'}, inplace = True)
    stats_df = pd.concat([
        ensemble_quantile(ensemble, 1.00, 'flow_max_m^3/s'),
        ensemble_quantile(ensemble, 0.75, 'flow_75%_m^3/s'),
        ensemble_quantile(ensemble, 0.50, 'flow_avg_m^3/s'),
        ensemble_quantile(ensemble, 0.25, 'flow_25%_m^3/s'),
        ensemble_quantile(ensemble, 0.00, 'flow_min_m^3/s'),
        high_res_df
    ], axis=1)
    return(stats_df)


