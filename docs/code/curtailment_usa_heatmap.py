import matplotlib.pyplot as plt
from powersimdata import Scenario

from postreise.analyze.generation.curtailment import calculate_curtailment_time_series
from postreise.plot.plot_heatmap import plot_heatmap

scenario = Scenario(3287)
curtailment = calculate_curtailment_time_series(scenario).sum(axis=1)

plot_heatmap(
    curtailment,
    cmap="PiYG_r",
    scale=1e-3,
    cbar_label="GW",
    vmin=0,
    vmax=250,
    cbar_tick_values=[0, 50, 100, 150, 200, 250],
    cbar_tick_labels=["0", "50", "100", "150", "200", "≥250"],
    time_zone="ETC/GMT+6",
    time_zone_label="(CST)",
    contour_levels=[250],
)
