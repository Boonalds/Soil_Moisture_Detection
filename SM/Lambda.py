"""
Script for automated downloading, preprocessing and processing of Sentinel-2 data.
It constructs SM maps, using the OPTRAM method.

"""



#====================================================================================================
# Import libraries and modules
#====================================================================================================
import os, os.path, optparse,sys
import osgeo
import io
import fnmatch
import numpy as np
import json
import shutil
import geojson
import zipfile
import time
import requests
import urllib
import rasterio
import pyproj

from osgeo import gdal, osr, gdalconst
from datetime import date
from rasterio.mask import mask
from pyproj import Proj

#====================================================================================================
# Define parameters, variables, and allocate directories
#====================================================================================================
# OPTRAM Parameters
i_d=0       # initial value, dry edge   %0-0
s_d=2.5     # slope, dry edge   %2.5-1.5
i_w=4       # initial value, wet edge  %4-2
s_w=13.5    # slope, wet edge   %18.5-12


# Data search parameters
tile='T31UFT'
start_date="2016-04-05"
end_date='2016-05-05'
s_platform="SENTINEL2A"     # SENTINEL2B
maxcloud=101                # Maximum cloudcover allowed, in percentages

# Other user parameters
REMOVE_ZIP = True                           # Remove downloaded .zip files after extracting the required bands
REMOVE_TILE = False                         # Remove the tile data after cropping
NODATA_VALUE = 0                            # Value given to masked out pixels

# Spectral Band Specifications
BANDS = ['SRE_B2', 'SRE_B3', 'SRE_B4']      # Requires a band with lowest resolution first (10m)
cld_mask = 'CLM_R1'                         # Name of the cloudmask to be used (R1 = 10m), using geophysical mask
VERSION = 'V1-4'                            # Version, based on Theia processing software

# Theia download information
server = "https://theia.cnes.fr/atdistrib"
token_ext = '/services/authenticate/>token.json'
resto = "resto2"
collection = "SENTINEL2"
curl_proxy = ""
token_type = "text"
login_theia = "robmaas77@hotmail.com"
password_theia = "abc123ZYX(*&"

# Directory and file allocations
write_dir="D:/S2_Download/"  # Map where all images are downloaded to
proc_dir=write_dir+'Processed/' # Map where processed geotiff is stored to
SM_outdir='C:/S2_Download/SM_Maps/'     # Map where the created SM maps should be stored in.
out_dir_raw=write_dir+"Raw/"        # Map where unzipped images are stored

valArea = './Data/Validation/Raam/Validation_area_Raam.json'    # Geojson file that defines validation area


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
BANDS[len(BANDS):] = [cld_mask]            # Adding 10m cloudmask to the list of bands 

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

#====================================================================================================
# 1. Search catalogue
#====================================================================================================

# Remove any old queries
if os.path.exists('search.json'):
    os.remove('search.json')

# Fill dictionary with query options
query_geom='location=%s' % tile
dict_query={'location':tile}

dict_query['platform']=s_platform
dict_query['startDate']=start_date
dict_query['completionDate']=end_date
dict_query['maxRecords']=500

# Construct query
query="%s/%s/api/collections/%s/search.json?" % (server, resto, collection) + urllib.parse.urlencode(dict_query)

# Execute the search using curl
search_catalog= 'curl -k %s -o search.json "%s"' % (curl_proxy, query)
os.system(search_catalog)
time.sleep(5)




#====================================================================================================
# 3. Download the imagery 
#====================================================================================================
# Read out search results
with open('search.json') as data_file:    
    data = json.load(data_file)

