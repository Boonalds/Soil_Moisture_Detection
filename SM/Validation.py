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
import datetime
import csv
import os
import fnmatch
from osgeo import gdal
import pyproj
from pyproj import Proj



#====================================================================================================
# Define parameters, variables, and allocate directories
#====================================================================================================
# Parameters:
sf = 0.1                        # Spacing factor, how much space should there be outside the bounding box; sf * difference min and max x (and y)
plot_sm_measurements = False    # Define whether the validation values should be plotted.
create_geojson = False          # Define whether a new GeoJSON should be created.

# Directory containing validation files
ValDir = 'C:/Users/r.maas/Source/Repos/Soil_Moisture_Detection/Data/Validation/Raam/'
ValDataDir = ValDir+ "data/station_data/"
valLocData = ValDir+ "data/metadata/Raam_station_locations_WGS84.csv"      # Locations of validation data points
img_dir = "C:/S2_Download/SM_Maps/"

#====================================================================================================
# Initialization
#====================================================================================================
label_names = []
Val_SM_05cm = []
Val_SM_10cm = []
img_list = []
SM_Est_ts = []

# Make a list of all soil moisture maps.
for file in os.listdir(img_dir):
    if fnmatch.fnmatch(file, 'SM_201?????-??????.tif'):
        img_list.append(img_dir+file)

#====================================================================================================
# Read in SM Measurements from validation data
#====================================================================================================
# Read in SM validation data
for file in os.listdir(ValDataDir):
    label_names = label_names + ["Field "+file[6:8]]
    with open(os.path.join(ValDataDir, file), newline='') as csvfile:
        r = csv.reader(csvfile, delimiter=',', quotechar='|')
        data = [i for i in r]
        del data[0]
        Val_SM_05cm = Val_SM_05cm + [np.array([np.float(i[1]) for i in data])]
        Val_SM_10cm = Val_SM_10cm + [np.array([np.float(i[3]) for i in data])]

# Read in validation timestamps (ts) from the first csv
csv_ts = os.listdir(ValDataDir)[0]
with open(os.path.join(ValDataDir, csv_ts), newline='') as csvfile:
    r = csv.reader(csvfile, delimiter=',', quotechar='|')
    data = [i for i in r]
    del data[0]
    Val_ts = [i[0] for i in data]

# Read in locations of the validation data and reproject to UTM 31 
with open(valLocData, newline='') as csvfile:
    r = csv.reader(csvfile, delimiter=';', quotechar='|')
    val_loc_data = [i for i in r]
    del val_loc_data[0]
    val_locs = [[float(r[1].replace(',', '.')),float(r[2].replace(',', '.'))] for r in val_loc_data]
    val_x = [i[0] for i in val_locs]
    val_y = [i[1] for i in val_locs]

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
    SM_Est_ts.append(img[-19:-4])   # Copy aquisition date for later use
    gdata = gdal.Open(img)          # Open image
    data = gdata.ReadAsArray().astype(np.float)
    gt = gdata.GetGeoTransform()    # Extract transform to reproject to map pixels
    gdata = None
    
    for j in range(len(val_locs)):
        x = int((val_locs[j][0] - gt[0])/gt[1])
        y = int((val_locs[j][1] - gt[3])/gt[5])
        print("Point "+str(j)+"; x: "+str(x)+ "     y: "+str(y))
        SM_est[i,j] = data[y,x]




#====================================================================================================
# Filter for the correct dates/times in the validation data
#====================================================================================================
# Transform acq dates

# Round to nearest quarter hour
#df['<column>'] = df['<column>'].apply(lambda dt: datetime.datetime(dt.year, dt.month, dt.day, dt.hour,15*round((float(dt.minute) + float(dt.second)/60) / 15)))


# match

#====================================================================================================
# Transform W -> omega
#====================================================================================================




#====================================================================================================
# Plot QQ plots and print validation results
#====================================================================================================
# Print RMSE, R^2 etc




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



