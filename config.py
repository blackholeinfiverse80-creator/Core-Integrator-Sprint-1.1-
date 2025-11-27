import os
from pathlib import Path

# Database configuration
DB_PATH = os.getenv("DB_PATH", "db/context.db")

# Ensure db directory exists
Path(DB_PATH).parent.mkdir(exist_ok=True)