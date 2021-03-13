import datetime

import numpy as np
import pandas as pd
from powersimdata.input.grid import Grid
from powersimdata.network.model import ModelImmutables
from powersimdata.scenario.analyze import Analyze
from powersimdata.scenario.scenario import Scenario


def _check_data_frame(df, label):
    """Ensure that input is a pandas data frame.

    :param pandas.DataFrame df: a data frame.
    :param str label: name of data frame (used for error messages).
    :raises TypeError: if df is not a data frame or label is not a str.
    :raises ValueError: if data frame is empty.
    """
    if not isinstance(label, str):
        raise TypeError("label must be a str")
    if not isinstance(df, pd.DataFrame):
        raise TypeError(label + " must be a pandas.DataFrame object")
    if not df.shape[0] > 0:
        raise ValueError(label + " must have at least one row")
    if not df.shape[1] > 0:
        raise ValueError(label + " must have at least one column")


def _check_time_series(ts, label):
    """Check that a time series is specified properly.

    :param pandas.DataFrame/pandas.Series ts: time series to check.
    :param str label: name of time series (used for error messages).
    :raises TypeError: if ts is not a data frame/time series or label is not a str.
    :raises ValueError: if indices are not timestamps.
    """
    if not isinstance(label, str):
        raise TypeError("label must be a str")
    if not isinstance(ts, (pd.DataFrame, pd.Series)):
        raise TypeError(label + " must be a pandas.DataFrame or pandas.Series object")
    if not ts.shape[0] > 0:
        raise ValueError(label + " must have at least one row")
    if not isinstance(ts.index, pd.DatetimeIndex):
        raise ValueError(label + " must be a time series")


def _check_grid(grid):
    """Ensure that grid is a Grid object.

    :param powersimdata.input.grid.Grid grid: a Grid instance.
    :raises TypeError: if input is not a Grid instance.
    """
    if not isinstance(grid, Grid):
        raise TypeError("grid must be a powersimdata.input.grid.Grid object")


def _check_scenario_is_in_analyze_state(scenario):
    """Ensure that scenario is a Scenario object in the analyze state.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :raises TypeError: if scenario is not a Scenario instance.
    :raises ValueError: if Scenario object is not in analyze state.
    """
    if not isinstance(scenario, Scenario):
        raise TypeError(f"scenario must be a {Scenario} object")
    if not isinstance(scenario.state, Analyze):
        raise ValueError("scenario must in analyze state")


def _check_areas_and_format(areas, grid_model="usa_tamu"):
    """Ensure that areas are valid. Duplicates are removed and state abbreviations are
    converted to their actual name.

    :param str/list/tuple/set areas: areas(s) to check. Could be load zone name(s),
        state name(s)/abbreviation(s) or interconnect(s).
    :param str grid_model: grid model.
    :raises TypeError: if areas is not a list/tuple/set of str.
    :raises ValueError: if areas is empty or not valid.
    :return: (*set*) -- areas as a set. State abbreviations are converted to state
        names.
    """
    mi = ModelImmutables(grid_model)
    if isinstance(areas, str):
        areas = {areas}
    elif isinstance(areas, (list, set, tuple)):
        if not all([isinstance(z, str) for z in areas]):
            raise TypeError("all areas must be str")
        areas = set(areas)
    else:
        raise TypeError("areas must be a str or a list/tuple/set of str")
    if len(areas) == 0:
        raise ValueError("areas must be non-empty")
    all_areas = (
        mi.zones["loadzone"]
        | mi.zones["abv"]
        | mi.zones["state"]
        | mi.zones["interconnect"]
    )
    if not areas <= all_areas:
        diff = areas - all_areas
        raise ValueError("invalid area(s): %s" % " | ".join(diff))

    abv_in_areas = [z for z in areas if z in mi.zones["abv"]]
    for a in abv_in_areas:
        areas.remove(a)
        areas.add(mi.zones["abv2state"][a])

    return areas


def _check_resources_and_format(resources, grid_model="usa_tamu"):
    """Ensure that resources are valid and convert variable to a set.

    :param str/list/tuple/set resources: resource(s) to check.
    :param str grid_model: grid model.
    :raises TypeError: if resources is not a list/tuple/set of str.
    :raises ValueError: if resources is empty or not valid.
    :return: (*set*) -- resources as a set.
    """
    mi = ModelImmutables(grid_model)
    if isinstance(resources, str):
        resources = {resources}
    elif isinstance(resources, (list, set, tuple)):
        if not all([isinstance(r, str) for r in resources]):
            raise TypeError("all resources must be str")
        resources = set(resources)
    else:
        raise TypeError("resources must be a str or a list/tuple/set of str")
    if len(resources) == 0:
        raise ValueError("resources must be non-empty")
    if not resources <= mi.plants["all_resources"]:
        diff = resources - mi.plants["all_resources"]
        raise ValueError("invalid resource(s): %s" % " | ".join(diff))
    return resources


