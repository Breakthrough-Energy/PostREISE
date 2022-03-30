import numpy as np
import pandas as pd
from powersimdata.input.helpers import summarize_plant_to_bus
from powersimdata.scenario.check import _check_scenario_is_in_analyze_state


def calculate_congestion_surplus(scenario):
    """Calculates hourly congestion surplus.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :return: (*pandas.DataFrame*) -- congestion surplus.
    """
    _check_scenario_is_in_analyze_state(scenario)

    grid = scenario.get_grid()
    lmp = scenario.get_lmp()
    pg = scenario.get_pg()

    bus_demand = scenario.get_bus_demand()
    bus_pg = summarize_plant_to_bus(pg, grid, all_buses=True)

    congestion_surplus = (lmp.to_numpy() * (bus_demand - bus_pg)).sum(axis=1)
    # Remove any negative values caused by barrier method imprecision
    congestion_surplus = np.clip(congestion_surplus, a_min=0, a_max=None)
    # Return a pandas Series with same index as pg
    congestion_surplus = pd.Series(data=congestion_surplus, index=pg.index)
    congestion_surplus.rename_axis(pg.index.name)
    return congestion_surplus
