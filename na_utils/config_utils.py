"""Utility functions for working with network configuration files.

This module provides helpers to compute differences between two
configuration files.  Two different approaches are offered:

``compare_configs``
    Uses Python's built‑in :mod:`difflib` library to produce a unified
    diff of two plain text files.  This is sufficient for simple
    comparisons where an ordered diff is acceptable.

``compare_configs_structured``
    Uses :class:`ciscoconfparse2.Diff` (if available) to produce a
    structured diff that understands Cisco configuration syntax.  This
    requires the third‑party ``ciscoconfparse2`` library to be
    installed and is optional.

Every function accepts file paths and optionally an output file.  If
an output path is provided the diff will be written there; otherwise
the diff is returned as a string.  Error handling ensures that
missing files or other exceptions do not crash the caller.
"""

from __future__ import annotations

import difflib
import os
from typing import Optional, List


def compare_configs(file1: str, file2: str, output_file: Optional[str] = None) -> Optional[str]:
    """Compare two configuration files using a unified diff.

    Reads both files line by line and generates a unified diff using
    :func:`difflib.unified_diff`.  The filenames are included in the
    diff header.  If ``output_file`` is specified the diff will be
    written to that file and the function returns ``None``.  If
    ``output_file`` is not provided the diff is returned as a single
    string.

    :param file1: Path to the first configuration file.
    :param file2: Path to the second configuration file.
    :param output_file: Optional path to write the diff to.
    :returns: A unified diff as a single string or ``None`` if written
        to ``output_file``.
    """
    try:
        with open(file1, "r") as f1, open(file2, "r") as f2:
            config1 = f1.readlines()
            config2 = f2.readlines()
        diff_iter = difflib.unified_diff(
            config1,
            config2,
            fromfile=file1,
            tofile=file2,
            lineterm="",
        )
        diff_lines: List[str] = list(diff_iter)
        diff_str = "\n".join(diff_lines)
        if output_file:
            with open(output_file, "w") as out:
                out.write(diff_str + "\n")
            return None
        return diff_str
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Error opening configuration file: {exc}")
    except Exception as exc:  # pragma: no cover - catch all for unexpected errors
        raise RuntimeError(f"Unexpected error while comparing configs: {exc}")


def compare_configs_structured(file1: str, file2: str, output_file: Optional[str] = None) -> Optional[str]:
    """Compare two configuration files using a structure aware diff.

    This function attempts to import :class:`ciscoconfparse2.Diff` to
    generate a structured diff.  If the library is unavailable a
    :class:`RuntimeError` is raised.  The returned value or behaviour
    mirrors :func:`compare_configs`.

    :param file1: Path to the first configuration file.
    :param file2: Path to the second configuration file.
    :param output_file: Optional path to write the diff to.
    :returns: The diff as a single string or ``None`` if written to
        ``output_file``.
    :raises RuntimeError: If the ``ciscoconfparse2`` library is not
        installed.
    """
    try:
        from ciscoconfparse2 import Diff  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "The ciscoconfparse2 library is required for structured diffs. "
            "Install it via 'pip install ciscoconfparse2' and try again."
        ) from exc
    try:
        diff_lines = Diff(file1, file2).get_diff()
        diff_str = os.linesep.join(diff_lines)
        if output_file:
            with open(output_file, "w") as out:
                out.write(diff_str + "\n")
            return None
        return diff_str
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Error opening configuration file: {exc}")
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(f"Unexpected error while performing structured diff: {exc}")