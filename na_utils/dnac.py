"""Helper functions for interacting with Cisco Catalyst Center.

This module centralises all interactions with Cisco DNA (Catalyst)
Center so that scripts in this repository can rely on a single
implementation.  Functions defined here load credentials from
environment variables at runtime and perform HTTP requests using the
`requests` library.  For security reasons the username and password
should be stored in a ``.env`` file that is *not* checked into
version control—see :mod:`dotenv` for details.  A template file
(``.env.template``) is provided to illustrate the required
variables.  Real credentials belong in a local ``.env`` file ignored
via ``.gitignore``.

The functions here are thin wrappers around the REST API exposed by
DNA Center.  They deliberately do not make assumptions about the
structure of the returned JSON beyond what is required, leaving
parsing up to calling code.  Should the API change in the future, the
modifications should largely be confined to this module.

Usage example:

    >>> from na_utils.dnac import get_device_list
    >>> devices = get_device_list()
    >>> for device in devices.get('response', []):
    ...     print(device['hostname'], device['managementIpAddress'])

Functions return dictionaries parsed from JSON responses.  If an
unexpected status code is returned, an exception is raised.

"""

from __future__ import annotations

import os
from typing import Dict, Any

import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Load environment variables from a .env file in the project root if present.
load_dotenv()

# Disable warnings for self‑signed certificates.  In production
# environments you should provide a proper CA bundle instead of
# disabling verification entirely.  See the requests documentation
# for details.
requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning
)


def _get_base_credentials() -> Dict[str, str]:
    """Return Catalyst Center base URL and credentials from environment.

    The function reads ``DNAC_BURL``, ``DNAC_USER`` and
    ``DNAC_PASS`` from environment variables.  It raises a
    :class:`RuntimeError` if any variable is missing, prompting the
    user to supply the missing configuration.

    :returns: A mapping containing the URL, username and password.
    :rtype: dict
    :raises RuntimeError: If required environment variables are not set.
    """
    base_url = os.getenv("DNAC_BURL")
    user = os.getenv("DNAC_USER")
    password = os.getenv("DNAC_PASS")
    missing = [name for name, value in {"DNAC_BURL": base_url, "DNAC_USER": user, "DNAC_PASS": password}.items() if not value]
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "Create a .env file based on the provided .env.template and set these values."
        )
    return {"base_url": base_url.rstrip("/"), "user": user, "password": password}


def get_auth_token(base_url: str | None = None, user: str | None = None, password: str | None = None) -> str:
    """Retrieve an authentication token from Catalyst Center.

    Catalyst Center uses a token based authentication mechanism.  The
    token is valid for a limited time and should be reused across
    multiple API calls until it expires.  This helper obtains a new
    token by sending a POST request to ``/dna/system/api/v1/auth/token``.

    :param base_url: Optional base URL of the Catalyst Center API.  If
        omitted the value from the environment will be used.
    :param user: Optional username.  Defaults to the value in the
        environment.
    :param password: Optional password.  Defaults to the value in
        the environment.
    :returns: A bearer token string.
    :raises RuntimeError: If credentials are not available.
    :raises requests.HTTPError: If the HTTP request fails.
    """
    creds = _get_base_credentials()
    url = (base_url or creds["base_url"]) + "/dna/system/api/v1/auth/token"
    auth = HTTPBasicAuth(user or creds["user"], password or creds["password"])
    response = requests.post(url, auth=auth, verify=False)
    response.raise_for_status()
    data: Dict[str, Any] = response.json()
    # The API returns a JSON object with the field 'Token'.  Raise if not present.
    token = data.get("Token")
    if not token:
        raise RuntimeError("Authentication token not found in response. Check credentials and base URL.")
    return token


def get_api_response(endpoint: str, base_url: str | None = None, token: str | None = None) -> Dict[str, Any]:
    """Make a GET request to a Catalyst Center API endpoint.

    This function constructs the full URL from the base URL and the
    provided endpoint, attaches the authentication token as a header
    and returns the parsed JSON.  If a token is not provided, a new
    one will be retrieved using :func:`get_auth_token`.

    :param endpoint: The path portion of the API after the base URL,
        e.g. ``/api/v1/network-device``.
    :param base_url: Optional base URL.  Defaults to the environment
        variable ``DNAC_BURL``.
    :param token: Optional authentication token.  If omitted, one
        will be fetched via :func:`get_auth_token`.
    :returns: Parsed JSON response as a dictionary.
    :raises requests.HTTPError: If the HTTP request fails.
    """
    creds = _get_base_credentials()
    full_url = (base_url or creds["base_url"]) + endpoint
    if not token:
        token = get_auth_token(base_url=creds["base_url"], user=creds["user"], password=creds["password"])
    headers = {"x-auth-token": token, "Content-Type": "application/json"}
    response = requests.get(full_url, headers=headers, verify=False)
    response.raise_for_status()
    return response.json()


