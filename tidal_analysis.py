"""copy write;
Author - James Galloway"""

# import the modules we need
import pandas as pd
import datetime
import os
import numpy as np
import uptide
import pytz
import math
from scipy import stats as sstats
import matplotlib.dates as mdates
import argparse


def read_tidal_data(filename):
    tide_data = pd.read_csv(filename, skiprows=11, header=None, sep=r'\s+')
#first 11 rows are header information so unessisary

    tide_data['Date'] = pd.to_datetime(
        tide_data[1]+' '+tide_data[2],
        format= '%Y/%m/%d %H:%M:%S',)

    tide_data = tide_data.drop([0,1], axis=1)#drops, cycle, date,. in
    tide_data = tide_data.rename(columns= {2:"Time", 3: "Sea Level", 4:"Residuel"})
    tide_data = tide_data.set_index('Date')
    tide_data['Sea Level'] = pd.to_numeric(tide_data['Sea Level'], errors='coerce')
    tide_data['Residuel'] = pd.to_numeric(tide_data['Residuel'], errors='coerce')

    tide_data = tide_data.replace([-99, -32767, -9999, -99.999], np.nan)

    return tide_data

def extract_single_year_remove_mean(year, data):
    Start_year = str(year) + "-01-01"
    End_year = str(year) + "-12-31"

    year_data = data.loc[Start_year:End_year].copy()
    year_data_mean = year_data['Sea Level'].mean()#calcualtes mean of SL
    year_data['Sea Level'] -= year_data_mean

    return year_data


def extract_section_remove_mean(start, end, data):
    section = data.loc[start:end].copy()#Gets data specified in the range(section)
    section_mean = section['Sea Level'].mean()
    section['Sea Level'] -= section_mean

    return section


def join_data(data1, data2):

    return pd.concat([data1, data2]).sort_index()

def sea_level_rise(data): #this is the usual trend with SL

    sl = data['Sea Level'].dropna()#drops all nan values in column
    x = mdates.date2num(sl.index)
    y = sl.values
    regression = sstats.linregress(x,y)
    print(regression.pvalue)
    print(regression.slope)
    return regression.slope, regression.pvalue

def tidal_analysis(data, constituents, start_datetime): #this is where the m2... amp pha go

    sl = data.dropna(subset=['Sea Level'])
    tide = uptide.Tides(constituents)
    tide.set_initial_time(start_datetime)

    times = sl.index.values
    start = np.datetime64(start_datetime.replace(tzinfo=None))
    seconds_since = (times - start)/np.timedelta64(1, 's')

    water_height = sl['Sea Level'].values

    amp, pha = uptide.harmonic_analysis(tide, water_height, seconds_since)

    return amp, pha

def get_longest_contiguous_data(data):#longest unbroken data strech

    grouping = data['Sea Level'].isna().cumsum()
    
    valid = data['Sea Level'].dropna()
    



    return 


def main(args_list=None):

    parser = argparse.ArgumentParser(
                     prog="UK Tidal analysis",
                     description="Calculate tidal constiuents and RSL from tide gauge data",
                     )

    parser.add_argument("directory",
                    help="the directory containing txt files with data")
    parser.add_argument('-v', '--verbose',
                    action='store_true',
                    default=False,
                    help="Print progress")

    args = parser.parse_args(args_list)
    dirname = args.directory
    verbose = args.verbose

    print("Add your code here to do things!")
    

if __name__ == '__main__':
    main()
