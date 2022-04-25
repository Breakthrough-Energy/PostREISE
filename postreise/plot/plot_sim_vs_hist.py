import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from postreise.analyze.generation.summarize import sum_generation_by_state


class PlotSettings:
    width = 0.3  # width of bars
    fontsize = 15
    size_inches = (20, 10)


def plot_generation_sim_vs_hist(
    scenario,
    hist_gen,
    state,
    show_max=True,
    plot_show=True,
):
    """Plot simulated vs historical generation of each resource in the scenario
    for the given state. Optionally include max generation.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param pandas.DataFrame hist_gen: historical generation data frame. Columns are
        resources and indices are state names.
    :param str state: the US state
    :param bool show_max: determine whether to additionally plot max generation of each
        resource.
    :param plot_show: show the plot or not, defaults to True.
    :return: (*matplotlib.axes.Axes*) -- axes object of the plot.
    :raises TypeError:
        if ``hist_gen`` is not a data frame.
        if ``state`` is not a str.
    :raises ValueError: if ``state`` is not in ``hist_gen`` or ``scenario``.
    """
    if not isinstance(hist_gen, pd.DataFrame):
        raise TypeError("hist_gen must be a pandas.DataFrame")
    if not isinstance(state, str):
        raise TypeError("state must be a str")

    sim_gen = sum_generation_by_state(scenario)
    if state not in sim_gen.index or state not in hist_gen.index:
        raise ValueError("Invalid state")

    all_resources = list(sim_gen.columns)

    sim = [int(round(sim_gen.loc[state, res])) for res in all_resources]
    hist = [int(round(hist_gen.loc[state, res])) for res in all_resources]

    grid = scenario.get_grid()
    pg = scenario.get_pg()

    def calc_max(fuel):
        loadzone = list(grid.model_immutables.area_to_loadzone(state, "state"))  # noqa
        capacity = grid.plant.query("type == @fuel & zone_name == @loadzone")[
            "Pmax"
        ].sum()
        if capacity == 0:
            print(f"No {fuel} generator in {state}")

        return int(capacity * pg.shape[0] / 1000)

    max_gen = []
    if show_max:
        max_gen = [calc_max(res) for res in all_resources]

    x = np.arange(len(all_resources))  # the label locations
    width = PlotSettings.width
    fontsize = PlotSettings.fontsize
    size_inches_x, size_inches_y = PlotSettings.size_inches

    fig, ax = plt.subplots()
    if show_max:
        rects1 = ax.bar(x - width, hist, width, label="Historical")
        rects2 = ax.bar(x, sim, width, label="Simulated")
        rects3 = ax.bar(x + width, max_gen, width, label="Max Generation")
    else:
        rects1 = ax.bar(x - width / 2, hist, width, label="Historical")
        rects2 = ax.bar(x + width / 2, sim, width, label="Simulated")

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel("GWh", fontsize=fontsize)
    ax.set_title(state, fontsize=fontsize)
    ax.set_xticks(x)
    ax.set_xticklabels(all_resources, fontsize=fontsize)
    ax.legend(fontsize=fontsize)

    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(
                str(height),
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    autolabel(rects1)
    autolabel(rects2)
    if show_max:
        autolabel(rects3)
    fig.tight_layout()
    fig.set_size_inches(size_inches_x, size_inches_y)
    if plot_show:
        plt.show()
    return ax
