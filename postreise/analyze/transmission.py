import numpy as np
import pandas as pd

from postreise.analyze.distance import great_circle_distance
from postreise.analyze import mapping


def get_congestion(branch, pf):
    """Generates utilization table to be used as input for congestion analyses.

    :param pandas.DataFrame branch: branch data frame.
    :param pandas.DataFrame pf: power flow data frame.
    :return: (*pandas.DataFrame*) -- normalized power flow data frame. For a
        given line and hour, value is one if power flowing on the line reaches
        capacity of the line.
    """

    return pf.divide(branch.rateA).apply(np.abs).replace(np.inf, 0)


def get_utilization(congestion, utilization):
    """Calculates number of hours above a given utilization threshold.

    :param pandas.DataFrame congestion: normalized power flow data frame as
        returned by :func:`get_congestion`.
    :param float utilization: utilization threshold ([0,1]).
    :return: (*pandas.Series*) -- number of hours above utilization threshold.
    """

    return (congestion > utilization).sum()


def flag(statistics, utilname, thresh, uflagname):
    """Flags branches that meet screening criteria for WECC.

    :param pandas.DataFrame statistics: congestion statistics as returned by
        :func:`statistics`.
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
    congestion = get_congestion(grid.branch, pf)
    n_hours = len(congestion)

    per_util1 = get_utilization(congestion, util1) / n_hours
    per_util2 = get_utilization(congestion, util2) / n_hours
    per_util3 = get_utilization(congestion, util3) / n_hours
    bind = (congestion == 1).sum()
    risk = (pf[congestion > util2].sum()).fillna(0).apply(np.abs)
    statistics = pd.concat([grid.branch['rateA'],
                            grid.branch['branch_device_type'], per_util1,
                            per_util2, per_util3, bind, risk], axis=1)

    statistics.loc[statistics.rateA == 0, ['rateA']] = np.nan
    statistics.columns = ['capacity', 'branch_device_type', 'per_util1',
                          'per_util2', 'per_util3', 'bind', 'risk']

    print("Flagging congested branches")
    vals = [['per_util1', thresh1, 'uflag1'], ['per_util2', thresh2, 'uflag2'],
            ['per_util3', thresh3, 'uflag3']]
    for x in vals:
        statistics = pd.concat([statistics,
                                flag(statistics, x[0], x[1], x[2])], axis=1)

    col_list = ['uflag1', 'uflag2', 'uflag3']
    statistics['sumflag'] = statistics[col_list].sum(axis=1)

    print("Calculating branch distance")
    distance = grid.branch.apply(great_circle_distance, axis=1).rename('dist')
    statistics = pd.concat([statistics, distance], axis=1)

    print("make branch_map")
    branch_map = mapping.projection_fields(grid.branch)

    print("flagging")
    congested = statistics[statistics.sumflag > 0]

    print("start first maps")
    mapping.makemap(congested, branch_map)
    mapping.makemap_all(congestion, branch_map)
    mapping.makemap_binding(congestion, branch_map)

    return statistics
