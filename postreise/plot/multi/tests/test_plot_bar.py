from postreise.plot.multi.plot_bar import (
    _construct_bar_ax_data,
    _get_bar_display_val,
    _get_bar_resource_types,
)
from postreise.plot.multi.tests.mock_graph_data import create_mock_graph_data

# Since these are unit tests we're intentionally not testing methods that only have visualization code


def test_construct_bar_ax_data_fills_in_missing_resources_with_0():
    ax_data_list = _construct_bar_ax_data("Washington", create_mock_graph_data(), None)
    assert ax_data_list[1]["labels"] == ["Wind", "Solar", "Coal", "Hydro"]
    assert ax_data_list[1]["values"] == {
        "2016 Simulated Base Case": [0, 1, 5, 4],
        "2016 NREL Data": [2, 1, 3, 4],
    }


def test_construct_bar_ax_data():
    ax_data_list = _construct_bar_ax_data("Washington", create_mock_graph_data(), None)
    expected_output = [
        {
            "title": "Generation (TWh)",
            "labels": ["Wind", "Solar", "Coal", "Hydro"],
            "values": {
                "2016 Simulated Base Case": [0, 1, 4, 5],
                "2016 NREL Data": [0, 1, 4, 5],
            },
            "unit": "TWh",
        },
        {
            "title": "Capacity (GW)",
            "labels": ["Wind", "Solar", "Coal", "Hydro"],
            "values": {
                "2016 Simulated Base Case": [0, 1, 5, 4],
                "2016 NREL Data": [2, 1, 3, 4],
            },
            "unit": "GW",
        },
    ]
    assert ax_data_list == expected_output


def test_construct_bar_ax_data_with_user_set_resource_types():
    ax_data_list = _construct_bar_ax_data(
        "Washington", create_mock_graph_data(), ["wind", "solar"]
    )
    expected_output = [
        {
            "title": "Generation (TWh)",
            "labels": ["Wind", "Solar"],
            "values": {"2016 Simulated Base Case": [0, 1], "2016 NREL Data": [0, 1]},
            "unit": "TWh",
        },
        {
            "title": "Capacity (GW)",
            "labels": ["Wind", "Solar"],
            "values": {"2016 Simulated Base Case": [0, 1], "2016 NREL Data": [2, 1]},
            "unit": "GW",
        },
    ]
    assert ax_data_list == expected_output


def test_get_bar_resource_types():
    resource_types = _get_bar_resource_types("Washington", create_mock_graph_data())
    assert resource_types == ["wind", "solar", "coal", "hydro"]


def test_get_bar_resource_types_does_not_have_duplicates():
    resource_types = _get_bar_resource_types("Washington", create_mock_graph_data())
    assert resource_types.sort() == list(set(resource_types)).sort()


def test_get_bar_resource_types_includes_resource_types_only_present_in_some_scenarios():
    resource_types = _get_bar_resource_types("Washington", create_mock_graph_data())
    assert "wind" in resource_types


def test_get_bar_resource_types_handles_resource_types_not_found_in_known_resource_types():
    mock_graph_data = create_mock_graph_data()
    mock_graph_data["87"]["gen"]["data"]["Washington"] = {
        "cereal": 1,
        "coal": 2,
        "milk": 1,
        "bananas": 3,
    }
    resource_types = _get_bar_resource_types("Washington", mock_graph_data)
    assert resource_types == [
        "wind",
        "solar",
        "coal",
        "hydro",
        "bananas",
        "cereal",
        "milk",
    ]


def test_get_bar_display_val_greater_than_ten():
    val = _get_bar_display_val(10.456)
    assert val == 10


def test_get_bar_display_val_less_than_ten():
    val = _get_bar_display_val(3.456)
    assert val == 3.5


def test_get_bar_display_val_zero():
    val = _get_bar_display_val(0)
    assert val == 0
