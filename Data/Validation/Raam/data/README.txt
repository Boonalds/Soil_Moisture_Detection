version of readme:        24-april-2017
############################################################################################################
This dataset has two directories:
- station_data:         contains the soil moisture and temperature data of all stations, stored in csv.
- metadata:             contains the metadata

############################################################################################################
directory station_data
############################################################################################################
The data columns in the csv-files should be interpreted as:
1.	Measurement time [day-month-year hour:minute:second]
2.	Volumetric water content in [m^3 m^-3] at 5 cm depth
3.	Temperature in [degrees Celcius] at 5 cm depth
4.	Volumetric water content in [m^3 m^-3] at 10 cm depth
5.	Temperature in [degrees Celcius] at 10 cm depth
6.	Volumetric water content in [m^3 m^-3] at 20 cm depth
7.	Temperature in [degrees Celcius] at 20 cm depth
8.	Volumetric water content in [m^3 m^-3] at 40 cm depth
9.	Temperature in [degrees Celcius] at 40 cm depth
10.	Volumetric water content in [m^3 m^-3] at 80 cm depth
11.	Temperature in [degrees Celcius] at 80 cm depth

The data is measured using Decagon 5TM capacitance sensors. The description of the sensors, the translation
from the raw sensor measurements and the calibration is described in detail in Benninga et al.(2016). 
DOI: AANVULLEN INDIEN BESCHIKBAAR!
############################################################################################################
directory metadata
############################################################################################################
additional_datasets.txt:            contains a description of and a link to other useful datasets

Locations_Raam_SM_network.kmz:      contains the locations of the stations

Raam_station_locations_WGS84.csv:   containts the locations of the stations in the WGS84 coordinate system
    - station_ID:   station number
    - x:            longitude
    - y:            latitude
    
############################################################################################################
Data availability
############################################################################################################
The Raam network has generated data since April 2016. After 12 months of operation, 95% of the
measurements are available. Some data gaps are caused by thirteen probes, which were not properly
connected for a period. The 10 cm depth sensor of RM_SM_12 broke down in the summer of 2016. The 5
cm depth sensor at RM_SM_06 was exposed to open air between October 2016 and January 2017.
The measurements in this period are removed from the dataset. 
