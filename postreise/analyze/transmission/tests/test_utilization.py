import pandas as pd
from pandas.testing import assert_frame_equal
from powersimdata.input.tests.test_helpers import check_dataframe_matches
from powersimdata.tests.mock_grid import MockGrid

from postreise.analyze.transmission.utilization import (
    _count_hours_gt_threshold,
    generate_cong_stats,
    get_utilization,
)

mock_branch = {
    "branch_id": [101, 102],
    "branch_device_type": ["Line"] * 2,
    "rateA": [20, 10],
    "from_lat": [47, 47],
    "from_lon": [122, 122],
    "to_lat": [47.12, 46.33],
    "to_lon": [122.23, 121.11],
}

mock_grid = MockGrid(grid_attrs={"branch": mock_branch})

mock_pf = pd.DataFrame(
    {
        101: [12, -8, -18, 2],
        102: [1, 8, 9, 6],
    },
    index=pd.date_range(start="2016-01-01", periods=4, freq="H"),
)


def test_get_utilization():
    expected = pd.DataFrame(
        {101: [0.6, 0.4, 0.9, 0.1], 102: [0.1, 0.8, 0.9, 0.6]}, index=mock_pf.index
    )
    check_dataframe_matches(expected, get_utilization(mock_grid.branch, mock_pf))


def test_get_utilization_median():
    expected = pd.DataFrame({101: [0.5], 102: [0.7]})
    check_dataframe_matches(
        expected,
        get_utilization(mock_grid.branch, mock_pf, median=True),
    )


def test_count_hours_gt_threshold():
    threshold = 0.25
    expected = pd.Series(data=[3, 3], index=[101, 102])

    utilization = get_utilization(mock_grid.branch, mock_pf)
    assert _count_hours_gt_threshold(utilization, threshold).equals(expected)


def test_generate_cong_stats():
    util = [0.5, 0.75, 0.85]
    threshold = [0.5, 0.25, 0.05]
    n = len(mock_pf)

    expected = pd.DataFrame(
        {
            "capacity": [20.0, 10.0],
            "branch_device_type": ["Line"] * 2,
            "per_util1": [2 / n, 3 / n],
            "per_util2": [1 / n, 2 / n],
            "per_util3": [1 / n, 1 / n],
            "bind": [0, 0],
            "risk": [-18.0, 17.0],
            "uflag1": [1, 1],
            "uflag2": [1, 1],
            "uflag3": [1, 1],
            "sumflag": [3, 3],
        },
        index=[101, 102],
    )
    expected.index.name = "branch_id"
    statistics = generate_cong_stats(
        mock_pf, mock_grid.branch, util=util, threshold=threshold
    )
    assert_frame_equal(expected, statistics.drop("dist", axis=1))
