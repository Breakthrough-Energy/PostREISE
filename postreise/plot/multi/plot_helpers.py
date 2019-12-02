import matplotlib.pyplot as plt
from postreise.plot.analyze_pg import AnalyzePG as apg
from postreise.plot.multi.constants import (BASELINES, CA_BASELINES,
                                            CA_TARGETS, DEMAND,
                                            SCENARIO_RESOURCE_TYPES, TARGETS,
                                            ZONES)
from powersimdata.scenario.scenario import Scenario


def handle_plot_inputs(interconnect, time, scenario_ids, scenario_names, \
    custom_data):
    """Checks input validity for plotting code, fetches data if necessary

    :param interconnect: either 'Western' or 'Texas'
    :type interconnect: string
    :param scenario_ids: list of scenario ids
    :type scenario_ids: list(string)
    :param scenario_names: list of scenario names of same len as scenario ids
    :type scenario_names: list(string), None
    :param custom_data: hand-generated data
    :type custom_data: dict
    :raises ValueError: zone must be one of Western or Texas
    :raises ValueError: if scenario names are provided,
        number of scenario names must match number of scenario ids
    :raises ValueError: must include at least two scenario ids and/or custom
        data
    :return: list of all zones in interconnect and formatted graph data
        (scenario data and custom data combined into one dict)
    :rtype: list(string), dict {'scenario_id': {
        'label': 'scenario_name',
        'gen': {'label': 'Generation', 'unit': 'TWh', 'data': {'zone_name':
            {'resource_type': float value(s), ...}, ...}},
        'cap': {'label': 'Capacity', 'unit': 'GW', 'data': {'zone_name':
            {'resource_type': float value(s), ...}, ...}}},
        ...}
    """
    if interconnect in ZONES.keys():
        zone_list = ZONES[interconnect]
    else:
        raise ValueError('ERROR: zone must be one of Western or Texas')
    if scenario_ids is None:
        scenario_ids = []
    if scenario_names is not None and \
        len(scenario_names) != len(scenario_ids):
        raise ValueError('ERROR: if scenario names are provided, \
            number of scenario names must match number of scenario ids')
    if custom_data is None:
        custom_data = {}
    if len(scenario_ids) + len(custom_data) <= 1:
        raise ValueError("ERROR: must include at least two scenario ids \
            and/or custom data")

    scenario_data = _get_scenario_data(
        time, scenario_ids, scenario_names, zone_list)
    graph_data = dict(scenario_data, **custom_data)
    return (zone_list, graph_data)


def handle_shortfall_inputs(is_match_CA, baselines, targets, demand):
    """Fetches baseline, target, and demand data if necessary

    :param is_match_CA: calculate shortfall using special rules that apply
        when all zones match California goals
    :type is_match_CA: bool
    :param baselines: baseline renewables generation for each zone
    :type baselines: dict {zone_name: float generation in TWh}
    :param targets: target renewables renewable generation for each zone
    :type targets: dict {zone_name: float generation in TWh}
    :param demand: total demand for each zone
    :type demand: dict {zone_name: float generation in TWh}
    :raises ValueError: zone must be one of Western or Texas
    :raises ValueError: must include scenario ids and/or custom data
    :return: baselines, targets, demand
    :rtype: dict, dict, dict
    """
    if baselines is None:
        baselines = CA_BASELINES if is_match_CA else BASELINES
    if targets is None:
        targets = CA_TARGETS if is_match_CA else TARGETS
    if demand is None:
        demand = DEMAND

    return baselines, targets, demand


def unit_conversion(val, change):
    """Converts between metric units and rounds to two decimal places

    :param val: the value to change
    :type val: float
    :param change: the distance between the starting unit and the desired unit.
        eg 2,500,000 MWh to TWh would be unit_conversion(2500000, 2),
        resulting in 2.50 TWh
    :type change: int
    :return: the new converted value
    :rtype: float
    """
    return round(val/1000**change, 2)


