import pandas as pd
from powersimdata.scenario.scenario import Scenario

from postreise.plot.plot_powerflow_snapshot import plot_powerflow_snapshot

if __name__ == "__main__":
    demand_centers = pd.read_csv("loadzone_centers.csv", index_col=0)
    scenario = Scenario(1270)
    b2b_dclines = {"from": range(7), "to": [7, 8]}
    hour_of_interest = pd.Timestamp(2016, 11, 2, 22)
    # Plot the whole USA
    plot_powerflow_snapshot(
        scenario,
        hour_of_interest,
        b2b_dclines=b2b_dclines,
        demand_centers=demand_centers,
        legend_font_size=20,
    )
    # Plot just Texas
    plot_powerflow_snapshot(
        scenario,
        hour_of_interest,
        b2b_dclines=b2b_dclines,
        demand_centers=demand_centers,
        x_range=(-11.9e6, -10.2e6),
        y_range=(2.7e6, 4.4e6),
        figsize=(800, 800),
        pf_width_scale_factor=0.002,
        bg_width_scale_factor=0.00125,
        circle_scale_factor=(1 / 3),
        legend_font_size=20,
        num_dc_arrows=4,
    )
