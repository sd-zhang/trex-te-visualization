## Nothing so far
#ToDo: add the export to desirable format
import os.path

import numpy as np
import matplotlib.pyplot as plt
from load_generation_models import get_house_data, bess
from corst_curves import calculate_pricepoint, market, calculate_grid_costs
def generate_house_data(steps):
    # generating the house data
    house_id = ["R5", "R6", "R7", "R8", "R9", "R10", "R11", "R12", "R13", "R14"]
    house_data = {}
    for house in house_id:
        if house in ["R6", "R8", "R10", "R12"]:
            scale_solar = 0
        else:
            scale_solar = 1.1
        solar, load = get_house_data(scale_load=1,
                                     scale_gen=scale_solar,
                                     steps=steps)

        house_data[house] = {'solar': solar,
                             'load': load,
                             'te-load': load-solar, #netload > 0 means we have load, smaller 0 means we have generation
                            'transactive_bill': np.zeros(steps),
                             'net_billing_bill': np.zeros(steps),
                             'savings': np.zeros(steps),
                             }

        if house in ["R5", "R7", "R9", "R11", "R14"]:
            house_data[house]['battery_SoC'] =  np.zeros(steps)

    return house_data

def plot_TE(house_data, steps, SD_ratio, market_settlement_price):
    system_bill = np.zeros(steps)
    system_savings = np.zeros(steps)
    system_load_demand = np.zeros(steps)
    system_generation = np.zeros(steps)
    net_billing_net_load = np.zeros(steps)
    te_net_load = np.zeros(steps)
    system_SoC = np.zeros(steps)
    num_batteries = 0

    for house in house_data:
        system_bill += house_data[house]['transactive_bill']
        system_savings += house_data[house]['savings']
        system_load_demand += house_data[house]['load']
        system_generation += house_data[house]['solar']
        net_billing_net_load += house_data[house]['load'] - house_data[house]['solar']
        te_net_load += house_data[house]['te-load']
        if 'battery_SoC' in house_data[house]:
            system_SoC += house_data[house]['battery_SoC']
            num_batteries += 1

    system_SoC = system_SoC/num_batteries


    fig, ax = plt.subplots(3, 1, sharex=True)
    ax[0].plot(system_generation, color='red', label='-Solar')
    ax[0].plot(system_load_demand, color='blue', label='Load')
    ax[0].set_ylabel('Power[kW]')
    ax[1].plot(net_billing_net_load, label="Net-Billing")
    ax[1].plot(te_net_load, label="TE")
    ax[1].set_ylabel('Net-Load[kW]')
    ax[2].plot(system_SoC)
    ax[2].set_ylabel('System SoC')
    #ax[3].plot(SD_ratio, label="Supply/Demand Ratio")
    #ax[3].set_ylabel('[kW/kW]')
    #ax[4].plot(market_settlement_price, label="Avg Settlement Price")
    #ax[4].set_ylabel('[$/Wh]')
    #ax[5].plot(system_bill, label='System Bill')
    #ax[5].set_ylabel('[$]')
    #ax[6].plot(system_savings, label='System Savings')
    #ax[6].set_ylabel('[$]')
    ax[-1].set_xlabel('t in [h]')

    for index in range(len(ax)):
        ax[index].legend(loc="upper right")
    plt.legend()
    plt.savefig('TE Systems performance overview.pdf')
    plt.show()

# generating simulation data
def simulate_TE():

    steps = int(24*3.3) #.5 because thats when the batteries are empty
    house_data = generate_house_data(steps)
    capacity_bess = 7
    market_settlement_price = np.zeros(steps)
    SD_ratio = np.zeros(steps)*np.nan

    for t in range(steps):
        bids = {}
        asks = {}
        market_demand_t = 0
        market_supply_t = 0

        for house in house_data:
            if 'battery_SoC' in house_data[house]: # get the max charge / discharge
                p_target = -house_data[house]['te-load'][t] #because batteries reverse signs
                soc_post_adjustment, [p_res, p_actual], [p_ch_max, p_dis_max] = bess(p_target=p_target, #just to query battery
                                                                                     soc_now=house_data[house]['battery_SoC'][t],
                                                                                     capacity=capacity_bess)
                house_data[house]['battery_SoC'][t:] = soc_post_adjustment
                house_data[house]['te-load'][t] += p_actual

            else:
                p_ch_max = 0
                p_dis_max = 0
            #ToDo: this makes S/D calculations inaccurate now (maybe?)
            # It definitively makes system load demand calculations inaccurate if we only charge from the market ... so we need to account for that later (?)
            market_target_q = house_data[house]['te-load'][t] + p_ch_max
            #ToDO: maybe implement the prosumer case for solar and BESS, for now we don't have this

            if market_target_q > 0:
                bids[house] = market_target_q
                market_demand_t += market_target_q
            elif market_target_q < 0:
                asks[house] = -market_target_q #so both are positive
                market_supply_t += market_target_q

        market_settlement_price[t], SD_ratio[t] = calculate_pricepoint(S=market_supply_t,
                                                                       D=market_demand_t,
                                                                       alpha=1)
        settled = market(bids, asks)
        # dumb
        for house in house_data:
            residual_net_load_grid = house_data[house]['te-load'][t]

            if house in settled:
                bill_market = market_settlement_price[t]*settled[house]
                residual_net_load_grid += - settled[house]
                if 'battery_SoC' in house_data[house]:
                     if residual_net_load_grid < 0: # we onbviously bought more from the market
                        soc_now = house_data[house]['battery_SoC'][t]
                        p_target = -residual_net_load_grid
                        soc_next, [p_res, p_actual], [p_ch_max, p_dis_max] = bess(p_target=p_target,
                                                                                   soc_now=soc_now,
                                                                                   capacity=capacity_bess,
                                                                                   )
                        if soc_now > soc_next:
                            print('staph!')
                        residual_net_load_grid += p_actual
                        if t < steps:
                            house_data[house]['battery_SoC'][t:] = soc_next
            else:
                bill_market = 0

            if t == 0:
                house_data[house]['transactive_bill'][t] = calculate_grid_costs(residual_net_load_grid) + bill_market
                house_data[house]['net_billing_bill'][t]  = calculate_grid_costs(house_data[house]['load'][t] - house_data[house]['solar'][t])
                house_data[house]['savings'][t] = house_data[house]['net_billing_bill'][t] - house_data[house]['transactive_bill'][t]
            else:
                house_data[house]['transactive_bill'][t] = calculate_grid_costs(residual_net_load_grid) + bill_market + house_data[house]['transactive_bill'][t - 1]
                house_data[house]['net_billing_bill'][t] = calculate_grid_costs(house_data[house]['load'][t] - house_data[house]['solar'][t]) + house_data[house]['net_billing_bill'][t-1]
                house_data[house]['savings'][t] = house_data[house]['net_billing_bill'][t] - house_data[house]['transactive_bill'][t] + house_data[house]['savings'][t-1]

    plot_TE(house_data, steps, SD_ratio, market_settlement_price)
    return house_data

def export_data_to_PFcsv():
    house_data = simulate_TE()
    house_ids = list(house_data.keys())
    for house_nbr in range(len(house_ids)):
        house_id = house_ids[house_nbr]
        net_load = house_data[house_id]['te-load']
        filename = str(house_nbr) + ".csv"
        folder = 'pf_data'
        path = os.path.join(folder, filename)
        np.savetxt(path, net_load, delimiter=",")