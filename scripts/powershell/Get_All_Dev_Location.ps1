$modDir = (Get-Item $PSCommandPath ).DirectoryName + '\Modules\Module_Get_Device_Location.psm1'
Import-Module $modDir

#changes table name (The green bar on top of the table.)
$device = 'All'

Get-DeviceLocation -device $device