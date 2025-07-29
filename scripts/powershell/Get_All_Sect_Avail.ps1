<#
#Title:Get_DCO_Avail.ps1 
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
#------------------ FAK-----------------
$query = 'hostname=FAK.*'
Get-DeviceList -Query $query -device $device
#------------------ERT / ERV------------
$device = 'ERTs / ERVs'
$query = 'hostname=.*ERT.*&hostname=.*ERV.*'
Get-DeviceList -Query $query -device $device
#------------------RRK------------------
$device = 'RRK'
$query = 'hostname=.*RRK.*'
Get-DeviceList -Query $query -device $device
#------------------IR-------------------
$device = 'IRs'
$query = 'hostname=.*IR.*'
Get-DeviceList -Query $query -device $device
#------------------WLCs-----------------
$device = 'WLCs'
$query = 'hostname=anhqwjmh99wl101.*&hostname=ARNORTHWLC.*&hostname=9800L.**'
Get-DeviceList -Query $query -device $device
#------------------APs------------------
$device = 'APs'
$query = 'hostname=B-.*&hostname=Voyager-8.*&hostname=SENT-AP.*&hostname=REG-01-AP.*&hostname=REG-06-AP.*&hostname=REG-09-AP.*'
Get-DeviceList -Query $query -device $device
#------------------TACEDGE--------------
$device = 'TACEDGE'
$query = 'hostname=.*TAC.*'
Get-DeviceList -Query $query -device $device