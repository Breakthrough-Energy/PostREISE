from postreise.process import transferdata as td


def test_setup_server_connection():
    td.setup_server_connection()


def test_get_scenario_file_from_server():
    ssh_client = td.setup_server_connection()
    td.get_scenario_table(ssh_client)

