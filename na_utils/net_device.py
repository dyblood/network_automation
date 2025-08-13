"""Network device connection helpers using Netmiko.

This module wraps common tasks when interacting with network devices
over SSH using the `netmiko` library.  By hiding connection setup
inside helper functions, scripts can focus on high‑level logic.  All
functions respect environment variables for credentials and attempt to
handle common error conditions gracefully.

Netmiko must be installed in your Python environment (see
``requirements.txt``).  Supported device types include Cisco IOS
variants such as ``cisco_ios`` and ``cisco_xe``.  Refer to the
Netmiko documentation for a full list of supported platforms.
"""

from __future__ import annotations

import os
from typing import List, Iterable, Optional, Dict, Any

from dotenv import load_dotenv
from netmiko import ConnectHandler
from netmiko import NetmikoTimeoutException, NetmikoAuthenticationException

load_dotenv()


def _get_device_credentials() -> Dict[str, str]:
    """Retrieve the SSH username and password from environment variables.

    Reads ``DNAC_USER`` and ``DNAC_PASS`` from the environment.
    Although these variables are primarily intended for Catalyst Center
    authentication they are often the same credentials used for device
    access.  Should you require different credentials, adjust this
    helper accordingly.

    :returns: Mapping with keys ``username`` and ``password``.
    :raises RuntimeError: If credentials are missing.
    """
    username = os.getenv("DNAC_USER")
    password = os.getenv("DNAC_PASS")
    missing = [name for name, value in {"DNAC_USER": username, "DNAC_PASS": password}.items() if not value]
    if missing:
        raise RuntimeError(
            f"Missing device credentials: {', '.join(missing)}. "
            "Populate these in your .env file."
        )
    return {"username": username, "password": password}


def connect_device(host: str, *, device_type: str = "cisco_xe", username: Optional[str] = None, password: Optional[str] = None, **kwargs: Any) -> Optional[ConnectHandler]:
    """Establish an SSH connection to a network device.

    This convenience wrapper around :class:`netmiko.ConnectHandler`
    handles credential lookup and common exceptions.  If connection
    succeeds the Netmiko connection object is returned; otherwise
    ``None`` is returned and an error is logged to ``stderr``.

    :param host: IP address or hostname of the target device.
    :param device_type: Netmiko device type (defaults to ``cisco_xe``).
    :param username: Optional SSH username.  Defaults to ``DNAC_USER``.
    :param password: Optional SSH password.  Defaults to ``DNAC_PASS``.
    :param kwargs: Additional keyword arguments passed to
        :class:`netmiko.ConnectHandler`.
    :returns: A Netmiko connection or ``None`` on failure.
    """
    creds = _get_device_credentials()
    user = username or creds["username"]
    pwd = password or creds["password"]
    try:
        conn = ConnectHandler(
            device_type=device_type,
            host=host,
            username=user,
            password=pwd,
            **kwargs,
        )
        return conn
    except NetmikoTimeoutException:
        print(f"Timeout connecting to {host}")
        return None
    except NetmikoAuthenticationException:
        print(f"Authentication failure for {host}")
        return None
    except Exception as exc:  # pragma: no cover
        print(f"Unexpected error connecting to {host}: {exc}")
        return None


def send_config_commands(connection: ConnectHandler, commands: Iterable[str]) -> str:
    """Send a list of configuration commands to a device.

    Uses Netmiko's :meth:`~netmiko.BaseConnection.send_config_set` to
    enter configuration mode, execute each command and exit.  Returns
    the combined output from the device.  Any exceptions raised by
    Netmiko will propagate to the caller.

    :param connection: An active Netmiko connection obtained via
        :func:`connect_device`.
    :param commands: An iterable of CLI commands as strings.
    :returns: The command output concatenated into a single string.
    :raises Exception: If the command execution fails.
    """
    if not connection:
        raise ValueError("Connection object must not be None")
    output = connection.send_config_set(list(commands))
    return output