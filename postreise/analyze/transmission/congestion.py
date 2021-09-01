import numpy as np
import pandas as pd
from powersimdata.input.helpers import summarize_plant_to_bus
from powersimdata.input.input_data import get_bus_demand
from powersimdata.scenario.analyze import Analyze
from powersimdata.scenario.scenario import Scenario


def calculate_congestion_surplus(scenario):
    """Calculates hourly congestion surplus.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :return: (*pandas.DataFrame*) -- congestion surplus.
    """

    if not isinstance(scenario, Scenario):
        raise TypeError("scenario must be a Scenario object")
    if not isinstance(scenario.state, Analyze):
        raise ValueError("scenario.state must be Analyze")

    grid = scenario.state.get_grid()
    lmp = scenario.state.get_lmp()
    pg = scenario.state.get_pg()

    bus_demand = get_bus_demand(scenario.info, grid).to_numpy()
    bus_pg = summarize_plant_to_bus(pg, grid, all_buses=True)

    congestion_surplus = (lmp.to_numpy() * (bus_demand - bus_pg)).sum(axis=1)
    # Remove any negative values caused by barrier method imprecision
    congestion_surplus = np.clip(congestion_surplus, a_min=0, a_max=None)
    # Return a pandas Series with same index as pg
    congestion_surplus = pd.Series(data=congestion_surplus, index=pg.index)
    congestion_surplus.rename_axis(pg.index.name)
    return congestion_surplus
