"""Automate configuration changes on ERT routers.

This script queries Cisco Catalyst Center (previously DNA Center) for all
routers in the network, filters them based on a substring in their
hostname (default: ``ERT``), and then applies a set of configuration
changes to each matching device.  The changes remove legacy voice and
media gateway settings that reference an old RHN (Red Hat Network)
connection.  A simple CSV tracker is updated to record which devices
have been processed and whether the update succeeded.

This refactored version relies on the ``na_utils`` package to handle
authentication with Catalyst Center and SSH connectivity via Netmiko.
All credentials are loaded from your ``.env`` file using
``python‑dotenv``.  See the accompanying ``.env.template`` for the
required variables and update it with your own details (but never
commit real credentials to version control).

Usage example::

    python ert_rtr_change_RHN_connection.py \
        --pattern ERT \
        --tracker ert_rtr_change_tracker.csv

You can override the list of configuration commands by specifying
``--commands-file`` pointing to a plain text file with one command per
line.  By default a reasonable set of ``no`` commands are used to
disable MGCP, remove call manager fallback, dial peers and other
voice‑related features.

Note that the commands in this script are representative; adjust
``DEFAULT_COMMANDS`` as needed for your environment.  The script
prints progress information to standard output and writes a summary
into the tracker file for auditing.
"""

from __future__ import annotations

import argparse
import csv
import os
from datetime import datetime
from typing import List, Iterable, Optional

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    # Fallback if python-dotenv is not installed.  In that case
    # environment variables must already be set in the environment.
    def load_dotenv(*args: any, **kwargs: any) -> None:
        return None
from ciscoconfparse import CiscoConfParse

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from na_utils import dnac
from na_utils import net_device


# Load environment variables from .env
load_dotenv()


# Default list of configuration commands to remove RHN/MGCP call
# manager settings.  These commands were distilled from legacy scripts
# in this repository.  Modify this list to suit your particular use
# case.  The exclamation marks are retained to mirror the style of
# Cisco configuration, although Netmiko will ignore empty lines.
DEFAULT_COMMANDS: List[str] = [
    "no voice register pool 1",
    "no voice service voip",
    "no mgcp",
    "no mgcp call-agent anhqa0cms.arnorth.army.mil 2427 service-type mgcp version 0.1",
    "no mgcp dtmf-relay voip codec all mode out-of-band",
    "no mgcp rtp unreachable timeout 1000 action notify",
    "no mgcp modem passthrough voip mode nse",
    "no mgcp package-capability rtp-package",
    "no mgcp package-capability sst-package",
    "no mgcp package-capability pre-package",
    "no mgcp sdp simple",
    "no mgcp fax t38 inhibit",
    "no mgcp rtp payload-type g726r16 static",
    "no mgcp bind control source-interface Vlan3186",
    "no mgcp bind media source-interface Vlan3186",
    "no mgcp behavior rsip-range tgcp-only",
    "no mgcp behavior comedia-role none",
    "no mgcp behavior comedia-check-media-src disable",
    "no mgcp behavior comedia-sdp-force disable",
    "no ccm-manager music-on-hold",
    "no ccm-manager fallback-mgcp",
    "no ccm-manager redundant-host anhqa0cmp.arnorth.army.mil",
    "no ccm-manager mgcp",
    "no ccm-manager config server 160.136.17.52",
    "no ccm-manager config",
    "no dial-peer voice 100 pots",
    "no dial-peer voice 101 pots",
    "no dial-peer voice 102 pots",
    "no dial-peer voice 103 pots",
    "no dial-peer voice 999012 pots",
    "no dial-peer voice 999010 pots",
    "no call-manager-fallback",
    "no mgcp profile default",
]


def load_commands_from_file(path: str) -> List[str]:
    """Load configuration commands from a text file.

    Each non‑empty line in the file is interpreted as a single command.
    Comment lines starting with ``#`` are ignored.  Whitespace around
    commands is stripped.

    :param path: Path to the file containing commands.
    :returns: List of commands.
    :raises FileNotFoundError: If the file does not exist.
    """
    commands: List[str] = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            commands.append(line)
    return commands


