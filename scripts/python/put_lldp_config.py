"""Disable LLDP on interfaces where CDP is disabled.

This script inspects running configurations on network devices and
disables LLDP on any interface that has CDP explicitly turned off.
In many environments CDP and LLDP are enabled by default, however
there are scenarios—such as inter‑domain or security zones—where CDP
is disabled on specific ports.  LLDP should also be disabled on those
ports to prevent the device from advertising topology information.

The script performs the following high‑level steps:

1.  Query Catalyst Center for all network devices (optionally
    restricted by device family).  By default all devices are
    processed.
2.  Connect to each device via SSH using Netmiko, leveraging
    credentials from your ``.env`` file.
3.  Parse the running configuration with :mod:`ciscoconfparse` to
    locate interface blocks.  For every interface that contains ``no
    cdp enable`` but does not already disable LLDP, build a set of
    commands to enter the interface and issue ``no lldp transmit`` and
    ``no lldp receive``.
4.  Send the commands to the device using Netmiko.  Results and
    errors are logged to a CSV tracker for auditing purposes.

Because fetching a full running configuration can be time consuming,
consider limiting the number of devices processed by specifying a
device family (e.g. ``--family Switches and Hubs``).  Use the
``--pattern`` option to restrict the script to devices whose hostname
contains a given substring (case‑insensitive).

Example::

    python put_lldp_config.py --family "Switches and Hubs" --pattern LAB

Security Note:  Credentials are loaded from environment variables via
``python‑dotenv``.  Ensure you have created a local ``.env`` file
based on the provided template and that sensitive information is not
committed to version control.  See the project README for more
details.
"""

from __future__ import annotations

import argparse
import csv
import os
from datetime import datetime
from typing import Iterable, List

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    # Provide a no‑op fallback when python‑dotenv is unavailable.  This
    # allows the script to run in environments where dependencies are
    # not yet installed, provided that necessary environment variables
    # are already set.
    def load_dotenv(*args: any, **kwargs: any) -> None:
        return None
from ciscoconfparse import CiscoConfParse

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from na_utils import dnac
from na_utils import net_device


load_dotenv()


def parse_interface_commands(config: str) -> List[str]:
    """Generate commands to disable LLDP on interfaces with CDP disabled.

    Parses the provided running configuration and locates all
    ``interface`` stanzas.  For each interface, if it contains the
    directive ``no cdp enable`` and does not already include ``no
    lldp transmit``, a sequence of commands is built to enter the
    interface configuration mode and disable LLDP transmit and
    receive.  The interface name is extracted from the first word of
    the interface header.

    :param config: The full running configuration of a device.
    :returns: A flat list of CLI commands to send to the device.
    """
    parse = CiscoConfParse(config.splitlines())
    commands: List[str] = []
    for iface in parse.find_objects(r"^interface "):
        # Determine if CDP is disabled on this interface
        children = [child.text.strip() for child in iface.children]
        has_no_cdp = any(line.lower().startswith("no cdp enable") for line in children)
        # Determine if LLDP already disabled
        has_no_lldp_tx = any(line.lower().startswith("no lldp transmit") for line in children)
        if has_no_cdp and not has_no_lldp_tx:
            int_name = iface.text.split()[1]
            commands.append(f"interface {int_name}")
            commands.append("no lldp transmit")
            commands.append("no lldp receive")
            commands.append("exit")
    return commands


def write_tracker_row(tracker_path: str, row: Iterable[str]) -> None:
    """Append a row to the CSV tracker file.

    Creates the file with headers if it does not already exist.

    :param tracker_path: Path to the CSV file.
    :param row: Iterable of values to write as a row.
    """
    file_exists = os.path.exists(tracker_path)
    with open(tracker_path, "a", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        if not file_exists:
            writer.writerow(["timestamp", "hostname", "ip", "status", "interfaces", "message"])
        writer.writerow(row)


def process_device(hostname: str, ip: str) -> tuple[bool, int, str]:
    """Connect to a device, build LLDP disable commands and apply them.

    :param hostname: Device name for logging.
    :param ip: Management IP address.
    :returns: Tuple of success flag, number of interfaces processed and a message.
    """
    conn = net_device.connect_device(ip)
    if not conn:
        return False, 0, "SSH connection failed"
    try:
        # Retrieve full running config.  In practice you might limit
        # this with a pipe (e.g. ``show run | section interface``) but
        # here we fetch the entire config to ensure LLDP state is
        # parsed correctly.
        running = conn.send_command("show running-config", read_timeout=90)
        commands = parse_interface_commands(running)
        if not commands:
            conn.disconnect()
            return True, 0, "No interfaces required changes"
        # Count interfaces by counting "interface" lines in commands
        num_interfaces = sum(1 for cmd in commands if cmd.startswith("interface "))
        output = net_device.send_config_commands(conn, commands)
        conn.disconnect()
        return True, num_interfaces, output.splitlines()[0] if output else "Commands sent"
    except Exception as exc:  # pragma: no cover
        try:
            conn.disconnect()
        except Exception:
            pass
        return False, 0, f"Error processing device: {exc}"


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Disable LLDP on interfaces where CDP is disabled")
    parser.add_argument(
        "--family",
        default=None,
        help=("Device family to filter on (e.g. 'Switches and Hubs'). "
              "If omitted all devices are processed."),
    )
    parser.add_argument(
        "--pattern",
        default=None,
        help="Substring used to match device hostnames (case‑insensitive).",
    )
    parser.add_argument(
        "--tracker",
        default="lldp_change_tracker.csv",
        help="Path to CSV tracker file. Defaults to 'lldp_change_tracker.csv'.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tracker = args.tracker
    family = args.family
    pattern = args.pattern.lower() if args.pattern else None

    # Retrieve devices from Catalyst Center
    try:
        device_json = dnac.get_device_list(family=family) if family else dnac.get_device_list()
    except Exception as exc:
        raise RuntimeError(f"Failed to retrieve device list: {exc}")
    devices = device_json.get("response", [])
    if not devices:
        print("No devices returned from Catalyst Center.")
        return

    # Filter by hostname pattern if provided
    if pattern:
        devices = [d for d in devices if pattern in str(d.get("hostname", "")).lower()]
        if not devices:
            print(f"No devices matching pattern '{args.pattern}' were found.")
            return

    print(f"Processing {len(devices)} device(s) to update LLDP configuration...")
    for dev in devices:
        hostname = dev.get("hostname", "unknown")
        ip = dev.get("managementIpAddress") or dev.get("ipAddress")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not ip:
            print(f"Skipping {hostname}: no management IP available")
            write_tracker_row(tracker, [timestamp, hostname, "", "skipped", 0, "No management IP"])
            continue
        print(f"\nProcessing {hostname} ({ip})...")
        success, num_ifaces, message = process_device(hostname, ip)
        status = "success" if success else "failure"
        if num_ifaces:
            summary = f"Updated {num_ifaces} interface(s)"
        else:
            summary = message
        print(summary)
        write_tracker_row(tracker, [timestamp, hostname, ip, status, num_ifaces, summary])


if __name__ == "__main__":  # pragma: no cover
    main()