## Nothing so far
#ToDo: add the export to desirable format

import numpy as np
import matplotlib.pyplot as plt
from load_generation_models import get_house_data
from corst_curves import calculate_pricepoint, market

house_id = ["R5", "R6", "R7", "R8", "R9", "R10", "R11", "R12", "R13", "R14"]
house_data = {}
steps = 24
for house in house_id:
    if house in ["R6", "R8", "R10", "R12"]:
        scale_solar = 0
    else:
        scale_solar = 1
    solar, load = get_house_data(scale_load=1,
                                 scale_gen=scale_solar)
    #ToDo: add battery
    house_data[house] = {'solar': solar,
                         'load': load,
                         'net_load': load-solar, #netload > 0 means we have load, smaller 0 means we have generation
                        'bill': np.zeros(steps),
                         }

system_load_demand = np.zeros(steps)
system_generation = np.zeros(steps)
for house in house_data:
    system_load_demand += house_data[house]['load']
    system_generation += house_data[house]['solar']

price_points, SD_ratio = calculate_pricepoint(system_generation, system_load_demand)

for t in range(steps):
    bids = {}
    asks = {}

    for house in house_data:
        net_load_t = house_data[house]['net_load'][t]
        if net_load_t > 0:
            bids[house] = net_load_t
        elif net_load_t < 0:
            asks[house] = -net_load_t #so both are positive

    settled = market(bids, asks)

    for house in house_data:
        net_load_grid = house_data[house]['net_load'][t]

        if house in settled:
            bill_market = price_points[t]*settled[house]
            net_load_grid += - settled[house]
        else:
            bill_market = 0

        if net_load_grid > 0:
            bill_grid = net_load_grid * 0.15
        else:
            bill_grid = net_load_grid * 0.07

        if t == 0:
            house_data[house]['bill'][t] = bill_grid + bill_market
        else:
            house_data[house]['bill'][t] = bill_grid + bill_market  + house_data[house]['bill'][t - 1]

system_bill = np.zeros(steps)
for house in house_data:
    system_bill += house_data[house]['bill']

fig, ax = plt.subplots(4, 1, sharex=True)
ax[0].plot(system_generation, color='red', label='Solar Power Supply')
ax[0].plot(system_load_demand, color='blue', label='Load Demand')
ax[0].legend(loc="upper right")
ax[0].set_ylabel('[kW]')
ax[1].plot(SD_ratio, label="Supply/Demand Ratio")
ax[1].set_ylabel('[kw/kw]')
ax[1].legend(loc="upper right")
ax[2].plot(price_points, label="Energy Price")
ax[2].set_ylabel('[$/Wh]')
ax[3].plot(system_bill, label='System Bill')
ax[3].set_ylabel('[$]')
ax[-1].set_xlabel('t in [h]')
plt.legend()
plt.show()
