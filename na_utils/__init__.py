"""Top level package for network automation utilities.

This package groups together shared functionality used across various
scripts in the ``network_automation`` repository.  The goal of
centralising common code is to promote code reuse, improve testability,
and simplify maintenance.  For example, rather than copy‑pasting
authentication logic into every script that talks to Cisco Catalyst
Center, the token generation lives in :mod:`na_utils.dnac`.  Likewise,
helper functions for comparing device configuration files reside in
:mod:`na_utils.config_utils`, and Netmiko connection helpers live in
:mod:`na_utils.net_device`.

Modules
=======

``dnac``
    Wraps Cisco DNA (Catalyst) Center API calls such as token
    retrieval, generic GET requests, and device listing.  See
    :mod:`na_utils.dnac` for details.

``config_utils``
    Contains helpers for performing configuration diffs using the
    standard library and third‑party libraries.

``net_device``
    Provides convenience wrappers around the Netmiko library for
    connecting to network devices and executing configuration sets.

The package attempts to follow Python best practices as described in
PEP 8 and the `Real Python`_ guide.  In particular, every public
function and module contains a docstring that briefly states its
purpose and behaviour.  Should you need to extend the package, be
sure to add appropriate documentation and unit tests.

.. _Real Python: https://realpython.com/python-pep8/
"""

from .dnac import get_device_list, get_api_response, get_auth_token  # noqa: F401
from .config_utils import compare_configs  # noqa: F401
from .net_device import connect_device, send_config_commands  # noqa: F401

__all__ = [
    "get_device_list",
    "get_api_response",
    "get_auth_token",
    "compare_configs",
    "connect_device",
    "send_config_commands",
]