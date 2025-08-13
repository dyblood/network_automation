import requests
import os
from requests.auth import HTTPBasicAuth
import csv
import datetime
from dotenv import load_dotenv

load_dotenv()

DNAC_BURL = os.getenv('DNAC_BURL')
DNAC_USER = os.getenv('DNAC_USER')
DNAC_PASS = os.getenv('DNAC_PASS')
WIN_DESK_PATH = os.getenv('WIN_DESK_PATH')

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
    save_to_cvs(device_list)

def save_to_cvs(device_list, filename=f'{os.getenv('WIN_DESK_PATH')}dev_configs/cvs/get_device_list.csv'):
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
    device_list_cvs = f'{os.getenv('WIN_DESK_PATH')}dev_configs/cvs/get_device_list.csv'
    # with open('get_device_list_cvs.csv', mode='r') as csvfile:
    with open(device_list_cvs, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        dev_list_dict = [row for row in reader]
    
    for i in dev_list_dict:
        if i['family'] != 'Unified AP' and i['family'] != 'Wireless Controller' and i['reachabilityStatus']:
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


def main():
    get_device_list()
    cvs_to_dict()

if __name__ == "__main__":
    main()