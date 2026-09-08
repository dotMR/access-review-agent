"""Milestone 1 eval runner: the three Orphaned fixtures, graded automatically.

Not the real eval harness yet (that's evals/cases/ in full, later
milestones) - this is the seed of it: run each fixture, diff findings
against expected.json, per SPEC.md's grading approach (deterministic
match, not vibes).
"""

import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

CASES = [
    "orphaned-clean-flag",
    "orphaned-clean-no-flag",
    "orphaned-contractor-scope-boundary",
]


def load_dotenv() -> None:
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def findings_set(findings: list[dict]) -> set[tuple]:
    return {
        (f["category"], f["system_name"], f["employee_id"])
        for f in findings
    }


async def run_case(case_name: str) -> bool:
    from access_review_agent.agent import run_orphaned_check
    from access_review_agent.grounding import GroundingError, validate_finding

    case_dir = Path(__file__).resolve().parent.parent / "evals" / "cases" / case_name
    expected = json.loads((case_dir / "expected.json").read_text())

    actual = await run_orphaned_check(case_dir)
    claimed_findings = actual.get("findings", [])

    # Grounding check first: an ungrounded (hallucinated) claim fails the
    # case outright, distinct from a plain expected-vs-actual mismatch -
    # this is the guardrail, not just a scoring detail.
    for finding in claimed_findings:
        try:
            validate_finding(finding, case_dir)
        except GroundingError as e:
            print(f"[FAIL] {case_name} — UNGROUNDED FINDING: {e}")
            return False

    expected_set = findings_set(expected["findings"])
    actual_set = findings_set(claimed_findings)

    passed = expected_set == actual_set
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {case_name} — {expected['description']}")
    if not passed:
        print(f"         expected: {expected_set}")
        print(f"         actual:   {actual_set}")
    return passed


async def main() -> None:
    load_dotenv()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("FAIL: ANTHROPIC_API_KEY not set (checked .env and environment)")
        sys.exit(1)

    results = [await run_case(case) for case in CASES]
    total, passed = len(results), sum(results)
    print(f"\n{passed}/{total} cases passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    asyncio.run(main())
