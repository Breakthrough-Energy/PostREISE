import matplotlib.pyplot as plt
import pandas as pd
from powersimdata.network.model import ModelImmutables

from postreise.analyze.generation.summarize import (
    sum_generation_by_state,
    sum_generation_by_type_zone,
)


def plot_bar_generation_max_min_actual(
    scenario,
    interconnect,
    gen_type,
    percentage=False,
    show_as_state=True,
    fontsize=15,
    plot_show=True,
):
    """Generate for a given scenario the bar plot of total capacity vs. actual
    generation vs. minimum generation for a specific type of generators in an
    interconnection.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param str interconnect: the interconnection name of interest.
    :param str gen_type: type of generator.
    :param bool percentage: show bars in percentage of total capacity or not,
        defaults to False.
    :param bool show_as_state: each bar represents a state within the given
        interconnection or not, defaults to True, if not, each bar will represent a
        loadzone instead.
    :param int/float fontsize: font size of the texts shown on the plot.
    :param plot_show: show the plot or not, defaults to True.
    :return: (*matplotlib.axes.Axes*) -- axes object of the plot.
    """
    grid = scenario.state.get_grid()
    plant = grid.plant[grid.plant.type == gen_type]
    mi = ModelImmutables(scenario.info["grid_model"])
    hour_num = (
        pd.Timestamp(scenario.info["end_date"])
        - pd.Timestamp(scenario.info["start_date"])
    ).total_seconds() / 3600 + 1
    if show_as_state:
        zone_list = [
            mi.zones["abv2state"][abv]
            for abv in mi.zones["interconnect2abv"][interconnect]
        ]
        all_max_min = (
            plant.groupby(plant.zone_name.map(mi.zones["loadzone2state"]))[
                ["Pmax", "Pmin"]
            ].sum()
            * hour_num
        )
        all_actual_gen = sum_generation_by_state(scenario)[gen_type] * 1000
    else:
        zone_list = mi.zones["interconnect2loadzone"][interconnect]
        all_max_min = plant.groupby("zone_name")[["Pmax", "Pmin"]].sum() * hour_num
        all_actual_gen = (
            sum_generation_by_type_zone(scenario)
            .rename(columns=grid.id2zone)
            .T[gen_type]
        )
    df = pd.concat([all_max_min, all_actual_gen], axis=1).loc[zone_list]
    if percentage:
        df_pct = df.copy()
        df_pct["Pmax"] = df["Pmax"].apply(lambda x: 1 if x > 0 else 0)
        df_pct["Pmin"] = df["Pmin"] / df["Pmax"]
        df_pct[gen_type] = df[gen_type] / df["Pmax"]
        df = df_pct
    df.sort_index(inplace=True)

    width = 0.8
    fig, ax = plt.subplots(figsize=[30, 15])
    df["Pmax"].plot(kind="bar", width=width, color="yellowgreen", ax=ax)
    df[gen_type].plot(kind="bar", width=width * 0.7, color="steelblue", ax=ax)
    df["Pmin"].plot(kind="bar", width=width * 0.4, color="firebrick", ax=ax)
    ax.legend(
        ["Total Capacity", "Actual Generation", "Minimum Generation"],
        bbox_to_anchor=(0.5, 0.95),
        loc="lower center",
        ncol=3,
        fontsize=fontsize,
    )
    ax.grid()
    if percentage:
        ax.set_title(f"{gen_type.capitalize()} Generation %")
    else:
        ax.set_title(f"{gen_type.capitalize()} Generation MWh")
    for item in (
        [ax.title, ax.xaxis.label, ax.yaxis.label]
        + ax.get_xticklabels()
        + ax.get_yticklabels()
    ):
        item.set_fontsize(fontsize)
    if plot_show:
        plt.show()
    return ax
