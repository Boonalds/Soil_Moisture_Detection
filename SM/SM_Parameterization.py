'''
Script for the actual calculation of the Soil Moisture, using the downloaded and preprocessed data
obtained with Data_Download_and_PP.py

### Information/notes
# - Python version 3.6


### Assumptions 

### (Potential) To-Do's:
# - Automated parameterization
# - 


### All downloaded images were manualy opened in Qgis to visually assess the amount of clouds/cloudsshadows (which were mostly masked out), so a list
        of good images for calibration and validation could be made:

# Cloudless images:
#           SENTINEL2A_20160411-105025-461_L2A_T31UFT_D.tif x
#           SENTINEL2A_20160508-104027-456_L2A_T31UFT_D.tif
#           SENTINEL2A_20160720-105547-946_L2A_T31UFT_D.tif
#           SENTINEL2A_20160826-104023-461_L2A_T31UFT_D.tif
#           SENTINEL2A_20160908-105416-359_L2A_T31UFT_D.tif
#           SENTINEL2A_20160915-104018-457_L2A_T31UFT_D.tif
#           SENTINEL2A_20160925-104115-186_L2A_T31UFT_D.tif
#           SENTINEL2A_20161204-104538-833_L2A_T31UFT_D.tif
#           SENTINEL2A_20161227-105527-361_L2A_T31UFT_D.tif
#           SENTINEL2A_20170215-105607-471_L2A_T31UFT_D.tif
#           SENTINEL2A_20170327-105021-460_L2A_T31UFT_D.tif

# Maybe images (~20% clouds):
#           SENTINEL2A_20160607-104026-455_L2A_T31UFT_D.tif  <- used
#           SENTINEL2A_20170126-105612-238_L2A_T31UFT_D.tif  <- used   
#           SENTINEL2A_20170324-104016-456_L2A_T31UFT_D.tif  <- not used, close to 20170327, so not needed
'''

#====================================================================================================
# Import libraries and modules
#====================================================================================================
import os, os.path, optparse,sys
from osgeo import gdal, osr, gdalconst
import io
import rasterio
import numpy as np

from rasterio import Affine
from rasterio.warp import reproject, Resampling

import matplotlib.pyplot as plt



#====================================================================================================
# Define parameters, variables, and allocate directories
#====================================================================================================
NODATA_VALUE = 0                            # Value given to masked out pixels
RESAMPLE_RES = 120                          # Resample resolution (in m) 

# Directory and file allocations
img_dir="C:/S2_Download/Processed/"  # Map where all images are downloaded to
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


#=========
# INIT
#=========
rf = RESAMPLE_RES/10  # resample factor

#=======================================
# Loop to process all suited images
#=======================================

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

        # Calculate the indicators
        out10 = np.zeros(shape=(2,red.shape[0],red.shape[1]), dtype=rasterio.float64)                   # create empty stack
        out10[0,...] = (NIR.astype(float)-red.astype(float))/(NIR.astype(float)+red.astype(float))      # band 1: NDVI
        out10[1,...] = np.power((1-SWIR.astype(float)),2)/(2*SWIR.astype(float))                        # band 2: STR
    
        # Masking out outliers (water bodies and shadows mostly)
        out10[:,out10[0,:,:] < 0] = NODATA_VALUE        # NDVI < 0
        out10[:,out10[1,:,:] < 0] = NODATA_VALUE        # STR < 0
        out10[:,out10[0,:,:] > 2] = NODATA_VALUE        # NDVI > 2
        out10[:,out10[1,:,:] > 40] = NODATA_VALUE       # STR > 40

        #=====================================
        # Resample to defined resolution 
        #=====================================
        outRES = np.empty(shape=(out10.shape[0], round(out10.shape[1] / rf), round(out10.shape[2] / rf)))

        # adjust the new affine transform to the 12 times larger cell size
        aff = src.transform
        newaff = rasterio.Affine(aff.a * rf, aff.b, aff.c,
                        aff.d, aff.e * rf, aff.f)
        # resample using the gdal-based reproject function from rasterio
        reproject(out10, outRES,
            src_transform = aff,
            dst_transform = newaff,
            src_crs = src.crs,
            dst_crs = src.crs,
            resampling = Resampling.bilinear)
        
        #===================================
        # Store the indicator values
        #===================================
        if i==0:
            # Initialization:   Create empty arrays to store NDVI and STR data in
            NDVI10 = np.empty(shape=(len(img_list),out10.shape[1],out10.shape[2]),dtype=rasterio.float64)
            STR10 = np.empty(shape=(len(img_list),out10.shape[1],out10.shape[2]),dtype=rasterio.float64)
            NDVIres = np.empty(shape=(len(img_list),outRES.shape[1],outRES.shape[2]),dtype=rasterio.float64)
            STRres = np.empty(shape=(len(img_list),outRES.shape[1],outRES.shape[2]),dtype=rasterio.float64)

        NDVI10[i,...] = out10[0,:,:]
        STR10[i,...] = out10[1,:,:]
        NDVIres[i,...] = outRES[0,:,:]
        STRres[i,...] = outRES[1,:,:]

#====================
# Plot Scatter plot  
#====================
plt.scatter(NDVI10[:,:,:], STR10[:,:,:], s=0.1,c="r")
plt.scatter(NDVIres[:,:,:], STRres[:,:,:], s=0.1, c="yellow")
plt.xlabel('NDVI')
plt.ylabel('STR')
plt.show()

