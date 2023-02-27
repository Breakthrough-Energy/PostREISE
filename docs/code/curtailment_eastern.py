from matplotlib import pyplot as plt
from powersimdata import Scenario

from postreise.plot.plot_curtailment_ts import plot_curtailment_time_series

scenario = Scenario(403)

t2c = {"wind_curtailment": "blue", "solar_curtailment": "blue"}

plot_curtailment_time_series(
    scenario,
    "Eastern",
    ["solar", "wind"],
    time_freq="D",
    t2c=t2c,
    label_fontsize=30,
    title_fontsize=35,
    tick_fontsize=25,
    legend_fontsize=25,
)
plt.show()
