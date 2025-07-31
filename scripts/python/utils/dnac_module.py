import requests
import os
from requests.auth import HTTPBasicAuth
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Disable SSL warning
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)



def get_auth_token(DNAC_BURL = os.getenv('DNAC_BURL'), DNAC_USER = os.getenv('DNAC_USER'), DNAC_PASS = os.getenv('DNAC_PASS')):
    """Get authentication token from Cisco DNA Center."""
    url = f"{DNAC_BURL}/dna/system/api/v1/auth/token"
    response = requests.post(url, auth=HTTPBasicAuth(DNAC_USER, DNAC_PASS), verify=False)
    response.raise_for_status()
    return response.json()['Token']


def get_api_response(endpoint, DNAC_BURL = os.getenv('DNAC_BURL')):
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