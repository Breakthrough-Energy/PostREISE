import numpy as np
import pandas as pd

from powersimdata.utility.distance import great_circle_distance


def get_utilization(branch, pf):
    """Generates utilization table to be used as input for congestion analyses.

    :param pandas.DataFrame branch: branch data frame.
    :param pandas.DataFrame pf: power flow data frame.
    :return: (*pandas.DataFrame*) -- normalized power flow data frame. For a
        given line and hour, value is one if power flowing on the line reaches
        capacity of the line.
    """

    return pf.divide(branch.rateA).apply(np.abs).replace(np.inf, 0)


def _count_hours_above_threshold(utilization, threshold):
    """Calculates number of hours above a given utilization threshold.

    :param pandas.DataFrame utilization: normalized power flow data frame as
        returned by :func:`get_utilization`.
    :param float threshold: utilization threshold ([0,1]).
    :return: (*pandas.Series*) -- number of hours above utilization threshold.
    """

    return (utilization > threshold).sum()


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


def generate_cong_stats(scenario, util1=0.75, thresh1=0.5, util2=0.9,
                        thresh2=0.2, util3=0.99, thresh3=0.05):
    """Generates WECC congestion statistics from the input congestion data
        (WECC parameters are defaults)

    :param powersimdata.scenario.scenario.Scenario scenario: scenario object
    :param float util1: utilization flag level 1.
        0.75 in WECC (flag if line congested >0.75 more than >0.50 of the time).
    :param float thresh1: threshold for percent time for flag level 1, which
        is 0.5 in WECC (if line is congested >0.75 more than >0.50 of the time,
        it is flagged).
    :param float util2: utilization congestion for flag level 2, which is 0.90
        in WECC (if line is congested >0.90 more than >0.2 of the time, it is
        flagged).
    :param float thresh2: threshold for percent time for flag level 2, which is
        0.2 in WECC (if line is congested >0.90 more than >0.2 of the time, it
        is flagged).
    :param float util3: utilization congestion to flag level 3, which is 0.99
        in WECC (if line is congested >0.99 more than >0.05 of the time, it is
        flagged).
    :param float thresh3: threshold for percent time for flag level 3, which is
        0.05 in WECC (if line is congested >0.99 more than >0.05 of the time,
        it is flagged).
    :return: (*pandas.DataFrame*) -- data frame with *'per_util1'*,
        *'per_util2'*, *'per_util3'*,*'u1flag'*,*'u2flag'*, *'u3flag'*,
        *'sumflag'*, *'risk'*.
    """

    print("Calculating utilization")
    pf = scenario.state.get_pf()
    grid = scenario.state.get_grid()
    utilization = get_utilization(grid.branch, pf)
    n_hours = len(utilization)

    per_util1 = _count_hours_above_threshold(utilization, util1) / n_hours
    per_util2 = _count_hours_above_threshold(utilization, util2) / n_hours
    per_util3 = _count_hours_above_threshold(utilization, util3) / n_hours
    bind = (utilization == 1).sum()
    risk = (pf[utilization > util2].sum()).fillna(0).apply(np.abs)
    statistics = pd.concat([grid.branch['rateA'],
                            grid.branch['branch_device_type'], per_util1,
                            per_util2, per_util3, bind, risk], axis=1)

    statistics.loc[statistics.rateA == 0, ['rateA']] = np.nan
    statistics.columns = ['capacity', 'branch_device_type', 'per_util1',
                          'per_util2', 'per_util3', 'bind', 'risk']

    vals = [['per_util1', thresh1, 'uflag1'], ['per_util2', thresh2, 'uflag2'],
            ['per_util3', thresh3, 'uflag3']]
    for x in vals:
        statistics = pd.concat([statistics,
                                _flag(statistics, x[0], x[1], x[2])], axis=1)

    col_list = ['uflag1', 'uflag2', 'uflag3']
    statistics['sumflag'] = statistics[col_list].sum(axis=1)

    distance = grid.branch.apply(great_circle_distance, axis=1).rename('dist')
    statistics = pd.concat([statistics, distance], axis=1)

    return statistics
