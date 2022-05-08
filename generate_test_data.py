## Nothing so far
#ToDo: add the export to desirable format

import numpy as np
import matplotlib.pyplot as plt
from load_generation_models import get_house_data, bess
from corst_curves import calculate_pricepoint, market, calculate_grid_costs

house_id = ["R5", "R6", "R7", "R8", "R9", "R10", "R11", "R12", "R13", "R14"]
house_data = {}
steps = 24
capacity_bess = 10
for house in house_id:
    if house in ["R6", "R8", "R10", "R12"]:
        scale_solar = 0
    else:
        scale_solar = 1
    solar, load = get_house_data(scale_load=1,
                                 scale_gen=scale_solar)

    house_data[house] = {'solar': solar,
                         'load': load,
                         'net_load': load-solar, #netload > 0 means we have load, smaller 0 means we have generation
                        'transactive_bill': np.zeros(steps),
                         'net_billing_bill': np.zeros(steps),
                         'savings': np.zeros(steps),
                         }

    if house in ["R7", "R9", "R11"]:
        house_data[house]['battery_SoC'] =  np.zeros(steps)

# ToDo: since we're doing batteries, this needs to be happening in 'real time' now (so move it into the loop)
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
        #ToDo: keep doing battery stuff
        # if 'battery_SoC' in house_data[house]:
        #    soc_now = house_data[house]['battery_SoC'][t]
        #    _, __, [p_ch_max, p_dis_max] = bess(0, soc_now=soc_now, capacity=capacity_bess)

        if net_load_t > 0:
            bids[house] = net_load_t
        elif net_load_t < 0:
            asks[house] = -net_load_t #so both are positive

    settled = market(bids, asks)
    # dumb
    for house in house_data:
        residual_net_load_grid = house_data[house]['net_load'][t]

        if house in settled:
            bill_market = price_points[t]*settled[house]
            residual_net_load_grid += - settled[house]
        else:
            bill_market = 0

        if t == 0:
            house_data[house]['transactive_bill'][t] = calculate_grid_costs(residual_net_load_grid) + bill_market
            house_data[house]['net_billing_bill'][t]  = calculate_grid_costs(house_data[house]['net_load'][t])
            house_data[house]['savings'][t] = house_data[house]['net_billing_bill'][t] - house_data[house]['transactive_bill'][t]
        else:
            house_data[house]['transactive_bill'][t] = calculate_grid_costs(residual_net_load_grid) + bill_market + house_data[house]['transactive_bill'][t - 1]
            house_data[house]['net_billing_bill'][t] = calculate_grid_costs(house_data[house]['net_load'][t]) + house_data[house]['net_billing_bill'][t-1]
            house_data[house]['savings'][t] = house_data[house]['net_billing_bill'][t] - house_data[house]['transactive_bill'][t] + house_data[house]['savings'][t-1]

system_bill = np.zeros(steps)
system_savings = np.zeros(steps)
for house in house_data:
    system_bill += house_data[house]['transactive_bill']
    system_savings += house_data[house]['savings']

fig, ax = plt.subplots(5, 1, sharex=True)
ax[0].plot(system_generation, color='red', label='Solar Power Supply')
ax[0].plot(system_load_demand, color='blue', label='Load Demand')
ax[0].set_ylabel('[kW]')
ax[1].plot(SD_ratio, label="Supply/Demand Ratio")
ax[1].set_ylabel('[kw/kw]')
ax[2].plot(price_points, label="Energy Price")
ax[2].set_ylabel('[$/Wh]')
ax[3].plot(system_bill, label='System Bill')
ax[3].set_ylabel('[$]')
ax[4].plot(system_savings, label='System Savings')
ax[4].set_ylabel('[$]')
ax[-1].set_xlabel('t in [h]')

for index in range(len(ax)):
    ax[index].legend(loc="upper right")
plt.legend()
plt.show()
