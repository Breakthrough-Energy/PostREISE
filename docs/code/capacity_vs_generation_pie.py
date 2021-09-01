from powersimdata.utility.helpers import PrintManager

from postreise.plot.plot_pie_generation_vs_capacity import (
    plot_pie_generation_vs_capacity,
)

with PrintManager():
    plot_pie_generation_vs_capacity(
        areas=["WA", "Western"],
        scenario_ids=[2497, 3101],
        scenario_names=[
            "Western 90% clean and 10% nuclear",
            "Western 90% clean and 10% nuclear \n with transmission upgrade",
        ],
    )
