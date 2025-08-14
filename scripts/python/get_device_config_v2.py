"""Fetch running configurations from reachable devices.

This script queries Catalyst Center for network devices, filters the
list to only those that report a ``reachabilityStatus`` of
``Reachable`` and then connects to each device via SSH to retrieve
its running configuration.  The configurations are saved to
``<output_dir>/<hostname>.conf``.  Use environment variables to set
device credentials; see ``.env.template`` for details.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Dict, Any

import sys

from dotenv import load_dotenv

load_dotenv()

# Ensure project root on sys.path for na_utils
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from na_utils.dnac import get_device_list
from na_utils.net_device import connect_device


def main() -> None:
    parser = argparse.ArgumentParser(description="Save running config from reachable devices")
    parser.add_argument(
        "--output-dir", "-o",
        help="Directory to write configuration files to",
        default="device_configs",
    )
    args = parser.parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    devices: Dict[str, Any] = get_device_list()
    reachable = [dev for dev in devices.get("response", []) if dev.get("reachabilityStatus") == "Reachable" and dev.get('family') != "Unified AP"]
    if not reachable:
        print("No reachable devices found")
        return
    for dev in reachable:
        hostname = dev.get("hostname") or dev.get("id")
        ip = dev.get("managementIpAddress")
        print(f"Connecting to {hostname} ({ip})…")
        conn = connect_device(ip)
        if not conn:
            continue
        try:
            output = conn.send_command("show running-config")
            file_path = out_dir / f"{hostname}.conf"
            with open(file_path, "w") as fh:
                fh.write(output)
            print(f"Saved config to {file_path}")
        except Exception as exc:
            print(f"Failed to retrieve config from {hostname}: {exc}")
        finally:
            conn.disconnect()


if __name__ == "__main__":
    main()