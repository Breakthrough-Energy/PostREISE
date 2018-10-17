import base64
import getpass
import pandas as pd
import paramiko

def setup_server_connection(key_filename):

    # Host public key from zeus
    key_str = b'AAAAB3NzaC1yc2EAAAADAQABAAABAQDc/Of5N37PGcvE6HD9p9IXBKM2htA0WAnc+eSIaJBEPOVy5ezjcz0tv+wX6rwY93wk91t1c2EyQWEv4jTqyYw5hDM0vFcVCQXxX0DVGyAUHxZ+ytIGJ7RokOLquLHEiFMGrQE8zBq839qf4Kbyz0HmxbAluIjSzWIiiTtXNLLgikfg3X/28n5Nw8QOZX9iwrb86dO3ZzYryviLYzvJ3wCgJe/JTr2bHcT8y1AjxJ3mn99Vc2vgZ+QhproKA2ZkBGnEeiX3PyAiNuiHsiAw9i/UxlHwaFTEy2Q9Em4E/UNFl0VjnYZzMLw3yYrJoqM47t23aKUJ5joxO+Mt9Rjc3nV3'
    key = paramiko.RSAKey(data=base64.b64decode(key_str))

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy)
    client.get_host_keys().add('zeus.intvenlab.com', 'ssh-rsa', key)
    client.connect('zeus.intvenlab.com',key_filename=key_filename)
    sftp = client.open_sftp()
    return sftp

def get_scenario_file_from_server(sftp):

    fullFilePath = '/home/EGM/ScenarioList.csv'
    fileObject = sftp.file(fullFilePath,'rb')
    scenario_list = pd.read_csv(fileObject)
    return scenario_list

def get_PG(sftp,scenario_list,scenario_name):
    # find scenarioname in scenario
    scenario = scenario_list[scenario_list['name'] == scenario_name]
    # Write exception if scenario not found
    output_filePG = scenario.output_data_location.values[0] + scenario_name +'PG.csv'
    outputObject = sftp.file(output_filePG,'rb')
    print('Reading PG file from server')
    PG = pd.read_csv(outputObject,index_col=0,parse_dates=True)
    print('Done reading')
    PG.columns = PG.columns.astype(int)
    # need to shift index because matlab starts from 1
    #PG = PG.rename(columns=lambda x: x-1)
    return PG

def get_PF(sftp,scenario_list,scenario_name):
    # find scenarioname in scenario
    scenario = scenario_list[scenario_list['name'] == scenario_name]
    # Write exception if scenario not found
    output_filePG = scenario.output_data_location.values[0] + scenario_name +'PF.csv'
    outputObject = sftp.file(output_filePG,'rb')
    print('Reading PF file from server')
    PF = pd.read_csv(outputObject,index_col=0,parse_dates=True)
    print('Done reading')
    return PF
