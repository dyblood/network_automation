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

def get_assurance_events(token, device_fam):
    """
    Building out function to retrieve syslog-config. Using requests.get
    """
    url = DNAC_BURL + f"/dna/data/api/v1/assuranceEvents?deviceFamily={device_fam}"
    hdr = {'x-auth-token': token, 'content-type' : 'application/json'}
    response = requests.get(url, headers=hdr, verify=False)  # Make the Get Request
    response.raise_for_status()
    return response.json()['response']

def main():
    token = get_auth_token()
    device_fam = "Routers"
    assurance_events = get_assurance_events(token, device_fam)

    for event in assurance_events:
        print("-"*130)
        for key, value in event.items():
            print(f'{key}: {value}')
        print("-"*130)
    # for key, value in assurance_events.items():
    #     print(f"{key}: {value}")

    # for i in device:
    #     print(i)

    # for i in tag_net_dev_list:
    #     print("-"*120)
    #     for key, value in i.items():
    #         print (f"{key}: {value}")
    #     print("-"*70)


if __name__ == "__main__":
    main()




"""
Cisco Doc URL: https://developer.cisco.com/docs/dna-center/query-assurance-events/

Request Parameters

deviceFamilyrequiredstring
Device family. Please note that multiple families across network device type and client type is not allowed. For example, choosing Routers along with Wireless Client or Unified AP is not supported.
Examples:

deviceFamily=Switches and Hubs (single deviceFamily requested)

deviceFamily=Switches and Hubs&deviceFamily=Routers (multiple deviceFamily requested)

default = "application/json"

startTimenumber
Start time from which API queries the data set related to the resource. It must be specified in UNIX epochtime in milliseconds. Value is inclusive.

If startTime is not provided, API will default to current time minus 24 hours.

default = "application/json"

endTimenumber
End time to which API queries the data set related to the resource. It must be specified in UNIX epochtime in milliseconds. Value is inclusive.

If endTime is not provided, API will default to current time.

default = "application/json"

messageTypestring
Message type for the event.

Examples:

messageType=Syslog (single messageType requested)

messageType=Trap&messageType=Syslog (multiple messageType requested)

default = "application/json"

severitynumber
Severity of the event between 0 and 6. This is applicable only for events related to network devices (other than AP) and Wired Client events.

Value	Severity
0	Emergency
1	Alert
2	Critical
3	Error
4	Warning
5	Notice
6	Info
Examples:

severity=0 (single severity requested)

severity=0&severity=1 (multiple severity requested)

default = "application/json"

siteIdstring
The UUID of the site. (Ex. flooruuid)

Examples:

?siteId=id1 (single siteId requested)

?siteId=id1&siteId=id2&siteId=id3 (multiple siteId requested)

default = "application/json"

siteHierarchyIdstring
The full hierarchy breakdown of the site tree in id form starting from Global site UUID and ending with the specific site UUID. (Ex. globalUuid/areaUuid/buildingUuid/floorUuid)

This field supports wildcard asterisk (*) character search support. E.g. *uuid*, *uuid, uuid*

Examples:

?siteHierarchyId=globalUuid/areaUuid/buildingUuid/floorUuid (single siteHierarchyId requested)

?siteHierarchyId=globalUuid/areaUuid/buildingUuid/floorUuid&siteHierarchyId=globalUuid/areaUuid2/buildingUuid2/floorUuid2 (multiple siteHierarchyId requested)

default = "application/json"

networkDeviceNamestring
Network device name. This parameter is applicable for network device related families.
This field supports wildcard (*) character-based search. Ex: *Branch* or Branch* or *Branch
Examples:

networkDeviceName=Branch-3-Gateway (single networkDeviceName requested)

networkDeviceName=Branch-3-Gateway&networkDeviceName=Branch-3-Switch (multiple networkDeviceName requested)

default = "application/json"

networkDeviceIdstring
The list of Network Device Uuids. (Ex. 6bef213c-19ca-4170-8375-b694e251101c)

Examples:

networkDeviceId=6bef213c-19ca-4170-8375-b694e251101c (single networkDeviceId requested)

networkDeviceId=6bef213c-19ca-4170-8375-b694e251101c&networkDeviceId=32219612-819e-4b5e-a96b-cf22aca13dd9&networkDeviceId=2541e9a7-b80d-4955-8aa2-79b233318ba0 (multiple networkDeviceId with & separator)

default = "application/json"

apMacstring
MAC address of the access point. This parameter is applicable for Unified AP and Wireless Client events.

This field supports wildcard (*) character-based search. Ex: *50:0F* or 50:0F* or *50:0F

Examples:

apMac=50:0F:80:0F:F7:E0 (single apMac requested)

apMac=50:0F:80:0F:F7:E0&apMac=18:80:90:AB:7E:A0 (multiple apMac requested)

default = "application/json"

clientMacstring
MAC address of the client. This parameter is applicable for Wired Client and Wireless Client events.

This field supports wildcard (*) character-based search. Ex: *66:2B* or 66:2B* or *66:2B

Examples:

clientMac=66:2B:B8:D2:01:56 (single clientMac requested)

clientMac=66:2B:B8:D2:01:56&clientMac=DC:A6:32:F5:5A:89 (multiple clientMac requested)

default = "application/json"

attributestring
The list of attributes that needs to be included in the response. If this parameter is not provided, then basic attributes (id, name, timestamp, details, messageType, siteHierarchyId, siteHierarchy, deviceFamily, networkDeviceId, networkDeviceName, managementIpAddress) would be part of the response.
Examples:

attribute=name (single attribute requested)

attribute=name&attribute=networkDeviceName (multiple attribute requested)

default = "application/json"

viewstring
The list of events views. Please refer to EventViews for the supported list
Examples:

view=network (single view requested)

view=network&view=ap (multiple view requested)

default = "application/json"

offsetnumber
Specifies the starting point within all records returned by the API. It's one based offset. The starting value is 1.

default = "application/json"

limitnumber
Maximum number of records to return

default = "application/json"

sortBystring
A field within the response to sort by.

default = "application/json"

orderstring
The sort order of the field ascending or descending.

default = "application/json"
"""