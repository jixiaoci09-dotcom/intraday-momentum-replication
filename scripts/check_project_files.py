#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


PIPELINE_VERSION = "boundary_corrected_v1"
SYMBOLS = ("es", "nq", "gc", "cl", "zn", "6e")
RETURN_COLUMNS = ("r_ONFH", "r_M", "r_SLH", "r_ROD", "r_LH")


def number(text: str) -> int:
    return int(text.replace(",", ""))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def table_lines_after_heading(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    try:
        start = lines.index(heading) + 1
    except ValueError:
        return []
    out = []
    for line in lines[start:]:
        if line.startswith("## ") and out:
            break
        if line.startswith("|"):
            out.append(line)
    return out


def row_counts(text: str) -> dict[str, int]:
    rows = {}
    for line in table_lines_after_heading(text, "## Row Counts"):
        match = re.match(r"\| ([^|]+) \| ([0-9,]+) \|", line)
        if match and match.group(1) not in {"Category", "---"}:
            rows[match.group(1).strip()] = number(match.group(2))
    return rows


def reason_counts(text: str) -> dict[str, int]:
    rows = {}
    for line in table_lines_after_heading(text, "## Exclusion Reasons"):
        match = re.match(r"\| `([^`]+)` \| ([0-9,]+) \|", line)
        if match:
            rows[match.group(1)] = number(match.group(2))
    return rows


def return_counts(text: str) -> dict[str, int]:
    rows = {}
    for line in table_lines_after_heading(text, "## Included Return Summary"):
        match = re.match(r"\| `([^`]+)` \| ([0-9,]+) \|", line)
        if match:
            rows[match.group(1)] = number(match.group(2))
    return rows


def check_daily_notes(errors: list[str]) -> None:
    root = Path("data/manifests")
    for symbol in SYMBOLS:
        summary_path = root / f"{symbol}_daily_data_summary.json"
        notes_path = root / f"{symbol}_daily_data_notes.md"
        summary = json.loads(read(summary_path))
        notes = read(notes_path)

        rows = row_counts(notes)
        expected_rows = {
            "Candidate dates": summary["rows_total"],
            "Included dates": summary["rows_included"],
            "Excluded dates": summary["rows_excluded"],
            "Included replication dates": summary["included_by_segment"]["replication"],
            "Included OOS dates": summary["included_by_segment"]["oos"],
        }
        check(rows == expected_rows, f"{notes_path}: row counts do not match {summary_path}", errors)

        reasons = reason_counts(notes)
        check(
            reasons == summary["excluded_by_reason"],
            f"{notes_path}: exclusion reasons do not match {summary_path}",
            errors,
        )

        returns = return_counts(notes)
        expected_returns = {
            column: summary["return_summary_included"][column]["count"]
            for column in RETURN_COLUMNS
        }
        check(
            returns == expected_returns,
            f"{notes_path}: return counts do not match {summary_path}",
            errors,
        )
        check(
            summary.get("pipeline_version") == PIPELINE_VERSION,
            f"{summary_path}: unexpected pipeline_version",
            errors,
        )


def check_analysis_notes(errors: list[str]) -> None:
    for path in sorted(Path("data/manifests").glob("*_analysis_notes.md")):
        text = read(path)
        check('"data_version"' not in text, f"{path}: uses old data_version field", errors)
        check('"pipeline_version"' in text, f"{path}: missing pipeline_version field", errors)


def check_report_tables(errors: list[str]) -> None:
    checked_patterns = (
        "*_core_regression_summary.csv",
        "*_core_oos_r2.csv",
        "*_core_beta_difference_tests.csv",
    )
    for pattern in checked_patterns:
        for path in sorted(Path("reports/tables").glob(pattern)):
            with path.open(newline="", encoding="utf-8") as handle:
                header = next(csv.reader(handle))
            check("pipeline_version" in header, f"{path}: missing pipeline_version column", errors)
            check("data_version" not in header, f"{path}: uses old data_version column", errors)


def check_readme_and_scripts(errors: list[str]) -> None:
    readme = read(Path("README.md"))
    check("--approved-total 0" not in readme, "README.md: download example still uses --approved-total 0", errors)

    run_analysis = read(Path("scripts/run_analysis.py"))
    check('"data_version": PIPELINE_VERSION' not in run_analysis, "scripts/run_analysis.py: still writes data_version", errors)
    check('"pipeline_version": PIPELINE_VERSION' in run_analysis, "scripts/run_analysis.py: missing pipeline_version output", errors)


def main() -> int:
    errors: list[str] = []
    check_daily_notes(errors)
    check_analysis_notes(errors)
    check_report_tables(errors)
    check_readme_and_scripts(errors)

    if errors:
        print("Project file check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Project file check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
