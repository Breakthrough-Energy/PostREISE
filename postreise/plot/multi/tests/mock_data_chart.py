import pandas as pd

# Factory for creating mock data chart
# will eventually have parameters to customize the data returned


def create_mock_data_chart():
    """Factory for creating mock data chart
        will eventually have parameters to customize the data returned

    :return: mock data chart
    :rtype: dict
    """
    return {
        "Washington": {
            "Generation": pd.DataFrame(
                {
                    "coal": {"12252016": 2000000, "12262016": 2000000},
                    "solar": {"12252016": 0000000, "12262016": 1000000},
                    "hydro": {"12252016": 3000000, "12262016": 2000000},
                }
            ),
            "Capacity": {"coal": 5000, "solar": 1000, "hydro": 4000},
        }
    }
