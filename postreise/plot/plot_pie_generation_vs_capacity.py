import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from powersimdata.network.model import ModelImmutables, area_to_loadzone
from powersimdata.scenario.scenario import Scenario

from postreise.analyze.generation.capacity import sum_capacity_by_type_zone
from postreise.analyze.generation.summarize import sum_generation_by_type_zone


def plot_pie_generation_vs_capacity(
    areas,
    area_types=None,
    scenario_ids=None,
    scenario_names=None,
    time_range=None,
    time_zone=None,
    custom_data=None,
    resource_labels=None,
    resource_colors=None,
    min_percentage=0,
):
    """Plot any number of scenarios as pie charts with two columns per scenario -
    generation and capacity.

    :param list/str areas: name of the area to focus on. Could be a loadzone, a state, a
        country, etc. This will depend on the grid model.
    :param list/str area_types: area supported by the grid model. See the
        :func:`powersimdata.network.model.area_to_loadzone` function for more details.
    :param int/list/str scenario_ids: list of scenario id(s), defaults to None.
    :param list/str scenario_names: list of scenario name(s) of same len as scenario
        ids, defaults to None
    :param tuple time_range: [start_timestamp, end_timestamp] where each time stamp
        is pandas.Timestamp/numpy.datetime64/datetime.datetime. If None, the entire
        time range is used for the given scenario.
    :param str time_zone: new time zone, defaults to None, which uses UTC.
    :param list custom_data: list of dictionaries with each element being
        hand-generated data as returned by
        :func:`postreise.plot_bar_generation_vs_capacity.make_gen_cap_custom_data`,
        defaults to None.
    :param dict resource_labels: a dictionary with keys being resource types and values
        being labels, which is used to customize resource labels for selected resource
        types to show in the plots. Defaults to None, in which case a default set of
        labels is used.
    :param dict resource_colors: a dictionary with keys being resource types and values
        being colors, which is used to customize resource colors for selected resource
        types to show in the plots. Defaults to None, in which case a default set of
        colors is used.
    :param float min_percentage: roll up small pie pieces into a single category,
        resources with percentage less than the set value will be pooled together,
        defaults to 0.
    :raises ValueError:
        if length of ``area_types`` and ``areas`` is different.
        if length of ``scenario_names`` and ``scenario_ids`` is different.
        if less than two ``scenario_ids`` and/or ``custom_data`` in total is provided.
    :raises TypeError:
        if ``resource_labels`` are provided but not in a dict format.
        if ``resource_colors`` are provided but not in a dict format.

    .. note::
        if one wants to plot scenario data and custom data together, custom data MUST be
        in TWh for generation and GW for capacity in order to conduct appropriate
        comparison.
    """
    if isinstance(areas, str):
        areas = [areas]
    if isinstance(area_types, str):
        area_types = [area_types]
    if not area_types:
        area_types = [None] * len(areas)
    if len(areas) != len(area_types):
        raise ValueError("area_types and areas must have same length")

    if not scenario_ids:
        scenario_ids = []
    if isinstance(scenario_ids, (int, str)):
        scenario_ids = [scenario_ids]
    if isinstance(scenario_names, str):
        scenario_names = [scenario_names]
    if scenario_names and len(scenario_names) != len(scenario_ids):
        raise ValueError("scenario_names and scenario_ids must have same length")
    if not custom_data:
        custom_data = {}
    if len(scenario_ids) + len(custom_data) <= 1:
        raise ValueError(
            "scenario_ids and/or custom_data must have at least two elements"
        )
    if not resource_labels:
        resource_labels = dict()
    if not isinstance(resource_labels, dict):
        raise TypeError("resource_labels must be a dict")
    if not resource_colors:
        resource_colors = dict()
    if not isinstance(resource_colors, dict):
        raise TypeError("resource_colors must be a dict")

    all_loadzone_data = {}
    scenario_data = {}
    for i, sid in enumerate(scenario_ids):
        scenario = Scenario(sid)
        mi = ModelImmutables(
            scenario.info["grid_model"], interconnect=scenario.info["interconnect"]
        )
        all_loadzone_data[sid] = {
            "gen": sum_generation_by_type_zone(scenario, time_range, time_zone).rename(
                columns=mi.zones["id2loadzone"]
            ),
            "cap": sum_capacity_by_type_zone(scenario).rename(
                columns=mi.zones["id2loadzone"]
            ),
        }
        scenario_data[sid] = {
            "name": scenario_names[i] if scenario_names else scenario.info["name"],
            "grid_model": mi.model,
            "type2color": {**mi.plants["type2color"], **resource_colors},
            "type2label": {**mi.plants["type2label"], **resource_labels},
            "gen": {"label": "Generation", "unit": "TWh", "data": {}},
            "cap": {"label": "Capacity", "unit": "GW", "data": {}},
        }
    for area, area_type in zip(areas, area_types):
        for sid in scenario_ids:
            loadzone = list(
                area_to_loadzone(scenario_data[sid]["grid_model"], area, area_type)
            )
            scenario_data[sid]["gen"]["data"][area] = (
                all_loadzone_data[sid]["gen"][loadzone]
                .sum(axis=1)
                .divide(1e6)
                .astype("float")
                .round(2)
                .to_dict()
            )
            scenario_data[sid]["cap"]["data"][area] = (
                all_loadzone_data[sid]["cap"][loadzone]
                .sum(axis=1)
                .divide(1e3)
                .astype("float")
                .round(2)
                .to_dict()
            )
    for c_data in custom_data:
        scenario_data[c_data["name"]] = c_data

    for area in areas:
        ax_data_list = []
        for sd in scenario_data.values():
            for side in ["gen", "cap"]:
                ax_data, labels = _roll_up_small_pie_wedges(
                    sd[side]["data"][area], sd["type2label"], min_percentage
                )

                ax_data_list.append(
                    {
                        "title": "{0}\n{1}".format(sd["name"], sd[side]["label"]),
                        "labels": labels,
                        "values": list(ax_data.values()),
                        "colors": [sd["type2color"][r] for r in ax_data.keys()],
                        "unit": sd[side]["unit"],
                    }
                )

        _construct_pie_visuals(area, ax_data_list)