def _get_scenario_data(time, scenario_ids, scenario_names, zone_list):
    """For each scenario, fetches data and then formats it
        so it's usable by our plotting code

    :param time: time related parameters. 1st element is the starting
        date. 2nd element is the ending date (left out). 3rd element is the
        timezone, only *'utc'*, *'US/Pacific'* and *'local'* are possible. 4th
        element is the frequency, which can be *'H'* (hour), *'D'* (day), *'W'*
         (week) or *'auto'*.
    :type time: tuple
    :param scenario_ids: optional list of scenario ids
    :type scenario_ids: list(string)
    :param scenario_names: list of scenario names of same len as scenario ids
    :type scenario_names: list(string), None
    :param zone_list:
    :type zone_list: list(string)
    :return: formatted scenario data
    :rtype: dict {'my_scenario_id': {
        'label': 'scenario_name',
        'gen': {'label': 'Generation', 'unit': 'TWh', 'data': {'zone_name':
            {'resource_type': value(s), ...}, ...}},
        'cap': { same as gen }},
        ...}
    """
    scenario_data = dict()
    for i in range(len(scenario_ids)):
        id = scenario_ids[i]
        data_chart, scenario_name = _get_data_chart_from_scenario(
            id, time, zone_list)
        if scenario_names is not None:
            scenario_name = scenario_names[i]
        scenario_data[id] = _format_scenario_data(data_chart, scenario_name)

    return scenario_data


def _get_data_chart_from_scenario(scenario_id, time, zone_list):
    """Uses apg to fetch and format data for a scenario

    :param scenario_id: the id of the scenario to fetch
    :type scenario_id: string
    :param zone_list: list of zone names
    :type zone_list: list(string)
    :return: scenario data chart generated by apg, scenario name
    :rtype: dict {'scenario_id': {
        'label': 'scenario_name',
        'gen': {'label': 'Generation', 'unit': 'TWh', 'data': {'zone_name':
            {'resource_type': flaot value(s), ...}, ...}},
        'cap': {'label': 'Capacity', 'unit': 'GW', 'data': {'zone_name':
            {'resource_type': flaot value(s), ...}, ...}}},
        ...},
        list(string)
    TODO do this ourselves instead of using apg as a middle man
    """
    scenario = Scenario(scenario_id)
    scenario_name = scenario.info['name']
    data_chart = apg(scenario,
                     time,
                     zone_list,
                     SCENARIO_RESOURCE_TYPES,
                     'chart', normalize=False).get_data()
    plt.close('all')
    return data_chart, scenario_name


def _format_scenario_data(data_chart, scenario_name):
    """Takes a data chart from a scenario and transforms it into a format
        usable by our plotting code

    :param data_chart: scenario data chart generated by apg, scenario name
    :type data_chart: dict {'zone_name': {'Generation/Capacity':
        {'resource_type': float value(s), ...}, ...}, ...}
    :param scenario_name: name of the scenario
    :type scenario_name: string
    :return: formatted scenario data
    :rtype: dict {
        'label': 'scenario_name',
        'gen': {'label': 'Generation', 'unit': 'TWh', 'data': {'zone_name':
            {'resource_type': float value(s), ...}, ...}},
        'cap': {'label': 'Capacity', 'unit': 'GW', 'data': {'zone_name':
            'resource_type': float value(s), ...}, ...}}}
    """
    formatted_data = {
        'label': scenario_name,
        'gen': {
            'label': 'Generation',
            'unit': 'TWh',
            'data': {}
        },
        'cap': {
            'label': 'Capacity',
            'unit': 'GW',
            'data': {}
        }
    }

    gen_data = {}
    cap_data = {}
    for zone in data_chart.keys():
        gen_data[zone] = {}
        cap_data[zone] = {}

        for resource in data_chart[zone]['Generation'].to_dict().keys():
            gen_data[zone][resource] = unit_conversion(
                sum(data_chart[zone]['Generation'][resource] \
                    .to_dict().values()), 2)  # MWh to TWh
            cap_data[zone][resource] = unit_conversion(
                data_chart[zone]['Capacity'][resource], 1)  # MW to GW

    formatted_data['gen']['data'] = gen_data
    formatted_data['cap']['data'] = cap_data

    return formatted_data
