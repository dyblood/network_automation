"""Generate an Excel spreadsheet containing pyATS device information.

This script queries Cisco Catalyst Center for network devices and
generates an Excel file listing attributes used by pyATS, such as
hostname, management IP, protocol and operating system.  It relies on
environment variables for authentication; see the root ``.env.template``
for details.  The output directory defaults to ``pyats/pyatstb`` but
can be overridden via ``--output``.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from na_utils.dnac import get_device_list


def filter_devices(device_json: Dict[str, Any]) -> List[Dict[str, str]]:
    """Extract relevant fields from the Catalyst Center device response.

    Only devices belonging to the 'Routers' or 'Switches and Hubs'
    families are included.  Hostnames are normalised by removing
    uppercase/lowercase variations of a domain suffix.  If your
    environment uses different families or naming conventions adjust
    this function accordingly.
    """
    filtered: List[Dict[str, str]] = []
    for device in device_json.get("response", []):
        if device.get("family") not in {"Routers", "Switches and Hubs"}:
            continue
        hostname = (device.get("hostname") or "N/A").split(".")[0]
        ip = f"{device.get('managementIpAddress', 'N/A')}:22"
        username = os.getenv("DNAC_USER", "user")
        password = os.getenv("DNAC_PASS", "pass")
        protocol = "ssh"
        os_type = (device.get("softwareType") or "N/A").replace("-", "").lower()
        filtered.append(
            {
                "hostname": hostname,
                "ip": ip,
                "username": username,
                "password": password,
                "protocol": protocol,
                "os": os_type,
            }
        )
    return filtered


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an Excel file with pyATS device info")
    parser.add_argument(
        "--output",
        "-o",
        help="Path to the output Excel file",
        default=str(Path(__file__).resolve().parent / "pyats_tb.xlsx"),
    )
    args = parser.parse_args()
    devices_json = get_device_list()
    rows = filter_devices(devices_json)
    df = pd.DataFrame(rows)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(out_path, index=False)
    print(f"Excel file created: {out_path}")


if __name__ == "__main__":
    main()