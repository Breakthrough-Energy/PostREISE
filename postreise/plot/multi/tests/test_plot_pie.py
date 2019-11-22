from postreise.plot.multi.constants import RESOURCE_COLORS
from postreise.plot.multi.plot_pie import (_construct_pie_ax_data,
                                           _roll_up_small_pie_wedges)
from postreise.plot.multi.tests.mock_graph_data import create_mock_graph_data

# Since these are unit tests we're intentionally not testing methods that only have visualization code


def test_construct_pie_ax_data():
    ax_data_list = _construct_pie_ax_data(
        'Washington', create_mock_graph_data(), min_percentage=0)
    expected_output = [{
        'title': '2016 Simulated Base Case\nGeneration',
        'labels': ['Coal', 'Solar', 'Hydro'],
        'values': [4, 1, 5],
        'colors': [RESOURCE_COLORS['coal'], RESOURCE_COLORS['solar'], RESOURCE_COLORS['hydro']],
        'unit': 'TWh'
    }, {
        'title': '2016 Simulated Base Case\nCapacity',
        'labels': ['Coal', 'Solar', 'Hydro'],
        'values': [5, 1, 4],
        'colors': [RESOURCE_COLORS['coal'], RESOURCE_COLORS['solar'], RESOURCE_COLORS['hydro']],
        'unit': 'GW'
    }, {
        'title': '2016 NREL Data\nGeneration',
        'labels': ['Coal', 'Solar', 'Hydro'],
        'values': [4, 1, 5],
        'colors': [RESOURCE_COLORS['coal'], RESOURCE_COLORS['solar'], RESOURCE_COLORS['hydro']],
        'unit': 'TWh'
    }, {
        'title': '2016 NREL Data\nCapacity',
        'labels': ['Coal', 'Solar', 'Hydro', 'Wind'],
        'values': [3, 1, 4, 2],
        'colors': [RESOURCE_COLORS['coal'], RESOURCE_COLORS['solar'], RESOURCE_COLORS['hydro'], RESOURCE_COLORS['wind']],
        'unit': 'GW'
    }]
    assert ax_data_list == expected_output


def test_roll_up_small_pie_wedges():
    ax_data, labels = _roll_up_small_pie_wedges(
        {'coal': 4, 'solar': 1, 'hydro': 5}, 0)
    assert ax_data == {'coal': 4, 'solar': 1, 'hydro': 5}
    assert labels == ['Coal', 'Solar', 'Hydro']


def test_roll_up_small_pie_wedges_with_zero_values():
    ax_data, labels = _roll_up_small_pie_wedges(
        {'coal': 0, 'solar': 1, 'hydro': 5}, 0)
    assert ax_data == {'solar': 1, 'hydro': 5}
    assert labels == ['Solar', 'Hydro']


def test_roll_up_small_pie_wedges_with_other_category():
    ax_data, labels = _roll_up_small_pie_wedges(
        {'coal': 3, 'solar': 1, 'hydro': 4, 'wind': 2}, 20)
    assert ax_data == {'coal': 3, 'hydro': 4, 'other': 3}
    assert labels == ['Coal', 'Hydro', f'Solar 10.0%\nWind 20.0%\n']
