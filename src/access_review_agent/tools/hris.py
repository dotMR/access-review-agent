"""Read and validate the HRIS file.

Per ADR-0001, HRIS is shared and non-isolated - available to every
system's detection logic unrestricted. For Tier 1 (deterministic)
categories this is called directly from plain Python (see detection/);
the SDK-tool-wrapped version used by reasoning-requiring categories lives
in reference/milestone-6-agent-sdk-patterns/.
"""

import csv
from pathlib import Path

REQUIRED_COLUMNS = {
    "employee_id",
    "name",
    "role",
    "start_date",
    "end_date",
    "status",
    "role_change_history",
}


def read_and_validate(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"HRIS file not found: {path}")

    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path}: missing required columns: {sorted(missing)}")
        return list(reader)
