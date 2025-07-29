<#
#Title: Authentication Environment Setup
#Author: Devon Youngblood
#Date: 2 Aug 2024
#Purpose:       #The purpose of this script is to set up your your environment authentication credentials
                 as your user enviornment variable. This way you will not have to put your acutal username
                 and password into the scripts.
#Instructions:  #Replace 'username:password' with your username and password and run the script.
                #After this is complete you will be able to run all of the scripts.
#>

#Encodes 'username:password' with base64.
$envCred = [Convert]::ToBase64String([char[]]'username:password')

#sets environmental variable.
[System.Environment]::SetEnvironmentVariable('CatCred', $envCred, 'User')

#verify's that the environmental variable was saved.
[System.Environment]::GetEnvironmentVariables([System.EnvironmentVariableTarget]::User)