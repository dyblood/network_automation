import requests
from requests.auth import HTTPBasicAuth
import time
from datetime import datetime, timedelta
import json
from statistics import mean
import csv
from env_DNAC import *


def get_auth_token():
    """
    Building out Auth requests. Using requests.post to make a call to the auth end
    """
    url = DNAC_BURL + '/dna/system/api/v1/auth/token'
    resp = requests.post(url, auth=(DNAC_USER, DNAC_PASS), verify=False)
    token = resp.json()['Token'] #retrieve token from resp
    return token # return statement for the token

# Disable SSL warnings if necessary
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Get the list of access points
def get_access_points(token):
    url = f"{DNAC_BURL}/dna/intent/api/v1/network-device?family=Unified AP"
    headers = {
        'Content-Type': 'application/json',
        'x-auth-token': token
    }
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    return response.json()["response"]

# Get users per access point over the last week
def get_users_per_ap(token, hostname):
    #UNIX epochtime in milliseconds

    # Current time in milliseconds
    current_time_ago = datetime.now() - timedelta(minutes=30)
    current_time_ms = int(current_time_ago.timestamp() * 1000)
    # current_time_ms = int(time.time() * 1000)

    # Time 1 day ago in milisecond
    seven_days_ago = datetime.now() - timedelta(days=1)
    seven_days_ago_ms = int(seven_days_ago.timestamp() * 1000)
    
    url = f"{DNAC_BURL}/dna/data/api/v1/clients?startTime={seven_days_ago_ms}&endTime={current_time_ms}&type=Wireless&connectedNetworkDeviceName={hostname}"
    headers = {
        'Content-Type': 'application/json',
        'x-auth-token': token
    }
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    return response.json()["response"]

# Main function
def main():
    token = get_auth_token()
    
    #retrieves list of access point through /dna/intent/api/v1/network-device api endpoint.
    access_points = get_access_points(token)
    
    #retrieves clients connected to access points through /dna/data/api/v1/clients api endpoint.

    access_points_clients = {}
    for i in access_points:
        ap_client_dict = get_users_per_ap(token, i['hostname'])
        access_points_clients[i['hostname']] = ap_client_dict

    #creates a dictionary with all access points and sets all their value to 0.
    ap_clients = {}
    for ap in access_points:
        ap_clients[ap['hostname']] = 0

    #iterates through all the clients connected and adds +1 to the AP it is connected to.
    for i in access_points_clients:
        for j in access_points_clients[i]:
            cp_name = j['connectedNetworkDevice']['connectedNetworkDeviceName']
            if cp_name in ap_clients:
                ap_clients[cp_name] += 1
            else:
                ap_clients[cp_name] = 1
    total = 0
    for key, value in ap_clients.items():
        total += value
        print(f'{key}: {value}')

    print (total)


if __name__ == "__main__":
    main()
