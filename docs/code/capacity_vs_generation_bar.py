from powersimdata.utility.helpers import PrintManager

from postreise.plot.plot_bar_generation_vs_capacity import (
    plot_bar_generation_vs_capacity,
)

with PrintManager():
    plot_bar_generation_vs_capacity(
        areas=["CA", "Western"],
        scenario_ids=[2497, 3101],
        scenario_names=[
            "Western 90% clean and 10% nuclear",
            "Western 90% clean and 10% nuclear with transmission upgrade",
        ],
    )
