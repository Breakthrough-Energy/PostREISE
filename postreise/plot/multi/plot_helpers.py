import matplotlib.pyplot as plt
from powersimdata.scenario.scenario import Scenario

from postreise.plot.analyze_pg import AnalyzePG as apg
from postreise.plot.multi.constants import (
    BASELINES,
    CA_BASELINES,
    CA_TARGETS,
    DEMAND,
    SCENARIO_RESOURCE_TYPES,
    TARGETS,
    ZONES,
)


def handle_plot_inputs(interconnect, time, scenario_ids, scenario_names, custom_data):
    """Check input validity for plotting code, fetches data if necessary.

    :param str interconnect: either 'Western' or 'Texas'
    :param tuple time: time related parameters.
        1st element is the starting date.
        2nd element is the ending date (left out).
        3rd element is the timezone, only *'utc'*, *'US/Pacific'* and *'local'* are
        possible.
        4th element is the frequency, which can be *'H'* (hour), *'D'* (day), *'W'*
        (week) or *'auto'*.
    :param list scenario_ids: list of scenario ids.
    :param list scenario_names: list of scenario names of same len as scenario ids.
    :param dict custom_data: hand-generated data.
    :raises ValueError: if interconnect is not Western or Texas, the number of scenario
        names is not equal to number of scenario ids, the number of scenario ids and/or
        custom data is less than two.
    :return: (*list*) -- list of all zones in interconnect and formatted graph data
    """
    if interconnect in ZONES.keys():
        zone_list = ZONES[interconnect]
    else:
        raise ValueError("ERROR: interconnect must be one of Western or Texas")
    if scenario_ids is None:
        scenario_ids = []
    if scenario_names is not None and len(scenario_names) != len(scenario_ids):
        raise ValueError(
            "ERROR: if scenario names are provided, number of scenario names must \
            match number of scenario ids"
        )
    if custom_data is None:
        custom_data = {}
    if len(scenario_ids) + len(custom_data) <= 1:
        raise ValueError(
            "ERROR: must include at least two scenario ids and/or custom data"
        )

    scenario_data = _get_scenario_data(time, scenario_ids, scenario_names, zone_list)
    graph_data = dict(scenario_data, **custom_data)
    return zone_list, graph_data


def handle_shortfall_inputs(is_match_CA, baselines, targets, demand):
    """Fetche baseline, target, and demand data if necessary.

    :param bool is_match_CA: calculate shortfall using special rules that apply when
        all zones match California goals
    :param dict baselines: baseline renewables generation for each zone.
    :param dict targets: target renewables renewable generation for each zone.
    :param dict demand: total demand for each zone.
    :return: (*tuple*) -- baselines, targets, demand.
    """
    if baselines is None:
        baselines = CA_BASELINES if is_match_CA else BASELINES
    if targets is None:
        targets = CA_TARGETS if is_match_CA else TARGETS
    if demand is None:
        demand = DEMAND

    return baselines, targets, demand


def make_gen_cap_custom_data(interconnect, label, gen_data=None, cap_data=None):
    """Helper function to create custom data formatted for plotting funcitons. You will
    still need to wrap this in a dict to use it. This lets us handle multiple custom
    scenarios.

    :param str interconnect: the interconnect - 'Western' or 'Texas'.
    :param str label: the name of the custom scenario to be shown in the plot.
    :param dict gen_data: generation data in TWh, defaults to None
    :param dict cap_data: capacity data in GW, defaults to None
    :raises ValueError: if interconnect is not 'Western' or 'Texas'.
    :return: (*dict*) --  of custom data.
    """
    if interconnect not in ZONES.keys():
        raise ValueError("ERROR: zone must be one of Western or Texas")

    gen_data = gen_data if gen_data is not None else _make_empty_data(interconnect)
    cap_data = cap_data if cap_data is not None else _make_empty_data(interconnect)

    return {
        "label": label,
        "gen": {"label": "Generation", "unit": "TWh", "data": gen_data},
        "cap": {"label": "Capacity", "unit": "GW", "data": cap_data},
    }


