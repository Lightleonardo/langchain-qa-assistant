"""Ensure the repo root (where assistant.py lives) is importable from tests/.

Without this, pytest inserts only the tests/ directory on sys.path and
``import assistant`` fails with ModuleNotFoundError.
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
