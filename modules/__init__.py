import sys
import pandas as pd

from .ensemble_forecast import get_ensemble_forecast, get_ensemble_stats
from .historical_simulation import get_historical_simulation, get_return_periods
from .warnings import get_warning

def geoglows_warnings(forecast_path, historical_path, reach_id, date):
    # Retrieve required data
    ensemble_forecast = get_ensemble_forecast(forecast_path, reach_id, date)
    ensemble_stats = get_ensemble_stats(ensemble_forecast)
    historical_simulation = get_historical_simulation(historical_path, reach_id)
    return_periods = get_return_periods(reach_id, historical_simulation)

    # Compute the actual warning
    warning = get_warning(ensemble_stats, ensemble_forecast, return_periods)
    return(warning)



class geoglows_analyzer():
    def __init__(self, forecast_path, historical_path, drainage_path) -> None:
        self.forecast_path = forecast_path
        self.historical_path = historical_path
        self.drainage = pd.read_excel(drainage_path)
        self.n = len(self.drainage.comid)

    def warnings(self, date):
        print(f"Warning analysis for date: {date.strftime('%Y-%m-%d')}")
        drainage_alerts = self.drainage
        for i in range(self.n):
            # Define the actual reach id
            reach_id = self.drainage.comid[i]
            warning = geoglows_warnings(self.forecast_path, self.historical_path, reach_id, date)
            drainage_alerts.loc[i, ['alert']] = warning
            
            # Print progress and alert
            prog = round(i/self.n * 100, 3)
            print("Progress: {0} %. Comid: {1}. Alert: {2}".format(prog, reach_id, warning), end='\r')
            sys.stdout.flush()
        print("\nFinished analysis...")
        return(drainage_alerts)
