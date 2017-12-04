

#====================================================================================================
# Import libraries and modules
#====================================================================================================
import matplotlib.pyplot as plt
import geojson
import numpy as np
from datetime import datetime, date, time
import csv
import os, os.path, optparse,sys
import fnmatch
from osgeo import gdal
import pyproj
from pyproj import Proj
import pandas as pd



#====================================================================================================
# Define parameters, variables, and allocate directories
#====================================================================================================
# Parameters:
sf = 0.1                        # Spacing factor, how much space should there be outside the bounding box; sf * difference min and max x (and y)
USE_BUFFER = True               # Take median value of 3x3 raster around the validation coordinates as input for Estimated values
plot_sm_measurements = False    # Define whether the validation values should be plotted.
create_geojson = False          # Define whether a new GeoJSON should be created.
PRINT_VAL_OVERVIEW = False      # Print overview of raw validation measurements
Max_Content = 0.5               # Max expected water content [m3/m3], used for plotting

# Directory containing validation files
ValDir = 'C:/Users/r.maas/Source/Repos/Soil_Moisture_Detection/Data/Validation/Raam/'
ValDataDir = ValDir+ "data/station_data/"
valLocData = ValDir+ "data/metadata/Raam_station_locations_WGS84.csv"      # Locations of validation data points
img_dir = "C:/S2_Download/SM_Maps/"


#====================================================================================================
# Defining functions that are to be used in this script
#====================================================================================================

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


def calc_rmse(trueVal, predVal):
    """Function that calculates the Root Mean Square Error, which is an indicator for the prediction error"""
    if len(trueVal) == len(predVal):
        if np.nansum(trueVal) > 0:
            RMSE = (np.nanmean((np.array(trueVal) - np.array(predVal))**2))**0.5
        else:
            return np.NaN
    else:
        print("ERROR: number of predicted and measured values must be equal; \n       n(predicted):"+str(len(predVal))+"\n       n(measured):"+str(len(trueVal)))
        sys.exit(-1)
    return RMSE
   

def calc_r2(trueVal,predVal):
    """Function that calculates the R^2 value, indicating the proportion of the variation that is explained by the predicted values"""
    if len(trueVal) == len(predVal):
        if np.nansum(trueVal) > 0:
            SSR = np.nansum((np.array(trueVal) - np.array(predVal))**2)
            SST = np.nansum(np.array(trueVal)**2)
            r2 = 1-(SSR/SST)
        else:
            return np.NaN
    else:
        print("ERROR: number of predicted and measured values must be equal; \n       n(predicted):"+str(len(predVal))+"\n       n(measured):"+str(len(trueVal)))
        sys.exit(-1)
    return r2


def calc_mae(trueVal, predVal):
    """Function that calculates the Mean Absolute Error, which is an indicator for the prediction error"""
    if len(trueVal) == len(predVal):
        if np.nansum(trueVal) > 0:
            MAE = np.nanmean(abs(np.array(trueVal) - np.array(predVal)))
        else:
            return np.NaN
    else:
        print("ERROR: number of predicted and measured values must be equal; \n       n(predicted):"+str(len(predVal))+"\n       n(measured):"+str(len(trueVal)))
        sys.exit(-1)
    return MAE


#====================================================================================================   
# Initialization
#====================================================================================================
label_names = []
img_list = []
SM_acq_dt = []

# Make a list of all soil moisture maps and validation files
for file in os.listdir(img_dir):
    if fnmatch.fnmatch(file, 'SM_201?????-??????.tif'):
        img_list.append(img_dir+file)

val_list = os.listdir(ValDataDir)

#====================================================================================================
# Read in SM validation locations from metadata
#====================================================================================================
with open(valLocData, newline='') as csvfile:
    r = csv.reader(csvfile, delimiter=';', quotechar='|')
    val_loc_data = [i for i in r]
    del val_loc_data[0]
    val_locs = [[float(r[1].replace(',', '.')),float(r[2].replace(',', '.'))] for r in val_loc_data]
    val_x = [i[0] for i in val_locs]
    val_y = [i[1] for i in val_locs]

# reproject to UTM 31 
wgs84 = Proj(init = 'epsg:4326')
wgs84utm31 = Proj(init = 'epsg:32631')

for coordPair in val_locs:
    x = coordPair[0]
    y = coordPair[1]
    coordPair[0],coordPair[1] = pyproj.transform(wgs84,wgs84utm31,x, y)

#====================================================================================================
# Read in SM Estimates from maps
#====================================================================================================
SM_est = np.empty([len(img_list), len(val_locs)])

