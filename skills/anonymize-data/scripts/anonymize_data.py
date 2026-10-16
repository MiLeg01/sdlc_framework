#!/usr/bin/env python3
"""Apply deterministic field-scoped anonymization rules to JSON, JSONL, or CSV data."""

from __future__ import annotations

import argparse
import csv
import hashlib
import hmac
import io
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


DROP = object()
ALLOWED_STRATEGIES = {"drop", "redact", "stable-token"}


def digest_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_config(config: Any) -> tuple[list[dict[str, Any]], bool, list[str]]:
    errors: list[str] = []
    if not isinstance(config, dict):
        return [], False, ["configuration root must be an object"]
    if config.get("schemaVersion") != "1.0.0":
        errors.append("schemaVersion must be 1.0.0")
    case_sensitive = config.get("caseSensitiveFields", True)
    if not isinstance(case_sensitive, bool):
        errors.append("caseSensitiveFields must be boolean")
        case_sensitive = True
    rules = config.get("rules")
    if not isinstance(rules, list) or not rules:
        return [], case_sensitive, errors + ["rules must be a non-empty array"]

    normalized_fields: dict[str, str] = {}
    seen_ids: set[str] = set()
    valid_rules: list[dict[str, Any]] = []
    for index, rule in enumerate(rules):
        label = f"rules[{index}]"
        if not isinstance(rule, dict):
            errors.append(f"{label} must be an object")
            continue
        rule_id = rule.get("id")
        if not isinstance(rule_id, str) or not rule_id.strip():
            errors.append(f"{label}.id is required")
            continue
        if rule_id in seen_ids:
            errors.append(f"duplicate rule id: {rule_id}")
        seen_ids.add(rule_id)
        fields = rule.get("fieldNames")
        if not isinstance(fields, list) or not fields or not all(isinstance(field, str) and field for field in fields):
            errors.append(f"{rule_id}: fieldNames must be a non-empty string array")
            continue
        strategy = rule.get("strategy")
        if strategy not in ALLOWED_STRATEGIES:
            errors.append(f"{rule_id}: strategy must be one of {sorted(ALLOWED_STRATEGIES)}")
        if "required" in rule and not isinstance(rule["required"], bool):
            errors.append(f"{rule_id}: required must be boolean")
        if strategy == "redact" and not isinstance(rule.get("replacement", "[REDACTED]"), str):
            errors.append(f"{rule_id}: replacement must be a string")
        if strategy == "stable-token":
            prefix = rule.get("prefix")
            if not isinstance(prefix, str) or not prefix or not prefix.replace("_", "").isalnum():
                errors.append(f"{rule_id}: stable-token requires an alphanumeric prefix")
        for field in fields:
            normalized = field if case_sensitive else field.casefold()
            if normalized in normalized_fields:
                errors.append(f"field {field} is assigned to both {normalized_fields[normalized]} and {rule_id}")
            normalized_fields[normalized] = rule_id
        valid_rules.append(rule)
    return valid_rules, case_sensitive, errors


def load_data(path: Path) -> tuple[str, Any, list[str] | None]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return "json", read_json(path), None
    if suffix in {".jsonl", ".ndjson"}:
        records = []
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid JSONL line {line_number}: {exc.msg}") from exc
        return "jsonl", records, None
    if suffix == ".csv":
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise ValueError("CSV header is required")
            return "csv", list(reader), list(reader.fieldnames)
    raise ValueError("input format must be .json, .jsonl, .ndjson, or .csv")


def rule_index(rules: list[dict[str, Any]], case_sensitive: bool) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for rule in rules:
        for field in rule["fieldNames"]:
            result[field if case_sensitive else field.casefold()] = rule
    return result


def token_for(value: Any, prefix: str, key: bytes) -> str:
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    token = hmac.new(key, canonical, hashlib.sha256).hexdigest()[:16].upper()
    return f"{prefix}_{token}"


def transform(value: Any, rules_by_field: dict[str, dict[str, Any]], case_sensitive: bool,
              key: bytes | None, counts: dict[str, int]) -> Any:
    if isinstance(value, list):
        return [transform(item, rules_by_field, case_sensitive, key, counts) for item in value]
    if not isinstance(value, dict):
        return value
    result: dict[str, Any] = {}
    for field, child in value.items():
        lookup = field if case_sensitive else field.casefold()
        rule = rules_by_field.get(lookup)
        if rule is None:
            result[field] = transform(child, rules_by_field, case_sensitive, key, counts)
            continue
        counts[rule["id"]] += 1
        strategy = rule["strategy"]
        if strategy == "drop":
            replacement = DROP
        elif strategy == "redact":
            replacement = rule.get("replacement", "[REDACTED]")
        else:
            if key is None:
                raise ValueError(f"{rule['id']}: stable-token requires --key-file")
            replacement = token_for(child, rule["prefix"], key)
        if replacement is not DROP:
            result[field] = replacement
    return result


def render_data(kind: str, value: Any, csv_fields: list[str] | None) -> bytes:
    if kind == "json":
        return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if kind == "jsonl":
        return ("\n".join(json.dumps(item, ensure_ascii=False, sort_keys=True) for item in value) + "\n").encode("utf-8")
    rows: list[dict[str, Any]] = value
    retained = [field for field in (csv_fields or []) if any(field in row for row in rows)]
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=retained, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
        Path(temporary).replace(path)
    except Exception:
        Path(temporary).unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("config", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--key-file", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        input_bytes = args.input.read_bytes()
        config_bytes = args.config.read_bytes()
        config = json.loads(config_bytes)
        rules, case_sensitive, errors = validate_config(config)
        if errors:
            raise ValueError("; ".join(errors))
        key = args.key_file.read_bytes().strip() if args.key_file else None
        if args.key_file and not key:
            raise ValueError("key file must not be empty")
        kind, data, csv_fields = load_data(args.input)
        counts = {rule["id"]: 0 for rule in rules}
        transformed = transform(data, rule_index(rules, case_sensitive), case_sensitive, key, counts)
        missing = [rule["id"] for rule in rules if rule.get("required", False) and counts[rule["id"]] == 0]
        if missing:
            raise ValueError("; ".join(f"required rule {rule_id} matched 0 values" for rule_id in missing))
        output_bytes = render_data(kind, transformed, csv_fields)
        report = {
            "schemaVersion": "1.0.0",
            "status": "dry-run" if args.dry_run else "ok",
            "format": kind,
            "inputDigest": digest_bytes(input_bytes),
            "configDigest": digest_bytes(config_bytes),
            "ruleMatches": {key: counts[key] for key in sorted(counts)},
            "totalMatches": sum(counts.values()),
            "outputDigest": digest_bytes(output_bytes),
        }
        if args.dry_run:
            sys.stdout.write(json.dumps(report, sort_keys=True) + "\n")
            return 0
        if args.output is None:
            raise ValueError("--output is required unless --dry-run is used")
        if args.output.resolve() == args.input.resolve():
            raise ValueError("output must not overwrite input")
        if args.report and args.report.resolve() in {args.input.resolve(), args.output.resolve()}:
            raise ValueError("report path must be distinct from input and output")
        atomic_write(args.output, output_bytes)
        if args.report:
            atomic_write(args.report, (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8"))
        sys.stdout.write(json.dumps(report, sort_keys=True) + "\n")
        return 0
    except (OSError, json.JSONDecodeError, ValueError, csv.Error) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
