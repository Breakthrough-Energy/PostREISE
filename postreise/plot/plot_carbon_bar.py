import numpy as np
from matplotlib import pyplot as plt
from powersimdata.scenario.scenario import Scenario

from postreise.analyze.generation.emissions import (
    generate_emissions_stats,
    summarize_emissions_by_bus,
)


def plot_carbon_bar(*args, labels=None, labels_size=15, show_plot=True):
    """Make bar chart of carbon emissions by fuel type for n scenarios.

    :param powersimdata.scenario.scenario.Scenario args: scenario instances.
    :param list/tuple/set labels: labels on plot. Default to scenario id.
    :param int labels_size: size of labels.
    :param bool show_plot: whether to save the plot.
    :raises ValueError:
        if ``args`` are not scenario instances.
        if ``labels`` has a different length than the number of passed scenarios.
    :raises TypeError:
        if ``labels`` is not an iterable.
        if ``labels_size`` is not an int.
    :return: (*tuple*) -- the figure elements that can be further modified.
    """
    if not all([isinstance(a, Scenario) for a in args]):
        raise ValueError("all inputs must be Scenario objects")
    if labels is not None and not isinstance(labels, (list, tuple, set)):
        raise TypeError("labels must be a list/tuple/set")
    if labels is not None and len(args) != len(labels):
        raise ValueError("labels must have same length as number of scenarios")
    if not isinstance(labels_size, int):
        raise TypeError("labels_size must be an integer")

    labels = tuple([s.info["id"] for s in args]) if labels is None else tuple(labels)

    carbon_val = {"coal": [], "ng": []}
    for i, s in enumerate(args):
        grid = s.state.get_grid()
        carbon_by_bus = summarize_emissions_by_bus(generate_emissions_stats(s), grid)
        carbon_val["coal"].append(sum(carbon_by_bus["coal"].values()))
        carbon_val["ng"].append(sum(carbon_by_bus["ng"].values()))

    fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(14, len(labels)))
    y_pos = np.arange(len(labels))

    for a, f, c, t in zip(
        [ax1, ax2],
        ["coal", "ng"],
        ["black", "purple"],
        ["Coal: CO$_2$  Emissions", "Natural Gas: CO$_2$ Emissions"],
    ):
        a.barh(y_pos, carbon_val[f], align="center", alpha=0.25, color=c)
        a.set_xlabel("Tons", fontsize=labels_size + 3)
        a.set_title(t, y=1.04, fontsize=labels_size + 5)
        a.tick_params(axis="both", labelsize=labels_size)

    plt.yticks(y_pos, labels)
    plt.subplots_adjust(wspace=0.1)
    if show_plot:
        plt.show()
    return ax1, ax2


def carbon_diff(scenario_1, scenario_2):
    """Prints percentage change in carbon emissions of two scenarios.

    :param powersimdata.scenario.scenario.Scenario scenario_1: scenario instance.
    :param powersimdata.scenario.scenario.Scenario scenario_2: scenario instance.
    :return: (*float*) -- relative difference in emission in percent.
    """
    carbon_by_bus_1 = summarize_emissions_by_bus(
        generate_emissions_stats(scenario_1), scenario_1.state.get_grid()
    )
    carbon_by_bus_2 = summarize_emissions_by_bus(
        generate_emissions_stats(scenario_2), scenario_2.state.get_grid()
    )

    sum_1 = sum(carbon_by_bus_1["coal"].values()) + sum(carbon_by_bus_1["ng"].values())
    sum_2 = sum(carbon_by_bus_2["coal"].values()) + sum(carbon_by_bus_2["ng"].values())

    return 100 * (1 - sum_2 / sum_1)
