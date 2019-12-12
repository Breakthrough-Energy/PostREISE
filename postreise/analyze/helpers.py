import pandas as pd
from powersimdata.input.grid import Grid

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
