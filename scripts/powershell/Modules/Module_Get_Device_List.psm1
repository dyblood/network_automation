<#
#Title: Module_Get_Device_List.psm1
#Author: Devon Youngblood
#Date: 6 Aug 2024
#Purpose:      #Contains functions for scripts to:
               #Query all the devices in catalyst center that match the query parameters in $query variable.
               #Parse information from the response and format it to be user friendly
               #Color codes online/offline devices
               #can also be used in get device ID for specific post/get requests for that device.
#Function List:
               #Get-AuthCatalyst: -post request to recieve auth token based on user environment credentials
                                  -to set up user environment credentials please see '1-auth_env_setup.ps1'.
               #Get-DeviceList:   -Get Request: https://{base_url}/dna/intent/api/v1/network-device
               #Format-ColorTable:-Formats response from Get-DeviceList function.
#Instruction:  #Ensure '\Modules\Module_Get_Device_List.psm1' is in the same directory with the script files and that 
                it is named exactly the same.
#Additional Info/Resources: 
               #You can get additional information by going to Catalyst Center and going to Platform / Developer tools.
               #(Platform>Developer Toolkit>Know Your Network>Get Device List)
               #Post Request: https://{base_url/
               #Get Request: https://{base_url}/dna/intent/api/v1/network-device
#>

#-------------------------- AUTHENTICATION --------------------------------------------------------------
function Get-AuthCatalyst {
        #retrive user environment catalyst credential.
        $cred = [System.Environment]::GetEnvironmentVariables([System.EnvironmentVariableTarget]::User).CatCred
        #Url for post request.
        $authUrl = "https://anhqwjmh99nmdna.nasw.ds.army.mil/dna/system/api/v1/auth/token"
        $headers = @{"authorization"="Basic $cred"}
        #Post Request     
        $response = Invoke-RestMethod -Uri $authUrl –Method POST -ContentType 'application/json' -Header $headers
        $token = $response.Token
        $token
}
    #----------------- Get List of all Faks ---------------------------------------------------
function Get-DeviceList {
        param (
        [Parameter(Mandatory = $true)]
        [string]$Query,
        [string]$device
        )
            $token = Get-AuthCatalyst
            $url = "https://anhqwjmh99nmdna.nasw.ds.army.mil/dna/intent/api/v1/network-device?$Query"
            $headers = @{'x-auth-token'=$token}
            $response = Invoke-RestMethod -Uri $url -Method GET -ContentType 'application/json' -Header $headers
            $resp = $response.response
            
            #creating a new pscustomobj
            $q = @()
            #Looping through the response and pulling values that we want for each device.
            #Adds them to a pscustomobj named $q. (For python people pscustomobject = dictionary).
            Foreach ($i in $resp){
                $q += [pscustomobject]@{'hostname' = $i.hostname; 'reachability_status' = $i.reachabilityStatus; 'mac' = $i.macAddress; 'ipAdd' = $i.dnsResolvedManagementAddress; 'S/N' = $i.serialNumber}
            }
            # Call the function to display the table with colors
            Format-ColorTable -Data $q -DeviceName $device
}
    # --------------- Function to format and colorize the output--------------------------------
function Format-ColorTable {
        param (
            #parameters to input while calling the function
            [Parameter(Mandatory = $true)]
            [array]$Data,
            [string]$DeviceName
        )
        #formatting for table title.
        Write-Host ("{0,-50} {1,-15} {2,-45}" -f '',$DeviceName,'') -BackgroundColor DarkGreen
        #formatting for column headers.
        Write-Host ("{0,-40} {1,-15} {2,-20} {3,-20} {4,-13}" -f 'hostname', 'Reachability', 'MAC', 'Management IP', 'S/N') -BackgroundColor DarkGray
        foreach ($item in $Data) {
            $color = switch ($item.reachability_status) {
                'reachable' { 'Green' }
                'unreachable' { 'Red' }
                default { 'Yellow' }
            }

            # Output each item with color
            Write-Host ("{0,-40} {1,-15} {2,-20} {3,-20} {4,-10}" -f $item.hostname, $item.reachability_status, $item.mac, $item.ipAdd, $item.'S/N') -ForegroundColor $color
        }
}