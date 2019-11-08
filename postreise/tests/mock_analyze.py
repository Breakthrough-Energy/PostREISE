from powersimdata.scenario.analyze import Analyze
from postreise.tests.mock_grid import MockGrid

class MockAnalyze:
    def __init__(self, grid_attrs, pg):
        """Constructor.

        :param dict grid_attrs: fields to be added to grid.
        :param pandas.DataFrame pg: dummy pg
        """
        self.grid = MockGrid(grid_attrs)
        self.pg = pg

    def get_grid(self):
        """Get grid

        :return: (MockGrid) -- mock grid
        """
        return self.grid

    def get_pg(self):
        """Get PG

        :return: (pandas.DataFrame) -- dummy pg
        """
        return self.pg
    
    @property
    def __class__(self):
        """If anyone asks, I'm an Analyze object!"""
        return Analyze
