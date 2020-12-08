import os
import csv
from enum import Enum
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Latest Log Added: 2/26/20

class LogType(Enum):
    NONE = 0
    DAMAGE_DONE = 1
    DAMAGE_TAKEN = 2
    HEALING_DONE = 3

def parse_amount(amnt_str):
    ''' Parses the Amount field of a warcraft log to get raw amount'''
    return(int(amnt_str.split('$')[0]))

def update_df(df,log_type,row):
    '''Updates the dataframe given new log type and row dict'''
    if log_type == LogType.NONE:
        print("ERROR: NONE")
        return
    
    # Initialize if new
    name = row['Name']
    if name not in df.index:
        df.loc[name,['damage_done','damage_taken','healing_done']] = [0,0,0]

    # Add data from log
    if log_type == LogType.DAMAGE_DONE:
        df.loc[name,'damage_done'] += parse_amount(row['Amount'])
    elif log_type == LogType.DAMAGE_TAKEN:
        df.loc[name,'damage_taken'] += parse_amount(row['Amount'])
    elif log_type == LogType.HEALING_DONE:
        df.loc[name,'healing_done'] += parse_amount(row['Amount'])
    return

def parse_metadata(reader):
    '''Determines the meta data reader'''
    if "DPS" in reader.fieldnames:
        log_type = LogType.DAMAGE_DONE
    elif "DTPS" in reader.fieldnames:
        log_type = LogType.DAMAGE_TAKEN
    elif "HPS" in reader.fieldnames:
        log_type = LogType.HEALING_DONE

    return(log_type)

# Create dataframe to store results
df = pd.DataFrame(columns=['damage_done','damage_taken','healing_done'])
directory = 'logs'
for filename in os.listdir(directory):
    print()
    print("Reading: "+filename)
    with open(directory+'/'+filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        log_type = parse_metadata(reader)
        for row in reader:
            update_df(df,log_type,row)

print(df.loc['Akecheta'])

# Compute percentage parameters
parameters = [parameter for parameter in df.columns]
for parameter in parameters:
    df[parameter+"_pct"] = df[parameter] / sum(df[parameter]) * 100.0

for parameter in parameters:
    df.sort_values(by=parameter,ascending=True,inplace=True)
    plt.figure()
    mask = df[parameter+"_pct"] >= 0.5
    plt.barh(df[mask].index,df[mask][parameter+"_pct"])
    plt.title(parameter)

plt.show()