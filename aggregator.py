import os
import csv
from enum import Enum
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Latest Log Added: 12/06/20

fields = [
    'total_damage_done',
    'total_damage_taken',
    'total_healing_done',
    'avg_dps',
    'avg_dtps',
    'avg_hps',
    'avg_overheal',
    'damage_done_report_count',
    'damage_taken_report_count',
    'healing_done_report_count',
    'raid_count',
    ]

class LogType(Enum):
    NONE = 0
    DAMAGE_DONE = 1
    DAMAGE_TAKEN = 2
    HEALING_DONE = 3

def parse_amount(inpt_str):
    ''' Parses the Amount field of a warcraft log to get raw amount
    (amnt)$(pct)%(thsd)k
    '''
    return(int(inpt_str.split('$')[0]))

def parse_pct(inpt_str):
    ''' Parses a field that contains %
    (pct)%
    '''
    pct = inpt_str.split('%')[0]
    if pct == '-':
        return(0.0)
    else:
        return(float(pct))

def update_df(df,log_type,row):
    '''Updates the dataframe given new log data'''
    if log_type == LogType.NONE:
        print("ERROR: NONE")
        return
    
    # Initialize if new
    name = row['Name']
    if name not in df.index:
        df.loc[name,fields] = 0

    # Add data from log
    if log_type == LogType.DAMAGE_DONE:
        n = df.loc[name,'damage_done_report_count']
        df.loc[name,'damage_done_report_count'] += 1
        df.loc[name,'total_damage_done'] += parse_amount(row['Amount'])
        df.loc[name,'avg_dps'] = (df.loc[name,'avg_dps']*n + parse_pct(row['DPS']))/df.loc[name,'damage_done_report_count']
    elif log_type == LogType.DAMAGE_TAKEN:
        n = df.loc[name,'damage_taken_report_count']
        df.loc[name,'damage_taken_report_count'] += 1
        df.loc[name,'total_damage_taken'] += parse_amount(row['Amount'])
        df.loc[name,'avg_dtps'] = (df.loc[name,'avg_dtps']*n + parse_pct(row['DTPS']))/df.loc[name,'damage_taken_report_count']
    elif log_type == LogType.HEALING_DONE:
        n = df.loc[name,'healing_done_report_count']
        df.loc[name,'healing_done_report_count'] += 1
        df.loc[name,'total_healing_done'] += parse_amount(row['Amount'])
        df.loc[name,'avg_hps'] = (df.loc[name,'avg_hps']*n + parse_pct(row['HPS']))/df.loc[name,'healing_done_report_count']
        df.loc[name,'avg_overheal'] = (df.loc[name,'avg_overheal']*n + parse_pct(row['Overheal']))/df.loc[name,'healing_done_report_count']

    # Update raid count
    df.loc[name,'raid_count'] = max(df.loc[name,'damage_done_report_count'],df.loc[name,'damage_taken_report_count'],df.loc[name,'healing_done_report_count'])

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
print("Reading Logs...")
for filename in os.listdir(directory):
    # print()
    # print("Reading: "+filename)
    with open(directory+'/'+filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        log_type = parse_metadata(reader)
        for row in reader:
            update_df(df,log_type,row)
print("Done!")

# Compute percentage parameters
parameters = ['total_damage_done','total_damage_taken','total_healing_done']
for parameter in parameters:
    df[parameter+"_pct"] = df[parameter] / sum(df[parameter]) * 100.0

# combine alts
alt_list = [
    'Gonz + Gaunz',
    'Dohvyk + Darunor',
    'Akecheta + Kagomi',
    'Pythagorean + Paskal',
    'Pemberstone + Kasako',
    'Enders + Buffymctank',
    'Wangcake + Trolleficent',
    'Jiero + Jiera',
    'Deyn + Dayn',
    'Dietolive + Pointed',
    ]
for alt_pair in alt_list:
    char1 = alt_pair.split(" + ")[0]
    char2 = alt_pair.split(" + ")[1]
    df.loc[alt_pair,'raid_count'] = df.loc[char1,'raid_count'] + df.loc[char2,'raid_count']

# plot
# raid count
df.sort_values(by='raid_count',ascending=True,inplace=True)
plt.figure()
mask = df['raid_count'] >= 40
plt.barh(df[mask].index,df[mask]['raid_count'])
plt.title('raid_count')
plt.grid()

# damage
parameters = ['total_damage_done','avg_dps']
for parameter in parameters:
    df.sort_values(by=parameter,ascending=True,inplace=True)
    plt.figure()
    mask = df['total_damage_done_pct'] >= 0.5
    plt.barh(df[mask].index,df[mask][parameter])
    plt.title(parameter)
    plt.grid()

# damage taken
df.sort_values(by='total_damage_taken',ascending=True,inplace=True)
plt.figure()
mask = df['total_damage_taken_pct'] >= 1
plt.barh(df[mask].index,df[mask]['total_damage_taken'])
plt.title('total_damage_taken')
plt.grid()

df.sort_values(by='avg_dtps',ascending=False,inplace=True)
plt.figure()
mask = df['raid_count'] >= 40
plt.barh(df[mask].index,df[mask]['avg_dtps'])
plt.title('avg_dtps')
plt.grid()

# healing
parameters = ['total_healing_done','avg_hps','avg_overheal']
for parameter in parameters:
    df.sort_values(by=parameter,ascending=True,inplace=True)
    plt.figure()
    mask = df['total_healing_done_pct'] >= 0.5
    plt.barh(df[mask].index,df[mask][parameter])
    plt.title(parameter)
    plt.grid()

plt.show()