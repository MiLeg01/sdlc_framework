#!/usr/bin/env python3
"""Audit a normalized delivery traceability CSV."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

CHAIN = ["source", "evidence", "rule", "gap", "requirement", "specification", "scenario", "implementation", "test", "result", "verification", "commit"]
MINIMUM = {
    "draft": ["source", "evidence", "requirement"],
    "approved": ["source", "evidence", "requirement", "specification", "scenario"],
    "implemented": ["source", "evidence", "requirement", "specification", "scenario", "implementation", "test", "result"],
    "verified": CHAIN,
    "complete": CHAIN,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("matrix", type=Path)
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    args = parser.parse_args()
    with args.matrix.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    findings = []
    seen = set()
    for number, row in enumerate(rows, start=2):
        record_id = (row.get("id") or f"ROW-{number}").strip()
        if record_id in seen:
            findings.append({"severity": "major", "code": "DUPLICATE_ID", "id": record_id, "row": number, "detail": "ID is not unique"})
        seen.add(record_id)
        status = (row.get("status") or "draft").strip().lower()
        required = MINIMUM.get(status, MINIMUM["draft"])
        for field in required:
            if not (row.get(field) or "").strip():
                severity = "critical" if status in {"verified", "complete"} else "major"
                findings.append({"severity": severity, "code": "MISSING_LINK", "id": record_id, "row": number, "detail": f"{status} record lacks {field}"})
        furthest = max((CHAIN.index(field) for field in CHAIN if (row.get(field) or "").strip()), default=-1)
        for index in range(furthest):
            field = CHAIN[index]
            if field in {"rule", "gap"}:
                continue
            if not (row.get(field) or "").strip():
                findings.append({"severity": "major", "code": "CHAIN_GAP", "id": record_id, "row": number, "detail": f"{field} is empty before a later lifecycle link"})
    result = {"status": "PASS" if not findings else "FAIL", "rows": len(rows), "findings": findings}
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"# Traceability audit\n\nStatus: **{result['status']}**  \nRows: {len(rows)}  \nFindings: {len(findings)}\n")
        for finding in findings:
            print(f"- **{finding['severity'].upper()} {finding['code']}** `{finding['id']}` row {finding['row']}: {finding['detail']}")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())

