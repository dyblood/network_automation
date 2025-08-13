import os
import requests
from requests.auth import HTTPBasicAuth
import csv
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException
from ciscoconfparse import CiscoConfParse
from env_DNAC import *
from dotenv import load_dotenv
load_dotenv()

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

DNAC_BURL = os.getenv('DNAC_BURL')
DNAC_USER = os.getenv('DNAC_USER')
DNAC_PASS = os.getenv('DNAC_PASS')
WIN_DESK_PATH = os.getenv('WIN_DESK_PATH')
CONFIG_DIR = f"{WIN_DESK_PATH}youngblood_netops/ERT_router_changes/"
TRACKER_CSV = f"{CONFIG_DIR}ert_rtr_change_tracker.csv"
DEVICE_LIST_CSV = f"{CONFIG_DIR}get_device_list.csv"

def get_auth_token():
    url = f"{DNAC_BURL}/dna/system/api/v1/auth/token"
    response = requests.post(url, auth=(DNAC_USER, DNAC_PASS), verify=False)
    response.raise_for_status()
    return response.json()['Token']

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def get_device_list(token):
    """
    Building out function to retrieve list of devices. Using requests.get
    """
   
    url = DNAC_BURL + "/api/v1/network-device"
    hdr = {'x-auth-token': token, 'content-type' : 'application/json'}
    resp = requests.get(url, headers=hdr, verify=False)  # Make the Get Request
    device_list = resp.json()
    save_to_cvs(device_list)

def save_to_cvs(device_list, filename=f'{win_desk_path}youngblood_netops/ERT_router_changes/get_device_list.csv'):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            "hostname", 
            "managementIpAddress", 
            "macAddress", 
            "serialNumber",
            "reachabilityStatus",
            "upTime",
            "type",
            "softwareType",
            "softwareVersion",
            "platformId",
            "role",
            "family",
            "instanceUuid",
            "instanceTenantId",
            "id"
        ])

        for i in device_list['response']:
            writer.writerow([
                i["hostname"],
                i["managementIpAddress"],
                i["macAddress"],
                i["serialNumber"],
                i["reachabilityStatus"],
                i["upTime"],
                i["type"],
                i["softwareType"],
                i["softwareVersion"],
                i["platformId"],
                i["role"],
                i["family"],
                i["instanceUuid"],
                i["instanceTenantId"],
                i["id"]
            ])

