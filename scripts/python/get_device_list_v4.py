"""Retrieve and display Catalyst Center device list with optional Excel export.

This refactored version uses :mod:`na_utils.dnac` to query the
Catalyst Center API rather than reimplementing token handling.  It
prints a formatted table of devices and can optionally save the list
to an Excel file.  Use command line arguments to control output.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Dict, Any, List

import pandas as pd
import sys
from colorama import init, Fore, Style

# Ensure project root on path for na_utils
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from na_utils.dnac import get_device_list


def safe_format(value: Any, default: str = "N/A") -> str:
    return str(value) if value is not None else default


def print_device_list(device_json: Dict[str, Any]) -> None:
    """Pretty print the device list with colour coded reachability."""
    init(autoreset=True)
    header = [
        "HOSTNAME", "ROLE", "SERIAL", "PLATFORM ID", "VERSION",
        "REACHABILITY", "MGMT IP", "MAC", "ID",
    ]
    col_widths = [50, 15, 12, 18, 12, 18, 18, 17, 35]
    # Print header
    row_fmt = "| " + " | ".join(f"{{:<{w}}}" for w in col_widths) + " |"
    print(row_fmt.format(*header))
    for device in device_json.get("response", []):
        status = device.get("reachabilityStatus", "Unknown")
        hostname = device.get("hostname")
        if status.lower() == "reachable":
            status_col = Fore.GREEN + status + Style.RESET_ALL
            hostname_col = Fore.GREEN + hostname + Style.RESET_ALL
        elif status.lower() == "unreachable":
            status_col = Fore.RED + status + Style.RESET_ALL
            hostname_col = Fore.RED + hostname + Style.RESET_ALL
        else:
            status_col = Fore.YELLOW + status + Style.RESET_ALL
            hostname_col = Fore.YELLOW + hostname + Style.RESET_ALL
        row = [
            hostname_col,
            safe_format(device.get("role")),
            safe_format(device.get("serialNumber")),
            safe_format(device.get("platformId")),
            safe_format(device.get("softwareVersion")),
            status_col,
            safe_format(device.get("managementIpAddress")),
            safe_format(device.get("macAddress")),
            safe_format(device.get("id")),
        ]
        print(row_fmt.format(*row))


def save_devices_to_excel(device_json: Dict[str, Any], filename: str) -> None:
    devices: List[Dict[str, Any]] = []
    for device in device_json.get("response", []):
        devices.append({
            'Hostname': safe_format(device.get('hostname')),
            'Management IP': safe_format(device.get('managementIpAddress')),
            'Serial Number': safe_format(device.get('serialNumber')),
            'Platform ID': safe_format(device.get('platformId')),
            'Software Version': safe_format(device.get('softwareVersion')),
            'Reachability Status': safe_format(device.get('reachabilityStatus')),
            'Role': safe_format(device.get('role')),
            'MAC Address': safe_format(device.get('macAddress')),
            'ID': safe_format(device.get('id')),
        })
    df = pd.DataFrame(devices)
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(filename, index=False)
    print(f"Device list saved to {filename}")


def main() -> None:
    parser = argparse.ArgumentParser(description="List devices from Catalyst Center")
    parser.add_argument(
        "--excel", "-e", help="Path to save Excel file with device information", default=None,
    )
    args = parser.parse_args()
    devices = get_device_list()
    print_device_list(devices)
    if args.excel:
        save_devices_to_excel(devices, args.excel)


if __name__ == "__main__":
    main()