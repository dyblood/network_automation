from netmiko import ConnectHandler
from getpass import getpass
from env_DNAC import *

password = DNAC_PASS
user = DNAC_USER


#----------------------------------------------------FAK_RTR------------------------------------------------#
FAK_01_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.19.201",
    "username": user,
    "password": password,
}

FAK_02_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.19.209",
    "username": user,
    "password": password,
}

FAK_03_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.19.225",
    "username": user,
    "password": password,
}

FAK_04_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.19.249",
    "username": user,
    "password": password,
}

FAK_05_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.20.1",
    "username": user,
    "password": password,
}

FAK_06_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.20.25",
    "username": user,
    "password": password,
}

FAK_07_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.20.41",
    "username": user,
    "password": password,
}

FAK_08_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.20.57",
    "username": user,
    "password": password,
}
FAK_09_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.20.72",
    "username": user,
    "password": password,
}

FAK_10_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.20.89",
    "username": user,
    "password": password,
}

FAK_11_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.20.105",
    "username": user,
    "password": password,
}

FAK_12_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.20.120",
    "username": user,
    "password": password,
}

FAK_13_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.20.136",
    "username": user,
    "password": password,
}

FAK_14_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.20.152",
    "username": user,
    "password": password,
}

FAK_15_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.20.161",
    "username": user,
    "password": password,
}

FAK_17_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.20.200",
    "username": user,
    "password": password,
}

FAK_18_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.20.216",
    "username": user,
    "password": password,
}

FAK_19_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.20.225",
    "username": user,
    "password": password,
}

FAK_20_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.20.248",
    "username": user,
    "password": password,
}
FAK_21_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.21.0",
    "username": user,
    "password": password,
}

FAK_22_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.23.24",
    "username": user,
    "password": password,
}

FAK_23_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.23.9",
    "username": user,
    "password": password,
}

FAK_24_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.23.47",
    "username": user,
    "password": password,
}
FAK_25_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.21.72",
    "username": user,
    "password": password,
}
FAK_26_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.30.65",
    "username": user,
    "password": password,
}

FAK_27_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.30.145",
    "username": user,
    "password": password,
}

FAK_28_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.30.17",
    "username": user,
    "password": password,
}

#-----------------------------------------------FAK_SW---------------------------------------------------#

FAK_01_SW = {
    "device_type": "cisco_xe",
    "host": "172.20.19.194",
    "username": user,
    "password": password,
}

FAK_02_SW = {
    "device_type": "cisco_xe",
    "host": "172.20.19.210",
    "username": user,
    "password": password,
}

FAK_03_SW = {
    "device_type": "cisco_xe",
    "host": "172.20.19.226",
    "username": user,
    "password": password,
}

FAK_04_SW = {
    "device_type": "cisco_xe",
    "host": "172.20.19.242",
    "username": user,
    "password": password,
}

FAK_05_SW = {
    "device_type": "cisco_xe",
    "host": "172.20.20.2",
    "username": user,
    "password": password,
}

FAK_06_SW = {
    "device_type": "cisco_xe",
    "host": "172.20.20.18",
    "username": user,
    "password": password,
}

FAK_07_SW = {
    "device_type": "cisco_xe",
    "host": "172.20.20.34",
    "username": user,
    "password": password,
}

FAK_08_SW = {
    "device_type": "cisco_xe",
    "host": "172.20.20.50",
    "username": user,
    "password": password,
}
FAK_09_SW = {
    "device_type": "cisco_xe",
    "host": "172.20.20.66",
    "username": user,
    "password": password,
}

FAK_10_SW = {
    "device_type": "cisco_xe",
    "host": "172.20.20.82",
    "username": user,
    "password": password,
}

FAK_11_SW = {
    "device_type": "cisco_xe",
    "host": "172.20.20.98",
    "username": user,
    "password": password,
}

FAK_12_SW = {
    "device_type": "cisco_xe",
    "host": "172.20.20.114",
    "username": user,
    "password": password,
}
FAK_13_SW = {
    "device_type": "cisco_xe",
    "host": "172.20.20.130",
    "username": user,
    "password": password,
}

FAK_14_SW = {
    "device_type": "cisco_xe",
    "host": "172.20.20.146",
    "username": user,
    "password": password,
}

FAK_15_SW = {
    "device_type": "cisco_xe",
    "host": "172.20.20.162",
    "username": user,
    "password": password,
}

