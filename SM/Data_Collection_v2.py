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
from xml.etree import ElementTree
from . import download
import os, os.path, optparse
import csv
import sys
import numpy as np
import requests
import urllib.request



#====================================================================================================
# Define variables
#====================================================================================================

# Image search definitions
date_start = '20160430'     # Starting date '20160606', '20160430' 
date_end = '20160502'       # End date      '20160608', '20160502' 
cloudMax = 100              # Maximum cloud cover [%]
tileID = '31UFT'         # Tile ID (For now, later I can loop through all 4 tiles (with 4 seperate 
                            # queries to download all NL data, or make only data from 6 december 2016 available.) 

# Directory allocation
dir_out = "C:/S2_Data/test/"          # Directory where images are to be downloaded to
val_loc_file = './Data/Validation/Raam/data/metadata/Raam_station_locations_WGS84.csv'      # Location of validation data

# SciHub API info
login_sh='boonalds'
password_sh='123abc987zyx'
sh_api_url = 'https://scihub.copernicus.eu/dhus'

# Parameters for transforming the old structure to SAFE
MAIN_URL = 'http://sentinel-s2-l1c.s3-website.eu-central-1.amazonaws.com/'



#====================================================================================================
# Function definitions
#====================================================================================================

# To create folders (if they do not exists already)
def make_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)

# To download files from url to selected locations (filenames)
def f_download(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)

# To edit names, by changing the 3rd code and optionally the 4th and/or deleting the last as well
def edit_name(name, code, add_code=None, delete_end=False):
    info = name.split('_')
    info[2] = code
    if add_code is not None:
        info[3] = add_code
    if delete_end:
        info.pop()
    return '_'.join(info)


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
# print(products_df)

# Start the downloading loop
#print("    ....:::: DOWNLOADING IMAGES ::::....")
for i in range(0,len(products_df)): # 
    print("Download of image " + str(i+1) + "/" + str(len(products_df)) + " started..")
    ts = products_df['beginposition'].iloc[i]
    i_name = products_df['title'].iloc[i]
    if ts >= datetime(2016, 12, 6):
        q = 1
        # download_safe_format(i_name,folder=dir_out)
    elif ts < datetime(2016, 12, 6):
        # Main urls to download from:
        url_prod = MAIN_URL+'#products/'+ts.strftime('%Y')+'/'+ts.strftime('%#m')+'/'+ts.strftime('%#d')+'/'+i_name+'/'
        url_tile = MAIN_URL+'#tiles/'+tileID[0]+'/'+tileID[1:2]+'/'+ts.strftime('%Y')+'/'+ts.strftime('%#m')+'/'+ts.strftime('%#d')+'/0/'
        
        ### Create and fill directories:
        # Main folder
        main = dir_out+i_name
        make_folder(main)

        ddd=url_prod+'preview.png'
        fff=main+'/'+edit_name(i_name, 'BWI')+'.png'



        #urllib.request.urlretrieve(ddd,fff)
        
        
        # f_download(url_prod+'metadata.xml',main+'/'+edit_name(i_name, 'MTD','SAFL1C')+'.xml')
        # f_download(url_prod+'inspire.xml',main+'/INSPIRE.xml')
        # f_download(url_prod+'manifest.safe',main+'/manifest.safe')
        # f_download(url_prod+'preview.png',main+'/'+edit_name(i_name, 'BWI')+'.png')
        
        
        # sf = get_safe_format(tile=(tileID, ts.strftime('%Y-%m-%d')), entire_product=False)
        # print(sf.keys())
    else:
        print("Incompatible Begin Position Date")

#print("All downloads completed.")


#====================================================================================================
# Process the images: L1C -> L2A
#====================================================================================================

#print("Starting Sen2Cor processing.")


