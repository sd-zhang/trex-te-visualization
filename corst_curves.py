import numpy as np
import matplotlib.pyplot as plt


max_SD = 5.0
min_SD = 1/5

min_price = 0.07
max_price = 0.14

def calculate_pricepoint(S=1, D=1, alpha=1/10):
    ratio = S/D

    delta = max_price - min_price
    shift = alpha*(ratio - 1.0)
    factor = 0.5 + shift

    price = min_price + np.maximum(0.0, np.minimum(delta, delta * factor ))

    return price, ratio