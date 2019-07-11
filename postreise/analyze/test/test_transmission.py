from postreise.analyze import transmission

import pandas as pd
import os


def test_transmission():
    """Tests postreise.analyze.transmission module by checking:

    1. all p-values are in [0,1].
    2. all line distances are shorter than the longest line in the US.

    .. note::
        To run faster, shortened versions of the branch and normalized power \
        flow files are used.
    """

    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

    branch = pd.read_csv(
        os.path.join(data_dir, 'branches_for_testing_100.csv'))
    cong_base = pd.read_csv(os.path.join(
        data_dir, 'congestion_base_for_testing_1000.csv'),
        index_col='Unnamed: 0')

    cong_base.index = pd.to_datetime(cong_base.index)
    branch.index = cong_base.columns

    cong_results = transmission.generate_cong_stats(cong_base,
                                                    branch,
                                                    'congestion_test_results')

    # Test that pvalues are between 0 and 1
    assert all((cong_results['pvalue'] >= 0) & (cong_results['pvalue'] <= 1))

    # Test that longest line in Western Interconnect is shorter than longest
    # line in the US
    assert all(cong_results['dist'] >= 0 & (cong_results['dist'] <= 1248.))
