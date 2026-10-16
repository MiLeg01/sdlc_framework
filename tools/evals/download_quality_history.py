#!/usr/bin/env python3
"""Download recent accepted Azure quality artifacts without exposing the access token."""

from __future__ import annotations

import argparse
import io
import json
import os
import stat
import urllib.parse
import urllib.request
from urllib.error import HTTPError, URLError
import zipfile
from pathlib import Path

from secure_http import azure_devops_origin, credentialed_download, secure_urlopen


MAX_ARCHIVE_BYTES = 50_000_000
MAX_EXPANDED_BYTES = 100_000_000
MAX_ARCHIVE_ENTRIES = 1000
MAX_COMPRESSION_RATIO = 100


def request_json(url: str, token: str) -> dict:
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with secure_urlopen(request, timeout=60) as response:
        return json.load(response)


def extract_zip_safely(archive: zipfile.ZipFile, destination: Path) -> None:
    root = destination.resolve()
    members = archive.infolist()
    if len(members) > MAX_ARCHIVE_ENTRIES:
        raise ValueError(f"archive exceeds {MAX_ARCHIVE_ENTRIES} entries")
    if sum(member.file_size for member in members) > MAX_EXPANDED_BYTES:
        raise ValueError(f"archive expands beyond {MAX_EXPANDED_BYTES} bytes")
    for member in members:
        mode = member.external_attr >> 16
        if stat.S_ISLNK(mode):
            raise ValueError(f"archive contains a symbolic link: {member.filename}")
        if member.file_size > 0 and member.file_size / max(member.compress_size, 1) > MAX_COMPRESSION_RATIO:
            raise ValueError(f"archive entry has unsafe compression ratio: {member.filename}")
        target = (root / member.filename).resolve()
        if root != target and root not in target.parents:
            raise ValueError(f"unsafe artifact path: {member.filename}")
    archive.extractall(root)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection-uri", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--definition", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-builds", type=int, default=7)
    parser.add_argument("--artifact", default="quality-aggregate")
    args = parser.parse_args()
    token = os.environ.get("SYSTEM_ACCESSTOKEN", "")
    if not token:
        raise SystemExit("SYSTEM_ACCESSTOKEN is required to download Azure quality history")
    try:
        azure_devops_origin(args.collection_uri)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    if not args.definition.isdigit() or int(args.definition) < 1:
        raise SystemExit("pipeline definition ID must be a positive integer")
    if args.max_builds < 1:
        raise SystemExit("--max-builds must be a positive integer")

    base = args.collection_uri.rstrip("/") + "/" + urllib.parse.quote(args.project, safe="")
    query = urllib.parse.urlencode({
        "definitions": args.definition,
        "branchName": "refs/heads/main",
        "statusFilter": "completed",
        "queryOrder": "finishTimeDescending",
        "$top": args.max_builds,
        "api-version": "7.1",
    })
    builds = request_json(f"{base}/_apis/build/builds?{query}", token).get("value", [])
    args.output.mkdir(parents=True, exist_ok=True)
    downloaded = 0
    for build in builds:
        build_id = str(build["id"])
        artifact_query = urllib.parse.urlencode({"artifactName": args.artifact, "api-version": "7.1"})
        try:
            artifact = request_json(
                f"{base}/_apis/build/builds/{build_id}/artifacts?{artifact_query}", token,
            )
        except (HTTPError, URLError):
            continue
        download_url = artifact.get("resource", {}).get("downloadUrl")
        if not download_url:
            continue
        try:
            payload = credentialed_download(
                download_url,
                token,
                credential_origin=args.collection_uri,
                timeout=120,
                max_bytes=MAX_ARCHIVE_BYTES,
            )
            with zipfile.ZipFile(io.BytesIO(payload)) as archive:
                extract_zip_safely(archive, args.output / build_id)
        except (HTTPError, URLError, zipfile.BadZipFile, ValueError):
            continue
        downloaded += 1
    print(json.dumps({"requested": args.max_builds, "downloaded": downloaded}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
