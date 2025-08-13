import json
import re
import os
import csv
from netmiko import ConnectHandler
from netmiko import NetmikoTimeoutException, NetmikoAuthenticationException
from ciscoconfparse import CiscoConfParse
from get_device_list_cvs import *
from dotenv import load_dotenv
load_dotenv()

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

DNAC_BURL = os.getenv('DNAC_BURL')
DNAC_USER = os.getenv('DNAC_USER')
DNAC_PASS = os.getenv('DNAC_PASS')
WIN_DESK_PATH = os.getenv('WIN_DESK_PATH')
CONFIG_DIR = f"{WIN_DESK_PATH}youngblood_netops/device_configs_backup/"

def connect_device(device):
    try:
        # Establish the connection | send the commmand | disconnect
        # connection = ConnectHandler(**device)
        connection = ConnectHandler(
            device_type = device["device_type"],
            host = device["host"],
            username = DNAC_USER,
            password = DNAC_PASS
        )
        return connection

    except NetmikoTimeoutException:
        print(f"Timeout connecting to {device["host"]}")
        return None
    except NetmikoAuthenticationException:
        print(f"Authentication failure for {device["host"]}")
        return None

def parse_device_config(connection, hostname):
    try:
        # saves running config as output variable.
        output = connection.send_command('show running-config')
        
        #saving running config as a .conf file so that it can get parsed by CiscoConfParse
        dev_config = output
        dev_name = f'{CONFIG_DIR}{hostname}.conf'
        with open(dev_name, 'w') as file:
            file.write(dev_config)
        print(f'sucessfully made {dev_name}')

        #Parse the running config w/ CiscoConfParse
        parse = CiscoConfParse(dev_name, syntax="ios")

        return parse

    except Exception as e:
        print(f'An error occured: {e}')
def save_and_exit(connection):
    try:
        #Just pulling the current running config so write memory is commented out
        #write memory
        #cmd_output = connection.send_command('write memory')
        #Fprint(cmd_output)

        #disconnect
        connection.disconnect()
    
    except Exception as e:
        print(f'An error occured: {e}')

def main():
    get_device_list()
    device_list = cvs_to_dict()
    for i in device_list:
        if i['reachability'] == 'Reachable':
            print('+' * 40, 'START', i["hostname"], 'START','+' * 43)
            device = i
            connection = connect_device(i)
            if connection:
                parse = parse_device_config(connection, i['hostname'])
                save_and_exit(connection)
            print('+' * 40, 'COMPLETE', i["hostname"], 'COMPLETE','+' * 40)
       
    print('*' * 70, 'COMPLETE','*' * 70)
    
if __name__ == "__main__":
    main()


