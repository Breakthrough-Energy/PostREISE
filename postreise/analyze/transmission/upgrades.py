from postreise.analyze.check import _check_data_frame, _check_grid


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
    :raises ValueError: if either data frame doesn't have required columns.
    """
    _check_data_frame(branch1, "branch1")
    _check_data_frame(branch2, "branch2")
    if not ("rateA" in branch1.columns) and ("rateA" in branch2.columns):
        raise ValueError("branch1 and branch2 both must have 'rateA' columns")
    branch1, branch2 = _reindex_as_necessary(branch1, branch2)
    branch_merge = branch1.merge(
        branch2, how="outer", right_index=True, left_index=True, suffixes=(None, "_2")
    )
    branch_merge["diff"] = branch_merge.rateA_2.fillna(0) - branch_merge.rateA.fillna(0)
    # Ensure that lats & lons get filled in as necessary from branch2 entries
    latlon_columns = ["from_lat", "from_lon", "to_lat", "to_lon"]
    missing_lat_indices = branch_merge.query("from_lat.isnull()").index
    branch_merge.loc[missing_lat_indices, latlon_columns] = branch_merge.loc[
        missing_lat_indices, [f"{l}_2" for l in latlon_columns]
    ].to_numpy()
    return branch_merge


def get_dcline_differences(grid1, grid2):
    """Calculate capacity differences between dcline tables, and add to/from lat/lon.

    :param powersimdata.input.grid.Grid grid1: first grid instance.
    :param powersimdata.input.grid.Grid grid2: second grid instance.
    :return: (*pandas.DataFrame*) -- data frame with all indices, plus new columns:
        diff, from_lat, from_lon, to_lat, to_lon.
    """
    _check_grid(grid1)
    _check_grid(grid2)
    dcline1, dcline2 = _reindex_as_necessary(grid1.dcline, grid2.dcline)
    # Get latitudes and longitudes for to & from buses
    for dcline, grid in [(dcline1, grid1), (dcline2, grid2)]:
        dcline["from_lat"] = grid.bus.loc[dcline.from_bus_id, "lat"].to_numpy()
        dcline["from_lon"] = grid.bus.loc[dcline.from_bus_id, "lon"].to_numpy()
        dcline["to_lat"] = grid.bus.loc[dcline.to_bus_id, "lat"].to_numpy()
        dcline["to_lon"] = grid.bus.loc[dcline.to_bus_id, "lon"].to_numpy()
    dc_merge = dcline1.merge(
        dcline2, how="outer", right_index=True, left_index=True, suffixes=(None, "_2")
    )
    # fillna for bus ids, since some lines in one frame won't be in the other frame
    dc_merge.fillna(
        {
            "from_lat": dc_merge.from_lat_2,
            "from_lon": dc_merge.from_lon_2,
            "to_lat": dc_merge.to_lat_2,
            "to_lon": dc_merge.to_lon_2,
        },
        inplace=True,
    )
    # Calculate differences in Pmax
    dc_merge["diff"] = dc_merge.Pmax_2.fillna(0) - dc_merge.Pmax.fillna(0)

    return dc_merge
