"""
Script for  downloading the required Sentinel-2 Data from the SciHub API. The Sentinelsat package
is used for this: http://sentinelsat.readthedocs.io/en/stable/
"""

### Import libraries
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from geojson import Polygon
import csv
import numpy as np

### Connect to the API
api = SentinelAPI('boonalds', '123abc987zyx', 'https://scihub.copernicus.eu/dhus')


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


### Download only 





### Download using Sentinelsat (full granules):
products = api.query(footprint,
                     date = ('20160505', '20160605'),
                     platformname='Sentinel-2',
                     cloudcoverpercentage=(0, 100))
# api.download_all(products)
