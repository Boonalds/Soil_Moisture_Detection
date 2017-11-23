'''
This script is pure for testing purposes and will be excluded from the end product.
'''

"""
Script to download the required Sentinel-2 data, longer description later.
"""

### Import libraries
import matplotlib.pyplot as plt
import geojson
import numpy as np
import csv
import os 

# Input parameters
sf = 0.1 # Spacing factor, how much space should there be outside the bounding box; sf * difference min and max x (and y)

### Initialization
label_names = []
Val_SM_05cm = []
Val_SM_10cm = []

### Directory containing validation files
ValDir = './Data/Validation/Raam/'
ValDataDir = './Data/Validation/Raam/data/station_data/'
valLocData = './Data/Validation/Raam/data/metadata/Raam_station_locations_WGS84.csv'      # Locations of validation data points

### Read Validation data and store SM and location data and headings in different arrays
for file in os.listdir(ValDataDir):
    label_names = label_names + ["Field "+file[6:8]]
    with open(os.path.join(ValDataDir, file), newline='') as csvfile:
        r = csv.reader(csvfile, delimiter=',', quotechar='|')
        data = [i for i in r]
        del data[0]
        Val_SM_05cm = Val_SM_05cm + [np.array([np.float(i[1]) for i in data])]
        Val_SM_10cm = Val_SM_10cm + [np.array([np.float(i[3]) for i in data])]




with open(valLocData, newline='') as csvfile:
    r = csv.reader(csvfile, delimiter=';', quotechar='|')
    val_loc_data = [i for i in r]

del val_loc_data[0]
[val_x, val_y] = [[float(r[1].replace(',', '.')) for r in val_loc_data], [float(r[2].replace(',', '.')) for r in val_loc_data]]

# Calculate x and y coordinates for a bounding box around the validation data and store as a .geojson file
[x_min, x_max] = [min(val_x)-sf*(max(val_x)-min(val_x)),max(val_x)+sf*(max(val_x)-min(val_x))]
[y_min, y_max] = [min(val_y)-sf*(max(val_y)-min(val_y)),max(val_y)+sf*(max(val_y)-min(val_y))]

#footprint = "POLYGON((" + str(x_min) + " " + str(y_min) + "," + str(x_max) + " " + str(y_min) + "," + str(x_max) + " " + str(y_max) + "," + str(x_min) + " " + str(y_max) + "," + str(x_min) + " " + str(y_min) + "))"
footprint = [{'type': 'Polygon', 'coordinates': [[(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max), (x_min, y_min)]]}]

with open(ValDir+'Validation_area_Raam.json', 'w') as fp:
    geojson.dump(footprint, fp)



### Soil Moisture Signals

plot_enable = False;

if plot_enable == True:
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




### Doc
# Original headers
# Measurement Time,5 cm VWC [m3/m3],5 cm Temp [oC],10 cm VWC [m3/m3],
#        10 cm Temp [oC],20 cm VWC [m3/m3],20 cm Temp [oC],40 cm VWC [m3/m3],
#        40 cm Temp [oC],80 cm VWC [m3/m3],80 cm Temp [oC]