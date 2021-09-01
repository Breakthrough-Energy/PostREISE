from powersimdata.input.check import _check_epsilon
from powersimdata.scenario.check import _check_scenario_is_in_analyze_state


def pmin_constraints(scenario, epsilon=1e-3):
    """Identify time periods in which generators are at minimum power.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param float epsilon: allowable 'fuzz' for whether constraint is binding.
    :return: (*pandas.DataFrame*) -- boolean data frame of same shape as PG.
    """
    _check_scenario_is_in_analyze_state(scenario)
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
    :return: (*pandas.DataFrame*) -- boolean data frame of same shape as PG.
    """
    _check_scenario_is_in_analyze_state(scenario)
    _check_epsilon(epsilon)

    pg = scenario.state.get_pg()
    grid = scenario.state.get_grid()
    pmax = grid.plant["Pmax"]
    binding_pmax_constraints = (pmax - pg) <= epsilon

    return binding_pmax_constraints


def ramp_constraints(scenario, epsilon=1e-3):
    """Identify time periods in which generators have binding ramp constraints.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param float epsilon: allowable 'fuzz' for whether constraint is binding.
    :return: (*pandas.DataFrame*) -- boolean data frame of same shape as PG.

    .. note:: The first time period will always return ``False`` for each column.
    """
    _check_scenario_is_in_analyze_state(scenario)
    _check_epsilon(epsilon)

    pg = scenario.state.get_pg()
    grid = scenario.state.get_grid()
    ramp = grid.plant["ramp_30"]
    diff = pg.diff(axis=0)
    binding_ramp_constraints = (ramp * 2 - abs(diff)) <= epsilon

    return binding_ramp_constraints
