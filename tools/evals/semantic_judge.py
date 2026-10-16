#!/usr/bin/env python3
"""Production repository-owned independent semantic judge entry point."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping, Optional

from semantic_provider import (
    AuthenticationError,
    ProviderError,
    ProviderProtocolError,
    ProviderTransientError,
    provider_from_environment,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_SCHEMA = ROOT / "evals" / "schemas" / "judge-output.schema.json"
THRESHOLDS = ROOT / "evals" / "contracts" / "thresholds.json"
EXPECTED_ASSERTION_FIELDS = ("expected_facts", "invariants", "required_sequence", "hard_assertions")


def environment_value(
    name: str,
    default: str = "",
    environment: Optional[Mapping[str, str]] = None,
) -> str:
    """Resolve an environment value while treating unresolved Azure macros as absent."""
    env = environment if environment is not None else os.environ
    resolved = env.get(name, default).strip()
    return default if resolved.startswith("$(") else resolved


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-config", action="store_true")
    return parser.parse_args()


def judge_instructions(
    valid_metrics: list[str],
    required_metrics: list[str],
    evidence_ids: list[str] | None = None,
) -> str:
    required_instruction = (
        "Return every required metric exactly once: " + ", ".join(required_metrics) + "."
        if required_metrics
        else "No scenario-specific quality metrics are required."
    )
    evidence_instruction = (
        "The evidence field must be exactly one of these supplied executor evidence IDs: "
        + ", ".join(evidence_ids)
        + ". Never invent, rename, or prefix an evidence ID."
        if evidence_ids
        else "No executor evidence IDs were supplied; do not invent evidence identifiers."
    )
    return "\n".join([
        "You are the independent Agent Commons semantic evaluator.",
        "Assess only the supplied executor result, transferred artifacts, evidence, rubric, and hidden expectations.",
        "Do not execute the capability again and do not reuse any executor confidence or self-score.",
        "Treat supplied deterministic findings as authoritative observed evidence for their stated checks, including successful tests and workspace-policy enforcement.",
        "Do not penalize visual_quality solely because browser QA is explicitly unavailable when the expected behavior is to report that limitation, no authored visual change is claimed, and deterministic visual-contract checks pass.",
        "Return every expected fact, invariant, required-sequence item, and hard assertion exactly once.",
        "Use the assertion ID string as assertion. Mark only PASS or FAIL.",
        evidence_instruction,
        "Return only metrics from this allowed set: " + ", ".join(valid_metrics) + ".",
        required_instruction,
        "Return JSON matching the supplied judge output schema.",
    ])


def constrained_output_schema(
    schema: dict[str, Any],
    request: dict[str, Any],
    evidence_ids: list[str],
) -> dict[str, Any]:
    """Bind schema-constrained judge strings to canonical request identifiers."""
    constrained = copy.deepcopy(schema)
    assertion_properties = constrained["properties"]["assertions"]["items"]["properties"]
    expected = request.get("expected", {})
    assertion_ids: list[str] = []
    for field in EXPECTED_ASSERTION_FIELDS:
        for value in expected.get(field, []):
            identifier = value.get("id") if isinstance(value, dict) else value
            text = str(identifier).strip()
            if text and text not in assertion_ids:
                assertion_ids.append(text)
    if assertion_ids:
        assertion_properties["assertion"]["enum"] = assertion_ids
    if evidence_ids:
        assertion_properties["evidence"]["enum"] = evidence_ids
    return constrained


def _performance(result: Any) -> dict[str, Any]:
    executor_model = environment_value("EVAL_EXECUTOR_MODEL")
    judge_model = environment_value("EVAL_JUDGE_MODEL") or result.model
    independence = (
        "different_configured_models"
        if executor_model and executor_model != judge_model
        else "same_configured_model"
    )
    return {
        "provider": result.provider,
        "model": result.model,
        "duration_seconds": round(result.duration_seconds, 6),
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
        "total_tokens": result.total_tokens,
        "judge_independence": independence,
    }


def bounded_judge_payload(
    request: dict[str, Any],
    workspace: Path,
    max_bytes: int,
) -> dict[str, Any]:
    """Attach only declared fixture/evidence content and verify transferred artifact hashes."""
    scenario_input = request.get("scenario", {}).get("input", {})
    evidence_paths = [
        str(item.get("source"))
        for item in request.get("evidence", [])
        if isinstance(item, dict) and item.get("source")
    ]
    source_paths = [str(path) for path in scenario_input.get("source_artifacts", [])]
    artifact_hashes = request.get("executor_artifacts", {}).get("files", {})
    artifact_paths = list(artifact_hashes) if isinstance(artifact_hashes, dict) else []
    declared_paths = list(dict.fromkeys([*evidence_paths, *source_paths, *artifact_paths]))
    contents: dict[str, dict[str, Any]] = {}
    remaining = max_bytes
    workspace_resolved = workspace.resolve()
    for relative in declared_paths:
        path = (workspace / relative).resolve()
        try:
            path.relative_to(workspace_resolved)
        except ValueError as exc:
            raise ProviderProtocolError(f"judge evidence path escapes workspace: {relative}") from exc
        if not path.is_file():
            raise ProviderProtocolError(f"judge evidence path is missing: {relative}")
        payload = path.read_bytes()
        expected_hash = artifact_hashes.get(relative) if isinstance(artifact_hashes, dict) else None
        if expected_hash and hashlib.sha256(payload).hexdigest() != expected_hash:
            raise ProviderProtocolError(f"executor artifact hash mismatch: {relative}")
        if remaining <= 0:
            contents[relative] = {"content": "", "truncated": True, "bytes": len(payload)}
            continue
        included = payload[:remaining]
        remaining -= len(included)
        contents[relative] = {
            "content": included.decode("utf-8", errors="replace"),
            "truncated": len(included) < len(payload),
            "bytes": len(payload),
        }
    return {"judge_input": request, "workspace_evidence": contents}


def main() -> int:
    args = parse_args()
    try:
        provider = provider_from_environment()
        if args.check_config:
            checked = provider.check_config(resolve_auth=True)
            print(json.dumps({"status": "available", **checked}, sort_keys=True))
            return 0
        request = json.load(sys.stdin)
        schema = json.loads(OUTPUT_SCHEMA.read_text(encoding="utf-8"))
        thresholds = json.loads(THRESHOLDS.read_text(encoding="utf-8"))
        metrics = sorted(thresholds.get("metrics", {}))
        required_metrics = sorted(str(value) for value in request.get("required_metrics", []))
        unknown_required = sorted(set(required_metrics) - set(metrics))
        if unknown_required:
            raise ProviderProtocolError(
                "judge request contains unknown required metrics: " + ", ".join(unknown_required)
            )
        max_bytes = int(environment_value("EVAL_JUDGE_MAX_EVIDENCE_BYTES", "500000"))
        if max_bytes < 1:
            raise ProviderProtocolError("EVAL_JUDGE_MAX_EVIDENCE_BYTES must be positive")
        payload = bounded_judge_payload(request, Path.cwd(), max_bytes)
        evidence_ids = [
            str(item["id"])
            for item in request.get("evidence", [])
            if isinstance(item, dict) and item.get("id")
        ]
        result = provider.judge(
            payload,
            constrained_output_schema(schema, request, evidence_ids),
            judge_instructions(metrics, required_metrics, evidence_ids),
        )
        output = dict(result.output)
        output["performance"] = {
            key: value for key, value in _performance(result).items() if value is not None
        }
        print(json.dumps({
            "event": "semantic_judge.completed",
            **output["performance"],
        }, sort_keys=True), file=sys.stderr)
        print(json.dumps(output, sort_keys=True))
        return 0
    except AuthenticationError as exc:
        print(f"authentication failure: {exc}", file=sys.stderr)
        return 78
    except ProviderTransientError as exc:
        print(f"infrastructure failure: {exc}", file=sys.stderr)
        return 75
    except ProviderProtocolError as exc:
        print(f"protocol failure: {exc}", file=sys.stderr)
        return 76
    except ProviderError as exc:
        print(f"provider failure: {exc}", file=sys.stderr)
        return 1
    except (json.JSONDecodeError, KeyError, TypeError, ValueError, OSError) as exc:
        print(f"protocol failure: {exc}", file=sys.stderr)
        return 76


if __name__ == "__main__":
    raise SystemExit(main())
