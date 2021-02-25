import pandas as pd

from postreise.plot.plot_bar_generation_vs_capacity import (
    _get_bar_display_val,
    make_gen_cap_custom_data,
)


def test_get_bar_display_val_greater_than_ten():
    val = _get_bar_display_val(10.456)
    assert val == 10


def test_get_bar_display_val_less_than_ten():
    val = _get_bar_display_val(3.456)
    assert val == 3.5


def test_get_bar_display_val_zero():
    val = _get_bar_display_val(0)
    assert val == 0


def test_make_gen_cap_custom_data_given_no_data():
    label = "my data"
    gen_cap_data = make_gen_cap_custom_data("Western", label)
    expected_gen_cap_data = {
        "name": label,
        "gen": {
            "label": "Generation",
            "unit": "TWh",
            "data": {"Western": {}},
        },
        "cap": {"label": "Capacity", "unit": "GW", "data": {"Western": {}}},
    }

    assert gen_cap_data == expected_gen_cap_data


def test_make_gen_cap_custom_data_given_cap_data():
    label = "my data"
    mock_data = pd.DataFrame(
        {
            "Western": [10, 10, 10, 10],
        },
        index=["wind", "solar", "hydro", "coal"],
    )
    gen_cap_data = make_gen_cap_custom_data("Western", label, cap_data=mock_data)
    expected_gen_cap_data = {
        "name": label,
        "gen": {
            "label": "Generation",
            "unit": "TWh",
            "data": {"Western": {}},
        },
        "cap": {"label": "Capacity", "unit": "GW", "data": mock_data.to_dict()},
    }

    assert gen_cap_data == expected_gen_cap_data


def test_make_gen_cap_custom_data_given_gen_and_cap_data():
    label = "my data"
    mock_gen_data = pd.DataFrame(
        {
            "Western": [100, 100, 100, 100],
        },
        index=["wind", "solar", "hydro", "coal"],
    )
    mock_cap_data = pd.DataFrame(
        {
            "Western": [10, 10, 10, 10],
        },
        index=["wind", "solar", "hydro", "coal"],
    )
    gen_cap_data = make_gen_cap_custom_data(
        "Western", label, mock_gen_data, mock_cap_data
    )
    expected_gen_cap_data = {
        "name": label,
        "gen": {"label": "Generation", "unit": "TWh", "data": mock_gen_data.to_dict()},
        "cap": {"label": "Capacity", "unit": "GW", "data": mock_cap_data.to_dict()},
    }

    assert gen_cap_data == expected_gen_cap_data
