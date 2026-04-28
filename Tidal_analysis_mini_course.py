#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 12:18:04 2026

@author: student
"""

# import the modules we need
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import wget
import os
import numpy as np
import uptide
import pytz
import math


"""now we have our envirnoment setup. we can create a coiple of 
helper functions to make life esier later"""

def read_and_process_data(filename):
    tide_data = pd.read_csv(filename, header=None)
    tide_data['Date'] = pd.to_datetime(dict(year=tide_data[0], month=tide_data[1], day=tide_data[2], hour=tide_data[3]))
    # col 0 is year, col 1 is month, col2 is day, col3 hour
    tide_data = tide_data.drop([0,1,2,3], axis = 1)
    tide_data = tide_data.rename(columns={4: "Tide"})
    tide_data = tide_data.set_index('Date')
    tide_data = tide_data.mask(tide_data['Tide'] < -300)

    return tide_data

def extract_single_year_remove_mean(year, data):
    year_string_start = str(year)+"0101"
    year_string_end = str(year)+"1231"
    year_data = data.loc[year_string_start:year_string_end, ['Tide']]
    # remove mean to oscillate around zero
    mmm = np.mean(year_data['Tide'])
    year_data['Tide'] -= mmm

    return year_data

"""we are going to be using data from the long term tidal record dataset held by the school of ocean 
and earth science and tech. There are some hella unc records here."""

FortDenison_url = "https://uhslc.soest.hawaii.edu/data/csv/fast/hourly/h333.csv"
BoobyIsland_url = "https://uhslc.soest.hawaii.edu/data/csv/fast/hourly/h336.csv"
Freemantle_url = "https://uhslc.soest.hawaii.edu/data/csv/fast/hourly/h175.csv"
urls = [FortDenison_url, BoobyIsland_url, Freemantle_url]

# fetch our data and store
for url in urls:
    file_name = os.path.basename(url) # get the full path to the file
    if os.path.exists(file_name):
        os.remove(file_name) # if exists, remove it directly
    file_name = wget.download(url, out=".")


#now wer have three csv files which should be stored in your current directory (wherever you are running code from)


# load and store as a pandas dataframe
Fort_Denison = read_and_process_data("h333.csv")
Booby_Island = read_and_process_data("h336.csv")
Freemantle = read_and_process_data("h175.csv")

"Now plot these, choosing an arbitary year to plot rather than all data"

# Let's plot 1 years' worth of tidal data
fig_summary=plt.figure()
ax=fig_summary.add_subplot(111)
fd = ax.plot(Fort_Denison['Tide'], color="blue", lw=1, label="Fort Denison")
bi = ax.plot(Booby_Island['Tide'], color="orange", lw=1, label="Booby_Island")
f = ax.plot(Freemantle['Tide'], color="red", lw=1, label="Freemantle")
ax.set_xlabel("Date")
ax.set_ylabel("Water height (mm)")
ax.tick_params(axis='x', rotation=45)
ax.legend()
ax.set_xlim([datetime.date(2008, 1, 1), datetime.date(2008, 12, 31)])
fig_summary.tight_layout()
plt.show()

"""Tide gauges often record the water level so can pick up storms and are 
affected by even small winds blowing onshore for example. 
This means the data you see might not be “just tides”, but also some aspect of weather,
 depending on how the data are processed. In addition, for long term records, the tide gauges will also record sea level rise.
 All heights are measured above a datum so you also have to be careful comparing raw data from one tide gauge to another."""

#For one month


fig_june=plt.figure()
ax=fig_june.add_subplot(111)
fd = ax.plot(Fort_Denison['Tide'], color="blue", lw=1, label="Fort Denison")
bi = ax.plot(Booby_Island['Tide'], color="orange", lw=1, label="Booby_Island")
f = ax.plot(Freemantle['Tide'], color="red", lw=1, label="Freemantle")
ax.set_xlabel("Date")
ax.set_ylabel("Water height (mm)")
ax.tick_params(axis='x', rotation=45)
ax.legend()
ax.set_xlim([datetime.date(2008, 6, 1), datetime.date(2008, 7, 1)])
fig_june.tight_layout()
plt.show()

"""we know what the frequency of the external forcing is for tides
(the rotation of the earth), which allows us to break up the signal into
constituent parts: these are often given labels, M2,S2,K1,O1. Each has
a particular frequency as given below"""

Decription
Darwin symbol
Period (h)
Speed (°/h)
Principal lunar semidiurnal
M2
12.4206012
28.9841042
Principal solar semidiurnal
S2
12
30
Lunar diurnal
K1
23.9344721
15.0410686
Lunar diurnal
O1
25.8193387
13.9430356
Lunisolar semidiurnal
K2
11.96723606
30.0821373
Larger lunar elliptic semidiurnal
N2
12.6583475
28.4397295













