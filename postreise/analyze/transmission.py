import numpy as np
import pandas as pd

from postreise.analyze import distance
from postreise.analyze import mapping


def generate_cong_df(branches_df, pf):
    """Generates utilization table to be used as input for congestion analyses.

    :param pandas.DataFrame branches_df: branch data frame.
    :param pandas.DataFrame pf: power flow data frame.
    :return: (*pandas.DataFrame*) -- normalized power flow data frame. For a
        given line and hour, value is one if power flowing on the line reaches
        capacity of the line.
    """

    branches_df.loc[branches_df.rateA != 0, 'capacity'] = branches_df['rateA']
    branches_df.loc[branches_df.rateA == 0, 'capacity'] = 99999.
    cong_df = pf.divide(branches_df.capacity).apply(np.abs)
    return cong_df


def get_hutil(cong_df, utilization):
    """Calculates number of hours above a given utilization threshold.

    :param pandas.DataFrame cong_df: normalized power flow data frame as
        returned by :func:`generate_cong_df`.
    :param float utilization: utilization threshold within [0,1].
    :return: (*pandas.DataFrame*) -- number of hours above utilization
        threshold.
    """

    hutil = (cong_df > utilization).sum().to_frame()
    return hutil


def flag(cong_stats, utilname, thresh, uflagname):
    """Flags branches that meet screening criteria for WECC.

    :param pandas.DataFrame cong_stats: congestion statistics as returned by
        :func:`generate_cong_stats`.
    :param string utilname: field with percent of time above threshold.
    :param float thresh: threshold for percent time for flag level.
    :param string uflagname: name of flag.
    :return: (*pandas.DataFrame*) -- data frame with *'uflagname'*.
    """

    cong_stats.loc[cong_stats[utilname] >= thresh, uflagname] = 1

    return cong_stats


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
    :return: (*pandas.DataFrame*) -- data frame with *'per_util1'*, *'per_util2'*,
        *'per_util3'*,*'u1flag'*,*'u2flag'*, *'u3flag'*, *'sumflag'*, *'risk'*.
    """
    pf = scenario.state.get_pf()
    branch = scenario.state.get_grid().branch.copy()
    print("Calculating utilization")
    cong_df = generate_cong_df(branch, pf)
    length = len(cong_df)

    cong_stats = pd.concat([branch['capacity'], branch['branch_device_type'],
                            (cong_df > util1).sum() / length,
                            (cong_df > util2).sum() / length,
                            (cong_df > util3).sum() / length,
                            (cong_df == 1).sum(),
                            (cong_df > util2).sum() * cong_df[
                                (cong_df > util2)].mean() * branch['capacity']],
                           axis=1)

    cong_stats.columns = ['capacity', 'branch_device_type', 'per_util1',
                          'per_util2', 'per_util3', 'bind', 'risk']
    vals = [['per_util1', thresh1, 'uflag1'],
            ['per_util2', thresh2, 'uflag2'],
            ['per_util3', thresh3, 'uflag3']]

    print("Flaging congested branches")
    for x in vals:
        flag(cong_stats, x[0], x[1], x[2])

    col_list = ['uflag1', 'uflag2', 'uflag3']
    cong_stats['sumflag'] = cong_stats[col_list].sum(axis=1)
    cong_stats = cong_stats.fillna(0)

    print("Calculating branch distance")
    branch['dist'] = branch.apply(distance.great_circle_distance, axis=1)

    cong_stats = pd.concat([cong_stats, branch['dist']], axis=1)
    print("make branch_map")
    branch_map = mapping.projection_fields(branch)
    print("flagging")
    congested = cong_stats[cong_stats.sumflag > 0]
    print("start first maps")
    mapping.makemap(congested, branch_map)
    mapping.makemap_all(cong_df, branch_map)
    mapping.makemap_binding(cong_df, branch_map)
    return cong_stats, binding_df
