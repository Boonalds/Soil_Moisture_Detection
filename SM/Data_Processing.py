#====================================================================================================
# Import libraries and modules
#====================================================================================================
from osgeo import gdal, osr
import numpy as np
import json
import geojson
import os
import io
import rasterio
from rasterio.mask import mask
import pyproj
from pyproj import Proj
import matplotlib.pyplot as plt



#====================================================================================================
# Define variables and directory allocations
#====================================================================================================

write_dir="C:/S2_Download/"  # Map where all images are downloaded to
fn='SENTINEL2A_20160411-105025-461_L2A_T31UFT_D'
out_dir='C:/S2_Download/test/'

# Geojson file that defines validation area
valArea = './Data/Validation/Raam/Validation_area_Raam.json'
input_tiff=write_dir+fn+'/SENTINEL2A_20160411-105025-461_L2A_T31UFT_D_V1-4_SRE_B8A.tif'

# Other lists
BANDS = ['SRE_B2', 'SRE_B3', 'SRE_B12']    # Requires a band with lowest resolution first (10m)


#====================================================================================================
# Loading the GeoJSON file that determines the crop area and project it to UTM 31
#====================================================================================================

# Loading the polygon GeoJSON geometry of the study area (created in the validation script)
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

#====================================================================================================
# Opening the the bands 1 by 1, cropping out the study area and storing the data in a new geotiff
#====================================================================================================

for i in range(len(BANDS)):
    band_fn=write_dir+fn+'_V1-4/'+fn+'_V1-4_'+BANDS[i]+'.tif'
    with rasterio.open(band_fn) as src:
        if i==0:
        # On first loop the output tiff is initialized (by creating empty array)
        # Also the meta data of the original GeoTIFF is copied and updated where needed to match output GeoTIFF
            # Crop the image
            out_image, out_transform = mask(src, geoms, crop=True)

            MOutput = np.zeros(shape=(len(BANDS),out_image.shape[1],out_image.shape[2]), dtype='int16')    
            out_meta = src.meta.copy()
            out_meta.update({"driver": "GTiff",
                "count":len(BANDS),
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform})
            
            # Copy the masked image to new  band
            MOutput[i,...]=out_image
            
            # Store pixel count for resample necessity check
            or_height=src.shape[1] 
        else:
            # Check if resampling is needed to match desired output resolution:
            res_f = int(or_height/src.shape[1])  # Resample factor: ration between band and output pixelcounts
            if res_f is not 1:
                src_res = np.empty(shape=(1,round(src.shape[0] * res_f), round(src.shape[1] * res_f)),dtype='int16')
                src.read(out=src_res)  # Decimated reading (basically nearest neighbor to adjust the resolution)
                src_res=np.squeeze(src_res) # Remove single-dimensional entry to match 2D format

                with rasterio.open('tmp.tif', 'w', driver='GTiff',
                            height=src.shape[0], width=src.shape[1],
                            count=1, dtype='int16',crs=src.crs, transform=out_meta['transform']) as dest:
                    dest.write(src_res,1)
                with rasterio.open('tmp.tif') as src:
                    # Crop the image & store it in the merged outputfile
                    out_image, out_transform = mask(src, geoms, crop=True)
                    MOutput[i,...]=out_image
            else:
                # Crop the image
                out_image, out_transform = mask(src, geoms, crop=True)
                MOutput[i,...]=out_image


# Copy the masked image to new  band


# Store on harddrive
with rasterio.open("masked.tif", "w",**out_meta) as dest:
    dest.write(MOutput)

with rasterio.open('masked.tif') as chk:
    print(chk.count)
    print(chk.crs)




### 
# In any case, the data are coded on 16bits and you have to divide by 10000 to obtain reflectances.
