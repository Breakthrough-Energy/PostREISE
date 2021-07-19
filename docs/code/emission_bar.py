from powersimdata import Scenario
from powersimdata.utility.helpers import PrintManager

from postreise.plot.plot_carbon_bar import plot_carbon_bar

scenarioA = Scenario(2497)
scenarioB = Scenario(3101)

with PrintManager():
    scenarioA = Scenario(2497)
    scenarioB = Scenario(3101)

plot_carbon_bar(
    scenarioA,
    scenarioB,
    labels=[
        "Western" + "\n" + "90% clean and 10% nuclear",
        "Western"
        + "\n"
        + "90% clean and 10% nuclear"
        + "\n"
        + "with transmission upgrade",
    ],
)
