import pandas as pd


class MockGrid:
    def __init__(self, field_name):
        """ Constructor.

        :param list field_name: field to be added.
        """
        if 'plant' in field_name:
            self.plant = pd.DataFrame(
                {'plant_id': [101, 102, 103, 104, 105],
                 'bus_id': [1001, 1002, 1003, 1004, 1005],
                 'type': ['solar', 'wind', 'ng', 'coal', 'dfo'],
                 'zone_id': [1, 2, 3, 1, 3],
                 'GenMWMax':[200, 150, 100, 300, 120],
                 'GenFuelCost': [0, 0, 3.3, 4.4, 5.5],
                 'Pmin': [20, 30, 25, 100, 20],
                 'Pmax': [40, 80, 50, 150, 80]})
            self.plant.set_index('plant_id', inplace=True)

        if 'branch' in field_name:
            self.branch = pd.DataFrame(
                {'from_zone_id': [1, 2, 3, 1, 3],
                 'to_zone_id': [1, 3, 2, 2, 3],
                 'branch_id': [11, 12, 13, 14, 15],
                 'rateA': [10, 20, 30, 40, 50],
                 'x': [0.1, 0.2, 0.3, 0.4, 0.5]})
            self.branch.set_index('branch_id', inplace=True)

        if 'dcline' in field_name:
            self.dcline = pd.DataFrame(
                {'dcline_id': [101, 102, 103, 104, 105],
                 'status': [1, 1, 1, 1, 1],
                 'Pmax': [100, 200, 300, 400, 500]})
            self.branch.set_index('dcline_id', inplace=True)

        if 'gencost' in field_name:
            self.gencost = pd.DataFrame(
                {'plant_id': [101, 102, 103, 104, 105],
                 'type': [2] * 5,
                 'startup': [0] * 5,
                 'shutdown': [0] * 5,
                 'n': [3] * 5,
                 'c2': [1, 2, 3, 4, 5],
                 'c1': [10, 20, 30, 40, 50],
                 'c0': [100, 200, 300, 400, 500],
                 'interconnect': ['Western'] * 5})
            self.gencost.set_index('plant_id', inplace=True)


class MockOutput:
    def __init__(self, period_num):
        """ Constructor.

        :param int period_num: number of hours.
        """
        self.gen_num = len(MockGrid(['plant']).plant)
        self.period_num = period_num

    def get_pg(self):
        """ Return power generated.

        :return: (*pandas.DataFrame*) -- power generated.
        """
        pg = pd.DataFrame({
            (i + 101): [(i+1)*(p+1) for p in range(self.period_num)]
            for i in range(self.gen_num)})
        pg.set_index(pd.date_range(
            start='2016-01-01', periods=self.period_num, freq='H'),
            inplace=True)
        pg.index.name = 'UTC'
        return pg


class MockScenario:
    def __init__(self, grid_field_name, period_num):
        """ Constructor.

        :param list grid_field_name: field to be added to grid.
        :param int n_period: number of hours
        """
        self.grid_field_name = grid_field_name
        self.period_num = period_num

    def get_grid(self):
        """Get grid

        :return: (GridMock) -- mock grid
        """
        return MockGrid(self.grid_field_name)

    def get_pg(self):
        return MockOutput(self.period_num).get_pg()

