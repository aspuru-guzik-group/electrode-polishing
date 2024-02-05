from pathlib import Path
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import sys
import os

def gaussian(x, A, mu, sigma, bkg):
    return bkg + A * np.exp(-(x - mu)**2 / (2 * sigma**2))

def fit_gauss(data):
    max_current_pos = np.argmax(data[:, 1])

    init_guess = [data[max_current_pos, 1] - data[0, 1], data[max_current_pos, 0], np.std(data[:, 0]), data[0, 1]]
    try:
        gau_opt, gau_cov = curve_fit(gaussian, data[:, 0], data[:, 1], p0=init_guess)
        return gau_opt
    except:
        return init_guess


def proc_dpv(data, decay_ms:int = 500, pulse_ms:int = 20, pulse_from_end: int = 4, decay_from_end: int =50):
    drop_pts = decay_ms + pulse_ms
    num_periods = data.shape[0] // drop_pts

    dpv = np.empty((num_periods, 6))
    for i in range (0, num_periods):
        decay_end_point = drop_pts * i + decay_ms
        drop_end_point = drop_pts * (i + 1)
        dpv_time = data[decay_end_point-1, 0]
        dpv_cycle = data[decay_end_point-1, 3]
        dpv_exp = data[decay_end_point-1, 4]
        dpv_v_apply = data[decay_end_point-1, 5]
        dpv_current = np.mean(data[decay_end_point-decay_from_end:decay_end_point-1, 2]) - \
        np.mean(data[drop_end_point-pulse_from_end:drop_end_point-1, 2])
        dpv_voltage = np.mean(data[decay_end_point-decay_from_end:decay_end_point-1, 1])
        dpv[i] = [dpv_time, dpv_voltage, dpv_current, dpv_cycle, dpv_exp, dpv_v_apply]
    return dpv

def dpv_phasing(data):
    """
    split ONE cycle of dpv to positive and negative phase
    :param data:
    :return:
    """
    dpv_min = np.argmin(data[:, 5])
    dpv_max = np.argmax(data[:, 5])
    if data[2, 5] < data[0, 5]:
        phase_up = data[dpv_min:dpv_max, 0:5]
        phase_down = np.row_stack((data[0:dpv_min, 0:5], data[dpv_max:, 0:5]))
    else:
        phase_down = data[dpv_max:dpv_min, 0:5]
        phase_up = np.row_stack((data[0:dpv_max, 0:5], data[dpv_min:, 0:5]))
    return phase_up, phase_down


data = np.genfromtxt(sys.argv[1],delimiter=',')
name = os.path.splitext(os.path.basename(sys.argv[1]))[0]
dpv = proc_dpv(data, decay_ms =500, pulse_ms = 50, pulse_from_end=4,decay_from_end=20)
#np.savetxt(f'{name}_proc.csv', dpv[:, 0:5], delimiter=',', fmt="%.2E,%.2E,%.2E,%d,%d")
dpv_up, dpv_down = dpv_phasing(dpv)
plt.scatter(dpv_up[:, 1], dpv_up[:, 2], c='b', s=5)
plt.scatter(dpv_down[:, 1], dpv_down[:, 2], c='g', s=5)
plt.xlim([-0.2, 0.45])
plt.ylim([-5e-7, 5e-7])
plt.savefig(f"{name}.png")
