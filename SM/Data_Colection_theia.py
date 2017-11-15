"""
Script to download sentinel-2 Level-2A products from the theia website.

### Information/notes
# - Python version 3.6
# - Now using curl, will need to use requests package later for AWS (should rewrite theia_download script)
# - 


"""



#====================================================================================================
# Import libraries and modules
#====================================================================================================
import time
import os, os.path, optparse,sys
from datetime import date
import json
import requests
import urllib



#====================================================================================================
# Define variables
#====================================================================================================
# Download data information
tile='T31UFT'
start_date="2016-04-05"
end_date='2016-05-05'
s_platform="SENTINEL2A"     # SENTINEL2B
maxcloud=101                # Maximum cloudcover allowed, in percentages

# Theia download information
server = "https://theia.cnes.fr/atdistrib"
token_ext = '/services/authenticate/>token.json'

resto = "resto2"
collection = "SENTINEL2"
curl_proxy = ""
token_type = "text"
login_theia = "robmaas77@hotmail.com"
password_theia = "abc123ZYX(*&"

# Directory allocation
write_dir="C:/S2_Download"  # Map where all images are downloaded to


#============================================================================================================================================
# Get a token to be allowed to bypass the authentification. 
#============================================================================================================================================

# Construct token query and request it using curl
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

# print(token)

#====================================================================================================
# Search catalogue
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
# Download the imagery
#====================================================================================================

with open('search.json') as data_file:    
    data = json.load(data_file)

for i in range(len(data["features"])):    
    prod=data["features"][i]["properties"]["productIdentifier"]
    feature_id=data["features"][i]["id"]

    cloudCover=int(data["features"][i]["properties"]["cloudCover"])
    print("(",i+1,"/",len(data["features"]),"): ",prod)
    print("cloudCover:",cloudCover)

    if write_dir==None :
        write_dir=os.getcwd()
    file_exists=os.path.exists("%s/%s.zip" % (write_dir,prod))
    tmpfile="%s/%s.tmp" % (write_dir, prod)
    get_product='curl %s -o %s -k -H "Authorization: Bearer %s" %s/%s/collections/%s/%s/download/?issuerId=theia' % (curl_proxy, tmpfile, token, server, resto, collection, feature_id)

    if not(file_exists):
        # Download only if cloudCover below maxcloud
        if cloudCover <= maxcloud:
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

            os.rename("%s" % (tmpfile),"%s/%s.zip" % (write_dir,prod))
            print("Product saved as : %s/%s.zip" % (write_dir,prod))
        else :
            print("Cloud cover too high : %s" % (cloudCover)) 
    elif file_exists:
        print("%s already exists" % (prod))


