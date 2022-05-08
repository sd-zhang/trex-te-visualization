import numpy as np
import matplotlib.pyplot as plt
import random


max_SD = 5.0
min_SD = 1/5

min_price = 0.07
max_price = 0.14
def calculate_grid_costs(net_load):
    if net_load > 0:
        bill_grid = net_load * 0.15
    else:
        bill_grid = net_load * 0.07

    return bill_grid

def calculate_pricepoint(S=1, D=1, alpha=1/1.8):
    ratio = D/(S + 1e-5)

    delta = max_price - min_price
    shift = alpha*(ratio - 1.0)
    factor = 0.5 + shift

    price = min_price + np.maximum(0.0, np.minimum(delta, delta * factor ))

    return price, ratio


def market(bids, asks):
    # settle quantity must be positive if you bid sucessfully (meaning you buy stuff)
    # negative if you sucessfully ask stuff

    if asks and bids:
        #settle stuff
        ask_ids = list(asks.keys())
        random.shuffle(ask_ids)
        bid_ids = list(bids.keys())
        random.shuffle(bid_ids)

        settled = {}
        for bidder in bid_ids:
            settled[bidder] = 0

            for asker in ask_ids:
                if asks[asker] > 0 and bids[bidder] > 0:
                    if asker not in settled:
                        settled[asker] = 0
                    sub_settlement = min(asks[asker], bids[bidder])
                    settled[bidder] += sub_settlement
                    settled[asker] += -sub_settlement

                    #update the ledger for current balance
                    bids[bidder] += - sub_settlement
                    asks[asker] += -sub_settlement


    else:
        settled = {}
    return settled