def _check_resources_are_renewable_and_format(resources, grid_model="usa_tamu"):
    """Ensure that resources are valid renewable resources and convert variable to
    a set.

    :param str/list/tuple/set resources: resource(s) to analyze.
    :param str grid_model: grid model.
    :raises ValueError: if resources are not renewables.
    return: (*set*) -- resources as a set
    """
    mi = ModelImmutables(grid_model)
    resources = _check_resources_and_format(resources, grid_model=grid_model)
    if not resources <= mi.plants["renewable_resources"]:
        diff = resources - mi.plants["all_resources"]
        raise ValueError("invalid renewable resource(s): %s" % " | ".join(diff))
    return resources


def _check_areas_are_in_grid_and_format(areas, grid):
    """Ensure that list of areas are in grid.

    :param dict areas: keys are area types: '*loadzone*', '*state*' or '*interconnect*'.
        Values are str/list/tuple/set of areas.
    :param powersimdata.input.grid.Grid grid: Grid instance.
    :return: (*dict*) -- modified areas dictionary. Keys are area types ('*loadzone*',
        '*state*' or '*interconnect*'). State abbreviations, if present, are converted
        to state names. Values are areas as a set.
    :raises TypeError: if areas is not a dict or its keys are not str.
    :raises ValueError: if area type is invalid, an area in not in grid or an
        invalid loadzone/state/interconnect is passed.
    """
    _check_grid(grid)
    if not isinstance(areas, dict):
        raise TypeError("areas must be a dict")

    mi = grid.model_immutables
    areas_formatted = {}
    for a in areas.keys():
        if a in ["loadzone", "state", "interconnect"]:
            areas_formatted[a] = set()

    all_loadzones = set()
    for k, v in areas.items():
        if not isinstance(k, str):
            raise TypeError("area type must be a str")
        elif k == "interconnect":
            interconnects = _check_areas_and_format(v)
            for i in interconnects:
                try:
                    all_loadzones.update(mi.zones["interconnect2loadzone"][i])
                except KeyError:
                    raise ValueError("invalid interconnect: %s" % i)
            areas_formatted["interconnect"].update(interconnects)
        elif k == "state":
            states = _check_areas_and_format(v)
            for s in states:
                try:
                    all_loadzones.update(mi.zones["state2loadzone"][s])
                except KeyError:
                    raise ValueError("invalid state: %s" % s)
            areas_formatted["state"].update(states)
        elif k == "loadzone":
            loadzones = _check_areas_and_format(v)
            for l in loadzones:
                if l not in mi.zones["loadzone"]:
                    raise ValueError("invalid load zone: %s" % l)
            all_loadzones.update(loadzones)
            areas_formatted["loadzone"].update(loadzones)
        else:
            raise ValueError("invalid area type")

    valid_loadzones = set(grid.plant["zone_name"].unique())
    if not all_loadzones <= valid_loadzones:
        diff = all_loadzones - valid_loadzones
        raise ValueError("%s not in in grid" % " | ".join(diff))

    return areas_formatted


def _check_resources_are_in_grid_and_format(resources, grid):
    """Ensure that resource(s) is represented in at least one generator in the grid
    used for the scenario.

    :param str/list/tuple/set resources: resource(s) to analyze.
    :param powersimdata.input.grid.Grid grid: a Grid instance.
    :return: (*set*) -- resources as a set.
    :raises ValueError: if resources is not used in scenario.
    """
    _check_grid(grid)
    resources = _check_resources_and_format(resources)
    valid_resources = set(grid.plant["type"].unique())
    if not resources <= valid_resources:
        diff = resources - valid_resources
        raise ValueError("%s not in in grid" % " | ".join(diff))
    return resources


def _check_plants_are_in_grid(plant_id, grid):
    """Ensure that list of plant id are in grid.

    :param list/tuple/set plant_id: list of plant id.
    :param powersimdata.input.grid.Grid grid: Grid instance.
    :raises TypeError: if plant_id is not a list of int or str.
    :raises ValueError: if plant id is not in network.
    """
    _check_grid(grid)
    if not (
        isinstance(plant_id, (list, tuple, set))
        and all([isinstance(p, (int, str)) for p in plant_id])
    ):
        raise TypeError("plant_id must be a a list/tuple/set of int or str")
    if not set([str(p) for p in plant_id]) <= set([str(i) for i in grid.plant.index]):
        raise ValueError("plant_id must be subset of plant index")


