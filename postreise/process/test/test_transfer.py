import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import transferdata as td


def test_setup_server_connection():
    transfer = td.TransferData()
    td._setup_server_connection()


def test_get_scenario_file_from_server():
    transfer = td.TransferData()
    sftp = td._setup_server_connection()
    td._get_scenario_file_from_server(sftp)


def test_get_data():
    od = td.OutputData()
    od.get_data('western_scenarioUnitTest02', 'PG')
    od.get_data('western_scenarioUnitTest02', 'PF')
