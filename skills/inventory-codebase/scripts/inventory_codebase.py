#!/usr/bin/env python3
"""Create a deterministic metadata inventory without interpreting behavior."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_PRUNE = {
    ".git", ".idea", ".venv", "node_modules", "target", "build", "dist", "out", "vendor",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".gradle", ".next",
}
SECRET_NAMES = {".env", ".npmrc", ".pypirc", "credentials", "credentials.json", "id_rsa", "id_ed25519"}
SECRET_SUFFIXES = {".key", ".pem", ".p12", ".pfx", ".jks", ".keystore"}
LANGUAGE = {
    ".cbl": "cobol", ".cob": "cobol", ".cpy": "copybook", ".pli": "pli", ".pl1": "pli",
    ".inc": "pli-include", ".csd": "cics-csd",
    ".java": "java", ".kt": "kotlin", ".cs": "csharp", ".vb": "vb", ".py": "python",
    ".js": "javascript", ".jsx": "javascript", ".ts": "typescript", ".tsx": "typescript",
    ".sql": "sql", ".xml": "xml", ".xsd": "xsd", ".wsdl": "wsdl", ".json": "json",
    ".yaml": "yaml", ".yml": "yaml", ".md": "markdown", ".html": "html", ".css": "css",
    ".sh": "shell", ".ps1": "powershell", ".tf": "terraform", ".sas": "sas", ".php": "php",
    ".gradle": "groovy",
}


def classify(path: Path) -> tuple[str, str]:
    name = path.name.lower()
    suffix = path.suffix.lower()
    language = LANGUAGE.get(suffix, "unknown")
    if name in {"pom.xml", "build.gradle", "build.gradle.kts", "package.json", "pyproject.toml", "requirements.txt"}:
        return "build-descriptor", language
    if suffix in {".jar", ".war", ".dll", ".exe", ".class", ".so", ".dylib"}:
        return "binary", language
    if suffix in {".zip", ".tar", ".gz", ".7z", ".rar"}:
        return "archive", language
    if suffix in {".yaml", ".yml", ".json", ".properties", ".ini", ".toml", ".conf"}:
        return "configuration", language
    if any(part.lower() in {"test", "tests", "spec", "specs", "fixtures"} for part in path.parts):
        return "test", language
    if language != "unknown":
        return "source", language
    return "other", language


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_secret(path: Path) -> bool:
    lower = path.name.lower()
    return lower in SECRET_NAMES or lower.startswith(".env.") or path.suffix.lower() in SECRET_SUFFIXES


def relative_failure_path(root: Path, filename: object) -> str:
    """Return a portable failure path without leaking an absolute source root."""
    if not filename:
        return "."
    path = Path(os.fsdecode(filename))
    if not path.is_absolute():
        path = root / path
    try:
        relative = Path(os.path.abspath(path)).relative_to(root)
    except (OSError, ValueError):
        return "."
    return relative.as_posix() or "."


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--hash", action="store_true", dest="with_hash")
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("--batch-size", type=int, default=50)
    parser.add_argument("--root-label", default=".", help="portable label stored in output; absolute root is not persisted")
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    if not root.is_dir():
        parser.error(f"root is not a directory: {root}")
    if args.batch_size < 1:
        parser.error("batch-size must be positive")

    prune = DEFAULT_PRUNE | set(args.exclude)
    records: list[dict[str, object]] = []
    failures: list[dict[str, str]] = []

    def record_walk_error(exc: OSError) -> None:
        failures.append({
            "path": relative_failure_path(root, exc.filename),
            "error": type(exc).__name__,
        })

    for current, dirs, files in os.walk(
        root, topdown=True, onerror=record_walk_error, followlinks=False
    ):
        current_path = Path(current)
        dirs[:] = sorted(d for d in dirs if d not in prune and not (current_path / d).is_symlink())
        for filename in sorted(files):
            absolute = current_path / filename
            relative = absolute.relative_to(root)
            if is_secret(relative):
                continue
            try:
                if absolute.is_symlink():
                    disposition, reason = "excluded", "symlink"
                    size, sha256 = 0, None
                else:
                    stat = absolute.stat()
                    kind, language = classify(relative)
                    disposition = "eligible" if kind in {"source", "configuration", "build-descriptor", "test"} else kind
                    reason = kind
                    size = stat.st_size
                    sha256 = digest_file(absolute) if args.with_hash else None
                kind, language = classify(relative)
                normalized = relative.as_posix()
                stable_id = "ART-" + hashlib.sha256(normalized.encode()).hexdigest()[:12].upper()
                records.append({"id": stable_id, "path": normalized, "size": size, "sha256": sha256,
                                "kind": kind, "language": language, "disposition": disposition, "reason": reason})
            except (OSError, PermissionError) as exc:
                failures.append({"path": relative.as_posix(), "error": type(exc).__name__})

    records.sort(key=lambda item: str(item["path"]))
    failures.sort(key=lambda item: (item["path"], item["error"]))
    batches = []
    eligible = [record["id"] for record in records if record["disposition"] == "eligible"]
    for index in range(0, len(eligible), args.batch_size):
        batches.append({"id": f"BATCH-{index // args.batch_size + 1:04d}", "artifact_ids": eligible[index:index + args.batch_size]})
    fingerprint_input = "\n".join(f"{r['path']}\t{r['sha256'] or r['size']}" for r in records)
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": args.root_label,
        "exclusions": sorted(prune),
        "fingerprint": hashlib.sha256(fingerprint_input.encode()).hexdigest(),
        "counts": {"files": len(records), "eligible": len(eligible), "failures": len(failures),
                   "kinds": dict(sorted(Counter(str(r["kind"]) for r in records).items()))},
        "artifacts": records,
        "batches": batches,
        "failures": failures,
    }
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
