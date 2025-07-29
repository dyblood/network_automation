import requests
from env_DNAC import DNAC_BURL, DNAC_PASS, DNAC_USER
#from requests.auth import HTTPBasicAuth

auth_url = "/dna/system/api/v1/auth/token"

# Authentication
#response = requests.post(DNAC_BURL + auth_url, auth=HTTPBasicAuth(DNAC_USER, DNAC_PASS), verify=False)
response = requests.post(DNAC_BURL + auth_url, auth=(DNAC_USER, DNAC_PASS), verify=False)
token = response.json()['Token']
print(response.text.encode('utf8'))


# Get network-device

headers = {'X-Auth-Token': token, 'Content-Type': 'application/json'}
url = '/dna/intent/api/v1/network-device?hostname=FAK.*'

response = requests.get(DNAC_BURL + url, headers = headers, verify=False)

#print(response.json())

for item in response.json()['response']:
    print("*" * 100)
    for i in item:
        print(i, ":", item[i])
    print("*" * 100)

# for item in response.json()['response']:
#     print(item['id'], item['hostname'], item['managementIpAddress'])