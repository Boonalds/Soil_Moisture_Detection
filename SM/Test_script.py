'''
This script is pure for testing purposes and will be excluded from the end product.
'''

import matplotlib.pyplot as plt
import rasterio
from rasterio.plot import show
from rasterio.plot import show_hist

#==============
# Plot SM Map
#==============

src = rasterio.open('C:/S2_Download/SM_Maps/SM_20170215.tif')

ax = plt.subplot()
im = show(src)

fig.colorbar(im,ax=ax)

plt.show()