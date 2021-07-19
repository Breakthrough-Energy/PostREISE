from powersimdata import Scenario

from postreise.plot.plot_energy_carbon_stack import plot_n_scenarios

scenarioA = Scenario(2497)
scenarioB = Scenario(3101)

plot_n_scenarios(scenarioA, scenarioB)
