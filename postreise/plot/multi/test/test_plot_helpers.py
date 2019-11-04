import pytest

from postreise.plot.multi.constants import ZONES
from postreise.plot.multi.test.mock_graph_data import create_mock_graph_data
from postreise.plot.multi.test.mock_data_chart import create_mock_data_chart
from postreise.plot.multi.plot_helpers import handle_plot_inputs, handle_shortfall_inputs, _format_scenario_data, unit_conversion

# Since these are unit tests we're intentionally not testing methods that pull in data
# handle_plot_inputs has more functionality than just pulling in data so we test that

def test_handle_plot_inputs():
    mock_graph_data = create_mock_graph_data()
    zone_list, graph_data = handle_plot_inputs('Western', None, mock_graph_data)
    assert zone_list == ZONES['Western']
    assert graph_data == mock_graph_data

def test_handle_shortfall_inputs():
    mock_graph_data = create_mock_graph_data()
    dummy_baselines = {'b': 1}
    dummy_targets = {'t': 2}
    dummy_demand = {'d': 9999}
    zone_list, graph_data, baselines, targets, demand = handle_shortfall_inputs('Western', None, mock_graph_data, False, dummy_baselines, dummy_targets, dummy_demand)
    assert zone_list == ZONES['Western']
    assert graph_data == mock_graph_data
    assert baselines == dummy_baselines
    assert targets == dummy_targets
    assert demand == dummy_demand

def test_handle_plot_inputs_throws_valueError_for_incorrect_interconnect():
    with pytest.raises(ValueError):
        handle_plot_inputs('The Moon', None, create_mock_graph_data())

def test_handle_plot_inputs_throws_valueError_if_missing_both_scenario_ids_and_custom_data():
    with pytest.raises(ValueError):
        handle_plot_inputs('Texas', None, None)

def test_format_scenario_data():
    formatted_scenario_data = _format_scenario_data(create_mock_data_chart(), '2016 Simulated Base Case')
    expected_result = create_mock_graph_data()['87']
    assert formatted_scenario_data == expected_result

def test_unit_conversion_increase_by_2():
    assert unit_conversion(2500000, 2) == 2.50

def test_unit_conversion_decrease_by_1():
    assert unit_conversion(0.32, -1) == 320.00
