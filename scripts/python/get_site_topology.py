import requests
from requests.auth import HTTPBasicAuth
from env_DNAC import *

def get_auth_token():
    """
    Building out Auth requests. Using requests.post to make a call to the auth end
    """
    url = DNAC_BURL + '/dna/system/api/v1/auth/token'
    resp = requests.post(url, auth=(DNAC_USER, DNAC_PASS), verify=False)
    token = resp.json()['Token'] #retrieve token from resp
    return token # return statement for the token

def get_site_topology():
    """
    Building out function to retrieve list of devices. Using requests.get
    """
    token = get_auth_token() #calls auth funtion
    url = DNAC_BURL + "/api/v1/topology/site-topology"
    hdr = {'x-auth-token': token, 'content-type' : 'application/json'}
    resp = requests.get(url, headers=hdr, verify=False)  # Make the Get Request
    site_list = resp.json()
    print_site_list(site_list)

def print_site_list(site_list):
    print("|{0:36} | {1:36} | {2:15} | {3:36} | {4:20} | {5:20} | {6:10} | {7:10}|".
        format( 'SITE FULL NAME','SITE ID', 'SITE NAME', 'SITE PARENT ID', 'LATITUDE', 'LONGITUDE', 'TYPE', 'DISP_NAME'))
    for site in site_list['response']['sites']:
        print("|{0:36} | {1:35} | {2:15} | {3:35} | {4:20} | {5:20} | {6:10} | {7:10}|".
              format(site["groupNameHierarchy"],
                     site['id'],
                     site['name'],
                     site['parentId'],
                     site['latitude'],
                     site['longitude'],
                     site['locationType'],
                    #  site['locationAddress'],
                    #  site['locationCountry'],
                     site['displayName']))

def main():
    get_site_topology()

if __name__ == "__main__":
    main()
