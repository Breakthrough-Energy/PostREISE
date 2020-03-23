import pandas as pd
from powersimdata.input.grid import Grid
from powersimdata.scenario.scenario import Scenario
from powersimdata.scenario.analyze import Analyze


def _check_df_grid(df, grid):
    """Ensure that dataframe and grid are of proper type for processing.

    :param pandas.DataFrame df: dataframe, columns are plant IDs in Grid.
    :param powersimdata.input.grid.Grid grid: Grid instance.
    :return: (*None*).
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError('df must be pandas.DataFrame')
    if not isinstance(grid, Grid):
        raise TypeError('grid must be powersimdata.input.grid.Grid object')
    if not set(df.columns) <= set(grid.plant.index):
        raise ValueError('columns of df must be subset of plant index')


def summarize_plant_to_bus(df, grid, all_buses=False):
    """Take a plant-column dataframe and sum to a bus-column dataframe.

    :param pandas.DataFrame df: dataframe, columns are plant IDs in Grid.
    :param powersimdata.input.grid.Grid grid: Grid instance.
    :param boolean all_buses: return all buses in grid, not just plant buses.
    :return: (*pandas.DataFrame*) -- index as df input, columns are buses.
    """
    _check_df_grid(df, grid)
    
    all_buses_in_grid = grid.plant['bus_id']
    buses_in_df = all_buses_in_grid.loc[df.columns]
    bus_data = df.T.groupby(buses_in_df).sum().T
    if all_buses:
        bus_data = pd.DataFrame(
            bus_data, columns=grid.bus.index, index=df.index).fillna(0.0)
    
    return bus_data


def summarize_plant_to_location(df, grid):
    """Take a plant-column dataframe and sum to a location-column dataframe.

    :param pandas.DataFrame df: dataframe, columns are plant IDs in Grid.
    :param powersimdata.input.grid.Grid grid: Grid instance.
    :return: (*pandas.DataFrame*) -- index: df index, columns: location tuples.
    """
    _check_df_grid(df, grid)
    
    all_locations = grid.plant[['lat', 'lon']]
    locations_in_df = all_locations.loc[df.columns].to_records(index=False)
    location_data = df.T.groupby(locations_in_df).sum().T
    
    return location_data


def sum_generation_by_type_zone(scenario):
    """Sums generation for a Scenario in Analyze state by {type, zone}.
    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :return: (*pandas.DataFrame*) -- total generation, indexed by {type, zone}.
    :raise Exception: if scenario is not a Scenario object in Analyze state.
    """
    if not isinstance(scenario, Scenario):
        raise TypeError('scenario must be a Scenario object')
    if not isinstance(scenario.state, Analyze):
        raise ValueError('scenario.state must be Analyze')

    pg = scenario.state.get_pg()
    grid = scenario.state.get_grid()
    plant = grid.plant

    summed_gen_series = pg.sum().groupby([plant.type, plant.zone_id]).sum()
    summed_gen_dataframe = summed_gen_series.unstack().fillna(value=0)

    return summed_gen_dataframe
