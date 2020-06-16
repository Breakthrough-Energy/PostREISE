from postreise.plot.multi.constants import ZONES
from postreise.plot.multi.plot_shortfall import (
    _construct_shortfall_ax_data,
    _construct_shortfall_data_for_western,
    _get_total_generated_renewables,
)
from postreise.plot.multi.tests.mock_graph_data import create_mock_graph_data

# Since these are unit tests we're intentionally not testing methods that only have visualization code


def test_construct_shortfall_ax_data():
    ax_data, shortfall_pct_list = _construct_shortfall_ax_data(
        "Washington",
        create_mock_graph_data(),
        is_match_CA=False,
        baseline=4,
        target=7,
        demand=20,
    )
    expected_data = {
        "2016 Simulated Base Case": {
            "2016 Renewables": 4,
            "Simulated increase in renewables": 2.0,
            "Missed target": 1,
        },
        "2016 NREL Data": {
            "2016 Renewables": 4,
            "Simulated increase in renewables": 2.0,
            "Missed target": 1,
        },
    }
    assert ax_data == expected_data
    assert shortfall_pct_list == [5.0, 5.0]


def test_construct_shortfall_ax_data_when_shortfall_is_zero():
    ax_data, shortfall_pct_list = _construct_shortfall_ax_data(
        "Washington",
        create_mock_graph_data(),
        is_match_CA=False,
        baseline=4,
        target=5,
        demand=20,
    )
    expected_data = {
        "2016 Simulated Base Case": {
            "2016 Renewables": 4,
            "Simulated increase in renewables": 2.0,
            "Missed target": 0,
        },
        "2016 NREL Data": {
            "2016 Renewables": 4,
            "Simulated increase in renewables": 2.0,
            "Missed target": 0,
        },
    }
    assert ax_data == expected_data
    assert shortfall_pct_list == [0.0, 0.0]


def test_construct_shortfall_ax_data_when_target_is_zero():
    ax_data, shortfall_pct_list = _construct_shortfall_ax_data(
        "Washington",
        create_mock_graph_data(),
        is_match_CA=False,
        baseline=4,
        target=0,
        demand=20,
    )
    expected_data = {
        "2016 Simulated Base Case": {
            "2016 Renewables": 4,
            "Simulated increase in renewables": 2.0,
            "Missed target": 0,
        },
        "2016 NREL Data": {
            "2016 Renewables": 4,
            "Simulated increase in renewables": 2.0,
            "Missed target": 0,
        },
    }
    assert ax_data == expected_data
    assert shortfall_pct_list == [0.0, 0.0]


def test_construct_shortfall_data_for_western_with_independent_scenario():
    mock_targets = {"Arizona": 12, "Colorado": 8, "Oregon": 10, "Western": 30}
    ax_data, shortfall_pct_list = _construct_shortfall_data_for_western(
        create_mock_graph_data(more_gen=True),
        is_match_CA=False,
        has_collaborative_scenarios=None,
        baseline=13,
        targets=mock_targets,
        demand=50,
    )
    expected_data = {
        "2016 Simulated Base Case": {
            "2016 Renewables": 13,
            # western target - shortfall - baseline
            "Simulated increase in renewables": 9.0,
            "Missed target": 8.0,
        },
        "2016 NREL Data": {
            "2016 Renewables": 13,
            # western target - shortfall - baseline
            "Simulated increase in renewables": 14.0,
            "Missed target": 3.0,
        },
    }
    assert ax_data == expected_data
    assert shortfall_pct_list == [16.0, 6.0]


def test_construct_shortfall_data_for_western_with_collaborative_scenarios():
    mock_targets = {"Arizona": 12, "Colorado": 8, "Oregon": 10, "Western": 30}
    collab = ["87", "2016_nrel"]
    ax_data, shortfall_pct_list = _construct_shortfall_data_for_western(
        create_mock_graph_data(more_gen=True),
        is_match_CA=False,
        has_collaborative_scenarios=collab,
        baseline=13,
        targets=mock_targets,
        demand=50,
    )
    expected_data = {
        "2016 Simulated Base Case": {
            "2016 Renewables": 13,
            # western target - shortfall - baseline
            "Simulated increase in renewables": 14.0,
            "Missed target": 3.0,
        },
        "2016 NREL Data": {
            "2016 Renewables": 13,
            # western target - shortfall - baseline
            "Simulated increase in renewables": 18.0,
            "Missed target": 0,
        },
    }
    assert ax_data == expected_data
    assert shortfall_pct_list == [6.0, 0.0]


def test_get_total_generated_renewables():
    total_renewables = _get_total_generated_renewables(
        "Arizona", {"coal": 4.0, "solar": 1.0, "hydro": 5.0}, is_match_CA=False
    )
    assert total_renewables == 1


def test_get_total_generated_renewables_for_CA():
    total_renewables = _get_total_generated_renewables(
        "California", {"coal": 4.0, "solar": 1.0, "hydro": 5.0}, is_match_CA=False
    )
    assert total_renewables == 33.045472


def test_get_total_generated_renewables_for_WA():
    total_renewables = _get_total_generated_renewables(
        "Washington", {"coal": 4.0, "solar": 1.0, "hydro": 5.0}, is_match_CA=False
    )
    assert total_renewables == 6


def test_get_total_generated_renewables_for_WA_with_is_match_CA():
    total_renewables = _get_total_generated_renewables(
        "Washington", {"coal": 4.0, "solar": 1.0, "hydro": 5.0}, is_match_CA=True
    )
    assert total_renewables == 1