def _roll_up_small_pie_wedges(resource_data, resource_label, min_percentage):
    """Combine small wedges into a single category. Removes wedges with value 0.

    :param dict resource_data: values for each resource type.
    :param dict resource_label: labels for each resource type.
    :param float min_percentage: roll up small pie pieces into a single category,
        resources with percentage less than the set value will be pooled together,
        defaults to 0.
    :return: (*dict*) -- updated axis data and a list of labels that includes the small
        category label if it exists
    """
    resource_list = list(resource_data.keys())
    total_resources = sum(resource_data.values())
    small_categories = []
    small_category_value = 0
    small_category_label = ""
    for resource in resource_list:
        percentage = round(resource_data[resource] / total_resources * 100, 1)
        if percentage == 0.0:
            resource_data.pop(resource)
        elif percentage <= min_percentage:
            small_categories.append(resource)
            small_category_label += "{0} {1}%\n".format(
                resource_label[resource], percentage
            )
            small_category_value += resource_data[resource]

    if len(small_categories) > 1:
        for resource in small_categories:
            resource_data.pop(resource)

    labels = [resource_label[resource] for resource in resource_data.keys()]

    if len(small_categories) > 1:
        resource_data["other"] = small_category_value
        labels.append(small_category_label)

    return resource_data, labels


def _construct_pie_visuals(zone, ax_data_list):
    """Plot formatted data.

    :param str zone: the zone name
    :param list ax_data_list: a list of dictionaries with keys being labels,
        values and colors.
    """
    rows = int(len(ax_data_list) / 2)
    fig, axes = plt.subplots(rows, 2, figsize=(20, 12 * rows))
    if rows > 1:
        axes = np.concatenate(axes)
    plt.suptitle(zone, fontsize=36, verticalalignment="bottom")

    for ax_data, ax in zip(ax_data_list, axes):
        df = pd.DataFrame({"": ax_data["values"]}, index=ax_data["labels"])
        df.plot(
            kind="pie",
            ax=ax,
            subplots=True,
            fontsize=18,
            autopct="%1.1f%%",
            startangle=180,
            pctdistance=0.55,
            colors=ax_data["colors"],
            wedgeprops={"edgecolor": "white", "linewidth": 6},
        )
        ax.set_title(ax_data["title"], fontsize=30)
        ax.get_legend().remove()
        ax.tick_params(axis="y", which="both", left=False)
        ax.add_artist(plt.Circle((0, 0), 0.70, fc="white"))
        ax.text(
            0,
            0,
            "{0}\n{1}".format(round(sum(ax_data["values"]), 1), ax_data["unit"]),
            fontsize=22,
            verticalalignment="center",
            horizontalalignment="center",
            weight="bold",
            color="lightgray",
        )

    plt.tight_layout()
    fig.subplots_adjust(hspace=-0.2)
