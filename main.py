import time
import pandas as pd
import datetime as dt
from modules import geoglows_analyzer
from multiprocessing import Process

# Environmental variables
forecast_path = "geoglows_forecasts"
historical_path = "geoglows_historical"
drainage_path = "geoglows_reachs_ids.xlsx"

# Define date range
start_date = dt.datetime(2014, 1, 1)
end_date = dt.datetime(2014, 12, 31)

# Maximum number of processes in parallel
MAX_PROC_NUM = 10

# Initialize geoglows analyzer
ga = geoglows_analyzer(
    forecast_path=forecast_path,
    historical_path=historical_path,
    drainage_path=drainage_path
)

# Function to obtain warnings in parallel for a given date
def get_warnings(date):
    warnings = ga.warnings(date)
    csv_filename = date.strftime('geoglows_warnings/%Y_%m_%d.csv')
    warnings.to_csv(csv_filename, index=False)
    print(f"Warnings for {date} stored in {csv_filename}")


if __name__ == "__main__":
    # List to store processes
    process = []

    # Iterate over the date range
    current_date = start_date
    while current_date <= end_date:
        # Create a group of processes
        group = []
        for i in range(MAX_PROC_NUM):
            if current_date <= end_date:
                p = Process(target=get_warnings, args=(current_date,))
                group.append(p)
                current_date += dt.timedelta(days=1)

        # Start and wait for processes in the group to finish
        for p in group:
            p.start()
        for p in group:
            p.join()
