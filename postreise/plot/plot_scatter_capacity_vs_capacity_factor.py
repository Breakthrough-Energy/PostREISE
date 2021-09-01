import matplotlib.pyplot as plt
import pandas as pd
from powersimdata.input.helpers import get_plant_id_for_resources_in_area

from postreise.analyze.generation.capacity import (
    get_capacity_by_resources,
    get_capacity_factor_time_series,
)
from postreise.analyze.time import change_time_zone, slice_time_series


def plot_scatter_capacity_vs_capacity_factor(
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
    capacity factor (y-axis) of generators located in area and fueled by resources over
    a time range.

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
        the second entry is the capacity weighted average of capacity factors over the
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
    cf = get_capacity_factor_time_series(scenario, area, resources, area_type=area_type)
    cf = change_time_zone(cf, time_zone)
    if not time_range:
        time_range = (
            pd.Timestamp(scenario.info["start_date"], tz="utc"),
            pd.Timestamp(scenario.info["end_date"], tz="utc"),
        )
    cf = slice_time_series(
        cf, time_range[0], time_range[1], between_time=between_time, dayofweek=dayofweek
    )
    cf = cf.mean()
    if percentage:
        cf = (cf * 100).round(2)
    total_cap = get_capacity_by_resources(
        scenario, area, resources, area_type=area_type
    ).sum()
    plant_id = get_plant_id_for_resources_in_area(
        scenario, area, resources, area_type=area_type
    )
    plant_df = scenario.state.get_grid().plant.loc[plant_id]
    if total_cap == 0:
        data_avg = 0
    else:
        data_avg = (plant_df["Pmax"] * cf).sum() / total_cap

    _, ax = plt.subplots(figsize=[20, 10])
    ax.scatter(plant_df["Pmax"], cf, s=markersize)
    ax.plot(plant_df["Pmax"], [data_avg] * len(plant_df.index), c="red")
    ax.grid()
    if title is None:
        ax.set_title(
            f'{area} {" ".join(resources) if isinstance(resources, list) else resources}'
        )
    else:
        ax.set_title(title)
    ax.set_xlabel("Capacity (MW)")
    if percentage:
        ax.set_ylabel("Capacity Factor %")
    else:
        ax.set_ylabel("Capacity Factor")
    for item in (
        [ax.title, ax.xaxis.label, ax.yaxis.label]
        + ax.get_xticklabels()
        + ax.get_yticklabels()
    ):
        item.set_fontsize(fontsize)
    if show_plot:
        plt.show()
    return ax, data_avg
