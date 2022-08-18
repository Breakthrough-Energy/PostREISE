import matplotlib.pyplot as plt
import pandas as pd
from powersimdata.input.check import (
    _check_resources_are_in_grid_and_format,
    _check_resources_are_renewable_and_format,
)
from powersimdata.scenario.check import _check_scenario_is_in_analyze_state

from postreise.analyze.generation.summarize import (
    sum_generation_by_state,
    sum_generation_by_type_zone,
)


def plot_bar_renewable_max_profile_actual(
    scenario,
    interconnect,
    gen_type,
    percentage=False,
    show_as_state=True,
    fontsize=15,
    plot_show=True,
):
    """Generate for a given scenario the bar plot of total capacity vs. available energy
    vs. actual generation for a specific renewable resource in an interconnection.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param str interconnect: the interconnection name of interest.
    :param str gen_type: renewable resource.
    :param bool percentage: show bars in percentage of total capacity or not,
        defaults to False.
    :param bool show_as_state: each bar represents a state within the given
        interconnection or not, defaults to True, if not, each bar will represent a
        loadzone instead.
    :param int/float fontsize: font size of the texts shown on the plot.
    :param plot_show: show the plot or not, defaults to True.
    :return: (*matplotlib.axes.Axes*) -- axes object of the plot.
    :raises TypeError:
        if ``interconnect`` and ``gen_type`` are not str
        if ``fontsize`` is not a int or a float
    :raises ValueError: if ``interconnect is not valid
    """
    _check_scenario_is_in_analyze_state(scenario)
    if not isinstance(interconnect, str):
        raise TypeError("interconnect must be a str")
    if not isinstance(gen_type, str):
        raise TypeError("gen_type must be a str")
    if not isinstance(fontsize, (int, float)):
        raise TypeError("fontsize must be either a int or a float")

    grid = scenario.get_grid()
    mi = grid.model_immutables
    _check_resources_are_in_grid_and_format(gen_type, grid)
    _check_resources_are_renewable_and_format(gen_type, mi=mi)

    plant = grid.plant[grid.plant.type == gen_type]
    if interconnect not in mi.zones["interconnect"]:
        raise ValueError(
            f"interconnect must be one of {sorted(mi.zones['interconnect'])}"
        )
    if (
        len(
            mi.zones["interconnect2abv"][interconnect]
            - mi.zones["interconnect2abv"][scenario.info["interconnect"]]
        )
        != 0
    ):
        raise ValueError("interconnect is incompatible with scenario's interconnect")

    if "wind" in gen_type:
        profile = scenario.get_wind().sum()
    else:
        profile = scenario.get_solar().sum()
    hour_num = (
        pd.Timestamp(scenario.info["end_date"])
        - pd.Timestamp(scenario.info["start_date"])
    ).total_seconds() / 3600 + 1
    if show_as_state:
        zone_list = [
            mi.zones["abv2state"][abv]
            for abv in mi.zones["interconnect2abv"][interconnect]
        ]
        group_criteria = plant.zone_name.map(mi.zones["loadzone2state"])
        profile_gen = profile.groupby(group_criteria).sum().rename("profile")
        total_capacity = plant.groupby(group_criteria)["Pmax"].sum() * hour_num
        actual_gen = sum_generation_by_state(scenario)[gen_type] * 1000
    else:
        zone_list = list(mi.zones["interconnect2loadzone"][interconnect])
        profile_gen = profile.groupby(plant.zone_name).sum().rename("profile")
        total_capacity = plant.groupby("zone_name")["Pmax"].sum() * hour_num
        actual_gen = (
            sum_generation_by_type_zone(scenario)
            .rename(columns=grid.id2zone)
            .T[gen_type]
        )
    df = pd.concat([total_capacity, profile_gen, actual_gen], axis=1).loc[zone_list]
    if percentage:
        df_pct = df.copy()
        df_pct["Pmax"] = df["Pmax"].apply(lambda x: 1 if x > 0 else 0)
        df_pct["profile"] = df["profile"] / df["Pmax"]
        df_pct[gen_type] = df[gen_type] / df["Pmax"]
        df = df_pct
    df.sort_index(inplace=True)

    width = 0.8
    fig, ax = plt.subplots(figsize=[30, 15])
    df["Pmax"].plot(kind="bar", width=width, color="yellowgreen", ax=ax)
    df["profile"].plot(kind="bar", width=width * 0.7, color="steelblue", ax=ax)
    df[gen_type].plot(kind="bar", width=width * 0.4, color="firebrick", ax=ax)
    ax.legend(
        ["Total Capacity", "Available Energy", "Actual Generation"],
        bbox_to_anchor=(0.5, 0.95),
        loc="lower center",
        ncol=3,
        fontsize=fontsize,
    )
    ax.grid()
    if percentage:
        ax.set_title(f"{gen_type.capitalize()} Curtailment %")
    else:
        ax.set_title(f"{gen_type.capitalize()} Curtailment MWh")
    for item in (
        [ax.title, ax.xaxis.label, ax.yaxis.label]
        + ax.get_xticklabels()
        + ax.get_yticklabels()
    ):
        item.set_fontsize(fontsize)
    if plot_show:
        plt.show()
    return ax
