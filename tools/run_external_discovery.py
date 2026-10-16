#!/usr/bin/env python3
"""Run external capability discovery independently and persist compact project state."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from pathlib import Path

import external_capabilities


ROOT = Path(__file__).resolve().parent.parent


def atomic_json(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def source_policy(scope: str) -> tuple[list[str], bool]:
    if scope == "official":
        return ["OFFICIAL"], False
    if scope == "official-curated":
        return ["OFFICIAL", "CURATED"], False
    return [], scope == "all"


def run(args: argparse.Namespace) -> int:
    delay = float(os.environ.get("AGENT_COMMONS_EXTERNAL_DISCOVERY_DELAY_SECONDS", "0") or 0)
    if delay > 0:
        time.sleep(delay)
    trust, include_community = source_policy(args.source_scope)
    request_key = external_capabilities.discovery_request_key(
        args.topic, args.source_scope, args.sources, args.snapshot,
    )
    lease_path = args.lock or args.project_root / ".agent-commons" / "external-discovery.lock"
    lease = external_capabilities.DiscoveryLease(lease_path, request_key, args.lease_stale_seconds)
    if not lease.acquire():
        failure = external_capabilities._structured_failure("local", "external-discovery", "lock-contention")
        try:
            existing = json.loads(args.state.read_text(encoding="utf-8")) if args.state.is_file() else {}
        except (OSError, json.JSONDecodeError):
            existing = {}
        if not existing or existing.get("request_key") == request_key:
            atomic_json(args.state, {
                "schema_version": 2,
                "status": "failed",
                "completed_at": external_capabilities.utc_now(),
                "request_key": request_key,
                "gaps": args.gap,
                "candidate_count": 0,
                "failures": [failure],
                "completed_source_tiers": [],
                "source_tiers": {},
                "result_path": str(args.output.relative_to(args.project_root)),
                "safety": {"installed": False, "executed_external_code": False, "mutated_commons": False},
            })
        return 0
    search_args = argparse.Namespace(
        sources=args.sources,
        topic=args.topic,
        project_root=args.project_root,
        source=[],
        trust=trust,
        include_community=include_community,
        per_source_limit=3,
        community_limit=8,
        limit=20,
        max_workers=4,
        snapshot=args.snapshot,
        cache_dir=args.cache_dir,
        cache_ttl_seconds=args.cache_ttl_seconds,
        repository_cache_ttl_seconds=args.repository_cache_ttl_seconds,
        source_scope=args.source_scope,
    )
    try:
        result = external_capabilities.search(search_args)
        atomic_json(args.output, result)
        failures = [value for value in result.get("failures", []) if isinstance(value, dict)]
        status = str(result.get("status", "failed"))
        state = {
            "schema_version": 2,
            "status": status,
            "completed_at": external_capabilities.utc_now(),
            "request_key": request_key,
            "gaps": args.gap,
            "candidate_count": len([candidate for candidate in result.get("candidates", []) if isinstance(candidate, dict)]),
            "failures": failures,
            "completed_source_tiers": result.get("completed_source_tiers", []),
            "source_tiers": result.get("source_tiers", {}),
            "cache": result.get("cache", {}),
            "result_path": str(args.output.relative_to(args.project_root)),
            "safety": result.get("safety", {}),
        }
        atomic_json(args.state, state)
        return 0
    except (external_capabilities.ExternalCapabilityError, OSError, ValueError) as exc:
        failure = external_capabilities._structured_failure("local", "external-discovery", "workflow-failure")
        atomic_json(args.output, {
            "schema_version": 2,
            "status": "failed",
            "queries": external_capabilities.normalize_topics(args.topic),
            "candidates": [],
            "candidate_count": 0,
            "failures": [failure],
            "completed_source_tiers": [],
            "safety": {"installed": False, "executed_external_code": False, "mutated_commons": False},
        })
        atomic_json(args.state, {
            "schema_version": 2,
            "status": "failed",
            "completed_at": external_capabilities.utc_now(),
            "request_key": request_key,
            "gaps": args.gap,
            "candidate_count": 0,
            "failures": [failure],
            "completed_source_tiers": [],
            "source_tiers": {},
            "result_path": str(args.output.relative_to(args.project_root)),
            "safety": {"installed": False, "executed_external_code": False, "mutated_commons": False},
        })
        return 0
    finally:
        lease.release()


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--project-root", type=Path, required=True)
    result.add_argument("--state", type=Path, required=True)
    result.add_argument("--output", type=Path, required=True)
    result.add_argument("--topic", action="append", default=[])
    result.add_argument("--gap", action="append", default=[])
    result.add_argument("--source-scope", choices=("configured", "official", "official-curated", "all"), default="configured")
    result.add_argument("--sources", type=Path, default=ROOT / "external" / "sources.yaml")
    result.add_argument("--snapshot", type=Path)
    result.add_argument("--cache-dir", type=Path, default=ROOT / "external" / "cache" / "search")
    result.add_argument("--cache-ttl-seconds", type=int, default=1800)
    result.add_argument("--repository-cache-ttl-seconds", type=int, default=86400)
    result.add_argument("--lock", type=Path)
    result.add_argument("--lease-stale-seconds", type=int, default=1800)
    return result


def main() -> int:
    args = parser().parse_args()
    args.project_root = args.project_root.resolve()
    args.state = args.state.resolve()
    args.output = args.output.resolve()
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
