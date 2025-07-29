from dotenv import load_dotenv
import os

load_dotenv()


DNAC_USER = os.getenv("DNAC_USER")

print(DNAC_USER)

filename = f"{os.getenv('win_base_path')}youngblood_netops/get_device_list/get_device_list.xlsx"

print(filename)