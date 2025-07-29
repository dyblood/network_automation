<#
#Title: Get_IR_Avail.ps1
#Author: Devon Youngblood
#Date: 6 Aug 2024
#Purpose:      #Query all the devices in catalyst center that match the query parameters in $query variable.
               #Parse information from the response and format it to be user friendly
#Instruction:  #Ensure '\Modules\Module_Get_Device_List.psm1' is in the same directory with the script files and that 
                it is named exactly the same.
#Additional Info/Resources: 
               #You can get additional information by going to Catalyst Center and going to Platform / Developer tools.
               #(Platform>Developer Toolkit>Know Your Network>Get Device List)
               #Post Request: https://{base_url/
               #Get Request: https://{base_url}/dna/intent/api/v1/network-device
#>

$modDir = (Get-Item $PSCommandPath ).DirectoryName + '\Modules\Module_Get_Device_List.psm1'
Import-Module $modDir

#changes table name (The green bar on top of the table.)
$device = 'IRs'
#adds a query to the get request. see Developer toolkit on catalyst center for additional information.
$query = 'hostname=.*IR.*'

Get-DeviceList -Query $query -device $device