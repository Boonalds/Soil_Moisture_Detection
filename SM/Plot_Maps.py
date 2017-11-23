"""
Script that allows for some plotting.

"""

import matplotlib.pyplot as plt
import numpy as np
import rasterio
import csv
import os
import pyproj
from pyproj import Proj
from osgeo import gdal

#=====================
# What maps to plot
#=====================
PLOT_SM_VALIDATION = False
PLOT_VAL_LOCATIONS = True

#=====================
# Sample input data
#=====================
SM_Map_sample = "C:/S2_Download/SM_Maps/SM_20160908-105416.tif"


if PLOT_SM_VALIDATION == True:
    ### Soil moisture maps of the validation area.
    # Load/read in data
    src = rasterio.open(SM_Map_sample)
    arr = src.read(1)

    # Create the plots
    plt.figure(1)

    plt.subplot(121)    # SM Map
    plt.imshow(arr, cmap="Blues")
    plt.colorbar()

    plt.subplot(122)    # Histogram
    plt.hist(arr.ravel(), bins=256, range=(0.0, 1.0), fc='k', ec='k')

    plt.show()

if PLOT_VAL_LOCATIONS == True:
    ### Soil moisture maps of the validation area.
    # Read in locations of the validation data
    valLocData = "C:/Users/r.maas/Source/Repos/Soil_Moisture_Detection/Data/Validation/Raam/data/metadata/Raam_station_locations_WGS84.csv"      # Locations of validation data points
    with open(valLocData, newline='') as csvfile:
        r = csv.reader(csvfile, delimiter=';', quotechar='|')
        val_loc_data = [i for i in r]
        del val_loc_data[0]
        val_locs = [[float(r[1].replace(',', '.')),float(r[2].replace(',', '.'))] for r in val_loc_data]

    # Reproject to UTM31
    wgs84 = Proj(init = 'epsg:4326')
    wgs84utm31 = Proj(init = 'epsg:32631')

    for coordPair in val_locs:
        x = coordPair[0]
        y = coordPair[1]
        coordPair[0],coordPair[1] = pyproj.transform(wgs84,wgs84utm31,x, y)


    # Transform back to the map pixel locations based on the geotiff metadata transform
    src = gdal.Open(SM_Map_sample)
    arr = src.ReadAsArray().astype(np.float)
    gt = src.GetGeoTransform()

    for coordPair in val_locs:
        coordPair[0] = int((coordPair[0] - gt[0])/gt[1])
        coordPair[1] = int((coordPair[1] - gt[3])/gt[5])

    # Split map pixels into x and y values for scatterplot
    val_x = [i[0] for i in val_locs]
    val_y = [i[1] for i in val_locs]


    # Construct the plot
    plt.imshow(arr, cmap="Blues")
    plt.colorbar()

    plt.scatter(x=val_x, y=val_y, c='r', s=40)
    plt.show()

