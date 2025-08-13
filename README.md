# Network Automation

This project contains scripts, Ansible assets and pyATS tooling for
automating network operations with Cisco Catalyst (DNA) Center as the
source of truth.  The original repository has been refactored to
consolidate duplicated code into a reusable Python package (`na_utils`).

## Python package: `na_utils`

Reusable functions for authentication and API calls to Catalyst Center
live in `na_utils/dnac.py`.  Helpers for performing configuration
diffs are available in `na_utils/config_utils.py` and functions for
connecting to devices via Netmiko are in `na_utils/net_device.py`.
Import these in your own scripts instead of copying authentication
logic around.

## Scripts

The `scripts/python` directory contains standalone programs that make
use of `na_utils`.  Examples include:

| Script | Purpose |
|-------|---------|
| `config_diff.py` | Compare two configuration files using a unified diff. |
| `config_diff_v2.py` | Perform a structured diff using `ciscoconfparse2`. |
| `dco_config_push.py` | Remove legacy voice configuration from routers. |
| `get_device_list_v4.py` | Retrieve the device list from Catalyst Center and display reachability with colour coding. |
| `get_device_config_v2.py` | Connect to each reachable device and archive its running configuration locally. |
| `get_bldg_wireless_clients_v2.py` | Generate a report of wireless clients per building over the last 30 days. |
| `ert_rtr_change_RHN_connection.py` | Apply configuration changes to routers whose hostnames match a pattern (default `ERT`), removing RHN/MGCP call manager settings. |
| `put_lldp_config.py` | Disable LLDP on interfaces where CDP has been disabled. |

Each script accepts command‑line arguments for maximum flexibility and prints progress information to standard output.  Consult the docstrings in each file for details.

The `scripts/powershell` directory contains standalone programs that make use of the `scripts/powershell/Modules`. These are scripts are just basic API calls to Catalyst Center and should only be used if you are not authorized to download python. Examples include:

| Script | Purpose |
|-------|---------|
| `0-ReadMe.docx`        | Instructs how to use the powershell scripts. |
| `1-auth_env_setup.ps1` | Script to set up environmental variables to do API calls to DNAC|
| `Get_All_Avail.ps1`    | Gets device list from DNAC and color coding for reachability. (Similar to `get_device_list_v4.py`) |

## Ansible

The `ansible` directory follows the structure recommended by the
Ansible documentation.  A dynamic inventory script
(`inventories/production/dnac_inventory.py`) queries Catalyst Center
for devices and returns a JSON inventory grouped by family.  Sample
playbooks and roles are provided under `playbooks/` and `roles/`.

To run a playbook:

```bash
cd ansible
ansible-playbook playbooks/show_version.yml
```

Ensure you have created a `.env` file in the project root with your
Catalyst Center credentials as described in `.env.template`.

## pyATS

The `pyats` directory contains tooling to generate testbed files
dynamically.  Run `python scripts/generate_testbed.py` to produce a
YAML testbed under `testbeds/`.  Testbeds are ignored by git for
security; avoid committing real credentials to source control.

## Getting started

1. Copy `.env.template` to `.env` and fill in your credentials and base URL.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Generate an Ansible inventory:

   ```bash
   cd ansible
   ansible-inventory -i inventories/production/dnac_inventory.py --list
   ```

4. Generate a pyATS testbed:

   ```bash
   python pyats/scripts/generate_testbed.py
   ```

5. Run one of the scripts in `scripts/python` as needed.

For more information see the inline documentation in each module and
script.