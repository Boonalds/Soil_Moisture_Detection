
import shutil

shutil.rmtree('C:/S2_Download/tttest')


#import zipfile

## VARS
#prod='SENTINEL2A_20160428-104500-651_L2A_T31UFT_D'
#write_dir="C:/S2_Download/"  # Map where all images are downloaded to
#zip_tardir = 'C:/S2_Download/'
#zip_file = write_dir+prod+'.zip'
#BANDS = ['SRE_B2', 'SRE_B3', 'SRE_B4']    # Requires a band with lowest resolution first (10m)
#VERSION = 'V1-4'
#cld_mask = 'CLM_R1'           


## INIT
#BANDS[len(BANDS):] = [cld_mask]            # Addding 10m cloudmask to the list of bands 


## LOOP

#with zipfile.ZipFile(zip_file,"r") as zip_ref:
#    for extr_b in BANDS:
#        if extr_b == cld_mask:
#            zip_ref.extract(prod+'_'+VERSION+'/MASKS/'+prod+'_'+VERSION+'_'+extr_b+'.tif',zip_tardir)
#        else:
#            zip_ref.extract(prod+'_'+VERSION+'/'+prod+'_'+VERSION+'_'+extr_b+'.tif',zip_tardir)

       
