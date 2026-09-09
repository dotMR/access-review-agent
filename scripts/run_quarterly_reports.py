"""Quarterly report entrypoint: rolls up the quarter's already-existing
Issue-tracker state into the two evidentiary reports per system plus the
aggregate (SPEC.md §6), and commits all six.

Called by .github/workflows/quarterly-audit.yml. No fresh detection here -
push-triggered runs already opened Issues throughout the quarter
(SPEC.md §2); this just reads and renders. GITHUB_WRITE_MODE stays unset
(dry-run, ADR-0007's default) until a deliberate decision to go live -
see development-plan.md's Milestone 5/7.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def main() -> None:
    from access_review_agent.orchestrator import generate_quarterly_reports

    period = os.environ.get("PERIOD")
    if not period:
        print("PERIOD env var not set (e.g. 2026-Q1)")
        sys.exit(1)

    repo_full_name = os.environ.get("REPO_FULL_NAME") or os.environ["GITHUB_REPOSITORY"]

    results = generate_quarterly_reports(repo_full_name, period)
    for name, result in results.items():
        status = "DRY RUN" if result.dry_run else "committed"
        print(f"{name}: {status} — {result.path}" + (f" ({result.commit_sha})" if result.commit_sha else ""))


if __name__ == "__main__":
    main()
