#!/usr/bin/env python3
"""Dynamic inventory for Ansible based on Catalyst Center.

This script queries Cisco Catalyst (DNA) Center for the list of
network devices and outputs a JSON structure consumable by Ansible.
Hosts are grouped by their ``family`` attribute (e.g. ``routers``,
``switches_and_hubs``).  Host variables include ``ansible_host`` (the
management IP), username, password and network OS derived from the
device's software type.  Credentials and the base URL for Catalyst
Center are read from environment variables ``DNAC_BURL``,
``DNAC_USER`` and ``DNAC_PASS``.

Usage:

    ansible-inventory -i dnac_inventory.py --list
    ansible-inventory -i dnac_inventory.py --host <hostname>

For further details on dynamic inventories see the Ansible
documentation.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

# Ensure that the project root is on sys.path.  When executed from
# within the inventories directory by Ansible, Python might not
# automatically include the repository root.  Adding the parent
# directories makes the `na_utils` package available.

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from na_utils.dnac import get_device_list, to_ansible_inventory


def generate_inventory() -> dict[str, Any]:
    """Fetch devices from Catalyst Center and build an inventory."""
    devices = get_device_list()
    return to_ansible_inventory(devices)


def main() -> None:
    inventory = generate_inventory()
    # Ansible passes arguments like --list or --host
    if len(sys.argv) == 2 and sys.argv[1] == "--list":
        print(json.dumps(inventory, indent=2))
    elif len(sys.argv) == 3 and sys.argv[1] == "--host":
        host = sys.argv[2]
        hostvars = inventory.get("_meta", {}).get("hostvars", {}).get(host, {})
        print(json.dumps(hostvars, indent=2))
    else:
        # When called with no args print entire inventory as per Ansible spec
        print(json.dumps(inventory, indent=2))


if __name__ == "__main__":
    main()