def write_tracker_row(tracker_path: str, row: Iterable[str]) -> None:
    """Append a row to the CSV tracker file.

    Creates the file with headers if it does not exist.

    :param tracker_path: Path to the CSV file.
    :param row: Iterable of strings to write as a row.
    """
    file_exists = os.path.exists(tracker_path)
    with open(tracker_path, "a", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        if not file_exists:
            writer.writerow(["timestamp", "hostname", "ip", "status", "message"])
        writer.writerow(row)


def apply_commands_to_device(hostname: str, ip: str, commands: List[str]) -> tuple[bool, str]:
    """Connect to a device and apply configuration commands.

    Uses the helper functions in :mod:`na_utils.net_device` to
    establish an SSH session and send the specified commands.  If the
    connection fails or commands cannot be sent, returns ``False``
    along with an error message.  Otherwise returns ``True`` and
    Netmiko's output.

    :param hostname: Device name (for logging purposes).
    :param ip: Management IP address.
    :param commands: List of CLI commands to send.
    :returns: Tuple of success flag and message.
    """
    conn = net_device.connect_device(ip)
    if not conn:
        return False, "SSH connection failed"
    try:
        output = net_device.send_config_commands(conn, commands)
        conn.disconnect()
        return True, output
    except Exception as exc:  # pragma: no cover - unexpected errors are logged
        try:
            conn.disconnect()
        except Exception:
            pass
        return False, f"Error sending commands: {exc}"


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Apply RHN connection changes on ERT routers")
    parser.add_argument(
        "--pattern",
        default="ERT",
        help="Substring used to match router hostnames (case‑insensitive). Defaults to 'ERT'.",
    )
    parser.add_argument(
        "--commands-file",
        dest="commands_file",
        help="Path to a file containing configuration commands to send. Overrides the built‑in defaults.",
    )
    parser.add_argument(
        "--tracker",
        default="ert_rtr_change_tracker.csv",
        help="Path to CSV tracker file for logging changes. Defaults to 'ert_rtr_change_tracker.csv'.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pattern = args.pattern.lower()
    tracker = args.tracker

    # Load command list either from file or defaults
    if args.commands_file:
        commands = load_commands_from_file(args.commands_file)
        if not commands:
            print(f"No commands loaded from {args.commands_file}; using defaults instead")
            commands = DEFAULT_COMMANDS
    else:
        commands = DEFAULT_COMMANDS

    # Fetch routers from Catalyst Center
    try:
        device_json = dnac.get_device_list(family="Routers")
    except Exception as exc:
        raise RuntimeError(f"Failed to retrieve device list: {exc}")

    devices = device_json.get("response", [])
    if not devices:
        print("No routers returned from Catalyst Center.")
        return

    # Filter based on hostname pattern
    targets = [d for d in devices if pattern in str(d.get("hostname", "")).lower()]
    if not targets:
        print(f"No routers matching pattern '{args.pattern}' were found.")
        return

    print(f"Found {len(targets)} router(s) matching pattern '{args.pattern}'. Starting updates...")

    for dev in targets:
        hostname = dev.get("hostname", "unknown")
        ip = dev.get("managementIpAddress") or dev.get("ipAddress")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not ip:
            print(f"Skipping {hostname}: no management IP available")
            write_tracker_row(tracker, [timestamp, hostname, "", "skipped", "No management IP"])
            continue
        print(f"\nProcessing {hostname} ({ip})...")
        success, message = apply_commands_to_device(hostname, ip, commands)
        status = "success" if success else "failure"
        print(message)
        write_tracker_row(tracker, [timestamp, hostname, ip, status, message.split("\n")[0]])


if __name__ == "__main__":  # pragma: no cover - skip during unit tests
    main()