# we generate the data here
# for now this is going to be 2 sinewaves
# we will end up having:
# chopped sinewave 1 for solar:     ___/'''\___
# sinewave 2 for load:              .-""-..-""-.

import numpy as np
import matplotlib.pyplot as plt

def get_house_data(scale_load=1, scale_gen=1):
    hours = np.arange(0,24)
    normalize_freq_to_24h=2*np.pi/24
    solar_shift_time = -6
    solar = 1.5*np.sin((hours+solar_shift_time)*normalize_freq_to_24h)
    solar = np.maximum(0.0, solar)

    base_load = 0.1
    half_day = int(hours[-1]/2)
    load_shift_time = 3
    load = np.sin((hours+1)*normalize_freq_to_24h)
    load[0:12] = load[0:12]**6
    load[12:] = load[12:]**2
    load[0:half_day] = load[0:half_day] * (1-base_load-0.2)
    load = load + base_load

    return solar*scale_gen, load*scale_gen

# p_target positive means we're charging
# p_target negative means we're discharging
def bess(p_target=10, soc_now=0.1, capacity=100):
    p_dis_max = -soc_now*capacity
    p_ch_max = (1-soc_now)*capacity

    p_possible = max(p_dis_max, min(p_ch_max, p_target))
    p_residual = p_target - p_possible

    soc_now = soc_now + p_possible/capacity

    return soc_now, p_residual

def plot():
    solar, load = get_house_data()
    plt.plot(load, color='blue', label='Load')
    plt.plot(solar, color='red', label='solar')
    plt.legend()
    plt.show()