FAK_16_SW = {
    "device_type": "cisco_xe",
    "host": "172.20.", #--------------------NOT in Catalyst Center
    "username": user,
    "password": password,
}
FAK_17_SW = {
    "device_type": "cisco_xe",
    "host": "172.20.20.194",
    "username": user,
    "password": password,
}

FAK_18_SW = {
    "device_type": "cisco_xe",
    "host": "172.20.20.210",
    "username": user,
    "password": password,
}

FAK_19_SW = {
    "device_type": "cisco_xe",
    "host": "172.20.20.226",
    "username": user,
    "password": password,
}

FAK_20_SW = {
    "device_type": "cisco_xe",
    "host": "172.20.20.242",
    "username": user,
    "password": password,
}

FAK_22_SW01 = {
    "device_type": "cisco_xe",
    "host": "172.20.23.18",
    "username": user,
    "password": password,
}

FAK_22_SW02 = {
    "device_type": "cisco_xe",
    "host": "172.20.23.19",
    "username": user,
    "password": password,
}

FAK_23_L_SW01 = {
    "device_type": "cisco_xe",
    "host": "172.20.23.2",
    "username": user,
    "password": password,
}

FAK_23_L_SW02 = {
    "device_type": "cisco_xe",
    "host": "172.20.23.3",
    "username": user,
    "password": password,
}

FAK_24_H_SW0 = {
    "device_type": "cisco_xe",
    "host": "172.20.23.50",
    "username": user,
    "password": password,
}

FAK_24_H_SW01 = {
    "device_type": "cisco_xe",
    "host": "172.20.23.51",
    "username": user,
    "password": password,
}

FAK_24_H_SW02 = {
    "device_type": "cisco_xe",
    "host": "172.20.23.52",
    "username": user,
    "password": password,
}

FAK_24_H_SW03 = {
    "device_type": "cisco_xe",
    "host": "172.20.23.53",
    "username": user,
    "password": password,
}

FAK_24_H_SW04 = {
    "device_type": "cisco_xe",
    "host": "172.20.23.54",
    "username": user,
    "password": password,
}

FAK_24_H_SW05 = {
    "device_type": "cisco_xe",
    "host": "172.20.23.55",
    "username": user,
    "password": password,
}

FAK_24_H_SW06 = {
    "device_type": "cisco_xe",
    "host": "172.20.23.56",
    "username": user,
    "password": password,
}

FAK_24_H_SW07 = {
    "device_type": "cisco_xe",
    "host": "172.20.23.57",
    "username": user,
    "password": password,
}

FAK_24_H_SW08 = {
    "device_type": "cisco_xe",
    "host": "172.20.23.58",
    "username": user,
    "password": password,
}

FAK_24_H_SW09 = {
    "device_type": "cisco_xe",
    "host": "172.20.23.59",
    "username": user,
    "password": password,
}

FAK_24_H_SW10 = {
    "device_type": "cisco_xe",
    "host": "172.20.23.60",
    "username": user,
    "password": password,
}

FAK_24_H_SW11 = {
    "device_type": "cisco_xe",
    "host": "172.20.23.61",
    "username": user,
    "password": password,
}

#--------------------------------------ERTs-----------------------------------
ERT01_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.28.144",
    "username": user,
    "password": password,
}

ERT01_OSW = {
    "device_type": "cisco_xe",
    "host": "172.20.28.131",
    "username": user,
    "password": password,
}

ERT03_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.25.161",
    "username": user,
    "password": password,
}

ERT03_SW1 = {
    "device_type": "cisco_xe",
    "host": "172.20.25.162",
    "username": user,
    "password": password,
}

ERT03_SW2 = {
    "device_type": "cisco_xe",
    "host": "172.20.25.163",
    "username": user,
    "password": password,
}

ERT03_OWS = {
    "device_type": "cisco_xe",
    "host": "172.20.25.164",
    "username": user,
    "password": password,
}

ERT04_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.28.33",
    "username": user,
    "password": password,
}

ERT04_SW1 = {
    "device_type": "cisco_xe",
    "host": "172.20.28.34",
    "username": user,
    "password": password,
}

ERT04_SW2 = {
    "device_type": "cisco_xe",
    "host": "172.20.28.35",
    "username": user,
    "password": password,
}


#-------------------------------------------IMAGING rtrs-----------------------

bldg_4012_image_sw = {
    "device_type": "cisco_xe",
    "host": "160.136.16.174",
    "username": user,
    "password": password,
}

bldg_44_image_sw = {
    "device_type": "cisco_xe",
    "host": "160.136.16.175",
    "username": user,
    "password": password,
}

