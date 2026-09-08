"""Read and validate one system's access data file.

Per ADR-0001, isolation is structural: callers pass their own system_name
and only ever read that system's file - there is no cross-system access
here. For Tier 1 (deterministic) categories this is called directly from
plain Python (see detection/); the SDK-tool-wrapped version used by
reasoning-requiring categories lives in reference/milestone-6-agent-sdk-patterns/.
"""

import csv
from pathlib import Path

REQUIRED_COLUMNS = {
    "employee_id",
    "system_name",
    "access_level",
    "granted_date",
    "approved_by",
    "last_used_date",
    "status",
    "provisioning_note",
}


def read_and_validate(path: Path, expected_system_name: str) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Access data file not found: {path}")

    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"{path}: missing required columns: {sorted(missing)}"
            )
        rows = list(reader)

    for row in rows:
        if row["system_name"] != expected_system_name:
            raise ValueError(
                f"{path}: row for {row['employee_id']} has system_name="
                f"{row['system_name']!r}, expected {expected_system_name!r} "
                "(same-file consistency check)"
            )
    return rows
