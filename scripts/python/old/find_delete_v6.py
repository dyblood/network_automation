import json
import re
import os
import csv
from netmiko import ConnectHandler
from netmiko import NetmikoTimeoutException, NetmikoAuthenticationException
from ciscoconfparse import CiscoConfParse
from testbed_FAK import *
from get_device_list_cvs import *

parent_search = '^ip access-list'
child_search = '160.136.16.63'
parent_search2 = '^interface'
child_search2 = 'NETFLOW'
child_search3 = 'flow monitor NETFLOW1'
child_search4 = 'flow exporter NETFLOW1'

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
        dev_name = f'C:\\Users\\devon.d.youngblood\\OneDrive - US Army\\Desktop\\dev_configs\\{hostname}.conf'
        with open(dev_name, 'w') as file:
            file.write(dev_config)
        print('sucessfully made {dev_name}')

        #Parse the running config w/ CiscoConfParse
        parse = CiscoConfParse(dev_name, syntax="ios")

        return parse

    except Exception as e:
        print(f'An error occured: {e}')

def find_acl_lines(connection, parse, parentspec, childspec):
    try:
        acl_obj_parent = parse.find_objects_w_child(parentspec=parent_search, childspec=child_search)
        for p_obj in acl_obj_parent: #iterates through all the acl names
            print(f'{p_obj.text}')
            for c_obj in p_obj.children: #iterates through all acl lines under acl
                if child_search in c_obj.text: 
                    cmd_list = [f'{p_obj.text}',
                                f'no{c_obj.text}'
                                ]
                    cmd_output = connection.send_config_set(cmd_list)
                    print(cmd_output)
    except Exception as e:
        print(f'An error occured: {e}')

def find_interface_lines(connection, parse, parentspec, childspec):
    try:
        #searching for interfaces and all values under those interfaces.
        interface_obj_parent = parse.find_objects_w_child(parentspec=parent_search2, childspec=child_search2)
        for p_obj in interface_obj_parent:
            print(f'{p_obj.text}')
            for c_obj in p_obj.children:
                if child_search2 in c_obj.text:
                    # print(f'{c_obj.text}')
                    cmd_list = [f'{p_obj.text.lstrip()}',
                                f'no {c_obj.text.lstrip()}'
                                ]
                    cmd_output = connection.send_config_set(cmd_list)
                    print(cmd_output)   
    except Exception as e:
        print(f'An error occured: {e}')

def find_any_lines(connection, parse, child_search):
    try:
        #deleting anything else that starts has 160.136.16.63 in it.
        obj_parent = parse.find_parents_wo_child(parentspec=child_search, childspec=child_search)
        for i in obj_parent:
            # print(f'{i}')
            cmd_output = connection.send_config_set(f'no {i.lstrip()}')
            print(cmd_output)
    except Exception as e:
        print(f'An error occured: {e}')

def additional_commands(connection):
    try:
        #After netflow is removed from the interfaces monitor NETFLOW1 and exporter NETFLOW1 can be removed. (has to be in that specific order)
        cmd_output = connection.send_config_set('no flow monitor NETFLOW1')
        print(cmd_output) 
        cmd_output = connection.send_config_set('no flow exporter NETFLOW1')
        print(cmd_output)  
    except Exception as e:
        print(f'An error occured: {e}')

def save_and_exit(connection):
    try:
        #write memory
        cmd_output = connection.send_command('write memory')
        print(cmd_output)

        #disconnect
        connection.disconnect()
    
    except Exception as e:
        print(f'An error occured: {e}')

def create_csv_tracker(device_list):
    filename = 'C:\\Users\\devon.d.youngblood\\OneDrive - US Army\\Desktop\\dev_configs\\cvs\\find_delete_tracker.csv'
    # filename = 'find_delete_tracker.cvs'
    
    # Check if the CSV file exists
    if not os.path.isfile(filename):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Write the header
            writer.writerow(['hostname', 'ip_address', 'configured'])
            # Write the rows from the dictionary
            for i in device_list:
                writer.writerow([i['hostname'], i['host'], 'no'])
        print(f"{filename} created.")
    else:
        print(f"{filename} already exists.")

def update_configured_status(hostname):
    filename = 'C:\\Users\\devon.d.youngblood\\OneDrive - US Army\\Desktop\\dev_configs\\cvs\\find_delete_tracker.csv'
    
    if not os.path.isfile(filename):
        print(f"{filename} does not exist. Please create it first.")
        return
    
    updated_rows = []
    with open(filename, mode='r', newline='') as file:
        reader = csv.reader(file)
        header = next(reader)  # Read the header
        updated_rows.append(header)  # Keep the header
        
        # Update the configured status
        for row in reader:
            if row[0] == hostname:
                row[2] = 'yes'  # Update the configured column to "yes"
            updated_rows.append(row)
    
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_rows)  # Write all rows back to the file
    print(f"Configured status for {hostname} updated to 'yes'.")

def not_configured_devices(tracker_path):
    dev_tracker_list = []
    with open(tracker_path, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        dev_tracker_list_dict = [row for row in reader]
    
    for i in dev_tracker_list_dict:
        if i['configured'] != 'yes':
            dev_tracker_list.append(i['hostname'])  
    return dev_tracker_list   


def main():
    get_device_list()
    device_list = cvs_to_dict()
    create_csv_tracker(device_list)
    tracker_path = 'C:\\Users\\devon.d.youngblood\\OneDrive - US Army\\Desktop\\dev_configs\\cvs\\find_delete_tracker.csv'
    not_conf_dev_list = not_configured_devices(tracker_path)
    dev_unreachable_list = []
    dev_already_conf_list = []
    dev_conf_list = []
    for i in device_list:
        if i['reachability'] == 'Reachable' and i['hostname'] in not_conf_dev_list:
            print('+' * 40, 'START', i["hostname"], 'START','+' * 43)
            device = i
            connection = connect_device(i)
            if connection:
                dev_conf_list.append(i['hostname'])
                parse = parse_device_config(connection, i['hostname'])
                find_acl_lines(connection, parse, parent_search, child_search)
                find_interface_lines(connection, parse, parent_search2, child_search2)
                find_any_lines(connection, parse, child_search)
                find_any_lines(connection, parse, child_search3)
                find_any_lines(connection, parse, child_search4)
                # additional_commands(connection)
                save_and_exit(connection)
            print('+' * 40, 'COMPLETE', i["hostname"], 'COMPLETE','+' * 40)
        elif i['reachability'] == 'Unreachable':
            dev_unreachable_list.append(i['hostname'])
        else:
            dev_already_conf_list.append(i['hostname'])        
    print('*' * 70, 'COMPLETE','*' * 70)

    print('The following devices have been configured and will be updated in the find_delete_tracker.cvs file:')
    for i in dev_conf_list:
        update_configured_status(i)
    
    # print("The following devices were unreachable:")
    # for i in dev_unreachable_list:
    #     print(i)
    
    # print("The following devices were reachable but already configured:")
    # for i in dev_already_conf_list:
    #     print(i)

    


if __name__ == "__main__":
    main()

