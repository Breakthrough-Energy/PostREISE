import pandas as pd
import paramiko

from postreise.process import const


class TransferData(object):
    """This class setup the connection to the server and gets the data from
        the server.
    """

    def __init__(self):
        self.sftp = None

    def _late_init(self):
        """This init is called when data is requested.

        """
        self.sftp = _setup_server_connection()
        self.scenario_list = _get_scenario_file_from_server(self.sftp)

    def get_data(self, scenario_name, field_name):
        """Get data from server.

        :param str scenario_name: name of scenario to get data from.
        :param str field_name: *'PG'*, *'PF'*, *'demand'*, *'hydro'*, \ 
            *'solar'* or *'wind'*.
        :return: (*pandas*) -- data frame.
        :raises NameError: If type not *'PG'*, *'PF'*, *'demand'*, *'hydro'*, \ 
            *'solar'* or *'wind'*.
        :raises FileNotFoundError: file not found on server.
        :raises LookupError: if scenario not found or more than one entry \ 
            is found.        
        """

        if field_name not in ['PG', 'PF', 'demand', 'hydro', 'solar', 'wind']:
            raise NameError('Can only get PG, PF, demand, hydro, solar and \
                            wind data.')
        if not self.sftp:
            self._late_init()
        scenario = self.scenario_list[
            self.scenario_list['name'] == scenario_name]
        if scenario.shape[0] == 0:
            raise LookupError('Scenario name not found in scenario list.')
        elif scenario.shape[0] > 1:
            print('More than one scenario found with same name.')
            raise LookupError('More than one scenario found with same name.')
        if field_name == "PG" or field_name == "PF":
            output_file = scenario.output_data_location.values[0] + \
                          scenario_name
            file = output_file + '_' + field_name + '.csv'
        else:
            input_file = scenario.input_data_location.values[0] + \
                         scenario_name
            file = input_file + '_' + field_name + '.csv'            
        try:
            file_object = self.sftp.file(file, 'rb')
        except FileNotFoundError:
            print('File not found on server in location:')
            print(file)
            print('File may not be converted from .mat format.')
            raise
        print('Reading ' + field_name + ' file from server.')
        p_out = pd.read_csv(file_object, index_col=0, parse_dates=True)
        
        if field_name != "demand":
            p_out.columns = p_out.columns.astype(int)
        
        return p_out

    def show_scenario_list(self):
        """Shows scenario list.

        """
        if not self.sftp:
            self._late_init()
        print(self.scenario_list['name'])

    def get_scenario_list(self):
        """Returns scenario list.

        """
        if not self.sftp:
            self._late_init()
        return self.scenario_list['name'].values

def _setup_server_connection():
    """This function setup the connection to the server.

        :return sftp: (*paramiko*) -- SFTP client object.
    """

    client = paramiko.SSHClient()
    try:
        client.load_system_host_keys()
    except IOError:
        print('Could not find ssh host keys.')
        ssh_known_hosts = input(
            'Please provide ssh known_hosts key file ='
        )
        while True:
            try:
                client.load_system_host_keys(str(ssh_known_hosts))
                break
            except IOError:
                print('Can not read file, try again')
                ssh_known_hosts = input(
                    'Please provide ssh known_hosts key file ='
                )

    client.connect(const.SERVER_ADDRESS)
    sftp = client.open_sftp()
    return sftp


def _get_scenario_file_from_server(sftp):
    """Get scenario list from server.

        :param paramiko sftp: Takes an SFTP client object.
        :return scenario_list: (*pandas*) -- data frame.
    """

    full_file_path = const.SCENARIO_LIST_LOCATION
    file_object = sftp.file(full_file_path, 'rb')
    scenario_list = pd.read_csv(file_object)
    return scenario_list
