import math

import pandas as pd
import scipy.special as scsp


def generate_cong_stats(pf, branch, name):
    """Generates congestion statistics from the input congestion data.

    :param pandas.DataFrame pf: Power flow data frame with values normalized to
        capacity
    :param pandas.DataFrame branch: branches in network.
    :param string name: filename of output.
    :return: (*pandas.DataFrame*) -- data frame with *'hutil1'*, *'hutil0p9-1'*,
        *'hutil0p8-0p9'*, *'hutil0p75-0p8'*, *'hutil>=0p9'*, *'hutil>=0p8'*,
        *'hutil>=0p75'*, *'dist'*, *'zscore'* and *'pvalue'*.

    .. todo::
        Current version assumes normal distribution; calculate real
        distribution, then do a lookup depending on distribution type.
    """

    cong_stats = pd.concat([branch['Capacity'],
                            pf[(pf == 1)].describe().loc['count', :],
                            pf[(pf < 1) & (pf >= 0.9)
                               ].describe().loc['count', :],
                            pf[(pf < 0.9) & (pf >= 0.8)
                               ].describe().loc['count', :],
                            pf[(pf < 0.8) & (pf >= 0.75)
                               ].describe().loc['count', :]
                            ], axis=1)
    cong_stats.columns = ['Capacity', 'hutil1', 'hutil0p9-1',
                          'hutil0p8-0p9', 'hutil0p75-0p8']

    cong_stats[['Capacity',
                'hutil1',
                'hutil0p9-1',
                'hutil0p8-0p9',
                'hutil0p75-0p8'
                ]] = cong_stats[['Capacity', 'hutil1',
                                 'hutil0p9-1', 'hutil0p8-0p9',
                                 'hutil0p75-0p8']].astype(int)

    cong_stats.index.name = 'line'
    cong_stats = pd.concat([cong_stats,
                            cong_stats[['hutil1', 'hutil0p9-1']].sum(axis=1),
                            cong_stats[['hutil1', 'hutil0p9-1',
                                        'hutil0p8-0p9']].sum(axis=1),
                            cong_stats[['hutil1', 'hutil0p9-1',
                                        'hutil0p8-0p9',
                                        'hutil0p75-0p8']].sum(axis=1)
                            ], axis=1).rename(columns={0: 'hutil>=0p9',
                                                       1: 'hutil>=0p8',
                                                       2: 'hutil>=0p75'})

    branch['dist'] = branch.apply(
        lambda row: _great_circle_distance(
            math.radians(row['from_lat']), math.radians(row['from_lon']),
            math.radians(row['to_lat']), math.radians(row['to_lon'])), axis=1)

    cong_stats = pd.concat([cong_stats, branch['dist']], axis=1)

    total_hours = len(pf)
    p_cong = cong_stats.loc[cong_stats['Capacity'] != 99999].describe().loc[
        'mean']['hutil>=0p75']/total_hours
    mu = total_hours*p_cong
    var = total_hours*p_cong*(1 - p_cong)

    cong_stats['zscore'] = (cong_stats['hutil>=0p75'] - mu)/math.sqrt(var)
    cong_stats['pvalue'] = cong_stats['zscore'].apply(lambda x: 1-scsp.ndtr(x))

    cong_stats.to_csv(name + '.csv')

    return cong_stats


def _great_circle_distance(lat1, lon1, lat2, lon2):
    """Calculates distance between two sites.

    :param float lat1: latitude of first site (in rad.).
    :param float lon1: longitude of first site (in rad.).
    :param float lat2: latitude of second site (in rad.).
    :param float lon2: longitude of second site (in rad.).
    :return: (*float*) -- distance between two sites (in km.).
    """
    radius = 6368

    def haversine(x):
        return math.sin(x/2)**2
    return radius * 2 * math.asin(math.sqrt(haversine(lat2 - lat1) +
                                            math.cos(lat1) * math.cos(lat2) *
                                            haversine(lon2 - lon1)))
