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
        self.execute_list = _get_execute_file_from_server(self.sftp)

    def download(self, scenario_id, field_name, from_dir):
        """Download data from server.

        :param str scenario_id: scenario id.
        :param str field_name: *'PG'*, *'PF'*, *'demand'*, *'hydro'*, \
            *'solar'*, *'wind'* or *'ct'*.
        :param str from_dir: remote directory.
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

        extension = '.pkl' if field_name == 'ct' else '.csv'
        file = scenario_id + '_' + field_name + extension

        try:
            file_object = self.sftp.file(from_dir + '/' + file, 'rb')
        except FileNotFoundError:
            print("%s not found in %s on server" % (file, from_dir))
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

    def get_execute_table(self):
        """Returns scenario table.

        :return: (*pandas*) -- execute table.
        """
        if not self.sftp:
            self._late_init()
        return self.execute_list


class PushData(object):
    """This class setup the connection to the server and gets the data from
        the server.

    """

    def upload(self, scenario_id, field_name, from_dir, to_dir):
        """Uploads data to server.

        :param str scenario_id: scenario index.
        :param str field_name: *'demand'*, *'hydro'*, *'solar'*, *'wind'* or \
            *'ct'*.
        :param str from_dir: local directory.
        :param str to_dir: remote directory.
        :raises ValueError: if second argument is not one of *'demand'*, \
            *'hydro'*, *'solar'*, *'wind'* or *'ct'*.
        :raises IOError: if file already exists on server.
        """
        possible = ['demand', 'hydro', 'solar', 'wind', 'ct']
        if field_name not in possible:
            raise ValueError("Only %s data can be uploaded" % "/".join(possible))

        extension = ".pkl" if field_name == 'ct' else ".csv"
        file_name = scenario_id + "_" + field_name + extension
        from_path = os.path.join(from_dir, file_name)

        if os.path.isfile(from_path) is False:
            raise FileNotFoundError("%s not found in %s on local machine" %
                                    (file_name, from_dir))
        else:
            ssh = setup_server_connection()
            sftp = ssh.open_sftp()
            scenario_list = _get_scenario_file_from_server(sftp)
            scenario = scenario_list[scenario_list.id == scenario_id]
            to_path = os.path.join(to_dir, file_name)
            stdin, stdout, stderr = ssh.exec_command("ls " + to_path)
            if len(stderr.readlines()) == 0:
                raise IOError("%s already exists in %s on server" %
                              (file_name, to_dir))
            else:
                print("Transferring %s to server" % from_path)
                sftp.put(from_path, to_path)
                sftp.close()

def setup_server_connection():
    """This function setup the connection to the server.

    :return: (*paramiko*) -- SSH client object.
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
    :return: (*pandas*) -- data frame.
    """
    full_file_path = const.SCENARIO_LIST
    file_object = sftp.file(full_file_path, 'rb')
    scenario_list = pd.read_csv(file_object)
    scenario_list.fillna('', inplace=True)
    return scenario_list.astype(str)

def _get_execute_file_from_server(sftp):
    """Get execute list from server.

    :param paramiko sftp: Takes an SFTP client object.
    :return: (*pandas*) -- data frame.
    """
    full_file_path = const.EXECUTE_LIST
    file_object = sftp.file(full_file_path, 'rb')
    execute_list = pd.read_csv(file_object)
    execute_list.fillna('', inplace=True)
    return execute_list.astype(str)
