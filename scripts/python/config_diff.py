"""Compare two configuration files and optionally write a diff.

This script wraps :func:`na_utils.config_utils.compare_configs` to
provide a convenient command‑line interface for comparing network
configurations.  It supports writing the diff to a file or printing
to stdout.  The underlying comparison uses a unified diff from the
standard library.

Usage example::

    python config_diff.py /path/to/config1.conf /path/to/config2.conf --output diff.txt

The module intentionally avoids hard‑coded paths.  If you used
previous versions of this script which contained example paths, you
should now specify your own files as arguments.
"""

from __future__ import annotations

import argparse
from na_utils.config_utils import compare_configs


def main() -> None:
    """Parse command line arguments and perform the configuration diff."""
    parser = argparse.ArgumentParser(description="Compare two configuration files")
    parser.add_argument("file1", help="Path to the first configuration file")
    parser.add_argument("file2", help="Path to the second configuration file")
    parser.add_argument("--output", "-o", help="Optional file to write diff to", default=None)
    args = parser.parse_args()

    diff_result = compare_configs(args.file1, args.file2, args.output)
    if diff_result is not None:
        print(diff_result)


if __name__ == "__main__":
    main()