import requests
import os
from requests.auth import HTTPBasicAuth
import pandas as pd
from env_DNAC import *

# Disable SSL warning
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'


def get_auth_token():
    """Get authentication token from Cisco DNA Center."""
    url = f"{DNAC_BURL}/dna/system/api/v1/auth/token"
    response = requests.post(url, auth=HTTPBasicAuth(DNAC_USER, DNAC_PASS), verify=False)
    response.raise_for_status()
    return response.json()['Token']


def get_api_response(endpoint):
    """General function to make GET requests to DNAC APIs."""
    token = get_auth_token()
    url = f"{DNAC_BURL}{endpoint}"
    headers = {'x-auth-token': token, 'content-type': 'application/json'}
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    return response.json()


def get_device_list():
    """Fetch the list of network devices."""
    return get_api_response("/api/v1/network-device")


def safe_format(value, default='N/A'):
    """Helper to safely format values."""
    return value if value is not None else default


def print_device_list(device_json):
    """Print formatted list of devices with color-coded reachability."""
    print("| {0:40} | {1:15} | {2:12} | {3:18} | {4:12} | {5:14} | {6:25} | {7:18} | {8:35} |"
          .format("HOSTNAME", "MGMT IP", "SERIAL", "PLATFORM ID", "VERSION", "REACHABILITY", "ROLE", "MAC", "ID"))

    for device in device_json.get('response', []):
        status = device.get('reachabilityStatus', 'Unknown')
        color = GREEN if status == 'Reachable' else RED if status == 'Unreachable' else YELLOW

        try:
            print("|{0:50} | {1:15} | {2:12} | {3:18} | {4:12} | {5:23} | {6:25} | {7:18} | {8:35} |"
                  .format(f"{color}{safe_format(device.get('hostname'))}{RESET}",
                          safe_format(device.get('role')),
                          safe_format(device.get('serialNumber')),
                          safe_format(device.get('platformId')),
                          safe_format(device.get('softwareVersion')),
                          f"{color}{status}{RESET}",
                          safe_format(device.get('managementIpAddress')),
                          safe_format(device.get('macAddress')),
                          safe_format(device.get('id'))))
        except Exception as e:
            print(f"Error formatting device data: {e}")
            print(device)


def save_devices_to_excel(device_json, filename):
    """Save device list to an Excel file."""
    devices = []
    for device in device_json.get('response', []):
        devices.append({
            'Hostname': safe_format(device.get('hostname')),
            'Management IP': safe_format(device.get('managementIpAddress')),
            'Serial Number': safe_format(device.get('serialNumber')),
            'Platform ID': safe_format(device.get('platformId')),
            'Software Version': safe_format(device.get('softwareVersion')),
            'Reachability Status': safe_format(device.get('reachabilityStatus')),
            'Role': safe_format(device.get('role')),
            'MAC Address': safe_format(device.get('macAddress')),
            'ID': safe_format(device.get('id'))
        })

    df = pd.DataFrame(devices)
    df.to_excel(filename, index=False)
    print(f"Device list saved to {filename}")


def main():
    # filename = "C:\\Users\\devon.d.youngblood\\OneDrive - US Army\\Desktop\\youngblood_netops\\get_device_list\\get_device_list.xlsx"
    filename = "/mnt/c/Users/devon.d.youngblood/OneDrive - US Army/Desktop/youngblood_netops/get_device_list/get_device_list.xlsx"

    os.makedirs(os.path.dirname(filename), exist_ok=True)

    devices = get_device_list()
    print_device_list(devices)
    save_devices_to_excel(devices, filename)

if __name__ == "__main__":
    main()