def _make_empty_data(interconnect):
    """Make empty data for a custom data dict.

    :param str interconnect: the interconnect - 'Western' or 'Texas'
    :return: (*dict*) -- empty dictionary.
    """
    return {
        zone: {r: 0 for r in SCENARIO_RESOURCE_TYPES} for zone in ZONES[interconnect]
    }


def unit_conversion(val, change):
    """Convert between metric units and rounds to two decimal places.

    :param float val: the value to change.
    :param int change: the distance between the starting unit and the desired unit.
        e.g. 2,500,000 MWh to TWh would be unit_conversion(2500000, 2), resulting in
        2.50 TWh
    :return: (*float*) -- the new converted value
    """
    return round(val / 1000 ** change, 2)


def _get_scenario_data(time, scenario_ids, scenario_names, zone_list):
    """Fetches data for each scenario and then formats it so it's usable by our
    plotting code

    :param tuple time: time related parameters.
        1st element is the starting date.
        2nd element is the ending date (left out).
        3rd element is the timezone, only *'utc'*, *'US/Pacific'* and *'local'* are
        possible.
        4th element is the frequency, which can be *'H'* (hour), *'D'* (day), *'W'*
        (week) or *'auto'*.
    :param list scenario_ids: optional list of scenario ids.
    :param list scenario_names: list of scenario names of same len as scenario ids.
    :param list zone_list: list of load zones.
    :return: (*dict*) -- formatted scenario data.
    """
    scenario_data = dict()
    for i in range(len(scenario_ids)):
        sid = scenario_ids[i]
        data_chart, scenario_name = _get_data_chart_from_scenario(sid, time, zone_list)
        if scenario_names is not None:
            scenario_name = scenario_names[i]
        scenario_data[sid] = _format_scenario_data(data_chart, scenario_name)

    return scenario_data


def _get_data_chart_from_scenario(scenario_id, time, zone_list):
    """Use :class:`postreise.plot.analyze_pg.AnalyzePG` to fetch and format data for a
    scenario

    :param str scenario_id: the id of the scenario to fetch.
    :param list zone_list: list of zone names
    :return: (*tuple*) -- scenario data chart and scenario name.

    .. todo::
        do this ourselves instead of using apg as a middle man
    """
    scenario = Scenario(scenario_id)
    scenario_name = scenario.info["name"]
    data_chart = apg(
        scenario, time, zone_list, SCENARIO_RESOURCE_TYPES, "chart", normalize=False
    ).get_data()
    plt.close("all")
    return data_chart, scenario_name


def _format_scenario_data(data_chart, scenario_name):
    """Take a data chart from a scenario and transforms it into a format usable by our
    plotting code.

    :param dict data_chart: scenario data chart generated by
        :class:`postreise.plot.analyze_pg.AnalyzePG`.
    :param str scenario_name: name of the scenario.
    :return: (*dict*) -- formatted scenario data
    """
    formatted_data = {
        "label": scenario_name,
        "gen": {"label": "Generation", "unit": "TWh", "data": {}},
        "cap": {"label": "Capacity", "unit": "GW", "data": {}},
    }

    gen_data = {}
    cap_data = {}
    for zone in data_chart.keys():
        gen_data[zone] = {}
        cap_data[zone] = {}

        for resource in data_chart[zone]["Generation"].to_dict().keys():
            gen_data[zone][resource] = unit_conversion(
                sum(data_chart[zone]["Generation"][resource].to_dict().values()), 2
            )  # MWh to TWh
            cap_data[zone][resource] = unit_conversion(
                data_chart[zone]["Capacity"][resource], 1
            )  # MW to GW

    formatted_data["gen"]["data"] = gen_data
    formatted_data["cap"]["data"] = cap_data

    return formatted_data
