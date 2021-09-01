import inspect
import os

from powersimdata.design.generation.clean_capacity_scaling import load_targets_from_csv
from powersimdata.utility.helpers import PrintManager

import postreise
from postreise.plot.plot_bar_shortfall import plot_bar_shortfall

data = os.path.join(os.path.dirname(inspect.getfile(postreise)), "data")
target = load_targets_from_csv(
    os.path.join(data, "2030_USA_Clean_Energy_Regular_Targets.csv")
)
with PrintManager():
    plot_bar_shortfall(
        "Nevada",
        [2497, 3101],
        target,
        scenario_names=[
            "Western 90% clean and 10% nuclear",
            "Western 90% clean and 10% nuclear" + "\n" + "with transmission upgrade",
        ],
        baseline_scenario=2497,
        baseline_scenario_name="Western 90% clean and 10% nuclear",
    )
