"""
This script is used for the validation of the Soil Maps as well as for creating the GeoJSON that defines the study area (which is used for
downloading and processing the correct imagery). The validation data that is used is from Benzinga et al (2017).



# Notes
# - Original validation file headers: Measurement Time,5 cm VWC [m3/m3],5 cm Temp [oC],10 cm VWC [m3/m3],
#        10 cm Temp [oC],20 cm VWC [m3/m3],20 cm Temp [oC],40 cm VWC [m3/m3],
#        40 cm Temp [oC],80 cm VWC [m3/m3],80 cm Temp [oC]

"""



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


#====================================================================================================   - np.nanmean(trueVal)
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
        SM_est[i,j] = data[y,x]


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
SM_est[SM_est>0.35] = np.nan
f_b = np.nanmin(SM_meas5)
f_a = (np.nanmax(SM_meas5)-np.nanmin(SM_meas5))/(np.nanmax(SM_est)-np.nanmin(SM_est))
SM_est_O = (f_a*SM_est)+f_b


#====================================================================================================
# Plot QQ plots and print validation results
#====================================================================================================

#### All validation data grouped (plot at different depths)
## Set up lists for loop
sp_ds = [SM_meas5, SM_meas10, SM_meas20, SM_meas40]
sp_t = ["All sites - 5cm depth", "All sites - 10cm depth", "All sites - 20cm depth", "All sites - 40cm depth"]

plt.figure(1, figsize=(10,10))

for i in range(len(sp_ds)):
    ax = plt.subplot(2,2,i+1)

    # Plots
    ax.plot((0,1), 'k', label='1:1')
    ax.scatter(sp_ds[i],SM_est_O)

    # Add statistics
    ax.text(0.99, 0.01, "$R^2$: %.2f \n MAE: %.2f \n RMSE: %.2f" % (round(calc_r2(sp_ds[i],SM_est),2),round(calc_mae(sp_ds[i],SM_est),2),round(calc_rmse(sp_ds[i],SM_est),2)),
        verticalalignment='bottom', horizontalalignment='right',
        transform=ax.transAxes,
        color='green', fontsize=12)

    # add labels, legend and make it nicer
    ax.set_xlabel("Measured "+ r'$\theta$' + " " + r'$[m^3/m^3]$')
    ax.set_ylabel("Estimated "+ r'$\theta$' + " " + r'$[m^3/m^3]$')
    ax.set_title(sp_t[i], y=.93)
    ax.set_xlim(0, Max_Content)
    ax.set_ylim(0, Max_Content)
    ax.legend()



#### Plot per validation location 
# Set Define which dataset tot use (whih depth)
sp_ds = SM_meas5


plt.figure(2, figsize=(15,10))

for i in range(0,np.shape(sp_ds)[1]):
    ax = plt.subplot(3,5,i+1)

    # Plots
    ax.plot((0,1), 'k', label='1:1')
    ax.scatter(sp_ds[:,i],SM_est_O[:,i])

    # Add statistics
    ax.text(0.99, 0.01, "$R^2$: %.2f \n MAE: %.2f \n RMSE: %.2f" % (round(calc_r2(sp_ds[:,i],SM_est[:,i]),2),round(calc_mae(sp_ds[:,i],SM_est[:,i]),2),round(calc_rmse(sp_ds[:,i],SM_est[:,i]),2)),
        verticalalignment='bottom', horizontalalignment='right',
        transform=ax.transAxes,
        color='green', fontsize=10)

    # add labels, legend and make it nicer
    ax.set_xlabel("Measured "+ r'$\theta$' + " " + r'$[m^3/m^3]$')
    ax.set_ylabel("Estimated "+ r'$\theta$' + " " + r'$[m^3/m^3]$')
    ax.set_title("Site "+ str(i+1), y=.9)
    ax.set_xlim(0, Max_Content)
    ax.set_ylim(0, Max_Content)
    ax.legend()



plt.tight_layout()
plt.show()



#### Plot histograms
#plt.figure(2)

#plt.subplot(121)    
#plt.hist(SM_est.ravel(), bins=256, range=(0.0, Max_Content), fc='k', ec='k')
#plt.title('Histogram of Estimated SM')

#plt.subplot(122)
#plt.hist(SM_meas5.ravel(), bins=256, range=(0.0, Max_Content), fc='k', ec='k')
#plt.title('Histogram of Measured SM')

#====================================================================================================
# Print validation Overview
#====================================================================================================
if PRINT_VAL_OVERVIEW == True:
    print("Dates used: ")
    print(SM_acq_dt)


    print("MEASURED-----------------")
    print("min: " + str(np.nanmin(SM_meas)))
    print("max: " + str(np.nanmax(SM_meas)))
    print("ESTIMATED----------------")
    print("min: " + str(np.nanmin(SM_est)))
    print("max: " + str(np.nanmax(SM_est)))


    for i in range(np.shape(SM_meas)[1]):
        print(val_list[i])
        print(SM_meas[:,i])

#====================================================================================================
# Create GeoJSON
#====================================================================================================
if create_geojson == True:
    # Calculate x and y coordinates for a bounding box around the validation data and store as a .geojson file
    [x_min, x_max] = [min(val_x)-sf*(max(val_x)-min(val_x)),max(val_x)+sf*(max(val_x)-min(val_x))]
    [y_min, y_max] = [min(val_y)-sf*(max(val_y)-min(val_y)),max(val_y)+sf*(max(val_y)-min(val_y))]

    footprint = [{'type': 'Polygon', 'coordinates': [[(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max), (x_min, y_min)]]}]

    with open(ValDir+'Validation_area_Raam.json', 'w') as fp:
        geojson.dump(footprint, fp)

#====================================================================================================
# Plots
#====================================================================================================
if plot_sm_measurements == True:
    plt.figure(1)
    
    # 5cm depth
    ax1 = plt.subplot(211)
    for k in range(len(Val_SM_05cm)):
        ax1.plot(Val_SM_05cm[k], label=label_names[k])
    ax1.legend()
    plt.title('5 cm depth')
    # 10cm depth
    ax2 = plt.subplot(212)
    for k in range(len(Val_SM_10cm)):
        ax2.plot(Val_SM_10cm[k], label=label_names[k])
    ax2.legend()
    plt.title('10 cm depth')

    plt.show()



