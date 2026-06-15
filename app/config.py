"""
config.py — Central configuration: secret key, DB path, server port.
"""

import os
from pathlib import Path

# Repo root is the parent of the app/ package.
ROOT = Path(__file__).resolve().parent.parent

DB_PATH = ROOT / "subscriptions.db"

# In production, set SUBTRACKER_SECRET in the environment.
SECRET_KEY = os.environ.get("SUBTRACKER_SECRET", "sub-manager-secret-key-change-in-prod")

PORT = int(os.environ.get("SUBTRACKER_PORT", "5001"))
