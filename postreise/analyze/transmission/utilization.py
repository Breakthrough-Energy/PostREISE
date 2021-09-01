import numpy as np
import pandas as pd
from powersimdata.utility.distance import great_circle_distance


def get_utilization(branch, pf, median=False):
    """Generate utilization table to be used as input for congestion analyses.

    :param pandas.DataFrame branch: branch data frame.
    :param pandas.DataFrame pf: power flow data frame.
    :param boolean median: take medians of pf for utilization calculation
    :return: (*pandas.DataFrame*) -- power flow data frame (per-unit).
    """
    pf = pf.abs()
    if median:
        pf = pd.DataFrame(pf.median()).T

    return pf.divide(branch.rateA).replace(np.inf, 0)


def _count_hours_gt_threshold(utilization, threshold):
    """Calculate number of hours above a given utilization threshold.

    :param pandas.DataFrame utilization: normalized power flow data frame as returned
        by :func:`get_utilization`.
    :param float threshold: utilization threshold ([0,1]).
    :return: (*pandas.Series*) -- number of hours above utilization threshold.
    """
    return (utilization > threshold).sum()


def _flag(statistics, utilname, threshold, uflagname):
    """Flag branches that meet screening criteria.

    :param pandas.DataFrame statistics: congestion statistics as returned by
        :func:`generate_cong_stats`.
    :param string utilname: field with percent of time above ``threshold``.
    :param float threshold: threshold for percent time for flag level.
    :param string uflagname: name of flag.
    :return: (*pandas.DataFrame*) -- data frame with *'uflagname'*.
    """
    return (statistics[utilname] >= threshold).astype(int).rename(uflagname)


def generate_cong_stats(pf, branch, util=None, threshold=None):
    """Generate congestion/utilization statistics from powerflow data (WECC congestion
    reports' analyses are the inspiration for these analyses and are the source of the
    default parameters). The report is available `here
    <https://www.wecc.org/Reliability/TAS_PathReports_Combined_FINAL.pdf>`_.

    :param pandas.DataFrame pf: power flow data frame
    :param pandas.DataFrame branch: branch data frame
    :param list util: utilization (float) flag level 1, 2, 3. Default values are values
        used by WECC: 0.75, 0.9, 99.
    :param list threshold: threshold for proportion time, for flag level 1, 2, 3.
        Default values are values used by WECC: 0.5, 0.2, 0.05.
    :return: (*pandas.DataFrame*) -- congestion statistics.
        *'per_util1'*, *'per_util2'*, *'per_util3'*, *'u1flag'*, *'u2flag'*,
        *'u3flag'*, *'sumflag'*, *'bind'*, *'risk'*.
    """

    if util is None:
        util = [0.75, 0.9, 0.99]
    if threshold is None:
        threshold = [0.5, 0.2, 0.05]
    print("Removing non line branches")
    branch = branch[branch.branch_device_type == "Line"]
    pf = pf.loc[:, branch.index]

    print("Removing lines that never are >75% utilized")
    pf = pf.loc[:, pf.abs().max().divide(branch.rateA).replace(np.inf, 0) > 0.75]
    branch = branch.loc[pf.columns, :]

    print("Getting utilization")
    utilization_df = get_utilization(branch, pf)

    print("Counting hours")
    n_hours = len(utilization_df)

    print("Getting fraction of hours above threshold")
    per_util1 = _count_hours_gt_threshold(utilization_df, util[0]) / n_hours
    per_util2 = _count_hours_gt_threshold(utilization_df, util[1]) / n_hours
    per_util3 = _count_hours_gt_threshold(utilization_df, util[2]) / n_hours

    print("Calculating binding hours")
    bind = (utilization_df >= 1).sum()

    print("Calculating risk")
    risk = (pf[utilization_df > util[1]].sum()).fillna(0)

    print("Combining branch and utilization info")
    statistics = pd.concat(
        [
            branch["rateA"],
            branch["branch_device_type"],
            per_util1,
            per_util2,
            per_util3,
            bind,
            risk,
        ],
        axis=1,
    )

    statistics.loc[statistics.rateA == 0, ["rateA"]] = np.nan
    statistics.columns = [
        "capacity",
        "branch_device_type",
        "per_util1",
        "per_util2",
        "per_util3",
        "bind",
        "risk",
    ]

    vals = [
        ["per_util1", threshold[0], "uflag1"],
        ["per_util2", threshold[1], "uflag2"],
        ["per_util3", threshold[2], "uflag3"],
    ]

    for x in vals:
        statistics = pd.concat(
            [statistics, _flag(statistics, x[0], x[1], x[2])], axis=1
        )

    col_list = ["uflag1", "uflag2", "uflag3"]
    statistics["sumflag"] = statistics[col_list].sum(axis=1)

    print("Calculating distance and finalizing results")
    distance = branch.apply(great_circle_distance, axis=1).rename("dist")
    statistics = pd.concat([statistics, distance], axis=1)

    return statistics
