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

def get_email_event_sub(token):
    """
    Building out function to retrieve syslog-config. Using requests.get
    """
    url = DNAC_BURL + "/dna/intent/api/v1/event/subscription/email"
    hdr = {'x-auth-token': token, 'content-type' : 'application/json'}
    response = requests.get(url, headers=hdr, verify=False)  # Make the Get Request
    response.raise_for_status()
    return response.json()

def main():
    token = get_auth_token()
    email_event_sub = get_email_event_sub(token)
    
    # for i in get_email_event_sub:
    #     print(i)

    for i in email_event_sub:
        print("-"*120)
        for key, value in i.items():
            print (f"{key}: {value}")
        print("-"*70)


if __name__ == "__main__":
    main()




"""
Request Parameters

parentInstanceId | string
Parent Audit Log record's instanceID.
default = "application/json"

instanceId | string
InstanceID of the Audit Log.
default = "application/json"

name | string
Audit Log notification event name.
default = "application/json"

eventId | string
Audit Log notification's event ID.
default = "application/json"

category | string
Audit Log notification's event category. Supported values: INFO, WARN, ERROR, ALERT, TASK_PROGRESS, TASK_FAILURE, TASK_COMPLETE, COMMAND, QUERY, CONVERSATION
default = "application/json"

severity | string
Audit Log notification's event severity. Supported values: 1, 2, 3, 4, 5.
default = "application/json"

domain | string
Audit Log notification's event domain.
default = "application/json"

subDomain string
Audit Log notification's event sub-domain.
default = "application/json"

sourcestring
Audit Log notification's event source.
default = "application/json"

userIdstring
Audit Log notification's event userId.
default = "application/json"

context | string
Audit Log notification's event correlationId.
default = "application/json"

eventHierarchy | string
Audit Log notification's event eventHierarchy. Example: "US.CA.San Jose" OR "US.CA" OR "CA.San Jose" - Delimiter for hierarchy separation is ".".
default = "application/json"

siteId | string
Audit Log notification's siteId.
default = "application/json"

deviceId | string
Audit Log notification's deviceId.
default = "application/json"

isSystemEvents | boolean
Parameter to filter system generated audit-logs.
default = "application/json"

description | string
String full/partial search - (Provided input string is case insensitively matched for records).
default = "application/json"

offset | number
Position of a particular Audit Log record in the data.
default = "application/json"

limit | number
Number of Audit Log records to be returned per page.
default = "application/json"

startTime | number
Start Time in milliseconds since Epoch Eg. 1597950637211 (when provided endTime is mandatory)
default = "application/json"

endTime | number
End Time in milliseconds since Epoch Eg. 1597961437211 (when provided startTime is mandatory)
default = "application/json"

sortBy | string
Sort the Audit Logs by certain fields. Supported values are event notification header attributes.
default = "application/json"

order | string
Order of the sorted Audit Log records. Default value is desc by timestamp. Supported values: asc, desc.
default = "application/json"
"""