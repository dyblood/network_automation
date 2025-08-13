import requests
from requests.auth import HTTPBasicAuth
from env_DNAC import *

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

def get_auth_token():
    """
    Building out Auth requests. Using requests.post to make a call to the auth end
    """
    url = DNAC_BURL + '/dna/system/api/v1/auth/token'
    resp = requests.post(url, auth=(DNAC_USER, DNAC_PASS), verify=False)
    token = resp.json()['Token'] #retrieve token from resp
    return token # return statement for the token

def get_device_list():
    """
    Building out function to retrieve list of devices. Using requests.get
    """
    token = get_auth_token() #calls auth funtion
    url = DNAC_BURL + "/api/v1/network-device"
    hdr = {'x-auth-token': token, 'content-type' : 'application/json'}
    resp = requests.get(url, headers=hdr, verify=False)  # Make the Get Request
    device_list = resp.json()
    print_device_list(device_list)
# Define color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_device_list(device_json):
    # Print the header row
    print("| {0:40} | {1:15} | {2:12} | {3:18} | {4:12} | {5:14} | {6:25} | {7:18} | {8:35} |".
          format("HOSTNAME", "MGMT IP", "SERIAL", "PLATFORM ID", "VERSION", "REACHABILITY", "ROLE", "MAC", "ID"))

    # Iterate over each device in the JSON response
    for device in device_json.get('response', []):
        # Determine the color based on reachability status
        if device.get('reachabilityStatus') == 'Reachable':
            color = GREEN
        elif device.get('reachabilityStatus') == 'Unreachable':
            color = RED
        else:
            color = YELLOW

        # Define a function to handle None values
        def safe_format(value, default='N/A'):
            return value if value is not None else defaultping 

        try:
            print("|{0:50} | {1:15} | {2:12} | {3:18} | {4:12} | {5:23} | {6:25} | {7:18} | {8:35} |".
                  format(f"{color}{safe_format(device.get('hostname'))}{RESET}",
                         safe_format(device.get('role')),
                         safe_format(device.get('serialNumber')),
                         safe_format(device.get('platformId')),
                         safe_format(device.get('softwareVersion')),
                         f"{color}{safe_format(device.get('reachabilityStatus'))}{RESET}",
                         safe_format(device.get('managementIpAddress')),
                         safe_format(device.get('macAddress')),
                         safe_format(device.get("id")))
            )
        except Exception as e:
            print(f"Error formatting device data: {e}")
            print(device)  # Print the device data for debugging


            
if __name__ == "__main__":
    get_device_list()