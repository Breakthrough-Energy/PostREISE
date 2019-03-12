import os

import pandas as pd
import paramiko

from postreise.process import const


class PullData(object):
    """This class setup the connection to the server and gets the data from
        the server.
    """

    def __init__(self):
        """Constructor.

        """
        self.sftp = None

    def _late_init(self):
        """This init is called when data is requested.

        """
        ssh = setup_server_connection()
        self.sftp = ssh.open_sftp()
        self.scenario_list = _get_scenario_file_from_server(self.sftp)

    def download(self, scenario_id, field_name):
        """Download data from server.

        :param str scenario_id: scenario index.
        :param str field_name: *'PG'*, *'PF'*, *'demand'*, *'hydro'*, \
            *'solar'*, *'wind'* or *'ct'*.
        :return: (*pandas*) -- data frame.
        :raises NameError: If type not *'PG'*, *'PF'*, *'demand'*, *'hydro'*, \
            *'solar'*, *'wind'* or *'ct'*.
        :raises FileNotFoundError: file not found on server.
        :raises LookupError: if scenario not found.
        """
        if field_name not in ['PG', 'PF',
                              'demand', 'hydro', 'solar', 'wind', 'ct']:
            raise NameError('Choose among PG, PF, demand, hydro,',
                            'solar, wind and ct data.')

        if not self.sftp:
            self._late_init()

        if int(scenario_id) not in self.scenario_list.index.tolist():
            raise LookupError("Scenario not found")
        else:
            scenario = self.scenario_list[
                self.scenario_list.index == int(scenario_id)]

        if field_name == "PG" or field_name == "PF":
            output_file = scenario.output_data_location.values[0] + scenario_id
            file = output_file + '_' + field_name + '.csv'
        else:
            extension = '.pkl' if field_name == 'ct' else '.csv'
            input_file = scenario.input_data_location.values[0] + scenario_id
            file = input_file + '_' + field_name + extension
        try:
            file_object = self.sftp.file(file, 'rb')
        except FileNotFoundError:
            print('File not found on server in location: %s' % file)
            raise
        print('Reading file from server')
        if field_name == 'ct':
            p_out = pd.read_pickle(file_object)
        else:
            p_out = pd.read_csv(file_object, index_col=0, parse_dates=True)
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

        :return: (*list*) -- list of available scenarios.
        """
        if not self.sftp:
            self._late_init()
        return self.scenario_list['name'].tolist()

    def get_scenario_table(self):
        """Returns scenario data frame.

        :return: (*pandas*) -- scenario data frame.
        """
        if not self.sftp:
            self._late_init()
        return self.scenario_list


class PushData(object):
    """This class setup the connection to the server and gets the data from
        the server.

    :param str local_dir: path to local folder where data are enclosed.
    """

    def __init__(self, local_dir=None):
        """Constructor.

        """
        self._check_dir(local_dir)
        self.local_dir = local_dir

    @staticmethod
    def _check_dir(local_dir):
        """Chekcs if local directory exists.

        :param str local_dir: path to local folder where data are enclosed.
        """
        if os.path.isdir(local_dir) is False:
            print("Local folder %s does not exist. Return." % local_dir)
            return

    def upload(self, scenario_id, field_name):
        """Upload data to server.

        :param str scenario_id: scenario index.
        :param str field_name: *'demand'*, *'hydro'*, *'solar'*, *'wind'* or \
            *'ct'*.
        :raises NameError: If type not *'demand'*, *'hydro'*, *'solar'*, \
            *'wind'* or *'ct'*.
        :raises FileNotFoundError: file not found locally.
        :raises LookupError: if scenario not found.
        """
        if field_name not in ['demand', 'hydro', 'solar', 'wind', 'ct']:
            raise NameError('Can only upload demand, hydro, solar, wind',
                            'and ct data.')
        extension = ".pkl" if field_name == 'ct' else ".csv"
        file_name = scenario_id + "_" + field_name + extension
        local_file_path = os.path.join(self.local_dir, file_name)
        if os.path.isfile(local_file_path) is False:
            print("Can't find %s. Return." % local_file_path)
            return
        else:
            ssh = setup_server_connection()
            sftp = ssh.open_sftp()
            scenario_list = _get_scenario_file_from_server(sftp)
            scenario = scenario_list[scenario_list.index == int(scenario_id)]
            remote_dir = scenario.input_data_location.values[0]
            remote_file_path = os.path.join(remote_dir, file_name)
            stdin, stdout, stderr = ssh.exec_command("ls " + remote_file_path)
            if len(stderr.readlines()) == 0:
                print("File already exists on server. Return.")
                return
            else:
                print("Transferring %s to server." % file_name)
                sftp.put(local_file_path, remote_file_path)
                sftp.close()

def setup_server_connection():
    """This function setup the connection to the server.

        :return client: (*paramiko*) -- SSH client object.
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
    return client


def _get_scenario_file_from_server(sftp):
    """Get scenario list from server.

        :param paramiko sftp: Takes an SFTP client object.
        :return scenario_list: (*pandas*) -- data frame.
    """

    full_file_path = const.SCENARIO_LIST_LOCATION
    file_object = sftp.file(full_file_path, 'rb')
    scenario_list = pd.read_csv(file_object)
    return scenario_list
