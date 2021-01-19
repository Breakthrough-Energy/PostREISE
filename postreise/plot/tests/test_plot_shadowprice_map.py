import random

import pandas as pd

from postreise.plot.plot_shadowprice_map import (
    _construct_branch_data,
    _construct_bus_data,
    _get_bus_legend_bars_and_labels,
    _get_lmp_split_points,
)


def test_construct_bus_data():
    hour = "2016-08-04 23:00:00"
    wrong_hour = "2016-08-04 20:00:00"
    mock_bus_map = pd.DataFrame(
        {1: {"x": 1, "y": 1}, 2: {"x": 2, "y": 2}, 3: {"x": 3, "y": 3}}
    ).T
    mock_lmp = pd.DataFrame(
        {
            1: {wrong_hour: 22, hour: 18.2},
            2: {wrong_hour: -1.2, hour: 5.5},
            3: {wrong_hour: 8.0, hour: 8.3},
        }
    )
    mock_split_points = [0, 10, 20]

    lmp_split_points, bus_segments = _construct_bus_data(
        mock_bus_map, mock_lmp, mock_split_points, hour
    )

    expected_bus_segments = [
        {2: {"lmp": 5.5, "x": 2.0, "y": 2.0}, 3: {"lmp": 8.3, "x": 3.0, "y": 3.0}},
        {1: {"lmp": 18.2, "x": 1.0, "y": 1.0}},
    ]

    assert lmp_split_points == mock_split_points
    bus_segments_as_dicts = [seg.T.to_dict() for seg in bus_segments]
    assert bus_segments_as_dicts == expected_bus_segments


def test_get_lmp_split_points_with_min_lmp_below_neg_one():
    lmp_vals = [-5, -2, 0, 2, 2, 6, 6, 10, 10, 12, 12, 14, 14, 16, 16, 18, 18, 20, 20]
    random.shuffle(lmp_vals)
    mock_bus_map = pd.DataFrame(
        {bus_id: {"lmp": lmp} for bus_id, lmp in zip(range(len(lmp_vals)), lmp_vals)}
    ).T

    lmp_split_points = _get_lmp_split_points(mock_bus_map)
    assert lmp_split_points == [-5, -1, 1, 6.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20]


def test_get_lmp_split_points_with_min_between_neg_one_and_one():
    lmp_vals = list(range(18))  # starts at 0
    random.shuffle(lmp_vals)
    mock_bus_map = pd.DataFrame(
        {bus_id: {"lmp": lmp} for bus_id, lmp in zip(range(len(lmp_vals)), lmp_vals)}
    ).T

    lmp_split_points = _get_lmp_split_points(mock_bus_map)
    assert lmp_split_points == [0, 1, 3.0, 5.0, 7.0, 9.0, 11.0, 13.0, 15.0, 17]


def test_get_lmp_split_points_with_min_lmp_more_than_one():
    lmp_vals = list(range(100, 1001))
    random.shuffle(lmp_vals)
    mock_bus_map = pd.DataFrame(
        {bus_id: {"lmp": lmp} for bus_id, lmp in zip(range(len(lmp_vals)), lmp_vals)}
    ).T

    lmp_split_points = _get_lmp_split_points(mock_bus_map)
    assert lmp_split_points == [
        100,
        200.0,
        300.0,
        400.0,
        500.0,
        600.0,
        700.0,
        800.0,
        900.0,
        1000,
    ]


def test_construct_branch_data():
    hour = "2016-08-04 23:00:00"
    wrong_hour = "2016-08-04 20:00:00"
    mock_branch_map = pd.DataFrame(
        {
            1: {
                "from_x": 1,
                "to_x": 10,
                "from_y": 1,
                "to_y": 10,
                "branch_device_type": "Line",
            },
            2: {
                "from_x": 2,
                "to_x": 20,
                "from_y": 2,
                "to_y": 20,
                "branch_device_type": "Line",
            },
            3: {
                "from_x": 3,
                "to_x": 30,
                "from_y": 3,
                "to_y": 30,
                "branch_device_type": "Line",
            },
            4: {
                "from_x": 4,
                "to_x": 40,
                "from_y": 4,
                "to_y": 40,
                "branch_device_type": "Stick",
            },
        }
    ).T
    mock_cong = pd.DataFrame(
        {
            1: {wrong_hour: 2, hour: 2},
            2: {wrong_hour: 2, hour: 1e-7},
            3: {wrong_hour: 1e-7, hour: 8},
            4: {wrong_hour: 1e-7, hour: 3},
        }
    )

    branches_selected = _construct_branch_data(mock_branch_map, mock_cong, hour)
    expected_branches_selected = {
        1: {
            "from_x": 1,
            "to_x": 10,
            "from_y": 1,
            "to_y": 10,
            "branch_device_type": "Line",
            "medianval": 2.0,
        },
        3: {
            "from_x": 3,
            "to_x": 30,
            "from_y": 3,
            "to_y": 30,
            "branch_device_type": "Line",
            "medianval": 8.0,
        },
    }
    assert branches_selected.T.to_dict() == expected_branches_selected


def test_get_bus_legend_bars_and_labels():
    mock_split_points = [-1, 1, 2, 3, 4]
    bars, bar_length_sum, labels = _get_bus_legend_bars_and_labels(mock_split_points)

    assert bars == {"0": [2], "1": [1], "2": [1], "3": [1]}
    assert bar_length_sum == 5
    assert labels == {0: "-1", 2: "1", 3: "2", 4: "3", 5: "4"}


def test_get_bus_legend_bars_and_labels_with_rounding():
    mock_split_points = [-1, 1, 1.9999, 3, 4]
    bars, bar_length_sum, labels = _get_bus_legend_bars_and_labels(mock_split_points)

    assert bars == {"0": [2], "1": [1], "2": [1.0001], "3": [1]}
    assert bar_length_sum == 5.0001
    assert labels == {0: "-1", 2: "1", 3: "1.9999", 4.0001: "3", 5.0001: "4"}


def test_get_bus_legend_bars_and_labels_clamps_large_numbers():
    mock_split_points = [-500, 100, 200, 300, 400]
    bars, bar_length_sum, labels = _get_bus_legend_bars_and_labels(mock_split_points)

    assert bars == {"0": [5], "1": [5], "2": [5], "3": [5]}
    assert bar_length_sum == 20
    assert labels == {0: "-500", 5: "100", 10: "200", 15: "300", 20: "400"}


def test_get_bus_legend_bars_and_labels_min_bar_len_is_one():
    mock_split_points = [-0.9, 0.1, 0.2, 0.3, 0.4]
    bars, bar_length_sum, labels = _get_bus_legend_bars_and_labels(mock_split_points)

    assert bars == {"0": [1], "1": [1], "2": [1], "3": [1]}
    assert bar_length_sum == 4.0
    assert labels == {0: "-0.9", 1: "0.1", 2: "0.2", 3: "0.3", 4: "0.4"}
