import matplotlib.pyplot as plt
from powersimdata.input.helpers import get_plant_id_for_resources_in_area
from powersimdata.scenario.check import _check_scenario_is_in_analyze_state


def plot_scatter_capacity_vs_cost_curve_slope(
    scenario,
    area,
    resources,
    area_type=None,
    markersize=50,
    fontsize=20,
    title=None,
    show_plot=True,
):
    """Generate for a given scenario the scatter plot of the capacity (x-axis) vs
    cost curve slope (y-axis) of generators located in area and fueled by resources

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance
    :param str area: one of *loadzone*, *state*, *state abbreviation*,
        *interconnect*, *'all'*
    :param str/list resources: one or a list of resources.
    :param str area_type: one of *'loadzone'*, *'state'*, *'state_abbr'*,
        *'interconnect'*
    :param int/float markersize: marker size, default to 50.
    :param int/float fontsize: font size, default to 20.
    :param str title: user specified figure title, default to None.
    :param bool show_plot: show the plot or not, default to True.
    :return: (*tuple*) -- the first entry is matplotlib.axes.Axes object of the plot,
        the second entry is the capacity weighted average of cost curve slopes over the
        selected time range.
    :raises TypeError:
        if markersize is not an integer or a float and/or
        if fontsize is not an integer or a float and/or
        if title is provided but not in a string format.
    """
    _check_scenario_is_in_analyze_state(scenario)
    if not isinstance(markersize, (int, float)):
        raise TypeError("markersize should be either an integer or a float")
    if not isinstance(fontsize, (int, float)):
        raise TypeError("fontsize should be either an integer or a float")
    if title is not None and not isinstance(title, str):
        raise TypeError("title should be a string")
    plant_id = get_plant_id_for_resources_in_area(
        scenario, area, resources, area_type=area_type
    )
    grid = scenario.state.get_grid()
    plant_df = grid.plant.loc[plant_id]
    cost_df = grid.gencost["after"].loc[plant_id]
    slope = (cost_df["f2"] - cost_df["f1"]) / (cost_df["p2"] - cost_df["p1"])
    total_cap = plant_df["Pmax"].sum()
    if total_cap == 0:
        data_avg = 0
    else:
        data_avg = (plant_df["Pmax"] * slope).sum() / total_cap

    _, ax = plt.subplots(figsize=[20, 10])
    ax.scatter(plant_df["Pmax"], slope, s=markersize)
    ax.plot(plant_df["Pmax"], [data_avg] * len(plant_df.index), c="red")
    ax.grid()
    if title is None:
        ax.set_title(
            f'{area} {" ".join(resources) if isinstance(resources, list) else resources}'
        )
    else:
        ax.set_title(title)
    ax.set_xlabel("Capacity (MW)")
    ax.set_ylabel("Slope")
    for item in (
        [ax.title, ax.xaxis.label, ax.yaxis.label]
        + ax.get_xticklabels()
        + ax.get_yticklabels()
    ):
        item.set_fontsize(fontsize)
    if show_plot:
        plt.show()
    return ax, data_avg
