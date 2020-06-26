from powersimdata.scenario.scenario import Scenario
from powersimdata.scenario.analyze import Analyze


def _check_scenario(scenario):
    """Private function used only for type-checking for public functions.
    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :raises TypeError: if scenario is not a Scenario object.
    :raises ValueError: if scenario is not in Analyze state.
    """
    if not isinstance(scenario, Scenario):
        raise TypeError("scenario must be a Scenario object")
    if not isinstance(scenario.state, Analyze):
        raise ValueError("scenario.state must be Analyze")


def _check_epsilon(epsilon):
    """Private function used only for type-checking for public functions.
    :param float/int epsilon: precision for binding constraints.
    :raises TypeError: if epsilon is not a float or an int.
    :raises ValueError: if epsilon is negative.
    """
    if not isinstance(epsilon, (float, int)):
        raise TypeError("epsilon must be numeric")
    if epsilon < 0:
        raise ValueError("epsilon must be non-negative")


def pmin_constraints(scenario, epsilon=1e-3):
    """Identify time periods in which generators are at minimum power.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param float epsilon: allowable 'fuzz' for whether constraint is binding.
    :return: (*pandas.DataFrame*) -- Boolean dataframe of same shape as PG.
    """
    _check_scenario(scenario)
    _check_epsilon(epsilon)

    pg = scenario.state.get_pg()
    grid = scenario.state.get_grid()
    pmin = grid.plant["Pmin"]
    binding_pmin_constraints = (pg - pmin) <= epsilon

    return binding_pmin_constraints


def pmax_constraints(scenario, epsilon=1e-3):
    """Identify time periods in which generators are at maximum power.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param float epsilon: allowable 'fuzz' for whether constraint is binding.
    :return: (*pandas.DataFrame*) -- Boolean dataframe of same shape as PG.
    """
    _check_scenario(scenario)
    _check_epsilon(epsilon)

    pg = scenario.state.get_pg()
    grid = scenario.state.get_grid()
    pmax = grid.plant["Pmax"]
    binding_pmax_constraints = (pmax - pg) <= epsilon

    return binding_pmax_constraints


def ramp_constraints(scenario, epsilon=1e-3):
    """Identify time periods in which generators have binding ramp constraints.
    .. note:: The first time period will always return *False* for each column.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param float epsilon: allowable 'fuzz' for whether constraint is binding.
    :return: (*pandas.DataFrame*) -- Boolean dataframe of same shape as PG.
    """
    _check_scenario(scenario)
    _check_epsilon(epsilon)

    pg = scenario.state.get_pg()
    grid = scenario.state.get_grid()
    ramp = grid.plant["ramp_30"]
    diff = pg.diff(axis=0)
    binding_ramp_constraints = (ramp * 2 - abs(diff)) <= epsilon

    return binding_ramp_constraints