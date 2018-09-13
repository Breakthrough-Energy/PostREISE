import unittest

import sys
sys.path.append("..")
import analyze

sftp = analyze.setup_server_connection("c:/Users/kmueller/.ssh/id_rsa")
scenario_list = analyze.get_scenario_file_from_server(sftp)
scenario_name = 'parallel_western_scenario03'
PG = analyze.get_PG(sftp,scenario_list,scenario_name)
PF = analyze.get_PF(sftp,scenario_list,scenario_name)
