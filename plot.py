###############################################################################
#                         LIBRARIES AND DEPENDENCIES                          #
###############################################################################
import pandas as pd


###############################################################################
#                             AUXILIAR FUNCTIONS                              #
###############################################################################
def combine(start_date, end_date):
    # Set date range to run the analysis
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    #
    # Alert map
    alert_map = {'R0': 0, 'R2': 2, 'R5': 5, 'R10': 10, 'R25': 25, 'R50': 50, 'R100': 100}
    #
    # Combine data in a single dataframe
    combined_data = pd.DataFrame()
    for date in date_range:
        csv_file = f"geoglows_warnings/{date.strftime('%Y_%m_%d')}.csv"
        df = pd.read_csv(csv_file, usecols=['comid', 'alert'])
        df["alert"] = df["alert"].map(alert_map)
        df.rename(columns={
            'alert': date.strftime('%Y-%m-%d'),
            'comid': 'date'
        }, inplace=True)
        df = df.set_index('date').T
        combined_data = pd.concat([combined_data, df], ignore_index=False)
    #
    # returning
    return combined_data


# Generate event matrix
def event_matrix(comid, combined_data):
    # Generate the input
    comid_data = pd.DataFrame()
    comid_data["date"] = pd.to_datetime(combined_data.index.tolist())
    comid_data["alert"] = combined_data[comid].to_list()
    #
    # Determine the event start
    F1 = list()
    for i in range(len(comid_data["date"]) - 1):
        value_start = comid_data.alert[i]
        value_end = comid_data.alert[i+1]
        temp_val = 1 if value_start == 0 and value_end > 0 else 0
        F1.append(temp_val)
    F1.append(0)
    #
    # Clasify events using cumulative sum (per events)
    F2 = list()
    temp = 0
    for num in F1:
        temp += num
        F2.append(temp)
    F2.append(0)
    #
    # Clasify events, without no alerts class (0)
    output = list()
    for i in range(len(comid_data["date"])):
        value = (comid_data.alert[i]>0) * F2[i]
        output.append(value)
    comid_data["event"] = output
    #
    # Summarized
    result = comid_data.groupby('event').agg(
        start=('date', 'min'),
        end=('date', 'max'),
        alert=('alert', 'max')
    ).reset_index()
    result = result[result['alert'] != 0].drop(columns=['event'])
    #
    # Returning
    return(result)


# Summarize the event matrix
def summary(event_matrix):
    alert_counts = event_matrix['alert'].value_counts().reset_index()
    alert_counts = alert_counts.sort_values(by='alert').reset_index(drop=True)
    alert_counts.rename(columns={
        "count": comid,
        "alert": "comid"
    }, inplace=True)
    alert_counts = alert_counts.set_index('comid').T
    alert_counts.columns = ['RP_' + str(col) if col != 'comid' else col for col in alert_counts.columns]
    return(alert_counts)




###############################################################################
#                               MAIN CONTROLLER                               #
###############################################################################

# Read drainage network
drainage = pd.read_excel("geoglows_reachs_ids.xlsx")["comid"].to_list()

# Setup date range
start_date = '2014-01-01'
end_date = '2019-12-31'

# Combined data
combined_data = combine(start_date, end_date)
combined_out = pd.DataFrame()

for comid in drainage:
    print(comid)
    em = event_matrix(comid, combined_data)
    summ = summary(em)
    combined_out = pd.concat([combined_out, summ], ignore_index=False)

combined_out = combined_out.fillna(0)
combined_out.to_csv("geoglows_analysis/results_comids.csv", index=True)