# Starting the big processing loop
for i in range(len(data["features"])):
    # 2. Get a token using curl
    get_token='curl -k -s -X POST %s --data-urlencode "ident=%s" --data-urlencode "pass=%s" %s/services/authenticate/>token.json' % (curl_proxy, login_theia, password_theia, server)
    os.system(get_token)
    # Read out the token
    token=""
    with open('token.json') as data_file:
        try :
            if token_type=="json":
                token_json = json.load(data_file)
                token=token_json["access_token"]
            elif token_type=="text":
                token=data_file.readline()
            else:
                print("error with config file, unknown token_type: " + token_type)
                sys.exit(-1)
        except :
            print("Authentification is probably wrong")
            sys.exit(-1)
    os.remove('token.json')

    # Extract image information from search results
    prod=data["features"][i]["properties"]["productIdentifier"]
    feature_id=data["features"][i]["id"]

    cloudCover=int(data["features"][i]["properties"]["cloudCover"])
    print("(",i+1,"/",len(data["features"]),"): ",prod)
    print("cloudCover:",cloudCover)

    if write_dir==None :
        write_dir=os.getcwd()
    file_exists=os.path.exists("%s/%s_%s" % (proc_dir,prod,VERSION))
    # file_exists=os.path.exists("%s/%s.zip" % (write_dir,prod))
    tmpfile="%s%s.tmp" % (write_dir, prod)
    get_product='curl %s -o %s -k -H "Authorization: Bearer %s" %s/%s/collections/%s/%s/download/?issuerId=theia' % (curl_proxy, tmpfile, token, server, resto, collection, feature_id)

    if not(file_exists):
        if cloudCover <= maxcloud: # Download only if cloudCover below maxcloud
            # Check if file is already downloaded, but not yet processed:
            zip_exists=os.path.exists("%s%s.zip" % (write_dir, prod))
            
            if not(zip_exists):

                os.system(get_product)
                # Check if binary product
                with open(tmpfile) as f_tmp:
                    try:
                        tmp_data=json.load(f_tmp)
                        print("Result is a text file")
                        print(tmp_data)
                        sys.exit(-1)
                    except ValueError:
                        pass

                os.rename("%s" % (tmpfile),"%s%s.zip" % (write_dir,prod))
                print("Product saved as : %s%s.zip" % (write_dir,prod))
            else:
                print("%s already downloaded, but not yet processed, started processing:" % (prod))

            #==============================================
            # 4. Unzipping
            #==============================================
            print("Started unzipping..")
            zip_file=write_dir+prod+'.zip'

            with zipfile.ZipFile(zip_file,"r") as zip_ref:
                for extr_b in BANDS:
                    if extr_b == cld_mask:
                        zip_ref.extract(prod+'_'+VERSION+'/MASKS/'+prod+'_'+VERSION+'_'+extr_b+'.tif',out_dir_raw)
                    else:
                        zip_ref.extract(prod+'_'+VERSION+'/'+prod+'_'+VERSION+'_'+extr_b+'.tif',out_dir_raw)

            # Removing zip file if desired
            if REMOVE_ZIP == True:
                os.remove(zip_file)

            #==============================================
            # 5. Cropping and 6. Resampling
            #==============================================
            print("Started cropping/resampling/masking..")
            # opening the bands 1 by 1 and cropping them according to the geojson provided in the initialization
            for j in range(len(BANDS)):
            # Assigning filename to be handled
                if BANDS[j] == cld_mask:
                    band_fn=out_dir_raw+prod+'_'+VERSION+ '/MASKS/'+prod+'_'+VERSION+'_'+BANDS[j]+'.tif'
                else:
                    band_fn=out_dir_raw+prod+'_'+VERSION+'/'+prod+'_'+VERSION+'_'+BANDS[j]+'.tif'

                with rasterio.open(band_fn) as src:
                    if j==0:
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
                        MOutput[j,...]=out_image
            
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
                                MOutput[j,...]=out_image
                        else:
                            # Crop the image without resampling
                            out_image, out_transform = mask(src, geoms, crop=True)
                            MOutput[j,...]=out_image
            
            #==============================================
            # 7. Cloud Masking
            #==============================================
            # Write nodata value (defined at start) in bands where the last band is not 0
            MOutput[0:-1,MOutput[-1,:,:] != 0] = NODATA_VALUE

            # Remove Cloudmask band
            MOutput = MOutput[:-1,:,:]

            #==============================================
            # 8. Writing file to disk
            #==============================================
            with rasterio.open(proc_dir+prod+".tif", "w",**out_meta) as dest:
                dest.write(MOutput)
                print("Successfully processed and stored %s on disk" % (prod))

            # Removing the tile images if desired
            if REMOVE_TILE == True:
                shutil.rmtree(out_dir_raw+prod+'_'+VERSION,ignore_errors=True)

            # End of loop, going back up for next image.


        else:
            print("Cloud cover too high : %s" % (cloudCover)) 
    elif file_exists:
        print("%s already downloaded and processed" % (prod))



## With masked out clouds (all images):
img_list = []
for file in os.listdir(proc_dir):
    if fnmatch.fnmatch(file, 'SENTINEL2A_201?????-??????-???_L2A_T31UFT_D.tif'):
        img_list.append(file)


for i in range(len(img_list)):
    img=proc_dir+img_list[i]
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


