"""Structured configuration diff using ciscoconfparse2.

This script compares two configuration files using the
``ciscoconfparse2`` library which understands Cisco configuration
syntax and can produce a more intuitive diff than a line‑by‑line
comparison.  It falls back to the unified diff implementation if
``ciscoconfparse2`` is not installed.

Example::

    python config_diff_v2.py config_a.conf config_b.conf

The diff is printed to stdout.  To save to a file pass ``--output``.
"""

from __future__ import annotations

import argparse
from na_utils.config_utils import compare_configs_structured, compare_configs


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two configs using a structured diff")
    parser.add_argument("file1", help="First configuration file")
    parser.add_argument("file2", help="Second configuration file")
    parser.add_argument("--output", "-o", help="Write diff to this file", default=None)
    args = parser.parse_args()
    try:
        diff = compare_configs_structured(args.file1, args.file2, args.output)
    except RuntimeError:
        # Fall back to unified diff if structured diff unavailable
        diff = compare_configs(args.file1, args.file2, args.output)
    if diff is not None:
        print(diff)


if __name__ == "__main__":
    main()