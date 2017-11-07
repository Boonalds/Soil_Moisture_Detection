# theia_download

This is a simple piece of code to automatically download the products provided by Theia land data center : https://theia.cnes.fr. It can download the products delivered by Theia, such as the [Sentinel-2 L2A products] (http://www.cesbio.ups-tlse.fr/multitemp/?page_id=6041), [Landsat L2A products](http://www.cesbio.ups-tlse.fr/multitemp/?page_id=3487) and the [SpotWorldHeritage L1C products](https://www.theia-land.fr/en/projects/spot-world-heritage).

This code was written thanks to the precious help of one my colleague at CNES [Jérôme Gasperi](https://www.linkedin.com/pulse/rocket-earth-your-pocket-gasperi-jerome) who developped the "rocket" interface which is used by Theia, and the mechanism to get a token. It was then adapted by Dominique Clesse for the new Muscate interface to download Sentinel-2 products.

This code relies on python 2.7 and on the curl utility. *Installing curl is therefore a prerequisite*. It has been developped and tested on Linux. It might work on windows, but I cannot test it. To use the code, you need to have an account and a password [at theia](http://theia.cnes.fr/atdistrib), and you need to add it to the config file as explaned in the authentification paragraph.

## Examples for various sensors
If you have an account at theia, you may download products using command lines like 

- `python ./theia_download.py -l 'Toulouse' -c SENTINEL2 -a config_theia.cfg -d 2016-09-01 -f 2016-10-01`

 which downloads the SENTINEL-2 products above Toulouse, acquired in September 2016.
 
 - `python ./theia_download.py -l 'Toulouse' -c SENTINEL2 -a config_theia.cfg -d 2016-09-01 -f 2016-10-01 -m  50`

 which downloads the SENTINEL-2 products above Toulouse, acquired in September 2016 with less tha 50% cloud cover

- `python ./theia_download.py -l 'Toulouse' -c Landsat -a config_landsat.cfg -d 2016-09-01 -f 2016-10-01`

 which downloads the LANDSAT-8 products above Toulouse, acquired in September 2016.

- `python ./theia_download.py -l 'Toulouse' -c SpotWorldHeritage -a config_landsat.cfg -d 2006-01-01 -f 2007-01-01`

 which downloads the SPOT World Heritage products above Toulouse, acquired in 2006.

 - `python ./theia_download.py -l 'Foix' -c Snow -a config_theia.cfg -d 2016-11-01 -f 2016-12-01`

 which downloads the Theia snow products above Foix (Pyrenees), acquired in November 2016. The collection option is case sensitive.

As you must have noted, there are two different config files, depending on the whether you are using SENTINEL2 data (config_theia.cfg) , or Landsat or Spot world Heritage data (config_landsat.cfg). This is temporary, due to the start of MUSCATE ground segment, and soon, all the products will accessed with the config_theia.cfg authentification.

## Other options

- `python ./theia_download.py -t T31TCJ -c SENTINEL2 -a config_theia.cfg -d 2016-09-01 -f 2016-10-01`

 which downloads the SENTINEL-2 products above tile T31TCJ, acquired in September 2016. 

- `python ./theia_download.py --lon 1 --lat 43.5 -c Landsat -a config_landsat.cfg -d 2015-11-01 -f 2015-12-01`

 which downloads the LANDSAT 8 products above --lon 1 --lat 43.5 (~Toulouse), acquired in November 2015.

- `python ./theia_download.py --lonmin 1 --lonmax 2 --latmin 43 --latmax 44 -c Landsat -a config_landsat.cfg -d 2015-11-01 -f 2015-12-01`

 which downloads the LANDSAT 8 products in latitude, longitude box around Toulouse, acquired in November 2015.

- `python theia_download.py -l 'Toulouse' -a config_landsat.cfg -c SpotWorldHeritage -p SPOT4 -d 2005-11-01 -f 2006-12-01`
 which downloads the SpotWorldHeritage products acquired by SPOT5 in 2005-2006

##Authentification 

The config file  config_landsat.cfg or  config_landsat.cfg  must contain your email address and your password as in the examples provided.

If you need to go through a proxy, and if you have not configured your proxy variable (`export http_proxy=http://moi:secret@proxy.mycompany.fr:8050`), you may also use one of the files like config_theia_proxy.cfg or config_landsat_proxy.cfg and add your passwords in them.

The program first fetches a token using your email address and password, and then uses it to download the products. As the token is only valid for two hours, it is advised to request only a reasonable number of products. It is necessary to make a first download from the site manually in order to validate your accound and the licence in the case of SpotWorldHeritage.

