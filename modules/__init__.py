import sys
import pandas as pd
import datetime as dt

from .ensemble_forecast import get_ensemble_forecast_ncfiles
from .ensemble_forecast import get_ensemble_forecast, get_ensemble_stats
from .historical_simulation import get_historical_simulation, get_return_periods
from .warnings import get_warning


class geoglows_analyzer:
    """
    A class designed to analyze hydrological forecasted data using GeoGLOWS datasets.
    
    Args:
        forecast_path (str): Path to the directory containing forecast data.
        historical_path (str): Path to the directory containing historical data.
        drainage_path (str): Path to the file containing drainage data (reach id).
        
    Methods:
        __init__: Initializes the geoglows_analyzer object.
        warnings: Compute the geoglows warnings considering return periods
    """

    def __init__(self, forecast_path:str, historical_path:str, drainage_path:str) -> None:
        """
        Initializes a geoglows_analyzer object with the provided forecast, historical, 
        and drainage data paths.
        """
        self.forecast_path = forecast_path
        self.historical_path = historical_path
        self.drainage = pd.read_excel(drainage_path)
        self.n = len(self.drainage.comid)

    def warnings(self, date:dt.datetime) -> pd.DataFrame:
        """
        Analyzes the hydrological forecast for a given date using geoglows data.
        
        Args:
            date (datetime): Date for which the forecast analysis needs to be performed.
        
        Returns:
            DataFrame: A DataFrame containing drainage alerts for each reach ID.
        """
        # Initialize drainage alerts DataFrame
        drainage_alerts = self.drainage
        
        # Read ensemble dataset
        dataset, ensemble_index = get_ensemble_forecast_ncfiles(self.forecast_path, date)

        for i in range(self.n):
            # Define the actual reach id
            reach_id = self.drainage.comid[i]

            # Retrieve required data
            ensemble_forecast = get_ensemble_forecast(dataset, ensemble_index, reach_id)
            ensemble_stats = get_ensemble_stats(ensemble_forecast)
            historical_simulation = get_historical_simulation(self.historical_path, reach_id)
            return_periods = get_return_periods(reach_id, historical_simulation)

            # Compute the actual warning
            warning = get_warning(ensemble_stats, ensemble_forecast, return_periods)
            drainage_alerts.loc[i, ['alert']] = warning
            
            # Print progress and alert
            prog = round(i/self.n * 100, 3)
            print("Progress: {0} %. Comid: {1}. Alert: {2}  ".format(prog, reach_id, warning), end='\r')
            sys.stdout.flush()
        
        print("\nFinished analysis...")
        return drainage_alerts
