import numpy as np
import pandas as pd

from powersimdata.utility.distance import great_circle_distance


def get_utilization(branch, pf, median=False):
    """Generates utilization table to be used as input for congestion analyses.

    :param pandas.DataFrame branch: branch data frame.
    :param pandas.DataFrame pf: power flow data frame.
    :param boolean median: take medians of pf for utilization calculation
    :return: (*pandas.DataFrame*) -- normalized power flow data frame. For a
        given line and hour, value is one if power flowing on the line reaches
        capacity of the line.
    """
    pf = pf.abs()
    if median:
        pf = pd.DataFrame(pf.median()).T

    return pf.divide(branch.rateA).replace(np.inf, 0)


def _count_hours_gt_thresh(utilization_df, threshold):
    """Calculates number of hours above a given utilization threshold.

    :param pandas.DataFrame utilization_df: normalized pf data frame as
        returned by :func:`get_utilization`.
    :param float threshold: utilization threshold ([0,1]).
    :return: (*pandas.Series*) -- number hours above utilization threshold.
    """
    return (utilization_df > threshold).sum()


def _flag(statistics, utilname, thresh, uflagname):
    """Flags branches that meet screening criteria for WECC.

    :param pandas.DataFrame statistics: congestion statistics as returned by
        :func:`generate_cong_stats`.
    :param string utilname: field with percent of time above threshold.
    :param float thresh: threshold for percent time for flag level.
    :param string uflagname: name of flag.
    :return: (*pandas.DataFrame*) -- data frame with *'uflagname'*.
    """

    return (statistics[utilname] >= thresh).astype(int).rename(uflagname)


def generate_cong_stats(pf, grid_branch,
                        util=None,
                        thresh=None):
    """Generates congestion/utilization statistics from powerflow data
        (WECC congestion reports' analyses are the inspiration
        for these analyses and are the source of the default parameters).

    :param pandas.DataFrame pf: power flow data frame
    :param pandas.DataFrame grid_branch: grid.branch branch info
    :param list util: utilization (float) flag level 1, 2, 3.
        Default values are values used by WECC: 0.75, 0.9, 99.
    :param list thresh: threshold for proportion time, for flag level 1, 2, 3.
        Default values are values used by WECC: 0.5, 0.2, 0.05.
     :return: (*pandas.DataFrame*) -- congestion statistics
        *'per_util1'*,*'per_util2'*, *'per_util3'*,
        *'u1flag'*,*'u2flag'*, *'u3flag'*,*'sumflag'*, *'risk'*.
    """

    if util is None:
        util = [0.75, 0.9, 0.99]
    if thresh is None:
        thresh = [0.5, 0.2, 0.05]
    print('Removing non line branches')
    grid_branch = grid_branch[grid_branch.branch_device_type == 'Line']
    pf = pf.loc[:, grid_branch.index]

    print('Removing lines that never are >75% utilized')
    pf = pf.loc[:,
                pf.abs().max().divide(grid_branch.rateA).replace(np.inf,
                                                                 0) > 0.75]
    grid_branch = grid_branch.loc[pf.columns, :]

    print('Getting utilization')
    utilization_df = get_utilization(grid_branch, pf)

    print("Counting hours")
    n_hours = len(utilization_df)

    print('Getting fraction of hours above threshold')
    per_util1 = _count_hours_gt_thresh(utilization_df, util[0]) / n_hours
    per_util2 = _count_hours_gt_thresh(utilization_df, util[1]) / n_hours
    per_util3 = _count_hours_gt_thresh(utilization_df, util[2]) / n_hours

    print("Calculating binding hours")
    bind = (utilization_df >= 1).sum()

    print("Calculating risk")
    risk = (pf[utilization_df > util[1]].sum()).fillna(0)

    print("Combining branch and utilization info")
    statistics = pd.concat([grid_branch['rateA'],
                            grid_branch['branch_device_type'], per_util1,
                            per_util2, per_util3, bind, risk], axis=1)

    statistics.loc[statistics.rateA == 0, ['rateA']] = np.nan
    statistics.columns = ['capacity', 'branch_device_type', 'per_util1',
                          'per_util2', 'per_util3', 'bind', 'risk']

    vals = [['per_util1', thresh[0], 'uflag1'],
            ['per_util2', thresh[1], 'uflag2'],
            ['per_util3', thresh[2], 'uflag3']]

    for x in vals:
        statistics = pd.concat([statistics,
                                _flag(statistics, x[0], x[1], x[2])], axis=1)

    col_list = ['uflag1', 'uflag2', 'uflag3']
    statistics['sumflag'] = statistics[col_list].sum(axis=1)

    print('Calculating distance and finalizing results')
    distance = grid_branch.apply(great_circle_distance,
                                 axis=1).rename('dist')
    statistics = pd.concat([statistics, distance], axis=1)

    return statistics
