from pprint import pprint

import pytest
from postreise.plot.multi.constants import (BASELINES, CA_BASELINES,
                                            CA_TARGETS, DEMAND, TARGETS, ZONES)
from postreise.plot.multi.data.historical_2016_data import (
    HISTORICAL_WESTERN_GEN,
    HISTORICAL_WESTERN_CAP)
from postreise.plot.multi.plot_helpers import (_format_scenario_data,
                                               _make_empty_data,
                                               handle_plot_inputs,
                                               handle_shortfall_inputs,
                                               make_gen_cap_custom_data,
                                               unit_conversion)
from postreise.plot.multi.tests.mock_data_chart import create_mock_data_chart
from postreise.plot.multi.tests.mock_graph_data import create_mock_graph_data

# Since these are unit tests we're intentionally
# not testing methods that pull in data
# handle_plot_inputs has more functionality than just pulling in data
# so we test that


def test_handle_plot_inputs():
    mock_graph_data = create_mock_graph_data()
    zone_list, graph_data = handle_plot_inputs(
        'Western', None, None, mock_graph_data)
    assert zone_list == ZONES['Western']
    assert graph_data == mock_graph_data


def test_handle_plot_inputs_throws_valueError_for_incorrect_interconnect():
    with pytest.raises(ValueError):
        handle_plot_inputs('The Moon', None, None, create_mock_graph_data())


def test_handle_plot_inputs_throws_valueError_when_wrong_number_of_scenario_names():
    with pytest.raises(ValueError):
        handle_plot_inputs(
            'The Moon', ['123', '456'], ['Hist. Moon Cheese'], None)


def test_handle_plot_inputs_throws_valueError_if_not_enough_scenario_ids_or_custom_data():
    with pytest.raises(ValueError):
        handle_plot_inputs('Western', ['123'], None, custom_data=None)


def test_handle_shortfall_inputs_where_is_match_CA_is_false():
    baselines, targets, demand = handle_shortfall_inputs(
        False, None, None, None)
    assert baselines == BASELINES
    assert targets == TARGETS
    assert demand == DEMAND


def test_handle_shortfall_inputs_where_is_match_CA_is_true():
    baselines, targets, demand = handle_shortfall_inputs(
        True, None, None, None)
    assert baselines == CA_BASELINES
    assert targets == CA_TARGETS
    assert demand == DEMAND


def test_handle_shortfall_inputs_with_baseline_target_and_demand_params():
    dummy_baselines = {'b': 1}
    dummy_targets = {'t': 2}
    dummy_demand = {'d': 9999}
    baselines, targets, demand = handle_shortfall_inputs(
        False, dummy_baselines, dummy_targets, dummy_demand)
    assert baselines == dummy_baselines
    assert targets == dummy_targets
    assert demand == dummy_demand


def test_format_scenario_data():
    formatted_scenario_data = _format_scenario_data(
        create_mock_data_chart(), '2016 Simulated Base Case')
    expected_result = create_mock_graph_data()['87']
    assert formatted_scenario_data == expected_result


def test_unit_conversion_increase_by_2():
    assert unit_conversion(2500000, 2) == 2.50


def test_unit_conversion_decrease_by_1():
    assert unit_conversion(0.32, -1) == 320.00


def test_make_empty_data_with_western():
    data = _make_empty_data('Western')
    empty_resources = {'wind': 0, 'solar': 0, 'ng': 0, 'coal': 0,
                       'nuclear': 0, 'geothermal': 0, 'hydro': 0}
    expected_data = {'Arizona': empty_resources,
                     'California': empty_resources, 'Colorado': empty_resources,
                     'Idaho': empty_resources, 'Montana Western': empty_resources,
                     'Nevada': empty_resources, 'New Mexico Western': empty_resources,
                     'Oregon': empty_resources, 'Utah': empty_resources,
                     'Washington': empty_resources, 'Wyoming': empty_resources,
                     'El Paso': empty_resources, 'Western': empty_resources}

    assert data == expected_data


def test_make_empty_data_with_texas():
    data = _make_empty_data('Texas')
    empty_resources = {'wind': 0, 'solar': 0, 'ng': 0, 'coal': 0,
                       'nuclear': 0, 'geothermal': 0, 'hydro': 0}
    expected_data = {'Far West': empty_resources, 'North': empty_resources,
                     'West': empty_resources, 'South': empty_resources,
                     'North Central': empty_resources, 'South Central': empty_resources,
                     'Coast': empty_resources, 'East': empty_resources,
                     'Texas': empty_resources}

    assert data == expected_data


def test_make_gen_cap_custom_data_given_no_data():
    label = "my data"
    gen_cap_data = make_gen_cap_custom_data('Western', label)
    expected_gen_cap_data = {
        'label': label,
        'gen': {
            'label': 'Generation',
            'unit': 'TWh',
            'data': _make_empty_data('Western')
        },
        'cap': {
            'label': 'Capacity',
            'unit': 'GW',
            'data': _make_empty_data('Western')
        }
    }

    assert gen_cap_data == expected_gen_cap_data


def test_make_gen_cap_custom_data_given_cap_data():
    label = "my data"
    gen_cap_data = make_gen_cap_custom_data(
        'Western', label, cap_data=HISTORICAL_WESTERN_CAP)
    expected_gen_cap_data = {
        'label': label,
        'gen': {
            'label': 'Generation',
            'unit': 'TWh',
            'data': _make_empty_data('Western')
        },
        'cap': {
            'label': 'Capacity',
            'unit': 'GW',
            'data': HISTORICAL_WESTERN_CAP
        }
    }

    assert gen_cap_data == expected_gen_cap_data


def test_make_gen_cap_custom_data_given_gen_and_cap_data():
    label = "my data"
    gen_cap_data = make_gen_cap_custom_data(
        'Western', label, HISTORICAL_WESTERN_GEN, HISTORICAL_WESTERN_CAP)
    expected_gen_cap_data = {
        'label': label,
        'gen': {
            'label': 'Generation',
            'unit': 'TWh',
            'data': HISTORICAL_WESTERN_GEN
        },
        'cap': {
            'label': 'Capacity',
            'unit': 'GW',
            'data': HISTORICAL_WESTERN_CAP
        }
    }

    assert gen_cap_data == expected_gen_cap_data
