_MOCK_GRAPH_DATA = {
    '87': {
        'label': '2016 Simulated Base Case',
        'gen': {
            'label': 'Generation',
            'unit': 'TWh',
            'data': {'Washington': {'coal': 4.0, 'solar': 1.0, 'hydro': 5.0}}
        },
        'cap': {
            'label': 'Capacity',
            'unit': 'GW',
            'data': {'Washington': {'coal': 5.0, 'solar': 1.0, 'hydro': 4.0}}
        }
    },
    '2016_nrel': {
        'label': '2016 NREL Data',
        'gen': {
            'label': 'Generation',
            'unit': 'TWh',
            'data': {'Washington': {'coal': 4.0, 'solar': 1.0, 'hydro': 5.0, 'wind': 0.0}}
        },
        'cap': {
            'label': 'Capacity',
            'unit': 'GW',
            'data': {'Washington': {'coal': 3.0, 'solar': 1.0, 'hydro': 4.0, 'wind': 2.0}}
        }
    }
}

# Factory for creating mock graph data
# will eventually have parameters to customize the data returned
def create_mock_graph_data():
    return _MOCK_GRAPH_DATA
