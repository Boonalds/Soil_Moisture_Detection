'''
The purpose of this script is to test certain parts or function. This script will not be part of any end-product, hence the lack of documentation. 
'''
from sentinelhub import download_safe_format, get_safe_format

nonsafe = "C:\S2_Data\S2A_OPER_MSI_L1C_TL_SGS__20160501T144220_A004481_T31UFT_N02.01"

r = get_safe_format(nonsafe)