c9200_4015_hotrack = {
    "device_type": "cisco_xe",
    "host": "160.136.16.166",
    "username": user,
    "password": password,
}

c9200l_4073_132 = {
    "device_type": "cisco_xe",
    "host": "160.136.16.164",
    "username": user,
    "password": password,
}
#----------------------------------------SENT-------------------------------------

SENT_RTR = {
    "device_type": "cisco_xe",
    "host": "172.20.24.65",
    "username": user,
    "password": password,
}

SENT_SW01 = {
    "device_type": "cisco_xe",
    "host": "172.20.24.66",
    "username": user,
    "password": password,
}

SENT_SW02 = {
    "device_type": "cisco_xe",
    "host": "172.20.24.73",
    "username": user,
    "password": password,
}

SENT_ESW = {
    "device_type": "cisco_xe",
    "host": "172.20.24.67",
    "username": user,
    "password": password,
}

SENT_TT_SW07 = {
    "device_type": "cisco_xe",
    "host": "172.20.24.77",
    "username": user,
    "password": password,
}

SENT_TT_SW09 = {
    "device_type": "cisco_xe",
    "host": "172.20.24.79",
    "username": user,
    "password": password,
}

SENT_TT_SW10 = {
    "device_type": "cisco_xe",
    "host": "172.20.24.80",
    "username": user,
    "password": password,
}

#----------------------------------------------IR------------------------------------------
IR829_07 = {
    "device_type": "cisco_ios",
    "host": "172.20.16.96",
    "username": user,
    "password": password,
}

IR829_27_NETOPS_G6 = {
    "device_type": "cisco_ios",
    "host": "172.20.18.240",
    "username": user,
    "password": password,
}

IR829_31_AK = {
    "device_type": "cisco_ios",
    "host": "172.20.17.224",
    "username": user,
    "password": password,
}

IR829_32_HD_LOANER = {
    "device_type": "cisco_ios",
    "host": "172.20.17.240",
    "username": user,
    "password": password,
}

#--------------------------------------------DCOs------------------------------------------------
DCO_101_RTR = {
    "device_type": "cisco_ios",
    "host": "172.20.4.16",
    "username": user,
    "password": password,
}

DCO_102_RTR = {
    "device_type": "cisco_ios",
    "host": "172.20.4.48",
    "username": user,
    "password": password,
}

DCO_201_RTR = {
    "device_type": "cisco_ios",
    "host": "172.20.4.80",
    "username": user,
    "password": password,
}

DCO_202_RTR = {
    "device_type": "cisco_ios",
    "host": "172.20.5.225",
    "username": user,
    "password": password,
}

DCO_202_SW = {
    "device_type": "cisco_ios",
    "host": "172.20.5.226",
    "username": user,
    "password": password,
}

DCO_301_RTR = {
    "device_type": "cisco_ios",
    "host": "172.20.4.113",
    "username": user,
    "password": password,
}

DCO_301_SW01 = {
    "device_type": "cisco_ios",
    "host": "172.20.4.99",
    "username": user,
    "password": password,
}

DCO_301_SW02 = {
    "device_type": "cisco_ios",
    "host": "172.20.4.100",
    "username": user,
    "password": password,
}

DCO_401_RTR = {
    "device_type": "cisco_ios",
    "host": "172.20.4.144",
    "username": user,
    "password": password,
}

DCO_501_RTR = {
    "device_type": "cisco_ios",
    "host": "172.20.4.176",
    "username": user,
    "password": password,
}

DCO_502_RTR = {
    "device_type": "cisco_ios",
    "host": "172.20.6.49",
    "username": user,
    "password": password,
}

DCO_601_RTR = {
    "device_type": "cisco_ios",
    "host": "172.20.4.208",
    "username": user,
    "password": password,
}

DCO_701_RTR = {
    "device_type": "cisco_ios",
    "host": "172.20.4.240",
    "username": user,
    "password": password,
}

DCO_801_RTR = {
    "device_type": "cisco_ios",
    "host": "172.20.5.17",
    "username": user,
    "password": password,
}
DCO_801_SW = {
    "device_type": "cisco_ios",
    "host": "172.20.5.3",
    "username": user,
    "password": password,
}
DCO_901_RTR = {
    "device_type": "cisco_ios",
    "host": "172.20.5.49",
    "username": user,
    "password": password,
}
DCO_1001_RTR = {
    "device_type": "cisco_ios",
    "host": "172.20.5.113",
    "username": user,
    "password": password,
}
