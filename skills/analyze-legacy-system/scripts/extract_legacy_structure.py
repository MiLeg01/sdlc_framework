#!/usr/bin/env python3
"""Conservatively extract source structure with exact coordinates and explicit unknowns."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


LANGUAGE_BY_SUFFIX = {
    ".cbl": "cobol", ".cob": "cobol", ".cpy": "cobol",
    ".java": "java",
    ".sql": "sql", ".ddl": "sql",
}


def mask_comments(text: str, language: str) -> str:
    lines = text.splitlines()
    if language == "cobol":
        masked = []
        for line in lines:
            if len(line) > 6 and line[6:7] in {"*", "/"}:
                masked.append(" " * len(line))
            else:
                marker = line.find("*>")
                masked.append(line if marker < 0 else line[:marker] + " " * (len(line) - marker))
        return "\n".join(masked)

    result = list(text)
    in_block = False
    i = 0
    while i < len(result):
        if in_block:
            if i + 1 < len(result) and result[i] == "*" and result[i + 1] == "/":
                result[i] = result[i + 1] = " "
                in_block = False
                i += 2
            else:
                if result[i] != "\n":
                    result[i] = " "
                i += 1
            continue
        if i + 1 < len(result) and result[i] == "/" and result[i + 1] == "*":
            result[i] = result[i + 1] = " "
            in_block = True
            i += 2
            continue
        line_comment = (
            language == "java" and i + 1 < len(result) and result[i] == "/" and result[i + 1] == "/"
        ) or (language == "sql" and i + 1 < len(result) and result[i] == "-" and result[i + 1] == "-")
        if line_comment:
            while i < len(result) and result[i] != "\n":
                result[i] = " "
                i += 1
            continue
        i += 1
    return "".join(result)


def coordinate(text: str, start: int) -> tuple[int, int, str]:
    line = text.count("\n", 0, start) + 1
    line_start = text.rfind("\n", 0, start) + 1
    column = start - line_start + 1
    evidence = text[line_start:text.find("\n", start) if "\n" in text[start:] else len(text)].strip()
    return line, column, evidence[:240]


def add_matches(records: list[dict], original: str, masked: str, kind: str, pattern: str, group: int = 1) -> None:
    for match in re.finditer(pattern, masked, re.IGNORECASE | re.MULTILINE):
        name = match.group(group).strip()
        line, column, evidence = coordinate(original, match.start(group))
        records.append({"kind": kind, "name": name, "line": line, "column": column, "evidence": evidence})


def extract_cobol(original: str, masked: str) -> tuple[list[dict], list[dict]]:
    records: list[dict] = []
    unresolved: list[dict] = []
    add_matches(records, original, masked, "program", r"\bPROGRAM-ID\s*\.\s*([A-Z0-9_-]+)")
    add_matches(records, original, masked, "copybook", r"\bCOPY\s+([A-Z0-9_-]+)")
    add_matches(records, original, masked, "procedure-call", r"\bPERFORM\s+([A-Z0-9_-]+)")
    add_matches(records, original, masked, "static-call", r"\bCALL\s+['\"]([A-Z0-9_-]+)['\"]")
    add_matches(records, original, masked, "table-read", r"\b(?:FROM|JOIN)\s+([A-Z0-9_.-]+)")
    add_matches(records, original, masked, "table-write", r"\b(?:INSERT\s+INTO|UPDATE|DELETE\s+FROM)\s+([A-Z0-9_.-]+)")
    quoted_spans = [(m.start(), m.end()) for m in re.finditer(r"\bCALL\s+['\"][A-Z0-9_-]+['\"]", masked, re.I)]
    for match in re.finditer(r"\bCALL\s+([A-Z0-9_-]+)", masked, re.I):
        if any(start <= match.start() < end for start, end in quoted_spans):
            continue
        line, column, evidence = coordinate(original, match.start(1))
        unresolved.append({"kind": "dynamic-call", "expression": match.group(1), "line": line, "column": column, "evidence": evidence})
    return records, unresolved


def extract_java(original: str, masked: str) -> tuple[list[dict], list[dict]]:
    records: list[dict] = []
    unresolved: list[dict] = []
    add_matches(records, original, masked, "package", r"^\s*package\s+([\w.]+)\s*;")
    add_matches(records, original, masked, "import", r"^\s*import\s+(?:static\s+)?([\w.*]+)\s*;")
    add_matches(records, original, masked, "type", r"\b(?:class|interface|enum|record)\s+([A-Za-z_$][\w$]*)")
    add_matches(records, original, masked, "method", r"\b(?:public|protected|private|static|final|synchronized|abstract|native|default|\s)+[\w<>\[\],.?]+\s+([A-Za-z_$][\w$]*)\s*\([^;{}]*\)\s*(?:throws\s+[^\{]+)?\{")
    add_matches(records, original, masked, "constructor-call", r"\bnew\s+([A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*)\s*\(")
    add_matches(records, original, masked, "qualified-call", r"\b([A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)+)\s*\(")
    for pattern, label in ((r"\bClass\.forName\s*\(([^)]+)\)", "reflection-class"), (r"\b(?:Method|Constructor)\.invoke\s*\(([^)]+)\)", "reflection-invoke")):
        for match in re.finditer(pattern, masked, re.I):
            line, column, evidence = coordinate(original, match.start(1))
            unresolved.append({"kind": label, "expression": match.group(1).strip(), "line": line, "column": column, "evidence": evidence})
    return records, unresolved


def extract_sql(original: str, masked: str) -> tuple[list[dict], list[dict]]:
    records: list[dict] = []
    unresolved: list[dict] = []
    add_matches(records, original, masked, "routine", r"\bCREATE\s+(?:OR\s+REPLACE\s+)?(?:PROCEDURE|FUNCTION)\s+([\w.$#]+)")
    add_matches(records, original, masked, "routine-call", r"\bCALL\s+([\w.$#]+)")
    add_matches(records, original, masked, "table-read", r"\b(?:FROM|JOIN)\s+([\w.$#]+)")
    add_matches(records, original, masked, "table-write", r"\b(?:INSERT\s+INTO|UPDATE|DELETE\s+FROM|MERGE\s+INTO)\s+([\w.$#]+)")
    for match in re.finditer(r"\bEXECUTE\s+IMMEDIATE\s+(.+?)(?:;|$)", masked, re.I | re.M):
        line, column, evidence = coordinate(original, match.start(1))
        unresolved.append({"kind": "dynamic-sql", "expression": match.group(1).strip(), "line": line, "column": column, "evidence": evidence})
    return records, unresolved


def detect_language(path: Path, requested: str) -> str:
    if requested != "auto":
        return requested
    language = LANGUAGE_BY_SUFFIX.get(path.suffix.lower())
    if not language:
        raise ValueError(f"cannot infer language for {path}; pass --language")
    return language


def extract(path: Path, requested_language: str) -> dict:
    raw = path.read_bytes()
    original = raw.decode("utf-8", errors="replace")
    language = detect_language(path, requested_language)
    masked = mask_comments(original, language)
    extractor = {"cobol": extract_cobol, "java": extract_java, "sql": extract_sql}[language]
    records, unresolved = extractor(original, masked)
    key = lambda item: (item["line"], item["column"], item["kind"], item.get("name", item.get("expression", "")))
    return {
        "path": str(path),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "language": language,
        "encoding": "utf-8-or-replacement",
        "observations": sorted(records, key=key),
        "unresolved": sorted(unresolved, key=key),
        "limitations": [
            "lexical extraction only; observations require semantic validation",
            "dynamic dispatch, macros, preprocessing, generated code, and dialect-specific syntax may be incomplete",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--language", choices=("auto", "cobol", "java", "sql"), default="auto")
    args = parser.parse_args()
    try:
        files = [extract(path.resolve(), args.language) for path in sorted(args.paths, key=lambda value: str(value))]
    except (OSError, ValueError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"schema_version": 1, "files": files}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
