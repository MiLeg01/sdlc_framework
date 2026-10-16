#!/usr/bin/env python3
"""Validate the prepared company-presentation demo checkpoints."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
DEFAULT_CONTRACT = HERE / "demo-checkpoints.json"


def source_fingerprint(root: Path) -> tuple[int, str]:
    source = root / "client_input"
    files = sorted(path for path in source.rglob("*") if path.is_file())
    digest = hashlib.sha256()
    for path in files:
        relative = path.relative_to(source).as_posix()
        file_digest = hashlib.sha256(path.read_bytes()).hexdigest()
        digest.update(f"{relative}\0{file_digest}\n".encode("utf-8"))
    return len(files), digest.hexdigest()


def validate_json(path: Path, errors: list[str]) -> None:
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid JSON: {path}: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("demo_root", type=Path)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    args = parser.parse_args()

    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    errors: list[str] = []
    expected_count = contract["source"]["file_count"]
    expected_fingerprint = contract["source"]["portable_fingerprint"]

    for stage_name, stage_contract in contract["stages"].items():
        stage = args.demo_root / stage_name
        if not stage.is_dir():
            errors.append(f"missing stage directory: {stage}")
            continue

        for relative in stage_contract.get("required", []):
            path = stage / relative
            if not path.exists():
                errors.append(f"{stage_name}: missing required path {relative}")

        for relative in stage_contract.get("prohibited", []):
            if (stage / relative).exists():
                errors.append(f"{stage_name}: later-stage path must be absent: {relative}")

        count, fingerprint = source_fingerprint(stage)
        if count != expected_count:
            errors.append(f"{stage_name}: source file count {count}, expected {expected_count}")
        if fingerprint != expected_fingerprint:
            errors.append(f"{stage_name}: source fingerprint {fingerprint}, expected {expected_fingerprint}")

        for relative in stage_contract.get("required", []):
            if relative.endswith(".json") and (stage / relative).is_file():
                validate_json(stage / relative, errors)

    if errors:
        print("Demo checkpoint validation: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Demo checkpoint validation: PASS")
    print(f"Demo: {contract['demo_id']}")
    print(f"Source files: {expected_count}")
    print(f"Source fingerprint: {expected_fingerprint}")
    print("Stages: 01-fresh, 02-initialized, 03-analyzed, 04-spec-ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
