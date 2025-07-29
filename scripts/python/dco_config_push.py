from netmiko import ConnectHandler
from netmiko import NetmikoTimeoutException, NetmikoAuthenticationException
from testbed_FAK import *
# Define the list of routers (you can add as many routers as needed)

routers = [ DCO_101_RTR, DCO_102_RTR, DCO_201_RTR, DCO_202_RTR, DCO_301_RTR,
            DCO_401_RTR, DCO_501_RTR, DCO_502_RTR, DCO_601_RTR, 
            DCO_701_RTR, DCO_801_RTR, DCO_901_RTR, DCO_1001_RTR
]

# Commands to run on the routers
cmd_list = [
    "no voice register pool 1",
    "no voice service voip",
    "no mgcp",
    "!",
    "no mgcp call-agent anhqa0cms.arnorth.army.mil 2427 service-type mgcp version 0.1",
    "no mgcp dtmf-relay voip codec all mode out-of-band",
    "no mgcp rtp unreachable timeout 1000 action notify",
    "!",
    "no mgcp modem passthrough voip mode nse",
    "no mgcp package-capability rtp-package",
    "no mgcp package-capability sst-package",
    "no mgcp package-capability pre-package",
    "!",
    "!",
    "no mgcp sdp simple",
    "no mgcp fax t38 inhibit",
    "no mgcp rtp payload-type g726r16 static",
    "no mgcp bind control source-interface Vlan3186",
    "no mgcp bind media source-interface Vlan3186",
    "no mgcp behavior rsip-range tgcp-only",
    "no mgcp behavior comedia-role none",
    "!",
    "!",
    "no mgcp behavior comedia-check-media-src disable",
    "no mgcp behavior comedia-sdp-force disable",
    "no ccm-manager music-on-hold",
    "no ccm-manager fallback-mgcp",
    "no ccm-manager redundant-host anhqa0cmp.arnorth.army.mil",
    "no ccm-manager mgcp",
    "!",
    "!",
    "no ccm-manager config server 160.136.17.52",
    "no ccm-manager config",
    "!",
    "!",
    "no dial-peer voice 100 pots",
    "no dial-peer voice 101 pots",
    "no dial-peer voice 102 pots",
    "no dial-peer voice 103 pots",
    "no dial-peer voice 999012 pots",
    "no dial-peer voice 999010 pots",
    "no call-manager-fallback",
    "no mgcp profile default"
]
# special command that requires a yes confirmation after.
cmd_spc = "no voice register global"

def connect_device(device):
    try:
        # Establish the connection | send the commmand | disconnect
        # connection = ConnectHandler(**device)
        connection = ConnectHandler(
            # device_type = device["device_type"],
            device_type = 'cisco_xe',
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

def additional_commands(connection, cmd_list, cmd_spc):
    try:
# list of commands.
        output = connection.send_config_set(cmd_list)
        print(output)
# special command that requires a yes confirmation after
        output = connection.send_command_timing("conf t")
        output += connection.send_command_timing(cmd_spc)
        if 'yes/no' in output.lower():
            output += connection.send_command_timing('yes')
        output += connection.send_command_timing('end')
        print(output)

    except Exception as e:
        print(f'An error occured: {e}')

def find_delete(connection):
    """Delete all dial-peer's and commands with mgcp."""
    try:
        sh_run = connection.send_command('show run | i dial-peer')
        sh_run_output = sh_run.splitlines()
        
        for command in sh_run_output:
            output = connection.send_config_set([f'no {command}'])
            print(output)
    
    except Exception as e:
        print(f"Failed to delete dial peer's: {e}")

def save_and_exit(connection):
    try:
        #write memory
        cmd_output = connection.send_command('write memory')
        print(cmd_output)

        #disconnect
        connection.disconnect()
    
    except Exception as e:
        print(f'An error occured: {e}')

def main():
    # Loop through the routers and execute commands
    for i in routers:
        connection = connect_device(i)
        if connection:
            print('+' * 40, 'START', i["host"], 'START','+' * 43)
            find_delete(connection)
            additional_commands(connection, cmd_list, cmd_spc)
            save_and_exit(connection)
            print('+' * 40, 'COMPLETE', i["host"], 'COMPLETE','+' * 40)
            
    print('*' * 70, 'COMPLETE','*' * 70)



if __name__ == "__main__":
    main()
