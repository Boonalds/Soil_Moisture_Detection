"""
Script for  downloading the required Sentinel-2 Data from the SciHub API. The Sentinelsat package
is used for this: http://sentinelsat.readthedocs.io/en/stable/. This script successfully downloads the images
at Level-1A processing level from the Amazon AWS Archive, at granule size.
"""

### Import libraries
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from sentinelhub import download_safe_format
from geojson import Polygon
from datetime import datetime
import csv
import sys
import numpy as np
import snappy

### Define area of interest, which is to  be downloaded
# based on validation data
val_loc_file = './Data/Validation/Raam/data/metadata/Raam_station_locations_WGS84.csv'
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



### Download Images:
# Connect to the SciHub API
api = SentinelAPI('boonalds', '123abc987zyx', 'https://scihub.copernicus.eu/dhus')

# Search database for all available images
products = api.query(footprint,
                     area_relation='Contains',
                     date = ('20161215', '20170115'),
                     platformname='Sentinel-2',
                     cloudcoverpercentage=(0, 100))


# Convert search results to Pandas DataFrame
products_df = api.to_dataframe(products)

# Download the tile for each image, download images with new naming convention from Amazon AWS
tile_name = '31UFT'   # For now, later I can loop through all 4 tiles (with 4 seperate queries to download all NL data, or make only data from 6 december 2016 available.) 

print("    ....:::: DOWNLOADING IMAGES ::::....")
for i in range(0,1): # len(products_df)
    # print("Download of image " + str(i+1) + "/" + str(len(products_df)) + " started..")
    ts = products_df['ingestiondate'].iloc[i]
    i_name = products_df['title'].iloc[i]
    if ts >= datetime(2016, 12, 6):
        print(i_name)
        # download_safe_format(i_name)
    elif ts < datetime(2016, 12, 6):
        print(i_name)
        # download_safe_format(tile=(tile_name, ts.strftime('%Y-%m-%d')))
    else:
        print("Incompatible Ingestion Date")


print("All downloads completed.")



