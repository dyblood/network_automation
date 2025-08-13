# pyATS assets

This directory contains scripts and resources for building pyATS
testbeds and running tests against network devices.  The key
components are:

* **scripts/generate_testbed.py** – Generates a pyATS testbed YAML file
  using the list of devices returned from Cisco Catalyst Center via
  :mod:`na_utils.dnac`.  The resulting YAML file is stored under
  ``testbeds/`` and should **not** be checked into version control.

* **testbeds/** – Holds generated testbed files.  Because these files
  contain sensitive credentials, they are ignored by ``.gitignore``.  Use
  an external secrets manager or vault if you need to share testbeds.

* **results/** – (optional) Directory where pyATS stores logs and
  reports.  You can configure this in your test harness or leave it
  empty.

Follow the instructions in ``generate_testbed.py`` to create a testbed
for your environment.  Once generated you can use it with pyATS
commands such as ``pyats run job``.