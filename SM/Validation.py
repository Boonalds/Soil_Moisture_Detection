"""
Script to download the required Sentinel-2 data, longer description later.
"""

### Import libraries
import matplotlib.pyplot as plt
import numpy as np
import csv
import os 

### Initialization
label_names = []
Val_SM_05cm = []
Val_SM_10cm = []

### Directory containing validation files
ValDir = './Data/Validation/Raam/data/station_data/'

### Read Validation data and store data and headings in different arrays
for file in os.listdir(ValDir):
    label_names = label_names + ["Field "+file[6:8]]
    with open(os.path.join(ValDir, file), newline='') as csvfile:
        r = csv.reader(csvfile, delimiter=',', quotechar='|')
        data = [i for i in r]
        del data[0]
        Val_SM_05cm = Val_SM_05cm + [np.array([np.float(i[1]) for i in data])]
        Val_SM_10cm = Val_SM_10cm + [np.array([np.float(i[3]) for i in data])]


### Soil Moisture Signals
plt.figure(1)

# 5cm depth
ax1 = plt.subplot(211)
for k in range(len(Val_SM_05cm)):
    ax1.plot(Val_SM_05cm[k], label=label_names[k])
ax1.legend()
plt.title('5 cm depth')
# 10cm depth
ax2 = plt.subplot(212)
for k in range(len(Val_SM_10cm)):
    ax2.plot(Val_SM_10cm[k], label=label_names[k])
ax2.legend()
plt.title('10 cm depth')

plt.show()



### Doc
# Original headers
# Measurement Time,5 cm VWC [m3/m3],5 cm Temp [oC],10 cm VWC [m3/m3],
#        10 cm Temp [oC],20 cm VWC [m3/m3],20 cm Temp [oC],40 cm VWC [m3/m3],
#        40 cm Temp [oC],80 cm VWC [m3/m3],80 cm Temp [oC]