#!/usr/bin/env python3
"""Verify read-only Azure pipeline definition, history, and baseline discovery access."""

from __future__ import annotations

import argparse
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Callable

from secure_http import azure_devops_origin, secure_urlopen


class AzureAccessError(RuntimeError):
    """Azure pipeline access or identity does not match the configured contract."""


Requester = Callable[[str, str], dict]


def request_json(url: str, token: str) -> dict:
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with secure_urlopen(request, timeout=60) as response:
            return json.load(response)
    except Exception as exc:
        raise AzureAccessError(f"Azure DevOps request failed for {url.split('?')[0]}: {exc}") from exc


def _normalized_yaml_path(value: str) -> str:
    return value.strip().lstrip("/")


def verify_pipeline_access(
    *,
    collection_uri: str,
    project: str,
    definition_id: str,
    expected_yaml_path: str,
    token: str,
    requester: Requester = request_json,
) -> dict:
    if not token:
        raise AzureAccessError("SYSTEM_ACCESSTOKEN is required")
    if not definition_id.isdigit() or int(definition_id) < 1:
        raise AzureAccessError("baseline pipeline definition ID must be a positive integer")
    try:
        azure_devops_origin(collection_uri)
    except ValueError as exc:
        raise AzureAccessError(str(exc)) from exc
    base = collection_uri.rstrip("/") + "/" + urllib.parse.quote(project, safe="")
    definition = requester(
        f"{base}/_apis/build/definitions/{definition_id}?api-version=7.1",
        token,
    )
    actual_yaml_path = _normalized_yaml_path(
        str(definition.get("process", {}).get("yamlFilename", ""))
    )
    expected = _normalized_yaml_path(expected_yaml_path)
    if actual_yaml_path != expected:
        raise AzureAccessError(
            f"definition {definition_id} uses {actual_yaml_path or 'no YAML path'}, expected {expected}"
        )

    def builds() -> dict:
        query_values: list[tuple[str, str]] = [
            ("definitions", definition_id),
            ("branchName", "refs/heads/main"),
            ("statusFilter", "completed"),
            ("queryOrder", "finishTimeDescending"),
            ("$top", "1"),
            ("api-version", "7.1"),
        ]
        query = urllib.parse.urlencode(query_values)
        return requester(f"{base}/_apis/build/builds?{query}", token)

    history = builds()
    return {
        "status": "PASS",
        "definition_id": int(definition_id),
        "definition_name": str(definition.get("name", "")),
        "yaml_path": actual_yaml_path,
        "history_builds_visible": int(history.get("count", len(history.get("value", [])))),
        "baseline_resolution": "latest successful Nightly artifact or versioned bootstrap",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection-uri", default=os.environ.get("SYSTEM_COLLECTIONURI", ""))
    parser.add_argument("--project", default=os.environ.get("SYSTEM_TEAMPROJECTID", ""))
    parser.add_argument(
        "--definition",
        default=os.environ.get("BASELINE_PIPELINE_DEFINITION_ID", ""),
    )
    parser.add_argument(
        "--expected-yaml-path",
        default=".azuredevops/commons-nightly-quality.yml",
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    token = os.environ.get("SYSTEM_ACCESSTOKEN", "")
    if not args.collection_uri or not args.project:
        raise SystemExit("Azure collection URI and project are required")
    try:
        report = verify_pipeline_access(
            collection_uri=args.collection_uri,
            project=args.project,
            definition_id=args.definition,
            expected_yaml_path=args.expected_yaml_path,
            token=token,
        )
    except AzureAccessError as exc:
        print(f"Azure pipeline access verification failed: {exc}")
        return 2
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
