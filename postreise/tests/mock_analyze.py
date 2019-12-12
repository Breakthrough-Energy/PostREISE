from powersimdata.scenario.analyze import Analyze
from postreise.tests.mock_grid import MockGrid


class MockAnalyze:
    def __init__(self, grid_attrs, demand=None, lmp=None, pg=None, solar=None,
                 wind=None):
        """Constructor.

        :param dict grid_attrs: fields to be added to grid.
        :param pandas.DataFrame pg: dummy pg
        """
        self.grid = MockGrid(grid_attrs)
        self.demand = demand
        self.lmp = lmp
        self.pg = pg
        self.solar = solar
        self.wind = wind

    def get_demand(self, original=None):
        """Get demand.
        :return: (pandas.DataFrame) -- dummy demand
        """
        return self.demand

    def get_grid(self):
        """Get grid.
        :return: (MockGrid) -- mock grid
        """
        return self.grid

    def get_lmp(self):
        """Get lmp.
        :return: (pandas.DataFrame) -- dummy lmp
        """
        return self.lmp

    def get_pg(self):
        """Get PG.
        :return: (pandas.DataFrame) -- dummy pg
        """
        return self.pg

    def get_solar(self):
        """Get solar.
        :return: (pandas.DataFrame) -- dummy solar
        """
        return self.solar

    def get_wind(self):
        """Get wind.
        :return: (pandas.DataFrame) -- dummy wind
        """
        return self.wind

    @property
    def __class__(self):
        """If anyone asks, I'm an Analyze object!"""
        return Analyze
