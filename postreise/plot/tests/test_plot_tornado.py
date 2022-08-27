import pandas as pd
import pytest

from postreise.plot.plot_tornado import plot_tornado

data = {
    "Arizona": 25,
    "California": 8,
    "Colorado": 15,
    "Idaho": 5,
    "Montana Western": 35,
    "Nevada": 1,
    "New Mexico Western": 15,
    "Oregon": 10,
    "Utah": 0,
    "Washington": -15,
    "Wyoming": -6,
    "El Paso": -1,
}


def test_plot_tornado():
    plot_tornado("Test data", data, sorted=True, plot_show=False)


def _assert_error(err_msg, *args, **kwargs):
    with pytest.raises(TypeError) as excinfo:
        plot_tornado(*args, **kwargs)
    assert err_msg in str(excinfo.value)


def test_plot_tornado_argument_type():
    _assert_error("title must be a str", pd.DataFrame(), data)
    _assert_error("data must be a dict", "bad data", [1, 2, 3])
    _assert_error("all keys of data must be str", "Keys", {"a": 1, 2: 2})
    _assert_error("all values of data must be int or float", "S", {"a": 1, "b": "B"})
    _assert_error("sorted must be a bool", "bad keyword type", data, sorted="no")
    _assert_error("plot_show must be a bool", "same as above", data, plot_show="yes")
