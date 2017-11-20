'''
Script for the actual calculation of the Soil Moisture, using the downloaded and preprocessed data
obtained with Data_Download_and_PP.py

### Information/notes
# - Python version 3.6


### Assumptions 

### (Potential) To-Do's:
# - Automated parameterization
# - 
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
# Indicators needed for the SM calculation
INDICATORS = ["NDVI", "STR"]

NODATA_VALUE = 0                            # Value given to masked out pixels


# Directory and file allocations
img_dir="C:/S2_Download/Processed/"  # Map where all images are downloaded to
img=img_dir+"SENTINEL2A_20160508-104027-456_L2A_T31UFT_D.tif"
outdir="C:/S2_Download/test/"
# Cloudless images:     SENTINEL2A_20161227-105527-361_L2A_T31UFT_D.tif
#                       SENTINEL2A_20160508-104027-456_L2A_T31UFT_D.tif
#                       SENTINEL2A_20160720-105547-946_L2A_T31UFT_D.tif        

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
    out = np.zeros(shape=(len(INDICATORS),red.shape[0],red.shape[1]), dtype=rasterio.float64)   # create empty stack
    out[0,...] = (NIR.astype(float)-red.astype(float))/(NIR.astype(float)+red.astype(float))    # band 1: NDVI
    out[1,...] = np.power((1-SWIR.astype(float)),2)/(2*SWIR.astype(float))                      # band 2: STR
    
    # Masking out outliers (water bodies and shadows mostly)
    out[:,out[0,:,:] < 0] = NODATA_VALUE       # NDVI < 0
    out[:,out[1,:,:] < 0] = NODATA_VALUE       # STR < 0
    out[:,out[0,:,:] > 2] = NODATA_VALUE     # NDVI > 1.2
    out[:,out[1,:,:] > 40] = NODATA_VALUE      # STR > 25

    # Create meta-data for the output GeoTIFF
    out_meta = src.meta.copy()
    out_meta.update({"count":len(INDICATORS),
                    "dtype": rasterio.float64})


    #====================
    # Resample to 120m   
    #====================
    out120 = np.empty(shape=(out.shape[0],  # same number of bands
                         round(out.shape[1] / 12), # 12 times lower resolution
                         round(out.shape[2] / 12)))

    # adjust the new affine transform to the 150% smaller cell size
    aff = src.transform
    newaff = rasterio.Affine(aff.a / 1.5, aff.b, aff.c,
                    aff.d, aff.e / 1.5, aff.f)

    reproject(out, out120,
        src_transform = aff,
        dst_transform = newaff,
        src_crs = src.crs,
        dst_crs = src.crs,
        resampling = Resampling.bilinear)

    #====================
    # Plot Scatter plot  
    #====================
    plt.scatter(out[0,:,:], out[1,:,:], s=0.3,c="r")
    plt.scatter(out120[0,:,:], out120[1,:,:], s=0.3, c="yellow")
    plt.show()



    
    # Write the GeoTIFF
    #with rasterio.open(outdir+"Indicators.tif", "w",**out_meta) as dest:
    #   dest.write(out)






