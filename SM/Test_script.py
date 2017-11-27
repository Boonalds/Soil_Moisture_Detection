

import numpy as np
from datetime import datetime, date, time
import csv
import os
import fnmatch

# Directory containing validation files
ValDir = 'C:/Users/r.maas/Source/Repos/Soil_Moisture_Detection/Data/Validation/Raam/'
ValDataDir = ValDir+ "data/station_data/"
valLocData = ValDir+ "data/metadata/Raam_station_locations_WGS84.csv"      # Locations of validation data points
img_dir = "C:/S2_Download/SM_Maps/"




def round2quarter(input_fn):
    """ Extract acquisition time from img filename, rounds the time to quarters and transforms to datetime class as output."""
    ts_tmp = img[-19:-4]                        
    if 0 <= int(ts_tmp[-4:]) < 730 or 5230 <= int(ts_tmp[-4:]) <= 5959:
        ts_rounded = ts_tmp[:-4]+'0000'
    elif 730 <= int(ts_tmp[-4:]) < 2230:
        ts_rounded = ts_tmp[:-4]+'1500'
    elif 2230 <= int(ts_tmp[-4:]) < 3730:
        ts_rounded = ts_tmp[:-4]+'3000'
    elif 3730 <= int(ts_tmp[-4:]) < 5230:
        ts_rounded = ts_tmp[:-4]+'4500'
    else:
        print("Unrecognized timeformat: "+ ts_tmp[-4:-2]+"m/"+ts_tmp[-2:]+"s.")
        sys.exit(-1)

    dt_obj = datetime.strptime(ts_rounded, "%Y%m%d-%H%M%S")
    dt = datetime.strftime(dt_obj, "%d-%b-%y %H:%M:%S")
    return dt


img_list = []
SM_acq_dt = []

# Make a list of all soil moisture maps.
for file in os.listdir(img_dir):
    if fnmatch.fnmatch(file, 'SM_201?????-??????.tif'):
        img_list.append(img_dir+file)



for i in range(len(img_list)):
    img = img_list[i]
    SM_acq_dt.append(round2quarter(img))        # Store acquisition dates, rounded to quarters


print(SM_acq_dt)