# Read in every image 1 by 1, and extract estimated SM value at each validation location and its acquisition date
for i in range(len(img_list)):
    img = img_list[i]
    SM_acq_dt.append(round2quarter(img))        # Store acquisition dates, rounded to quarters

    gdata = gdal.Open(img)                      # Open image
    data = gdata.ReadAsArray().astype(np.float) # Read data as float
    gt = gdata.GetGeoTransform()                # Extract transform to reproject to map pixels
    gdata = None
    # print(img)
    for j in range(len(val_locs)):
        x = int((val_locs[j][0] - gt[0])/gt[1])
        y = int((val_locs[j][1] - gt[3])/gt[5])
        # print("Point "+str(j)+"; x: "+str(x)+ "     y: "+str(y) + ". SM Value: " + str(data[y,x]))
        if USE_BUFFER == False:
            SM_est[i,j] = data[y,x]
        elif USE_BUFFER == True:
            SM_est[i,j] = np.nanmedian(data[y-1:y+2,x-1:x+2])
        else:
            print("Non acceptable value for USE_BUFFER")


#====================================================================================================
# Load in the SM validation data and extract the values that correspond the acquisition date
#====================================================================================================
SM_meas5 = np.empty(shape=np.shape(SM_est))
SM_meas10 = np.empty(shape=np.shape(SM_est))
SM_meas20 = np.empty(shape=np.shape(SM_est))
SM_meas40 = np.empty(shape=np.shape(SM_est))

for i in range(len(val_list)):              # i cycles over locations
    file = val_list[i]
    with open(os.path.join(ValDataDir, file), newline='') as csvfile:
        r = csv.reader(csvfile, delimiter=',', quotechar='|')
        next(r)
        for j in range(len(SM_acq_dt)):     # j cycles over timestamps
            for mt, sm_5, t_5, sm_10, t_10, sm_20, t_20,sm_40, t_40,sm_80,t_80 in r:
                if mt == SM_acq_dt[j]:
                    SM_meas5[j,i] = sm_5
                    SM_meas10[j,i] = sm_10
                    SM_meas20[j,i] = sm_20
                    SM_meas40[j,i] = sm_40
                    break
            else:
                SM_meas5[j,i] = np.NaN
                SM_meas10[j,i] = np.NaN
                SM_meas20[j,i] = np.NaN
                SM_meas40[j,i] = np.NaN
                csvfile.seek(0)                 # Ensures that the csv is being read from the top again
 
 
##====================================================================================================
# Transformation (W -> Theta)   and Statistical calculations
#====================================================================================================
# Estimated RS Water content is normalized between 0 and 1, while validation measurements are in water content (theta) in m3/m3. 
# Using linear relation between W (estimated) and O (Theta,measured): O = a*W+b. (Full description in Sadeghi 2017)
SM_est[SM_est>0.35] = np.nan   # outliers based on histograms below
f_b = np.nanmin(SM_meas5)
f_a = (np.nanmax(SM_meas5)-np.nanmin(SM_meas5))/(np.nanmax(SM_est)-np.nanmin(SM_est))
SM_est_O = (f_a*SM_est)+f_b


#====================================================================================================
# PLOTS
#====================================================================================================
#### Plot through time
# Load data and time as datetime objects
sp_ds = SM_est_O - SM_meas5

dates = []
for d in SM_acq_dt:
    dates.append(datetime.strptime(d, "%d-%b-%y %H:%M:%S"))

date_labels = []
for dl in SM_acq_dt:
    dt_obj = datetime.strptime(dl, "%d-%b-%y %H:%M:%S")
    date_labels.append(datetime.strftime(dt_obj, "%d-%b-%y"))

# Determine x-axis positions
x1 = datetime.strptime('05-Mar-16', "%d-%b-%y")
x2 = datetime.strptime('05-May-17', "%d-%b-%y")
pos = []
for d in dates:
    pos.append((d - x1).days)


# Filter data using np.isnan
mask = ~np.isnan(sp_ds)
filtered_data = [d[m] for d, m in zip(sp_ds, mask)]


## Construct the plot
fig, ax = plt.subplots( figsize=(10,10) )
bplot1 = ax.boxplot(filtered_data, positions=pos, widths=5, patch_artist=True)

# add labels, legend and make it nicer
ax.set_xlabel("Time")
ax.set_ylabel("Estimated "+ r'$\theta$'+ "- measured "+r'$\theta$' + " " + r'$[m^3/m^3]$')
ax.set_xlim( [ 0, (x2-x1).days ] )
ax.set_xticklabels(date_labels, rotation=45 )
ax.axhline(y=0,c="black",ls="--",linewidth=0.5,zorder=0)
colors = ['pink', 'lightblue', 'lightgreen']
for box in bplot1['boxes']:
    # change outline color
    box.set( color='royalblue', linewidth=1)
    # change fill color
    box.set( facecolor = 'lightskyblue' )

for median in bplot1['medians']:
    median.set(color='royalblue', linewidth=2)


plt.tight_layout()
plt.show()