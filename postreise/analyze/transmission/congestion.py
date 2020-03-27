import numpy as np
import pandas as pd

from powersimdata.input.grid import Grid
from powersimdata.scenario.analyze import Analyze
from powersimdata.scenario.scenario import Scenario
from postreise.analyze.helpers import summarize_plant_to_bus


def map_demand_to_buses(grid, demand):
    """Map demand by (hour, zone) to (hour, bus).

    :param powersimdata.input.grid.Grid grid: Grid instance.
    :param pandas.DataFrame demand: demand DataFrame.
    :return: (*pandas.DataFrame*) -- bus_demand, indices (hour, bus).
    """

    if not isinstance(grid, Grid):
        raise TypeError('grid must be a Grid object')
    if not isinstance(demand, pd.DataFrame):
        raise TypeError('demand must be a pandas DataFrame')

    bus = grid.bus
    zones = list(grid.id2zone.keys())
    bus_demands = {}
    for z in zones:
        # Calculate share of zone demand to each zone bus
        zone_buses = bus[bus['zone_id'] == z]
        load_sum = zone_buses['Pd'].sum()
        load_ratio = zone_buses['Pd'] / load_sum
        # Then distribute time-series demand to buses
        bus_demands[z] = pd.DataFrame(
            data=np.outer(demand[z].to_numpy(), load_ratio.to_numpy()),
            columns=load_ratio.index,
            index=demand.index)
    bus_demand = pd.concat([bus_demands[z] for z in zones], axis=1)
    return bus_demand


def calculate_congestion_surplus(scenario):
    """Calculates hourly congestion surplus.
    
    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :return: (*pandas.DataFrame*) -- congestion surplus.
    """

    if not isinstance(scenario, Scenario):
        raise TypeError('scenario must be a Scenario object')
    if not isinstance(scenario.state, Analyze):
        raise ValueError('scenario.state must be Analyze')

    demand = scenario.state.get_demand(original=False)
    grid = scenario.state.get_grid()
    lmp = scenario.state.get_lmp()
    pg = scenario.state.get_pg()

    bus_demand = map_demand_to_buses(grid, demand).to_numpy()
    bus_pg = summarize_plant_to_bus(pg, grid, all_buses=True)

    congestion_surplus = (lmp.to_numpy() * (bus_demand - bus_pg)).sum(axis=1)
    # Remove any negative values caused by barrier method imprecision
    congestion_surplus = np.clip(congestion_surplus, a_min=0, a_max=None)
    # Return a pandas Series with same index as pg
    congestion_surplus = pd.Series(data=congestion_surplus, index=pg.index)
    congestion_surplus.rename_axis(pg.index.name)
    return congestion_surplus