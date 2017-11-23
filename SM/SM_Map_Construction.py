"""
This script calculates the soil moisture using the OPTRAM method. The parameters for this method are derrived in
the SM_Parameterization script.

### Information/notes
# - Python version 3.6

### (Potential) To-Do's:
# - 
# - 

"""



#====================================================================================================
# Import libraries and modules
#====================================================================================================
import os, os.path, optparse,sys
from osgeo import gdal, osr, gdalconst
import io
import rasterio
import numpy as np
import matplotlib.pyplot as plt


#====================================================================================================
# Define parameters, variables, and allocate directories
#====================================================================================================
# OPTRAM Parameters
i_d=0       # initial value, dry edge
s_d=2.5     # slope, dry edge
i_w=4       # initial value, wet edge
s_w=18.5    # slope, wet edge


# Directory and file allocations
SM_outdir='C:/S2_Download/SM_Maps/'     # Map where the created SM maps should be stored in.
img_dir="C:/S2_Download/Processed/"     # Map where all input images are stored.

img_list=["SENTINEL2A_20160508-104027-456_L2A_T31UFT_D.tif",
          "SENTINEL2A_20160607-104026-455_L2A_T31UFT_D.tif",
          "SENTINEL2A_20160720-105547-946_L2A_T31UFT_D.tif",
          "SENTINEL2A_20160826-104023-461_L2A_T31UFT_D.tif",
          "SENTINEL2A_20160908-105416-359_L2A_T31UFT_D.tif",
          "SENTINEL2A_20160915-104018-457_L2A_T31UFT_D.tif",
          "SENTINEL2A_20160925-104115-186_L2A_T31UFT_D.tif",
          "SENTINEL2A_20161204-104538-833_L2A_T31UFT_D.tif",
          "SENTINEL2A_20161227-105527-361_L2A_T31UFT_D.tif",
          "SENTINEL2A_20170126-105612-238_L2A_T31UFT_D.tif",
          "SENTINEL2A_20170215-105607-471_L2A_T31UFT_D.tif",
          "SENTINEL2A_20170327-105021-460_L2A_T31UFT_D.tif"]

for i in range(len(img_list)):
    img=img_dir+img_list[i]
    with rasterio.open(img) as src:
        # Read the data from the GeoTIFF
        red=src.read(1, masked=True)
        NIR=src.read(2, masked=True)
        SWIR=src.read(3, masked=True)
        
        # Transform to reflectance:
        red = red/10000
        NIR = NIR/10000
        SWIR = SWIR/10000

        # Calculate indicators
        ndvi_tmp = (NIR.astype(float)-red.astype(float))/(NIR.astype(float)+red.astype(float))      # NDVI
        str_tmp = np.power((1-SWIR.astype(float)),2)/(2*SWIR.astype(float))                         # STR
        SM_tmp = (i_d + s_d*ndvi_tmp - str_tmp)/(i_d - i_w + (s_d - s_w)*ndvi_tmp)                  # Soil Moisture W

        # adjust pixel values
        SM_tmp[SM_tmp>1] = 1        # Oversatured pixels are now shown as satured
        SM_tmp[SM_tmp<0] = 0        # Set pixels with negative moisture content to 0

        # Construct meta-data for storage
        out_meta = src.meta.copy()
        out_meta.update({"count":1,
                        "dtype":rasterio.float64})

        # Store as new GeoTIFF
        out_fn="SM_"+img_list[i][11:26]+".tif"      # Define filename
        with rasterio.open(SM_outdir+out_fn, "w",**out_meta) as dest:
            dest.write_band(1,SM_tmp)