def get_device_list(family: str | None = None, *, token: str | None = None, base_url: str | None = None) -> Dict[str, Any]:
    """Return the dictionary of network devices from Catalyst Center.

    The ``/api/v1/network-device`` endpoint returns a list of devices
    across all families.  If ``family`` is provided the list will be
    filtered to only include devices where the ``family`` field
    matches (case insensitive).  The returned dictionary is the
    unmodified JSON from the API except for filtering.

    :param family: Optional device family to filter on, e.g. ``Routers``
        or ``Switches and Hubs``.  If omitted no filtering occurs.
    :param token: Optional pre‑obtained token.
    :param base_url: Optional base URL.
    :returns: The JSON response from Catalyst Center, potentially with
        the ``response`` list filtered.
    """
    data = get_api_response("/api/v1/network-device", base_url=base_url, token=token)
    if family:
        devices = data.get("response", [])
        family_lower = family.lower()
        filtered = [d for d in devices if str(d.get("family", "")).lower() == family_lower]
        data["response"] = filtered
    return data


def to_ansible_inventory(device_json: Dict[str, Any], *, group_by_family: bool = True) -> Dict[str, Any]:
    """Transform a Catalyst Center device list into an Ansible inventory.

    Produces a dynamic inventory structure consumed by Ansible.  The
    resulting dictionary contains group definitions keyed by device
    family, a top‑level ``all`` group listing the groups as children,
    and a ``_meta`` section with per‑host variables.  Each host
    variable set includes at minimum the management IP address as
    ``ansible_host`` and the credentials loaded from the environment.

    :param device_json: A dictionary returned from
        :func:`get_device_list`.
    :param group_by_family: If true, hosts are grouped by their
        ``family`` attribute.  If false, all hosts are placed under
        ``ungrouped``.
    :returns: A dictionary ready to be serialized to JSON and consumed
        by Ansible as a dynamic inventory.
    """
    creds = _get_base_credentials()
    username = creds["user"]
    password = creds["password"]
    inventory: Dict[str, Any] = {"_meta": {"hostvars": {}}}
    all_children: list[str] = []
    for dev in device_json.get("response", []):
        hostname = dev.get("hostname") or dev.get("id")
        mgmt_ip = dev.get("managementIpAddress")
        family = (dev.get("family") or "ungrouped").replace(" ", "_").lower()
        # Initialize group if required
        if group_by_family:
            if family not in inventory:
                inventory[family] = {"hosts": []}
                all_children.append(family)
            inventory[family]["hosts"].append(hostname)
        else:
            if "ungrouped" not in inventory:
                inventory["ungrouped"] = {"hosts": []}
                all_children.append("ungrouped")
            inventory["ungrouped"]["hosts"].append(hostname)
        # Host specific variables
        inventory["_meta"]["hostvars"][hostname] = {
            "ansible_host": mgmt_ip,
            "ansible_user": username,
            "ansible_password": password,
            "ansible_network_os": (dev.get("softwareType", "iosxe").replace("-", "").lower() or "iosxe"),
        }
    inventory["all"] = {"children": all_children}
    return inventory


def to_pyats_testbed(device_json: Dict[str, Any], *, testbed_name: str = "generated_testbed") -> Dict[str, Any]:
    """Convert a device list into a pyATS testbed structure.

    The returned dictionary can be dumped to YAML via :mod:`yaml`
    into a file consumable by pyATS.  Each device entry includes
    credentials and connection information suitable for SSH.  In
    keeping with security best practices, credentials are pulled
    exclusively from the environment and not persisted in the source
    repository.  See `networkjourney blog`_ for guidance on securing
    testbed files.

    :param device_json: Device list returned from Catalyst Center.
    :param testbed_name: Name assigned to the testbed.
    :returns: A dictionary representing the pyATS testbed.

    .. _networkjourney blog: https://networkjourney.com (not accessible from here)
    """
    creds = _get_base_credentials()
    username = creds["user"]
    password = creds["password"]
    testbed: Dict[str, Any] = {
        "testbed": {"name": testbed_name},
        "devices": {},
    }
    for dev in device_json.get("response", []):
        hostname = dev.get("hostname") or dev.get("id")
        mgmt_ip = dev.get("managementIpAddress")
        os_type = dev.get("softwareType", "iosxe").replace("-", "").lower()
        dev_type = dev.get("family", "router").lower()
        testbed["devices"][hostname] = {
            "os": os_type,
            "type": dev_type,
            "connections": {
                "defaults": {
                    "class": "unicon.Unicon"
                },
                "ssh": {
                    "protocol": "ssh",
                    "ip": mgmt_ip,
                    "port": 22,
                }
            },
            "credentials": {
                "default": {
                    "username": username,
                    "password": password,
                }
            }
        }
    return testbed