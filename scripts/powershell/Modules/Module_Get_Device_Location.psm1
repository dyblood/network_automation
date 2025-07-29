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
#-----------------------------------------------------

function Get-DeviceLocation {
        param(
        [Parameter(Mandatory = $true)]
        [string]$device
    )

            $token = Get-AuthCatalyst
            $url = "https://anhqwjmh99nmdna.nasw.ds.army.mil/dna/intent/api/v1/device-health?limit=500"
            $headers = @{'x-auth-token'=$token}
            $response = Invoke-RestMethod -Uri $url -Method GET -ContentType 'application/json' -Header $headers
            $resp = $response.response
          
            $q = @()
            #Looping through the response and pulling values that we want for each device.
            #Adds them to a pscustomobj named $q. (For python people pscustomobject = dictionary).
            Foreach ($i in $resp){
                $q += [pscustomobject]@{'hostname' = $i.name; 'reachability_status' = $i.reachabilityHealth; 'mac' = $i.macAddress; 'ipAdd' = $i.ipAddress; 'location' = $i.location}
    }
            # Call the function to display the table with colors
            Format-ColorTable -Data $q -DeviceName $device
}
    # --------------- Function to format and colorize the output--------------------------------
function Format-ColorTable {
    param (
        [Parameter(Mandatory = $true)]
        [array]$Data,
        [string]$DeviceName
    )
    
    # Sort the data by 'hostname' property
    $SortedData = $Data | Sort-Object hostname
    
    # Formatting for table title
    Write-Host ("{0,-50} {1,-15} {2,-45}" -f '', $DeviceName, '') -BackgroundColor DarkGreen
    
    # Formatting for column headers
    Write-Host ("{0,-40} {1,-15} {2,-20} {3,-20} {4,-13}" -f 'hostname', 'Reachability', 'MAC', 'Management IP', 'Location') -BackgroundColor DarkGray
    
    foreach ($item in $SortedData) {
        $color = switch ($item.reachability_status) {
            'reachable' { 'Green' }
            'up' { 'Green' }
            'down' { 'Red' }
            'unreachable' { 'Red' }
            default { 'Yellow' }
        }

        # Output each item with color
        Write-Host ("{0,-40} {1,-15} {2,-20} {3,-20} {4,-10}" -f $item.hostname, $item.reachability_status, $item.mac, $item.ipAdd, $item.location) -ForegroundColor $color
    }
}