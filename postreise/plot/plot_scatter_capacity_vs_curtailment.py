import matplotlib.pyplot as plt
import pandas as pd
from powersimdata.input.check import _check_resources_are_renewable_and_format
from powersimdata.input.helpers import get_plant_id_for_resources_in_area

from postreise.analyze.generation.capacity import get_capacity_by_resources
from postreise.analyze.generation.curtailment import calculate_curtailment_time_series
from postreise.analyze.time import change_time_zone, slice_time_series


def plot_scatter_capacity_vs_curtailment(
    scenario,
    area,
    resources,
    time_zone="utc",
    time_range=None,
    area_type=None,
    between_time=None,
    dayofweek=None,
    markersize=50,
    fontsize=20,
    title=None,
    percentage=False,
    show_plot=True,
):
    """Generate for a given scenario the scatter plot of the capacity (x-axis) vs
    curtailment as a fraction of available resources (y-axis) of generators
    located in area and fueled by resources over a time range.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance
    :param str area: one of *loadzone*, *state*, *state abbreviation*,
        *interconnect*, *'all'*
    :param str/list resources: one or a list of resources.
    :param str time_zone: new time zone, default to be *'utc'*.
    :param tuple time_range: [start_timestamp, end_timestamp] where each time stamp
        is pandas.Timestamp/numpy.datetime64/datetime.datetime. If None, the entire
        time range is used for the given scenario.
    :param str area_type: one of *'loadzone'*, *'state'*, *'state_abbr'*,
        *'interconnect'*
    :param list between_time: specify the start hour and end hour of each day
        inclusively, default to None, which includes every hour of a day. Note that if
        the end hour is set before the start hour, the complementary hours of a day are
        picked.
    :param set dayofweek: specify the interest days of week, which is a subset of
        integers in [0, 6] with 0 being Monday and 6 being Sunday, default to None,
        which includes every day of a week.
    :param int/float markersize: marker size, default to 50.
    :param int/float fontsize: font size, default to 20.
    :param str title: user specified figure title, default to None.
    :param bool percentage: show capacity factor in percentage or not, default to False
    :param bool show_plot: show the plot or not, default to True.
    :return: (*tuple*) -- the first entry is matplotlib.axes.Axes object of the plot,
        the second entry is the capacity weighted average of curtailment over the
        selected time range.
    :raises TypeError:
        if markersize is not an integer or a float and/or
        if fontsize is not an integer or a float and/or
        if title is provided but not in a string format.
    """
    if not isinstance(markersize, (int, float)):
        raise TypeError("markersize should be either an integer or a float")
    if not isinstance(fontsize, (int, float)):
        raise TypeError("fontsize should be either an integer or a float")
    if title is not None and not isinstance(title, str):
        raise TypeError("title should be a string")
    resources = _check_resources_are_renewable_and_format(
        resources, grid_model=scenario.info["grid_model"]
    )
    curtailment = calculate_curtailment_time_series(scenario)
    plant_list = get_plant_id_for_resources_in_area(
        scenario, area, resources, area_type=area_type
    )
    curtailment = curtailment[set(plant_list) & set(curtailment.columns)]
    curtailment = change_time_zone(curtailment, time_zone)
    if not time_range:
        time_range = (
            pd.Timestamp(scenario.info["start_date"], tz="utc"),
            pd.Timestamp(scenario.info["end_date"], tz="utc"),
        )
    curtailment = slice_time_series(
        curtailment,
        time_range[0],
        time_range[1],
        between_time=between_time,
        dayofweek=dayofweek,
    )
    profiles = pd.concat(
        [scenario.state.get_solar(), scenario.state.get_wind()], axis=1
    )
    curtailment = curtailment.sum() / profiles[curtailment.columns].sum()
    if percentage:
        curtailment = (curtailment * 100).round(2)
    total_cap = get_capacity_by_resources(
        scenario, area, resources, area_type=area_type
    ).sum()
    plant_df = scenario.state.get_grid().plant.loc[plant_list]
    if total_cap == 0:
        data_avg = 0
    else:
        data_avg = (plant_df["Pmax"] * curtailment).sum() / total_cap

    _, ax = plt.subplots(figsize=[20, 10])
    ax.scatter(plant_df["Pmax"], curtailment, s=markersize)
    ax.plot(plant_df["Pmax"], [data_avg] * len(plant_df.index), c="red")
    ax.grid()
    if title is None:
        ax.set_title(
            f"{area} "
            f'{" ".join(resources) if isinstance(resources, (list, set)) else resources}'
        )
    else:
        ax.set_title(title)
    ax.set_xlabel("Capacity (MW)")
    if percentage:
        ax.set_ylabel("Curtailment %")
    else:
        ax.set_ylabel("Curtailment")
    for item in (
        [ax.title, ax.xaxis.label, ax.yaxis.label]
        + ax.get_xticklabels()
        + ax.get_yticklabels()
    ):
        item.set_fontsize(fontsize)
    if show_plot:
        plt.show()
    return ax, data_avg