def cvs_to_dict():
    dev_list = []
    device_list_cvs = f'{DEVICE_LIST_CSV}'
    # with open('get_device_list_cvs.csv', mode='r') as csvfile:
    with open(device_list_cvs, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        dev_list_dict = [row for row in reader]
    
    for i in dev_list_dict:
        if i['family'] == 'Routers' and 'ERT' in i['hostname']:
            # Update device_type based on softwareType
            if i['softwareType'] == 'IOS-XE':
                device_type = 'cisco_xe'
            elif i['softwareType'] == 'IOS':
                device_type = 'cisco_ios'
            else:
                device_type = 'cisco_ios'  # Keep original if it doesn't match

            dev_dict = {
                'hostname': i['hostname'],
                'host': i['managementIpAddress'],
                'device_type': device_type,
                'family': i['family'],
                'reachability': i["reachabilityStatus"]
            }
            dev_list.append(dev_dict)  
    return dev_list


def connect_device(device):
    try:
        connection = ConnectHandler(
            device_type=device["device_type"],
            host=device["host"],
            username=DNAC_USER,
            password=DNAC_PASS
        )
        return connection
    except (NetmikoTimeoutException, NetmikoAuthenticationException) as e:
        print(f"[ERROR] Connection to {device['host']} failed: {e}")
        return None


def get_and_parse_config(connection, hostname):
    output = connection.send_command("show running-config")
    config_path = os.path.join(CONFIG_DIR, f"{hostname}.conf")
    with open(config_path, "w") as f:
        f.write(output)
    return CiscoConfParse(config_path, syntax="ios")


def find_and_remove_lines(connection, parse, parent=None, child=None, exact_line=None):
    """
    If parent and child are provided, removes matching child lines under parent.
    If exact_line is provided, removes that line directly.
    """
    try:
        if parent and child:
            parent_objs = parse.find_objects_w_child(parentspec=parent, childspec=child)
            for p_obj in parent_objs:
                for c_obj in p_obj.children:
                    if child in c_obj.text:
                        cmd_set = [p_obj.text.strip(), f'no {c_obj.text.strip()}']
                        print(f"Removing: {cmd_set}")
                        print(connection.send_config_set(cmd_set))
        elif exact_line:
            matching_lines = parse.find_lines(exact_line)
            for line in matching_lines:
                cmd = f'no {line.strip()}'
                print(f"Removing exact line: {cmd}")
                print(connection.send_config_set([cmd]))
    except Exception as e:
        print(f"[ERROR] Failed to remove lines: {e}")


def additional_commands(connection, commands):
    try:
        print(connection.send_config_set(commands))
    except Exception as e:
        print(f"[ERROR] Failed to run '{commands}': {e}")


def save_and_exit(connection):
    try:
        print(connection.send_command("write memory"))
        connection.disconnect()
    except Exception as e:
        print(f"[ERROR] Save or disconnect failed: {e}")


def create_csv_tracker(device_list, filename):
    if not os.path.isfile(filename):
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(['hostname', 'ip_address', 'configured'])
            for dev in device_list:
                writer.writerow([dev['hostname'], dev['host'], 'no'])
        print(f"[INFO] Tracker file created: {filename}")


def update_configured_status(hostname, filename):
    if not os.path.isfile(filename):
        print(f"[ERROR] Tracker file {filename} does not exist.")
        return

    rows = []
    with open(filename, "r") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows.append(header)
        for row in reader:
            if row[0] == hostname:
                row[2] = 'yes'
            rows.append(row)

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print(f"[INFO] Updated status for {hostname}.")


def get_not_configured_devices(filename):
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        return [row["hostname"] for row in reader if row["configured"].lower() != 'yes']


def process_device(device, patterns):
    connection = connect_device(device)
    if not connection:
        return False

    parse = get_and_parse_config(connection, device["hostname"])

    for pattern in patterns:
        find_and_remove_lines(
            connection,
            parse,
            parent=pattern.get("parent"),
            child=pattern.get("child"),
            exact_line=pattern.get("exact")
        )

    if "additional" in patterns[-1]:
        additional_commands(connection, patterns[-1]["additional"])

    save_and_exit(connection)
    return True


def main():
    ensure_dir(CONFIG_DIR)
    token = get_auth_token() 
    get_device_list(token)
    device_list = cvs_to_dict()

    create_csv_tracker(device_list, TRACKER_CSV)
    unconfigured = get_not_configured_devices(TRACKER_CSV)
    patterns = [
        # {"parent": "^ip access-list", "child": "<thing to search>"},
        # {"parent": "^interface", "child": "NETFLOW"},
        {"exact": "VPN-NEXT-HOP-"},
        {"exact": "interface Tunnel"},
        {"additional": ["ip route 0.0.0.0 0.0.0.0 GigabitEthernet0/0/0 dhcp 250", 
                        "ip route 0.0.0.0 0.0.0.0 GigabitEthernet0/0/1 dhcp",
                        "no key chain OSPF_KEY_CHAIN",

                        "interface GigabitEthernet0/0/0",
                        "description Comm over RHN",
                        "ip address dhcp",
                        "no ip redirects",
                        "no ip unreachables",
                        "no ip proxy-arp",
                        "ip mtu 1100",
                        "ip access-group WAN-ACL-IN in",
                        "ip tcp adjust-mss 1150",
                        "negotiation auto",
                        "no ipv6 pim",
                        "no ipv6 redirects",
                        "no ipv6 unreachables",
                        "no mop enabled",
                        "no mop sysid",
                        "crypto map IKEV2_IPSEC_VPN",
                        "service-policy output QOS_POLICY_SWITCHPORT",
                        "exit",
                        "event manager applet reset_ikev2_sa",
                        "event syslog pattern \"%LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/0/1, changed state to down\"",
                        "action 1 cli command \"enable\"",
                        "action 2 cli command \"clear crypto ikev2 sa\"",
                        "exit",
                        "no crypto ikev2 profile IKEV2_VTI_PROFILE",
                        "no crypto ikev2 keyring IKEV2_VTI_KEYRING",
                        "no crypto ipsec profile SHA256_AES256_VPN_VTI"
                        ]}
    ]

    for device in device_list:
        hostname = device["hostname"]
        if device["reachability"] == "Reachable" and hostname in unconfigured: 
        # if hostname == 'ERT12-RTR.nasw.ds.army.mil' and hostname in unconfigured: 
            print(f"\n{'-'*20} Processing {hostname} {'-'*20}")
            if process_device(device, patterns):
                update_configured_status(hostname, TRACKER_CSV)
            print(f"{'-'*20} Done with {hostname} {'-'*20}")

    print("Devices currently not configured:")
    for i in unconfigured:
        print(i)


if __name__ == "__main__":
    main()
