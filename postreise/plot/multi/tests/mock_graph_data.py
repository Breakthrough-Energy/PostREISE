# Factory for creating mock graph data
# param: more_gen - adds more robust data to mock data generation
# will eventually have more parameters to customize the data returned


def create_mock_graph_data(more_gen=False):
    mock_data = {
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
    more_mock_data = {
        '87': {
            'Arizona': {'solar': 17.0},
            'Colorado': {'ng': 12.0, 'solar': 3.0, 'hydro': 10.0},
            'Oregon': {'wind': 7.0, 'hydro': 5.0},
            'Western': {'solar': 20.0, 'wind': 7.0, 'ng': 12.0, 'hydro': 15}
        },
        '2016_nrel': {
            'Arizona': {'solar': 15.0},
            'Colorado': {'ng': 14.0, 'solar': 5.0, 'hydro': 10.0},
            'Oregon': {'wind': 11.0, 'hydro': 5.0},
            'Western': {'solar': 20.0, 'wind': 11.0, 'ng': 14.0, 'hydro': 15}
        }
    }

    if more_gen is False:
        return mock_data
    else:
        for scenario, data in more_mock_data.items():
            mock_data[scenario]['gen']['data'] = data
        return mock_data
