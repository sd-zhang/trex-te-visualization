## Nothing so far

import numpy as np
import matplotlib.pyplot as plt

from load_generation_models import get_house_data
from corst_curves import calculate_pricepoint

solar, load = get_house_data(scale_load=1, scale_gen=1)

price_points, SD_ratio = calculate_pricepoint(solar, load)

fig, ax = plt.subplots(3,1, sharex=True)

ax[0].plot(solar, color='red', label='Solar Power Supply')
ax[0].plot(load, color='blue', label='Load Demand')
ax[0].legend(loc="upper right")
ax[0].set_ylabel('Power [kWh]')
ax[1].plot(SD_ratio, label="Supply/Demand Ratio")
ax[1].legend(loc="upper right")
ax[2].plot(price_points, label='energy_price')
ax[2].set_ylabel('Price [$]')
ax[2].set_xlabel('t[h]')
plt.legend()
plt.show()
