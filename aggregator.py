import os
import csv
from enum import Enum

class LogType(Enum):
    NONE = 0
    DAMAGE_DONE = 1
    DAMAGE_TAKEN = 2
    HEALING_DONE = 3

def parse_amount(amnt_str):
    ''' Parses the Amount field of a warcraft log to get raw amount'''
    return(float(amnt_str.split('$')[0]))

class player_stats:
    def __init__(self,name):
        self.name = name
        self.count = 0
        self.damage_done = 0.0
        self.damage_taken = 0.0
        self.healing_done = 0.0

    def _update_stats(self,log_type,row):
        '''Updates the stats given new log type and row dict'''
        if log_type == LogType.NONE:
            print("ERROR: NONE")
            return

        self.count += 1 #TODO, actually need to count unique dates of raids
        if log_type == LogType.DAMAGE_DONE:
            self.damage_done += parse_amount(row['Amount'])
        elif log_type == LogType.DAMAGE_TAKEN:
            self.damage_taken += parse_amount(row['Amount'])
        elif log_type == LogType.HEALING_DONE:
            self.healing_done += parse_amount(row['Amount'])
        return

    def __str__(self):
        return("{}\n\tcount: {}\n\tdamage_done: {}\n\tdamage_taken: {}\n\thealing_done: {}".format(self.name,self.count,self.damage_done,self.damage_taken,self.healing_done))

def determine_log_type(filename):
    '''Determines the log type given filename'''
    log_type_str = filename.split('_')[2].split('.')[0]
    print(log_type_str)
    if log_type_str == 'DD':
        return(LogType.DAMAGE_DONE)
    elif log_type_str == 'DT':
        return(LogType.DAMAGE_TAKEN)
    elif log_type_str == 'HD':
        return(LogType.HEALING_DONE)
    else:
        return(LogType.NONE)


data = {} # dictionary of player name to player_stats
directory = 'logs'
for filename in os.listdir(directory):
    print()
    print("Reading: "+filename)
    # get log type
    log_type = determine_log_type(filename)
    print(log_type)
    with open(directory+'/'+filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row['Name']
            if name not in data:
                data[name] = player_stats(name)
            else:
                data[name]._update_stats(log_type,row)

print(data['Akecheta'])