# we generate the data here
# for now this is going to be 2 sinewaves
# we will end up having:
# chopped sinewave 1 for solar:     ___/'''\___
# sinewave 2 for load:              .-""-..-""-.

import numpy as np
import matplotlib.pyplot as plt

def get_house_data(scale_load=1, scale_gen=1, steps=24):
    hours = np.arange(0,steps)
    normalize_freq_to_24h=2*np.pi/24
    solar_shift_time = -6
    solar = 1.5*np.sin((hours+solar_shift_time)*normalize_freq_to_24h)
    solar = np.maximum(0.0, solar)

    base_load = 0.1
    day = np.arange(0, 24)
    load_day = np.sin((day+1)*normalize_freq_to_24h)
    load_day[0:12] = load_day[0:12]**6
    load_day[0:12] = load_day[0:12] * (1-base_load-0.2)
    load_day[12:] = load_day[12:]**2
    load_day = load_day + base_load

    load = np.zeros(steps)
    for t in range(steps):
        load[t] = load_day[t%24]


    return solar*scale_gen, load*scale_load

# p_target positive means we're charging
# p_target negative means we're discharging
def bess(p_target=10, soc_now=0.1, capacity=100):
    p_dis_max = -soc_now*capacity
    p_ch_max = (1-soc_now)*capacity

    p_possible = max(p_dis_max, min(p_ch_max, p_target))
    p_residual = p_target - p_possible
    delta = 0
    if capacity > 0:
        delta = p_possible/capacity
    soc_now = soc_now + delta

    return soc_now,\
           [p_residual, p_possible],\
           [p_ch_max, p_dis_max]

def plot():
    solar, load = get_house_data()
    plt.plot(load, color='blue', label='Load')
    plt.plot(solar, color='red', label='solar')
    plt.legend()
    plt.show()


