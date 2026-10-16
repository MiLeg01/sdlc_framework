#!/usr/bin/env python3
"""Detect a project's build ecosystems and recommend one mutation-testing adapter per ecosystem.

Reuses tooling the project already configures, adds nothing, and reports technologies with no
maintained mutation engine as NOT_SUPPORTED instead of silently omitting them. The adapter details
are documented in ``references/tool-adapters.md``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


IGNORED_DIRECTORIES = frozenset({
    ".git", ".hg", ".svn", "node_modules", "target", "build", "dist", "out", "bin", "obj",
    "__pycache__", ".venv", "venv", ".tox", ".gradle", ".idea", ".vs", "vendor", ".mypy_cache",
})

# Each ecosystem lists the manifests that prove it exists, the recommended adapter, and the
# markers that prove mutation tooling is already configured.
ECOSYSTEMS = (
    {
        "id": "jvm",
        "label": "JVM (Java, Kotlin, Scala)",
        "manifests": ("pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts"),
        "adapter": "pitest",
        "configured_markers": ("pitest-maven", "pitest-junit5-plugin", "info.solidsoft.pitest", "org.pitest"),
    },
    {
        "id": "dotnet",
        "label": ".NET (C#, F#, VB.NET)",
        "manifests": ("*.sln", "*.csproj", "*.fsproj", "*.vbproj"),
        "adapter": "stryker-net",
        "configured_markers": ("dotnet-stryker", "stryker-config.json", "StrykerMutator"),
    },
    {
        "id": "javascript",
        "label": "JavaScript and TypeScript",
        "manifests": ("package.json",),
        "adapter": "stryker-js",
        "configured_markers": ("@stryker-mutator/core", "stryker.conf.json", "stryker.config.mjs", "stryker.config.js"),
    },
    {
        "id": "python",
        "label": "Python",
        "manifests": ("pyproject.toml", "setup.cfg", "setup.py", "tox.ini", "requirements.txt"),
        "adapter": "mutmut",
        "configured_markers": ("mutmut", "cosmic-ray", "cosmic_ray"),
    },
    {
        "id": "rust",
        "label": "Rust",
        "manifests": ("Cargo.toml",),
        "adapter": "cargo-mutants",
        "configured_markers": ("cargo-mutants",),
    },
    {
        "id": "php",
        "label": "PHP",
        "manifests": ("composer.json",),
        "adapter": "infection",
        "configured_markers": ("infection/infection", "infection.json", "infection.json5"),
    },
    {
        "id": "ruby",
        "label": "Ruby",
        "manifests": ("Gemfile", "*.gemspec"),
        "adapter": "mutant",
        "configured_markers": ("mutant-rspec", "mutant-minitest", "\"mutant\"", "'mutant'"),
    },
)

# Source families with no maintained mutation engine. Presence is reported, never mutated.
UNSUPPORTED_SOURCES = (
    {"id": "cobol", "label": "COBOL", "suffixes": (".cbl", ".cob", ".cpy", ".cobol")},
    {"id": "pli", "label": "PL/I", "suffixes": (".pli", ".pl1")},
    {"id": "jcl", "label": "Job control language", "suffixes": (".jcl", ".prc", ".proc")},
    {"id": "natural-adabas", "label": "Natural or Adabas", "suffixes": (".nsp", ".nsn", ".nsg")},
    {"id": "rpg", "label": "RPG", "suffixes": (".rpgle", ".sqlrpgle", ".rpg")},
    {"id": "assembler", "label": "Assembler", "suffixes": (".asm", ".hlasm", ".mac")},
    {"id": "sql-schema", "label": "SQL schema and stored procedures", "suffixes": (".sql", ".ddl", ".prc")},
)


def relevant_files(root: Path) -> list[Path]:
    found: list[Path] = []
    for path in root.rglob("*"):
        if any(part in IGNORED_DIRECTORIES for part in path.relative_to(root).parts):
            continue
        if path.is_file():
            found.append(path)
    return found


def matches_manifest(name: str, pattern: str) -> bool:
    if pattern.startswith("*"):
        return name.endswith(pattern[1:])
    return name == pattern


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def detect(root: Path) -> dict:
    files = relevant_files(root)
    ecosystems: list[dict] = []
    for definition in ECOSYSTEMS:
        evidence = sorted(
            str(path.relative_to(root))
            for path in files
            if any(matches_manifest(path.name, pattern) for pattern in definition["manifests"])
        )
        if not evidence:
            continue
        # Only the ecosystem's own manifests are scanned for declared tooling, plus any file whose
        # name is itself a mutation-tool configuration marker.
        configured: list[str] = []
        for path in files:
            relative = str(path.relative_to(root))
            if path.name in definition["configured_markers"]:
                configured.append(relative)
                continue
            if not any(matches_manifest(path.name, pattern) for pattern in definition["manifests"]):
                continue
            content = read_text(path)
            for marker in definition["configured_markers"]:
                if marker in content:
                    configured.append(f"{relative}:{marker}")
        configured = sorted(set(configured))
        ecosystems.append({
            "id": definition["id"],
            "label": definition["label"],
            "evidence": evidence[:20],
            "evidence_count": len(evidence),
            "recommended_adapter": definition["adapter"],
            "already_configured": bool(configured),
            "configuration_evidence": configured[:20],
            "status": "SUPPORTED_CONFIGURED" if configured else "SUPPORTED_AVAILABLE",
            "action": (
                "reuse the existing configuration"
                if configured
                else f"add the minimum {definition['adapter']} configuration to the existing build"
            ),
        })

    unsupported: list[dict] = []
    for definition in UNSUPPORTED_SOURCES:
        evidence = sorted(
            str(path.relative_to(root))
            for path in files
            if path.suffix.lower() in definition["suffixes"]
        )
        if not evidence:
            continue
        unsupported.append({
            "id": definition["id"],
            "label": definition["label"],
            "evidence": evidence[:20],
            "evidence_count": len(evidence),
            "status": "NOT_SUPPORTED",
            "reason": "no maintained mutation engine exists for this source technology",
            "action": (
                "assess the migrated target implementation, the characterization harness, or an "
                "equivalent supported implementation instead, and record the compensating verification"
            ),
        })

    return {
        "schema_version": 1,
        "root": str(root),
        "ecosystems": ecosystems,
        "unsupported_sources": unsupported,
        "recommended": [
            {"ecosystem": entry["id"], "adapter": entry["recommended_adapter"], "status": entry["status"]}
            for entry in ecosystems
        ],
        "status": "SUPPORTED" if ecosystems else "NOT_SUPPORTED",
        "note": (
            "Detection proves which build systems exist. It does not install anything, does not verify "
            "that a tool version resolves, and does not choose the mutated scope."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="project root to inspect")
    parser.add_argument("--output", type=Path, help="write the detection JSON to this path")
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR not a directory: {root}", file=sys.stderr)
        return 1
    result = detect(root)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if result["status"] == "SUPPORTED" else 3


if __name__ == "__main__":
    raise SystemExit(main())