def _check_number_hours_to_analyze(scenario, hours):
    """Ensure that number of hours is greater than simulation length.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param int hours: number of hours to analyze.
    :raises TypeError: if hours is not int.
    :raises ValueError: if hours is negative or greater than simulation length
    """
    _check_scenario_is_in_analyze_state(scenario)
    start_date = pd.Timestamp(scenario.info["start_date"])
    end_date = pd.Timestamp(scenario.info["end_date"])
    if not isinstance(hours, int):
        raise TypeError("hours must be an int")
    if hours < 1:
        raise ValueError("hours must be positive")
    if hours > (end_date - start_date).total_seconds() / 3600 + 1:
        raise ValueError("hours must not be greater than simulation length")


def _check_date(date):
    """Check date is valid.

    :param pandas.Timestamp/numpy.datetime64/datetime.datetime date: timestamp.
    :raises TypeError: if date is improperly formatted.
    """
    if not isinstance(date, (pd.Timestamp, np.datetime64, datetime.datetime)):
        raise TypeError(
            "date must be a pandas.Timestamp, a numpy.datetime64 or a datetime.datetime object"
        )


def _check_date_range_in_scenario(scenario, start, end):
    """Check if start time and end time define a valid time range of the given scenario.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param pandas.Timestamp/numpy.datetime64/datetime.datetime start: start date.
    :param pandas.Timestamp/numpy.datetime64/datetime.datetime end: end date.
    :raises ValueError: if the date range is invalid.
    """
    _check_scenario_is_in_analyze_state(scenario)
    _check_date(start)
    _check_date(end)
    scenario_start = pd.Timestamp(scenario.info["start_date"])
    scenario_end = pd.Timestamp(scenario.info["end_date"])

    if not scenario_start <= start <= end <= scenario_end:
        raise ValueError("Must have scenario_start <= start <= end <= scenario_end")


def _check_date_range_in_time_series(ts, start, end):
    """Check if start time and end time define a valid time range of the time series.

    :param pandas.DataFrame/pandas.Series ts: a time series with timestamp as indices.
    :param pandas.Timestamp/numpy.datetime64/datetime.datetime start: start date.
    :param pandas.Timestamp/numpy.datetime64/datetime.datetime end: end date.
    :raises ValueError: if the date range is invalid.
    """
    _check_time_series(ts, "time series")
    _check_date(start)
    _check_date(end)

    if not ts.index[0] <= start <= end <= ts.index[-1]:
        raise ValueError(
            "Must have time_series_start <= start <= end <= time_series_end"
        )


def _check_epsilon(epsilon):
    """Ensure epsilon is valid.

    :param float/int epsilon: precision for binding constraints.
    :raises TypeError: if epsilon is not a float or an int.
    :raises ValueError: if epsilon is negative.
    """
    if not isinstance(epsilon, (float, int)):
        raise TypeError("epsilon must be numeric")
    if epsilon < 0:
        raise ValueError("epsilon must be non-negative")


def _check_gencost(gencost):
    """Check that gencost is valid.

    :param pandas.DataFrame gencost: cost curve polynomials.
    :raises TypeError: if gencost is not a data frame and polynomial degree is not
        an int.
    :raises ValueError: if data frame has no rows, does not have the required columns,
        curves are not polynomials and have not the appropriate coefficients.
    """

    # check for nonempty dataframe
    if isinstance(gencost, pd.DataFrame):
        _check_data_frame(gencost, "gencost")
    else:
        raise TypeError("gencost must be a pandas.DataFrame object")

    # check for proper columns
    required_columns = ("type", "n")
    for r in required_columns:
        if r not in gencost.columns:
            raise ValueError("gencost must have column " + r)

    # check that gencosts are all specified as type 2 (polynomial)
    cost_type = gencost["type"]
    if not cost_type.where(cost_type == 2).equals(cost_type):
        raise ValueError("each gencost must be type 2 (polynomial)")

    # check that all gencosts are specified as same order polynomial
    if not (gencost["n"].nunique() == 1):
        raise ValueError("all polynomials must be of same order")

    # check that this order is an integer > 0
    n = gencost["n"].iloc[0]
    if not isinstance(n, (int, np.integer)):
        raise TypeError("polynomial degree must be specified as an int")
    if n < 1:
        raise ValueError("polynomial must be at least of order 1 (constant)")

    # check that the right columns are here for this dataframe
    coef_columns = ["c" + str(i) for i in range(n)]
    for c in coef_columns:
        if c not in gencost.columns:
            raise ValueError("gencost of order {0} must have column {1}".format(n, c))
