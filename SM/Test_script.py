import numpy as np
import os, os.path, optparse,sys
import scipy.stats

def rmse(trueVal, predVal):
    """Function that calculates the Root Mean Square Error, which is an indicator for the prediction error"""
    if len(trueVal) == len(predVal):
        RMSE = (np.nanmean((np.array(trueVal) - np.array(predVal))**2))**0.5
    else:
        print("ERROR: number of predicted and measured values must be equal; \n       n(predicted):"+str(len(predVal))+"\n       n(measured):"+str(len(trueVal)))
        sys.exit(-1)
    return RMSE



def calc_r2(trueVal,predVal):
    """Function that calculates the R^2 value, indicating the proportion of the variation that is explained by the predicted values"""
    if len(trueVal) == len(predVal):
        SSR = np.nansum((np.array(trueVal) - np.array(predVal))**2)
        SST = np.nansum((trueVal - np.nanmean(trueVal))**2)
        r2 = 1-(SSR/SST)
    else:
        print("ERROR: number of predicted and measured values must be equal; \n       n(predicted):"+str(len(predVal))+"\n       n(measured):"+str(len(trueVal)))
        sys.exit(-1)
    return r2




## Data:
trueVal = [0.29,0.35,0.54,0.27,0.94]
predVal= [0.31,0.33,0.51,0.27,0.97]

trueVal = [[0.29,0.35,0.54,0.27,0.94],[0.13,0.56,0.76,0.87,0.54]]
predVal = [[0.31,0.33,0.51,0.27,0.97],[0.11,0.54,0.76,0.88,0.57]]


true_1D = [0.29,0.35,0.54,0.27,0.94]
pred_1D= [0.31,0.33,0.51,0.27,0.97]

true_2D = [[0.29,0.35,0.54,0.27,0.94],[0.13,0.56,0.76,0.87,0.54]]
pred_2D = [[0.31,0.33,0.51,0.27,0.97],[0.11,0.54,0.76,0.88,0.77]]

### Test
#rmse1d = calc_r2(true_1D,pred_1D)
rmse2d = calc_r2(true_2D,pred_2D)
#print(rmse1d)
print(rmse2d)

test = rsquared(np.array(true_2D), np.array(pred_2D))

print(test)