import requests
import os
from requests.auth import HTTPBasicAuth
import pandas as pd
from env_pyats import *

# Disable SSL warning
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

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

def save_filtered_devices_to_excel(device_json, filename):
    """Filter and save specific fields to an Excel file."""
    devices = device_json.get('response', [])
    filtered_devices = []

    for device in devices:
        if device.get('family') in ['Routers', 'Switches and Hubs']:
            hostname = f"{device.get('hostname', 'N/A')}".replace(".nasw.ds.army.mil", "").replace(".NASW.DS.ARMY.MIL", "")
            # hostname = f"{device.get('hostname', 'N/A')}"
            ip = f"{device.get('managementIpAddress', 'N/A')}:22"
            username = DNAC_USER
            password = DNAC_PASS
            protocol = 'ssh'
            os_type = f"{device.get('softwareType', 'N/A')}".replace("-", "").lower()
            
            

            filtered_devices.append({
                'hostname': hostname,
                'ip': ip,
                'username': username,
                'password': password,
                'protocol': protocol,
                'os': os_type
            })

    df = pd.DataFrame(filtered_devices)
    df.to_excel(filename, index=False)
    print(f"Excel file created: {filename}")

def main():
    wsl_na_path = os.getenv('WSL_NA_PATH')
    domain_n = os.getenv('DOMAIN_N')

    filename = f"{wsl_na_path}/pyats/pyatstb/pyats_tb.xlsx"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    devices = get_device_list()
    save_filtered_devices_to_excel(devices, filename)

if __name__ == "__main__":
    main()
