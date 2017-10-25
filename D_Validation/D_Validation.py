'''
This script is for validation of the SM indicator used. Validation data used for this was
obtained by Benninga et al (2017) and is available at http://dx.doi.org/10.4121/uuid:2411bbb8-2161-4f31-985f-7b65b8448bc9
'''

import pandas as pd
df = pd.read_csv('Test.csv', sep=',')

for i in range(29):
    print(df)
    print(i)


import sys  
from math import sin, cos, radians 

for i in range(360):        
    print(cos(radians(i))
