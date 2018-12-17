import os
import sys
from pathlib import Path

import pandas as pd
import paramiko


sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import const

class OutputData(object):
    """Output Data class.
        This class enables you to download data from the server as well
        as from a local folder. The get_data function will first look locally
        if it can find the data requested. If it can't find locally it will
        download it from the server if it can find it there.

        :param str data_dir: Defined local folder location
            to read or save data.

    """

    def __init__(self, data_dir=None):

        self.data_dir = data_dir
        self.TD = TransferData()
        # Check if data can be found localy
        if not data_dir:
            home_dir = str(Path.home())
            self.data_dir = os.path.join(home_dir, 'scenario_data', '')

            print('Use ', self.data_dir, ' to save/load local scenario data.')

    def get_data(self, run_name, field_name):
        """Get data either from server or from local dir.

            :param str run_name: Name of run to get data from.
            :param str field_name: PG or PF data.
            :return: Returns pandas DataFrame.
            :raises FileNotFoundError: run_name file neither localy nor on
                the server.
            :raises NameError: If type not PG or PF.
        """
        if field_name not in ['PG', 'PF']:
            raise NameError('Can only get PG or PF data.')
        try:
            p_out = pd.read_pickle(
                self.data_dir + run_name + field_name + '.pkl'
            )
        except FileNotFoundError:
            print('Local file not found will',
                  'download data from server and save locally.')
            try:
                p_out = self.TD.get_data(run_name, field_name)
            except FileNotFoundError as e:
                raise FileNotFoundError(
                    'File found neither localy nor on server.'
                ) from e
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
            print('Saving file localy.')
            p_out.to_pickle(self.data_dir + run_name + field_name + '.pkl')
        return p_out


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

    def get_data(self, run_name, field_name):
        """Get data either from server.

            :param str run_name: Name of run to get data from.
            :param str field_name: PG or PF data.
            :return: Returns pandas DataFrame.
            :raises NameError: If type not PG or PF.
            :raises FileNotFoundError: run name file not on server.
            :raises LookupError: If run_name can not be found in scenario_list
                or more than one entry found.
        """
        if field_name not in ['PG', 'PF']:
            raise NameError('Can only get PG or PF data.')
        if not self.sftp:
            self._late_init()
        run = self.scenario_list[self.scenario_list['name'] == run_name]
        if run.shape[0] == 0:
            raise LookupError('Run name not found in scenario list.')
        elif run.shape[0] > 1:
            print('More than one run found with same name.')
            raise LookupError('More than one run found with same name.')
        output_file = run.output_data_location.values[0] + run_name
        output_file = output_file + field_name + '.csv'
        try:
            output_object = self.sftp.file(output_file, 'rb')
        except FileNotFoundError:
            print('File not found on server in location:')
            print(output_file)
            print('File may not be converted from .mat format.')
            raise
        print('Reading ' + field_name + ' file from server.')
        p_out = pd.read_csv(output_object, index_col=0, parse_dates=True)
        p_out.columns = p_out.columns.astype(int)
        return p_out

    def show_scenario_list(self):
        """Show scenario list

        """
        if not self.sftp:
            self._late_init()
        print(self.scenario_list['name'])


def _setup_server_connection():
    """This function setup the connection to the server.

        :return sftp: Returns the sftp object.
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

        :param sftp: Takes an sftp object.
        :return scenario_list: Returns scenario_list pandas DataFrame
    """

    full_file_path = const.SCENARIO_LIST_LOCATION
    file_object = sftp.file(full_file_path, 'rb')
    scenario_list = pd.read_csv(file_object)
    return scenario_list
