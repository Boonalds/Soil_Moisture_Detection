#====================================================================================================
# Import libraries and modules
#====================================================================================================
from osgeo import gdal, osr, gdalconst
import numpy as np
import json
import geojson
import os
import io
import rasterio
from rasterio.mask import mask
import pyproj
from pyproj import Proj



#====================================================================================================
# Define variables and directory allocations
#====================================================================================================
# Directory and file allocations
write_dir="C:/S2_Download/"  # Map where all images are downloaded to
out_dir='C:/S2_Download/Processed/' # Map where cropped geotiff is stored to
out_dir_raw="C:/S2_Download/raw/"
prod='SENTINEL2A_20160411-105025-461_L2A_T31UFT_D' # SENTINEL2A_20160411-105025-461_L2A_T31UFT_D
valArea = 'C:/Users/r.maas/Source/Repos/Soil_Moisture_Detection/Data/Validation/Raam/Validation_area_Raam.json'    # Geojson file that defines validation area

# Other lists
BANDS = ['SRE_B2', 'SRE_B3', 'SRE_B4']    # Requires a band with lowest resolution first (10m)
cld_mask = 'CLM_R1'                        # Name of the cloudmask to be used (R1 = 10m), using geophysical mask

# Variables
NODATA_VALUE = 0


#====================================================================================================
# Defining functions that are to be used in this script
#====================================================================================================

# To resample the resolution of the input geotiff to the resolution of the reference geotiff,
# and storing the newly created raster as the outputfile.
def resample_gtiff(inputfile, referencefile, outputfile):
    input = gdal.Open(inputfile, gdalconst.GA_ReadOnly)
    inputProj = input.GetProjection()
    inputTrans = input.GetGeoTransform()

    reference = gdal.Open(referencefile, gdalconst.GA_ReadOnly)
    referenceProj = reference.GetProjection()
    referenceTrans = reference.GetGeoTransform()
    bandreference = reference.GetRasterBand(1)    
    x = reference.RasterXSize 
    y = reference.RasterYSize

    driver= gdal.GetDriverByName('GTiff')
    output = driver.Create(outputfile,x,y,1,bandreference.DataType)
    output.SetGeoTransform(referenceTrans)
    output.SetProjection(referenceProj)

    gdal.ReprojectImage(input,output,inputProj,referenceProj,gdalconst.GRA_NearestNeighbour)

    del output


#====================================================================================================
# Initialization
#====================================================================================================
BANDS[len(BANDS):] = [cld_mask]            # Addding 10m cloudmask to the list of bands 

# Loading the GeoJSON file that determines the crop area (created in validation script) and project it to UTM 31
with open(valArea) as json_file:
    geoms = geojson.load(json_file)

# Reprojection the coordinates    
wgs84 = Proj(init = 'epsg:4326')
wgs84utm31 = Proj(init = 'epsg:32631')

for coords in geoms[0]['coordinates']:
    for coordPair in coords:
        x1 = coordPair[0]
        y1 = coordPair[1]
        coordPair[0],coordPair[1] = pyproj.transform(wgs84,wgs84utm31,x1, y1)



#==============================================
# Cropping and Resampling
#==============================================
# opening the bands 1 by 1 and cropping them according to the geojson provided in the initialization

for i in range(len(BANDS)):
    # Assigning filename to be handled
    if BANDS[i] == cld_mask:
        band_fn=write_dir+prod+'_V1-4/MASKS/'+prod+'_V1-4_'+BANDS[i]+'.tif'
    else:
        band_fn=write_dir+prod+'_V1-4/'+prod+'_V1-4_'+BANDS[i]+'.tif'

    
    with rasterio.open(band_fn) as src:

        if i==0:
        # On first loop the output tiff is initialized (by creating empty array)
        # Also the meta data of the original GeoTIFF is copied and updated where needed to match output GeoTIFF
            # Crop the image
            out_image, out_transform = mask(src, geoms, crop=True)

            MOutput = np.zeros(shape=(len(BANDS),out_image.shape[1],out_image.shape[2]), dtype='int16')    
            out_meta = src.meta.copy()
            out_meta.update({"driver": "GTiff",
                "count":len(BANDS)-1,           # removing cloudmask before writing, so -1
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform,
                "nodata": NODATA_VALUE})

            # Copy the masked image to new  band
            MOutput[i,...]=out_image
            
            # Store pixel count and filename for resample necessity check and potentially the resampling
            init_height=src.shape[1] 
            init_band_fn= band_fn
        else:
            # Check if resampling is needed to match desired output resolution:
            res_f = int(init_height/src.shape[1])  # Resample factor: ration between band and output pixelcounts
            if res_f is not 1:
                resample_gtiff(band_fn,init_band_fn,'tmp.tif')
                with rasterio.open('tmp.tif') as src:
                    # Crop the image & store it in the merged outputfile
                    out_image, out_transform = mask(src, geoms, crop=True)
                    MOutput[i,...]=out_image
            else:
                # Crop the image without resampling
                out_image, out_transform = mask(src, geoms, crop=True)
                MOutput[i,...]=out_image


#==============================================
# Cloud Masking
#==============================================
# Write nodata value (defined at start) in bands where the last band is not 0
MOutput[0:-1,MOutput[-1,:,:] != 0] = NODATA_VALUE

# remove band 4
MOutput = MOutput[:-1,:,:]

#==============================================
# Writing file to disk
#==============================================
with rasterio.open(out_dir+prod+".tif", "w",**out_meta) as dest:
    dest.write(MOutput)
