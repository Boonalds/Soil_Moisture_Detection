"""
Script for  downloading the required Sentinel-2 Data from the SciHub API. The Sentinelsat package
is used for this: http://sentinelsat.readthedocs.io/en/stable/. This script successfully downloads the images
at Level-1A processing level from the Amazon AWS Archive, at granule size.

Next the script also carries out Atmospheric Correction using the Sen2Cor standalone installation. This 

### Information/notes
# - Python version 3.6
# - Now usi


"""

#====================================================================================================
# Import libraries and modules
#====================================================================================================
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from sentinelhub import *
from geojson import Polygon
from datetime import datetime
import os, os.path, optparse,sys
import csv
import sys
import numpy as np



#====================================================================================================
# Define variables
#====================================================================================================
# Image search definitions
date_start = '20170205'     # Starting date
date_end = '20170305'       # End date
cloudMax = 100              # Maximum cloud cover [%]
tile_name = '31UFT'         # Tile ID (For now, later I can loop through all 4 tiles (with 4 seperate 
                            # queries to download all NL data, or make only data from 6 december 2016 available.) 


# Directory allocation
dir_out = "C:\S2_Data"          # Directory where images are to be downloaded to
val_loc_file = './Data/Validation/Raam/data/metadata/Raam_station_locations_WGS84.csv'      # Location of validation data

# SciHub API info
login_sh='boonalds'
password_sh='123abc987zyx'
sh_api_url = 'https://scihub.copernicus.eu/dhus'



#====================================================================================================
# Area of Interest
#====================================================================================================
### Define area of interest, which is to  be downloaded, based on validation data.
with open(val_loc_file, newline='') as csvfile:
    r = csv.reader(csvfile, delimiter=';', quotechar='|')
    val_loc_data = [i for i in r]

del val_loc_data[0]
[val_x, val_y] = [[float(r[1].replace(',', '.')) for r in val_loc_data], 
                  [float(r[2].replace(',', '.')) for r in val_loc_data]]
[x_min, x_max] = [min(val_x)-0.5*(max(val_x)-min(val_x)),max(val_x)+0.5*(max(val_x)-min(val_x))]
[y_min, y_max] = [min(val_y)-0.5*(max(val_y)-min(val_y)),max(val_y)+0.5*(max(val_y)-min(val_y))]

# Store as geojson format:
footprint = "POLYGON((" + str(x_min) + " " + str(y_min) + "," + str(x_max) + " " + str(y_min) + "," + str(x_max) + " " + str(y_max) + "," + str(x_min) + " " + str(y_max) + "," + str(x_min) + " " + str(y_min) + "))"



#====================================================================================================
# Download the Images
#====================================================================================================
# Connect to the SciHub API
api = SentinelAPI(login_sh, password_sh, sh_api_url)

# Search database for all available images
products = api.query(footprint,
                     area_relation='Contains',
                     date = (date_start, date_end),
                     platformname='Sentinel-2',
                     cloudcoverpercentage=(0,cloudMax))

# Convert search results to Pandas DataFrame
products_df = api.to_dataframe(products)

# Start the downloading loop
print("    ....:::: DOWNLOADING IMAGES ::::....")
for i in range(0,len(products_df)): # 
    print("Download of image " + str(i+1) + "/" + str(len(products_df)) + " started..")
    ts = products_df['beginposition'].iloc[i]
    i_name = products_df['title'].iloc[i]
    if ts >= datetime(2016, 12, 6):
        # print(i_name)
        download_safe_format(tile=(tile_name, ts.strftime('%Y-%m-%d')),folder=dir_out)
        # download_safe_format(i_name,folder=dir_out)
    elif ts < datetime(2016, 12, 6):
        # print(i_name)
        download_safe_format(tile=(tile_name, ts.strftime('%Y-%m-%d')),folder=dir_out)
    else:
        print("Incompatible Begin Position Date")

print("All downloads completed.")



