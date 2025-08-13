import os
import sys
from pathlib import Path


# Ensure project root on path for na_utils
PROJECT_ROOT = Path(__file__).resolve().parents[2]

print(PROJECT_ROOT)

# print(PROJECT_ROOT)
# if str(PROJECT_ROOT) not in sys.path:
#     sys.path.insert(0, str(PROJECT_ROOT))