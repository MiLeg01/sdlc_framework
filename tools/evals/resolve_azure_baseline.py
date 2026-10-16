#!/usr/bin/env python3
"""Resolve the latest accepted Azure baseline artifact or use the versioned bootstrap."""

from __future__ import annotations

import argparse
import io
import json
import os
import shutil
import tempfile
import urllib.parse
import zipfile
from pathlib import Path
from typing import Callable

from download_quality_history import MAX_ARCHIVE_BYTES, extract_zip_safely
from eval_common import validate_against_schema
from secure_http import azure_devops_origin, credentialed_download
from verify_azure_pipeline_access import AzureAccessError, request_json


Downloader = Callable[[str, str, str], bytes]
Requester = Callable[[str, str], dict]


def download_bytes(url: str, token: str, credential_origin: str) -> bytes:
    try:
        return credentialed_download(
            url,
            token,
            credential_origin=credential_origin,
            timeout=120,
            max_bytes=MAX_ARCHIVE_BYTES,
        )
    except Exception as exc:
        raise AzureAccessError("Azure baseline artifact download failed") from exc


def resolve_baseline(
    *,
    collection_uri: str,
    project: str,
    definition_id: str,
    token: str,
    bootstrap: Path,
    output: Path,
    requester: Requester = request_json,
    downloader: Downloader = download_bytes,
) -> dict:
    if not token:
        raise AzureAccessError("SYSTEM_ACCESSTOKEN is required")
    if not definition_id.isdigit() or int(definition_id) < 1:
        raise AzureAccessError("baseline pipeline definition ID must be a positive integer")
    try:
        azure_devops_origin(collection_uri)
    except ValueError as exc:
        raise AzureAccessError(str(exc)) from exc
    if not bootstrap.is_file():
        raise AzureAccessError(f"bootstrap baseline is missing: {bootstrap}")
    try:
        bootstrap_value = json.loads(bootstrap.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AzureAccessError("bootstrap baseline is invalid JSON") from exc
    bootstrap_errors = validate_against_schema(
        bootstrap_value,
        "evals/schemas/last-green-baseline.schema.json",
    )
    if bootstrap_errors or bootstrap_value.get("status") != "bootstrap":
        detail = "; ".join(bootstrap_errors) or "status must be bootstrap"
        raise AzureAccessError(f"bootstrap baseline violates the contract: {detail}")
    base = collection_uri.rstrip("/") + "/" + urllib.parse.quote(project, safe="")
    query = urllib.parse.urlencode([
        ("definitions", definition_id),
        ("branchName", "refs/heads/main"),
        ("statusFilter", "completed"),
        ("resultFilter", "succeeded"),
        ("queryOrder", "finishTimeDescending"),
        ("$top", "50"),
        ("api-version", "7.1"),
    ])
    builds = requester(f"{base}/_apis/build/builds?{query}", token).get("value", [])
    output.parent.mkdir(parents=True, exist_ok=True)
    selected_build_id = None
    download_url = None
    for build in builds:
        build_id = int(build["id"])
        artifact_query = urllib.parse.urlencode({"api-version": "7.1"})
        artifacts = requester(
            f"{base}/_apis/build/builds/{build_id}/artifacts?{artifact_query}",
            token,
        )
        values = artifacts.get("value")
        candidates = values if isinstance(values, list) else [artifacts]
        for artifact in candidates:
            if artifact.get("name") != "last-green-baseline":
                continue
            candidate_url = artifact.get("resource", {}).get("downloadUrl")
            if isinstance(candidate_url, str) and candidate_url:
                selected_build_id = build_id
                download_url = candidate_url
                break
        if download_url:
            break

    if download_url is None or selected_build_id is None:
        shutil.copyfile(bootstrap, output)
        return {
            "status": "PASS",
            "source": "bootstrap",
            "definition_id": int(definition_id),
            "build_id": None,
        }

    build_id = selected_build_id
    payload = downloader(download_url, token, collection_uri)
    with tempfile.TemporaryDirectory(prefix="agent-commons-baseline-") as temporary:
        extracted = Path(temporary)
        try:
            with zipfile.ZipFile(io.BytesIO(payload)) as archive:
                extract_zip_safely(archive, extracted)
        except zipfile.BadZipFile as exc:
            raise AzureAccessError(
                f"baseline artifact from build {build_id} is not a ZIP archive"
            ) from exc
        candidates = list(extracted.rglob("last-green-baseline.json"))
        if len(candidates) != 1:
            raise AzureAccessError(
                f"baseline artifact from build {build_id} contains {len(candidates)} baseline files"
            )
        try:
            baseline = json.loads(candidates[0].read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise AzureAccessError(f"baseline artifact from build {build_id} is invalid JSON") from exc
        errors = validate_against_schema(baseline, "evals/schemas/last-green-baseline.schema.json")
        if errors:
            raise AzureAccessError(
                f"baseline artifact from build {build_id} violates the schema: {'; '.join(errors)}"
            )
        if baseline.get("status") != "accepted":
            raise AzureAccessError(f"baseline artifact from build {build_id} is not accepted")
        accepted_run = baseline.get("accepted_run", {})
        if str(accepted_run.get("id")) != str(build_id):
            raise AzureAccessError(
                f"baseline artifact accepted run {accepted_run.get('id')} does not match build {build_id}"
            )
        shutil.copyfile(candidates[0], output)
    return {
        "status": "PASS",
        "source": "accepted-nightly",
        "definition_id": int(definition_id),
        "build_id": build_id,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection-uri", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--definition", required=True)
    parser.add_argument("--bootstrap", type=Path, default=Path("evals/baselines/v1.0.0.json"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = resolve_baseline(
            collection_uri=args.collection_uri,
            project=args.project,
            definition_id=args.definition,
            token=os.environ.get("SYSTEM_ACCESSTOKEN", ""),
            bootstrap=args.bootstrap,
            output=args.output,
        )
    except AzureAccessError as exc:
        print(f"Azure baseline resolution failed: {exc}")
        return 2
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
