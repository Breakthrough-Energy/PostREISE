from postreise.process import const

import os
import pandas as pd
import paramiko
from pathlib import Path



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

        :param str scenario_id: scenario id.
        :param str field_name: *'PG'*, *'PF'*, *'demand'*, *'hydro'*, \
            *'solar'*, *'wind'* or *'ct'*.
        :return: (*pandas*) -- data frame.
        :raises ValueError: if second argument is not one of *'PG'*, \
            *'PF'*, *'demand'*, *'hydro'*, *'solar'*, *'wind'* or *'ct'*.
        :raises FileNotFoundError: if file not found on server.
        :raises LookupError: if scenario not found.
        """
        possible = ['PG', 'PF', 'demand', 'hydro', 'solar', 'wind', 'ct']
        if field_name not in possible:
            raise ValueError("Only %s data can be downloaded" % "/".join(possible))

        if not self.sftp:
            self._late_init()

        if scenario_id not in self.scenario_list.id.tolist():
            raise LookupError("Scenario not found")
        else:
            scenario = self.scenario_list[self.scenario_list.id == scenario_id]

        if field_name == "PG" or field_name == "PF":
            dir = const.REMOTE_DIR_OUTPUT
            file = scenario_id + '_' + field_name + '.csv'
        else:
            extension = '.pkl' if field_name == 'ct' else '.csv'
            dir = const.REMOTE_DIR_INPUT
            file = scenario_id + '_' + field_name + extension

        try:
            file_object = self.sftp.file(dir + '/' + file, 'rb')
        except FileNotFoundError:
            print("%s not found in %s on server" % (file, dir))
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
        """Returns scenario table.

        :return: (*pandas*) -- scenario table.
        """
        if not self.sftp:
            self._late_init()
        return self.scenario_list


class PushData(object):
    """This class setup the connection to the server and gets the data from
        the server.

    """

    def __init__(self):
        """Constructor.

        """
        self.local_dir = const.LOCAL_DIR
        # Check if data can be found locally
        if not self.local_dir:
            home_dir = str(Path.home())
            self.local_dir = os.path.join(home_dir, 'scenario_data', '')

    def upload(self, scenario_id, field_name):
        """Upload data to server.

        :param str scenario_id: scenario index.
        :param str field_name: *'demand'*, *'hydro'*, *'solar'*, *'wind'* or \
            *'ct'*.
        :raises ValueError: if second argument is not one of *'demand'*, \
            *'hydro'*, *'solar'*, *'wind'* or *'ct'*.
        """
        possible = ['demand', 'hydro', 'solar', 'wind', 'ct']
        if field_name not in possible:
            raise ValueError("Only %s data can be uploaded" % "/".join(possible))

        extension = ".pkl" if field_name == 'ct' else ".csv"
        file_name = scenario_id + "_" + field_name + extension
        local_file_path = os.path.join(self.local_dir, file_name)

        if os.path.isfile(local_file_path) is False:
            print("%s not found." % local_file_path)
            return
        else:
            ssh = setup_server_connection()
            sftp = ssh.open_sftp()
            scenario_list = _get_scenario_file_from_server(sftp)
            scenario = scenario_list[scenario_list.id == scenario_id]
            remote_file_path = os.path.join(const.REMOTE_DIR_INPUT, file_name)
            stdin, stdout, stderr = ssh.exec_command("ls " + remote_file_path)
            if len(stderr.readlines()) == 0:
                print("File already on server. Return.")
                return
            else:
                print("Transferring %s to server" % local_file_path)
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
        ssh_known_hosts = input('Please provide ssh known_hosts key file =')
        while True:
            try:
                client.load_system_host_keys(str(ssh_known_hosts))
                break
            except IOError:
                print('Can not read file, try again')
                ssh_known_hosts = input(
                    'Please provide ssh known_hosts key file =')

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
    scenario_list.fillna('', inplace=True)
    return scenario_list.astype(str)
