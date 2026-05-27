"""
Author - James Galloway

Decription: This code completes tidal analysis on datasets provided by the 
BODC, """

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
#first 11 rows are header information unessisary so skipped

    tide_data['Date'] = pd.to_datetime(
        tide_data[1]+' '+tide_data[2],
        format= '%Y/%m/%d %H:%M:%S',)

    tide_data = tide_data.drop([0,1], axis=1)#drops, cycle, date,. in
    tide_data = tide_data.rename(columns= {2:"Time", 3: "Sea Level", 4:"Residual"})
    tide_data = tide_data.set_index('Date')

    data_cols = ["Sea Level", "Residual"]

    for col in data_cols:
        tide_data[col] = tide_data[col].astype(str)

        tide_data.loc[tide_data[col].str.contains(r"[MNmn]", na = False),col]=(
             np.nan)#if value flagged with N or M, it is set nan

        tide_data[col] = tide_data[col].str.replace(r"[Tt]","", regex=True)


    tide_data['Sea Level'] = pd.to_numeric(tide_data['Sea Level'], errors='coerce')
    tide_data['Residual'] = pd.to_numeric(tide_data['Residual'], errors='coerce')

    for col in data_cols:
        tide_data.loc[tide_data[col]<= -99, col] = np.nan #any error codes set null

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

    grouping = data['Sea Level'].isna().cumsum()#for every nan, a number is assigned, all values inbetween are assigned the same value as the prvious nan, effectivly grouping
    
    valid = data.dropna(subset=['Sea Level']) #singles SL data out
    valid_grouping = grouping.loc[valid.index]
    
    longest = valid_grouping.value_counts().idxmax()

    return valid[valid_grouping == longest]


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

    #print("Add your code here to do things!")

    txt_files = sorted([os.path.join(dirname, f)
                       for f in os.listdir(dirname)
                       if f.endswith(".txt")])

    if not txt_files:
        if verbose:
            print(f"error: No txt files found in '{dirname}'.")
        return

    if verbose:
        print(f"processing target directory: {dirname}")
        print(f"Found {len(txt_files)} data files compiling")
        print("Stiching datasets by date")

    combined_data = read_tidal_data(txt_files[0])
    for extra_file in txt_files[1:]:
        next_data = read_tidal_data(extra_file)
        combined_data = join_data(combined_data, next_data)


#Harmonic analysis 

    constituents = ['M2','S2']
    start = datetime.datetime(combined_data.index[0].year,1,1, tzinfo = pytz.utc)
    amp, pha = tidal_analysis(combined_data,constituents,start)

    amp = np.asarray(amp).flatten()
    pha = np.asarray(pha).flatten()

#Sl rise per annum

    slope, p_value = sea_level_rise(combined_data)

    location = os.path.basename(os.path.normpath(dirname))
    analysis = "\n".join([
        f"location: {location}",
        f"M2 amp: {float(amp[0]):.4f} m phase: {float(pha[0]):.2f} deg",
        f"S2 amp: {float(amp[1]):.4f} m phase: {float(pha[1]):.2f} deg",
        f"Sea Level Rise Slope:{float(slope):.6f}",
        f"p-value: {float(p_value):.6f}",])


    if verbose:
        print(analysis)


if __name__ == '__main__':
    main()



















