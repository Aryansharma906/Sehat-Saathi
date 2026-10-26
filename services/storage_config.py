"""Shared location for local prototype data files.

Set ``SEHAT_DATA_DIR`` before starting the process to direct all local
record/database storage to a disposable or operator-selected directory.
"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def get_data_dir() -> Path:
    """Return configured local data directory, defaulting to the repo's data/."""
    configured = os.environ.get("SEHAT_DATA_DIR", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    return PROJECT_ROOT / "data"
