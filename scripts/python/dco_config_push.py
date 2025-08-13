"""Push removal of obsolete voice configuration to routers.

This script demonstrates how to use the helper functions in
``na_utils`` to connect to a list of routers and remove legacy voice
configuration.  The original version of this script hardcoded a
``testbed_FAK`` module containing device definitions and embedded
credentials.  In keeping with Python best practices, this refactored
version delegates connection handling to :func:`na_utils.net_device.connect_device`
and reads credentials from environment variables.  Hostnames or IPs
can be specified via a YAML testbed file, a comma separated list on
the command line or by default using the ``get_device_list`` helper
from :mod:`na_utils.dnac` to pull all routers from Catalyst Center.

**Security notice:** this script uses the same credentials defined
for Catalyst Center to authenticate to devices.  If your network
devices use different credentials you should either set the
``ROUTER_USER`` and ``ROUTER_PASS`` environment variables or modify
the helper in :mod:`na_utils.net_device` accordingly.

Example usage::

    python dco_config_push.py --hosts 192.0.2.10,192.0.2.11

To use devices discovered from Catalyst Center::

    python dco_config_push.py --from-dnac

To specify a YAML file containing a list of hosts::

    python dco_config_push.py --testbed my_routers.yaml

The YAML file should contain a top‑level ``hosts`` list with either
``hostname`` or ``ip`` keys.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Iterable, List, Dict, Any

import yaml

import os
import sys
from pathlib import Path

# Adjust sys.path so that 'na_utils' can be imported when this script
# is executed directly from its own directory.  Without this, Python
# only searches the current working directory and the standard paths.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from na_utils.net_device import connect_device, send_config_commands
from na_utils.dnac import get_device_list


# Commands to run on the routers.  These were extracted from the
# original dco_config_push.py.  If new commands need to be added,
# modify this list.
CMD_LIST: List[str] = [
    "no voice register pool 1",
    "no voice service voip",
    "no mgcp",
    "!",
    "no mgcp call-agent anhqa0cms.arnorth.army.mil 2427 service-type mgcp version 0.1",
    "no mgcp dtmf-relay voip codec all mode out-of-band",
    "no mgcp rtp unreachable timeout 1000 action notify",
    "!",
    "no mgcp modem passthrough voip mode nse",
    "no mgcp package-capability rtp-package",
    "no mgcp package-capability sst-package",
    "no mgcp package-capability pre-package",
    "!",
    "!",
    "no mgcp sdp simple",
    "no mgcp fax t38 inhibit",
    "no mgcp rtp payload-type g726r16 static",
    "no mgcp bind control source-interface Vlan3186",
    "no mgcp bind media source-interface Vlan3186",
    "no mgcp behavior rsip-range tgcp-only",
    "no mgcp behavior comedia-role none",
    "!",
    "!",
    "no mgcp behavior comedia-check-media-src disable",
    "no mgcp behavior comedia-sdp-force disable",
    "no ccm-manager music-on-hold",
    "no ccm-manager fallback-mgcp",
    "no ccm-manager redundant-host anhqa0cmp.arnorth.army.mil",
    "no ccm-manager mgcp",
    "!",
    "!",
    "no ccm-manager config server 160.136.17.52",
    "no ccm-manager config",
    "!",
    "!",
    "no dial-peer voice 100 pots",
    "no dial-peer voice 101 pots",
    "no dial-peer voice 102 pots",
    "no dial-peer voice 103 pots",
    "no dial-peer voice 999012 pots",
    "no dial-peer voice 999010 pots",
    "no call-manager-fallback",
    "no mgcp profile default",
]

# Special command that requires confirmation.  Netmiko's send_command_timing
# will be used to handle the yes/no prompt.
CMD_SPECIAL: str = "no voice register global"


def load_hosts_from_yaml(path: str) -> List[str]:
    """Load a list of hosts from a YAML file.

    The YAML file should contain a top‑level ``hosts`` list where
    each element is either a string (host/IP) or a mapping with
    ``hostname`` or ``ip`` keys.

    :param path: Path to the YAML file.
    :returns: A list of hostnames or IP addresses.
    :raises RuntimeError: If the file format is incorrect.
    """
    with open(path, "r") as fh:
        data = yaml.safe_load(fh) or {}
    hosts: List[str] = []
    raw_hosts = data.get("hosts")
    if not isinstance(raw_hosts, list):
        raise RuntimeError("The YAML file must define a top-level 'hosts' list")
    for entry in raw_hosts:
        if isinstance(entry, str):
            hosts.append(entry)
        elif isinstance(entry, dict):
            hosts.append(entry.get("hostname") or entry.get("ip"))
        else:
            raise RuntimeError("Each host entry must be a string or a mapping with hostname/ip keys")
    return hosts


def load_hosts_from_dnac() -> List[str]:
    """Retrieve router hostnames from Catalyst Center.

    Uses :func:`na_utils.dnac.get_device_list` with the family
    'Routers' to limit to router devices.  Returns the hostname for
    each router.
    """
    devices = get_device_list(family="Routers")
    hosts: List[str] = []
    for dev in devices.get("response", []):
        host = dev.get("managementIpAddress") or dev.get("hostname")
        if host:
            hosts.append(host)
    return hosts


def connect_and_run(host: str) -> None:
    """Connect to a single device and apply the command set.

    Handles the special command requiring confirmation via send_command_timing.
    """
    from netmiko import BaseConnection
    conn = connect_device(host)
    if not conn:
        return
    try:
        # Send standard commands
        output = send_config_commands(conn, CMD_LIST)
        print(output)
        # Handle special command that prompts for confirmation
        # Use send_command_timing to interactively send 'yes'
        output = conn.send_command_timing("conf t")
        output += conn.send_command_timing(CMD_SPECIAL)
        if "yes/no" in output.lower():
            output += conn.send_command_timing("yes")
        output += conn.send_command_timing("end")
        print(output)
        # Save configuration
        print(conn.send_command("write memory"))
    finally:
        conn.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Remove voice configuration from routers")
    parser.add_argument(
        "--hosts",
        help="Comma separated list of hosts/IPs to target",
        default=None,
    )
    parser.add_argument(
        "--testbed",
        help="Path to YAML file describing hosts",
        default=None,
    )
    parser.add_argument(
        "--from-dnac",
        action="store_true",
        help="Discover router hosts from Catalyst Center",
    )
    args = parser.parse_args()
    hosts: List[str] = []
    if args.hosts:
        hosts.extend([h.strip() for h in args.hosts.split(",") if h.strip()])
    if args.testbed:
        hosts.extend(load_hosts_from_yaml(args.testbed))
    if args.from_dnac or not hosts:
        # If --from-dnac specified or no hosts provided, query DNAC
        hosts.extend(load_hosts_from_dnac())
    if not hosts:
        print("No hosts to configure.  Provide --hosts, --testbed or --from-dnac", file=sys.stderr)
        sys.exit(1)
    for host in hosts:
        print(f"Configuring {host}")
        connect_and_run(host)
    print("Configuration complete")


if __name__ == "__main__":
    main()