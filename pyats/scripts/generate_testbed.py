#!/usr/bin/env python3
"""Generate a pyATS testbed from Catalyst Center devices.

This utility queries Cisco Catalyst (DNA) Center for all network
devices and converts the result into a pyATS testbed YAML file.  The
credentials used for SSH connections are pulled from the same
environment variables used for Catalyst Center authentication.  The
generated file is written to the ``testbeds`` directory relative to
this script and is ignored by ``.gitignore`` for security reasons.

Example::

    python generate_testbed.py --output my_testbed.yaml

If ``--output`` is omitted the default file name is ``generated_testbed.yaml``.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any, Dict

import yaml

import sys
from pathlib import Path

# Ensure project root is on sys.path when executing directly
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from na_utils.dnac import get_device_list, to_pyats_testbed


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a pyATS testbed YAML from Catalyst Center devices")
    parser.add_argument(
        "--output", "-o",
        help="Name of the output YAML file (stored under testbeds/)",
        default="generated_testbed.yaml",
    )
    parser.add_argument(
        "--name",
        help="Optional name for the testbed",
        default="generated_testbed",
    )
    args = parser.parse_args()
    # Fetch devices from Catalyst Center
    devices = get_device_list()
    testbed_dict: Dict[str, Any] = to_pyats_testbed(devices, testbed_name=args.name)
    # Determine output path under testbeds/
    base_dir = Path(__file__).resolve().parent.parent / "testbeds"
    base_dir.mkdir(parents=True, exist_ok=True)
    out_path = base_dir / args.output
    with open(out_path, "w") as fh:
        yaml.safe_dump(testbed_dict, fh, default_flow_style=False, sort_keys=False)
    print(f"pyATS testbed written to {out_path}")


if __name__ == "__main__":
    main()