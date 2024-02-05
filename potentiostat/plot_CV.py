import numpy as np
from pathlib import Path
from matplotlib import pyplot as plt
import sys
import os



def filter_outlier(raw_array, outlier_filt: float = 2):
    # filter outliers of 2nd column of a 2D array
    mean = np.mean(raw_array[:,1])
    std = np.std(raw_array[:, 1])
    for i in range(0, raw_array.shape[0]):
        if (raw_array[i, 1] < mean - std * outlier_filt) or (raw_array[i, 1] > mean + std * outlier_filt):
            raw_array[i, :] = [np.nan, np.nan]
    return raw_array

def avg_vi(cv, block_size: int = 16, outlier_filt: float = 2):
    # calculate the block average to denoize the CV plot
    new_cv_len = cv.shape[0] // block_size
    new_cv = np.zeros((new_cv_len, 2))
    for i in range(0, new_cv_len):
        filtered_block = filter_outlier(cv[i * block_size : (i+1) * block_size, :], outlier_filt)
        avg_voltage = np.nanmean(filtered_block[:, 0])
        avg_current = np.nanmean(filtered_block[:, 1])
        new_cv[i] = [avg_voltage, avg_current]
    return new_cv

def slice_cv(cv_array, side_points: int = 7):
    """
    slice cv based on v_min and v_max
    :param cv_array:
    :param side_points:
    :return:
    """
    v_min_pos = []
    v_max_pos = []
    for i in range(side_points, cv_array.shape[0]-side_points):
        if (np.mean(cv_array[i-side_points:i, 0]) < cv_array[i, 0]) and (cv_array[i, 0] > np.mean(cv_array[i:i+side_points, 0])):
            v_max_pos.append(i)
        elif (np.mean(cv_array[i-side_points:i, 0]) > cv_array[i, 0]) and (cv_array[i, 0] < np.mean(cv_array[i:i+side_points, 0])):
            v_min_pos.append(i)
    return (v_min_pos, v_max_pos)


def compact_minmax(vals):
    """
    remove min-1, max+1, min-2, max+2, etc. and only yield min, max of list of mins and maxs
    :param vals:
    :return:
    """
    compact_val = []
    i = 0
    while i < len(vals) -1:
        index = [i]
        while vals[i+1] == vals[i] + 1:
            index.append(i+1)
            i += 1
            if i == len(vals)-1:
                break
        num_mid = len(index) // 2
        compact_val.append(vals[index[num_mid]])
        i += 1
    return compact_val


cv_raw = np.genfromtxt(sys.argv[1], delimiter=',')
cv_raw= cv_raw[:, 1:3]
cv_avg = avg_vi(cv_raw, 16, 1)
plt.scatter(cv_avg[:, 0], cv_avg[:, 1], s=1)
plt.xlim([-1.5, 0.5])
#plt.ylim([-4e-5, 4e-5])

name = os.path.splitext(os.path.basename(sys.argv[1]))[0]
plt.savefig(f"{name}.png")
