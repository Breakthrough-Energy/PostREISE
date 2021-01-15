from postreise.analyze.helpers import _check_data_frame


def _reindex_as_necessary(df1, df2):
    """Check for indices with mismatched to/from bus ids, reindex as necessary.

    :param pandas.DataFrame df1: data frame containing ["from_bus_id", "to_bus_id"]
    :param pandas.DataFrame df2: data frame containing ["from_bus_id", "to_bus_id"]
    :return: (*tuple*) -- data frames, reindexed as necessary.
    """
    shared_indices = set(df1.index) & set(df2.index)
    check_columns = ["from_bus_id", "to_bus_id"]
    check1 = df1.loc[shared_indices, check_columns]
    check2 = df2.loc[shared_indices, check_columns]
    if not check1.equals(check2):
        df1 = df1.set_index(keys=check_columns, drop=False, append=True)
        df2 = df2.set_index(keys=check_columns, drop=False, append=True)
    return df1, df2


def get_branch_differences(branch1, branch2):
    """Given two branch dataframes, calculate capacity differences.

    :param pandas.DataFrame branch1: data frame containing rateA
    :param pandas.DataFrame branch2: data frame containing rateA
    :return: (*pandas.DataFrame*) -- data frame with all indices and 'diff' column.
    :raises ValueError: if either dataframe doesn't have required columns.
    """
    _check_data_frame(branch1, "branch1")
    _check_data_frame(branch2, "branch2")
    if not ("rateA" in branch1.columns) and ("rateA" in branch2.columns):
        raise ValueError("branch1 and branch2 both much have 'rateA' columns")
    branch1, branch2 = _reindex_as_necessary(branch1, branch2)
    branch_merge = branch1.merge(
        branch2, how="outer", right_index=True, left_index=True, suffixes=(None, "_2")
    )
    branch_merge["diff"] = branch_merge.rateA_2.fillna(0) - branch_merge.rateA.fillna(0)
    return branch_merge


def get_dcline_differences(dcline1, dcline2, bus):
    """Calculate capacity differences between dcline tables, and add to/from lat/lon.

    :param pandas.DataFrame dcline1: data frame containing Pmax, from_bus_id, to_bus_id.
    :param pandas.DataFrame dcline2: data frame containing Pmax, from_bus_id, to_bus_id.
    :param pandas.DataFrame bus: data frame containing lat & lon.
    :raises ValueError: if any dataframe doesn't have required columns.
    :return: (*pandas.DataFrame*) -- data frame with all indices, plus new columns:
        diff, from_lat, from_lon, to_lat, to_lon.
    """
    _check_data_frame(dcline1, "dcline1")
    _check_data_frame(dcline2, "dcline2")
    _check_data_frame(bus, "bus")
    dcline_req_cols = {"Pmax", "from_bus_id", "to_bus_id"}
    if not dcline_req_cols <= set(dcline1.columns):
        raise ValueError(f"dcline1 must have columns: {dcline_req_cols}")
    if not dcline_req_cols <= set(dcline2.columns):
        raise ValueError(f"dcline2 must have columns: {dcline_req_cols}")
    if not {"lat", "lon"} <= set(bus.columns):
        raise ValueError("bus must have 'lat' & 'lon' columns")
    dcline1, dcline2 = _reindex_as_necessary(dcline1, dcline2)
    dc_merge = dcline1.merge(
        dcline2, how="outer", right_index=True, left_index=True, suffixes=(None, "_2")
    )
    # fillna for bus ids, since some lines in one frame won't be in the other frame
    dc_merge.fillna(
        {
            "from_bus_id": dc_merge.from_bus_id_2,
            "to_bus_id": dc_merge.to_bus_id_2,
        },
        inplace=True,
    )
    # Calculate differences in Pmax
    dc_merge["diff"] = dc_merge.Pmax_2.fillna(0) - dc_merge.Pmax.fillna(0)
    # get lat lon for dclines
    dc_merge["from_lon"] = bus.loc[dc_merge.from_bus_id, "lon"].values
    dc_merge["from_lat"] = bus.loc[dc_merge.from_bus_id, "lat"].values
    dc_merge["to_lon"] = bus.loc[dc_merge.to_bus_id, "lon"].values
    dc_merge["to_lat"] = bus.loc[dc_merge.to_bus_id, "lat"].values

    return dc_merge
