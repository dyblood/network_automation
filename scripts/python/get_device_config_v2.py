import json
import re
import os
import csv
from netmiko import ConnectHandler
from netmiko import NetmikoTimeoutException, NetmikoAuthenticationException
from ciscoconfparse import CiscoConfParse
from get_device_list_cvs import *

load_dotenv()

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
        # dev_name = f'C:\\Users\\devon.d.youngblood\\OneDrive - US Army\\Desktop\\youngblood_netops\\dev_configs_backup\\{hostname}.conf'
        dev_name = f'/mnt/c/Users/devon.d.youngblood/OneDrive - US Army/Desktop/youngblood_netops/dev_configs_backup/{hostname}.conf'
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
    # create_csv_tracker(device_list)
    # tracker_path = 'C:\\Users\\devon.d.youngblood\\OneDrive - US Army\\Desktop\\dev_configs\\cvs\\find_delete_tracker.csv'
    # not_conf_dev_list = not_configured_devices(tracker_path)
    # dev_unreachable_list = []
    # dev_already_conf_list = []
    # dev_conf_list = []
    for i in device_list:
        if i['reachability'] == 'Reachable':
            print('+' * 40, 'START', i["hostname"], 'START','+' * 43)
            device = i
            connection = connect_device(i)
            if connection:
                # dev_conf_list.append(i['hostname'])
                parse = parse_device_config(connection, i['hostname'])
                # find_acl_lines(connection, parse, parent_search, child_search)
                # find_interface_lines(connection, parse, parent_search2, child_search2)
                # find_any_lines(connection, parse, child_search)
                # find_any_lines(connection, parse, child_search3)
                # find_any_lines(connection, parse, child_search4)
                # additional_commands(connection)
                save_and_exit(connection)
            print('+' * 40, 'COMPLETE', i["hostname"], 'COMPLETE','+' * 40)
       
    print('*' * 70, 'COMPLETE','*' * 70)

    # print('The following devices have been configured and will be updated in the find_delete_tracker.cvs file:')
    # for i in dev_conf_list:
    #     update_configured_status(i)
    
    # print("The following devices were unreachable:")
    # for i in dev_unreachable_list:
    #     print(i)
    
    # print("The following devices were reachable but already configured:")
    # for i in dev_already_conf_list:
    #     print(i)

    


if __name__ == "__main__":
    main()


