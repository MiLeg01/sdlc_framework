#!/usr/bin/env python3
"""Executable regressions for full, bounded, and resumable legacy analysis."""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "analyze-legacy-system" / "scripts" / "coordinate_analysis.py"
INVENTORY_SCRIPT = ROOT / "skills" / "inventory-codebase" / "scripts" / "inventory_codebase.py"
SPEC = importlib.util.spec_from_file_location("coordinate_analysis", SCRIPT)
assert SPEC and SPEC.loader
coordinator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(coordinator)


def artifact(identifier: str, path: str, language: str, kind: str = "source", disposition: str = "eligible") -> dict:
    return {
        "id": identifier,
        "path": path,
        "size": 10,
        "sha256": (identifier.lower() * 64)[:64],
        "kind": kind,
        "language": language,
        "disposition": disposition,
        "reason": kind,
    }


def inventory() -> dict:
    artifacts = [
        artifact("ART-CBL", "COBOL/finish/REQUEST.cbl", "cobol"),
        artifact("ART-PLI", "PLI/finish/REQUEST.pli", "pli"),
        artifact("ART-JAVA", "src/main/java/example/Resource.java", "java"),
        artifact("ART-COPY", "COPY/REQUEST.cpy", "copybook"),
        artifact("ART-API", "Api/src/main/api/service.yaml", "yaml", "configuration"),
        artifact("ART-BUILD", "build.gradle", "groovy", "build-descriptor"),
        artifact("ART-LICENSE", "LICENSE", "unknown", "other", "other"),
    ]
    return {
        "schema_version": 1,
        "root": "client_input",
        "fingerprint": "inventory-fingerprint",
        "counts": {"files": len(artifacts), "eligible": 6, "failures": 0},
        "artifacts": artifacts,
        "batches": [],
        "failures": [],
    }


def args(path: Path, **overrides: object) -> argparse.Namespace:
    values = {
        "inventory": path,
        "output": None,
        "mode": "full",
        "scope": [],
        "checkpoint": None,
        "requirements": "required",
        "specifications": "openspec",
        "dashboard": "enabled",
        "max_concurrency": 4,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def deep_packet(record: dict) -> dict:
    evidence_id = "EVID-" + record["artifact_id"]
    return {
        "status": "ANALYZED",
        "evidence_ids": [evidence_id],
        "reason": None,
        "depth_status": "DEEP_VERIFIED" if record["language_type"] in {"cobol", "pli", "java"} else "ANALYZED",
        "depth_dimensions": {
            name: {"status": "VERIFIED", "evidence_ids": [evidence_id]}
            for name in coordinator.DEPTH_DIMENSIONS
        },
        "semantic_counts": {
            "flows": 1, "business_rules": 1, "data_structures": 1, "dependencies": 1,
            "interfaces": 1, "defect_candidates": 0, "unknowns": 0,
        },
        "complexity": [{"metric": "coupling", "basis": "ASSESSED", "value": "medium"}],
    }


class AnalysisCoordinatorScenarios(unittest.TestCase):
    def write_inventory(self, root: Path) -> Path:
        path = root / "inventory.json"
        path.write_text(json.dumps(inventory()), encoding="utf-8")
        return path

    def test_full_is_default_and_accounts_for_the_entire_configured_denominator(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_inventory(Path(temporary))
            state = coordinator.plan_state(args(path))
        self.assertEqual((state["mode"], state["target_mode"]), ("FULL", "FULL"))
        self.assertEqual(state["coverage"]["summary"]["relevant"], 6)
        self.assertEqual(state["coverage"]["summary"]["unaccounted"], 6)
        self.assertEqual({item["status"] for item in state["coverage"]["artifacts"] if item["assigned_slice"]}, {"PENDING"})
        self.assertEqual(next(item for item in state["coverage"]["artifacts"] if item["artifact_id"] == "ART-LICENSE")["status"], "OUT-OF-SCOPE")
        first_stage = state["execution_plan"]["stages"][0]
        self.assertEqual(first_stage["mode"], "parallel")
        self.assertGreaterEqual(len(first_stage["task_ids"]), 3)
        cobol = next(item for item in state["slices"] if item["domain"] == "cobol")
        self.assertEqual(cobol["context_package"]["tool"], "manage-project-memory")
        self.assertIn("unrelated domains", cobol["context_package"]["irrelevant"])

    def test_workers_cannot_write_the_shared_dashboard(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            state = coordinator.plan_state(args(self.write_inventory(Path(temporary))))

        self.assertTrue(state["slices"])
        self.assertTrue(all("dashboard" in item["prohibited_writes"] for item in state["slices"]))

    def test_verified_depth_dimensions_require_evidence(self) -> None:
        dimensions = {
            name: {"status": "VERIFIED", "evidence_ids": ["EVID-1"]}
            for name in coordinator.DEPTH_DIMENSIONS
        }
        dimensions["behavior"]["evidence_ids"] = []
        update = {
            "status": "ANALYZED",
            "depth_status": "DEEP_VERIFIED",
            "depth_dimensions": dimensions,
            "semantic_counts": {name: 1 for name in coordinator.SEMANTIC_COUNT_FIELDS},
            "complexity": [{"metric": "coupling", "basis": "ASSESSED", "value": "medium"}],
        }

        with self.assertRaisesRegex(coordinator.AnalysisStateError, "lacks evidence"):
            coordinator._validate_depth_update({"artifact_id": "ART-CBL", "language_type": "cobol"}, update)

    def test_bounded_mode_requires_explicit_scope_and_records_every_exclusion(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_inventory(Path(temporary))
            with self.assertRaisesRegex(coordinator.AnalysisStateError, "requires at least one"):
                coordinator.plan_state(args(path, mode="bounded"))
            state = coordinator.plan_state(args(path, mode="bounded", scope=["COBOL"] ))
        selected = [item for item in state["coverage"]["artifacts"] if item["assigned_slice"]]
        excluded = [item for item in state["coverage"]["artifacts"] if item["artifact_id"] == "ART-PLI"][0]
        self.assertEqual([item["artifact_id"] for item in selected], ["ART-CBL"])
        self.assertEqual(excluded["status"], "OUT-OF-SCOPE")
        self.assertIn("bounded", excluded["reason"])

    def test_unaccounted_source_blocks_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_inventory(Path(temporary))
            state = coordinator.plan_state(args(path))
        with self.assertRaisesRegex(coordinator.AnalysisStateError, "relevant artifacts are unaccounted"):
            coordinator.validate_complete(state)

    def test_full_completion_requires_depth_as_well_as_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            state = coordinator.plan_state(args(self.write_inventory(Path(temporary))))
        for record in state["coverage"]["artifacts"]:
            if record["assigned_slice"]:
                record.update({
                    "status": "ANALYZED", "evidence_ids": ["EVID-" + record["artifact_id"]],
                    "depth_status": "PARTIAL", "reason": None,
                })
        for stage in state["lifecycle"].values():
            if stage["required"]:
                stage["status"] = "VALIDATED"
        coordinator.recompute(state)
        with self.assertRaisesRegex(coordinator.AnalysisStateError, "depth gate"):
            coordinator.validate_complete(state)

    def test_continue_preserves_validated_slices_and_schedules_only_remaining_work(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = self.write_inventory(root)
            checkpoint = coordinator.plan_state(args(path))
            cobol = next(item for item in checkpoint["slices"] if item["domain"] == "cobol")
            record = next(item for item in checkpoint["coverage"]["artifacts"] if item["artifact_id"] == "ART-CBL")
            record.update(deep_packet(record))
            cobol["status"] = "VALIDATED"
            coordinator.recompute(checkpoint)
            checkpoint_path = root / "checkpoint.json"
            checkpoint_path.write_text(json.dumps(checkpoint), encoding="utf-8")
            resumed = coordinator.plan_state(args(path, mode="continue", checkpoint=checkpoint_path))
        self.assertEqual(resumed["mode"], "CONTINUE")
        self.assertEqual(next(item for item in resumed["slices"] if item["domain"] == "cobol")["status"], "VALIDATED")
        pending_tasks = {task for stage in resumed["execution_plan"]["stages"] for task in stage["task_ids"]}
        self.assertNotIn("slice-cobol", pending_tasks)
        self.assertIn("slice-pli", pending_tasks)

    def test_changed_source_invalidates_prior_slice_and_downstream_fan_in(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = self.write_inventory(root)
            checkpoint = coordinator.plan_state(args(path))
            for record in checkpoint["coverage"]["artifacts"]:
                if record["assigned_slice"]:
                    record.update({"status": "ANALYZED", "evidence_ids": ["EVID-" + record["artifact_id"]], "reason": None})
            for item in checkpoint["slices"]:
                item["status"] = "VALIDATED"
            checkpoint["lifecycle"]["analysis_slices"]["status"] = "VALIDATED"
            checkpoint["lifecycle"]["synthesis"]["status"] = "VALIDATED"
            coordinator.recompute(checkpoint)
            checkpoint_path = root / "checkpoint.json"
            checkpoint_path.write_text(json.dumps(checkpoint), encoding="utf-8")
            changed = inventory()
            next(item for item in changed["artifacts"] if item["id"] == "ART-PLI")["sha256"] = "f" * 64
            path.write_text(json.dumps(changed), encoding="utf-8")
            resumed = coordinator.plan_state(args(path, mode="continue", checkpoint=checkpoint_path))
        self.assertEqual(next(item for item in resumed["coverage"]["artifacts"] if item["artifact_id"] == "ART-PLI")["status"], "PENDING")
        self.assertEqual(resumed["lifecycle"]["synthesis"]["status"], "PENDING")

    def test_changed_context_artifact_invalidates_dependent_language_slice(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = self.write_inventory(root)
            checkpoint = coordinator.plan_state(args(path))
            cobol = next(item for item in checkpoint["slices"] if item["domain"] == "cobol")
            record = next(item for item in checkpoint["coverage"]["artifacts"] if item["artifact_id"] == "ART-CBL")
            record.update(deep_packet(record))
            cobol["status"] = "VALIDATED"
            coordinator.recompute(checkpoint)
            checkpoint_path = root / "checkpoint.json"
            checkpoint_path.write_text(json.dumps(checkpoint), encoding="utf-8")
            changed = inventory()
            next(item for item in changed["artifacts"] if item["id"] == "ART-COPY")["sha256"] = "e" * 64
            path.write_text(json.dumps(changed), encoding="utf-8")
            resumed = coordinator.plan_state(args(path, mode="continue", checkpoint=checkpoint_path))

        resumed_cobol = next(item for item in resumed["slices"] if item["domain"] == "cobol")
        self.assertEqual(resumed_cobol["status"], "PENDING")
        self.assertIn("ART-COPY", resumed_cobol["context_artifact_ids"])

    def test_analyzed_executable_artifact_requires_semantic_depth_packet(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state = coordinator.plan_state(args(self.write_inventory(root)))
            target = next(item for item in state["slices"] if item["domain"] == "cobol")
            state_path = root / "state.json"
            state_path.write_text(json.dumps(state), encoding="utf-8")
            result_path = root / "result.json"
            result_path.write_text(json.dumps({
                "slice_id": target["id"],
                "input_fingerprint": target["input_fingerprint"],
                "output_path": "analysis/slices/slice-cobol.json",
                "validation": {"status": "PASS"},
                "artifacts": [{
                    "artifact_id": "ART-CBL", "status": "ANALYZED",
                    "evidence_ids": ["EVID-CBL"], "related_requirements": [],
                }],
            }), encoding="utf-8")
            record_args = argparse.Namespace(state=state_path, result=result_path, output=None)
            with self.assertRaisesRegex(coordinator.AnalysisStateError, "depth"):
                coordinator.record_slice(record_args)

            dimensions = {
                name: {"status": "VERIFIED", "evidence_ids": ["EVID-CBL"]}
                for name in (
                    "structure", "behavior", "data", "dependencies", "business_rules", "interfaces",
                    "error_handling", "non_functional", "maintainability", "migration_significance",
                )
            }
            result_path.write_text(json.dumps({
                "slice_id": target["id"],
                "input_fingerprint": target["input_fingerprint"],
                "output_path": "analysis/slices/slice-cobol.json",
                "validation": {"status": "PASS"},
                "artifacts": [{
                    "artifact_id": "ART-CBL", "status": "ANALYZED",
                    "evidence_ids": ["EVID-CBL"], "related_requirements": [],
                    "depth_status": "DEEP_VERIFIED", "depth_dimensions": dimensions,
                    "semantic_counts": {
                        "flows": 2, "business_rules": 3, "data_structures": 2, "dependencies": 1,
                        "interfaces": 1, "defect_candidates": 1, "unknowns": 1,
                    },
                    "complexity": [
                        {"metric": "logical-loc", "basis": "MEASURED", "value": 20},
                        {"metric": "coupling", "basis": "ASSESSED", "value": "medium"},
                    ],
                }],
            }), encoding="utf-8")
            recorded = coordinator.record_slice(record_args)

        artifact_record = next(item for item in recorded["coverage"]["artifacts"] if item["artifact_id"] == "ART-CBL")
        self.assertEqual(artifact_record["depth_status"], "DEEP_VERIFIED")
        self.assertEqual(artifact_record["semantic_counts"]["business_rules"], 3)
        self.assertEqual(recorded["coverage"]["summary"]["depth"]["deep_verified"], 1)

    def test_legacy_support_extensions_are_in_scope_inventory_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            source.mkdir()
            (source / "shared.inc").write_text("DCL VALUE CHAR(1);\n", encoding="utf-8")
            (source / "transactions.csd").write_text("DEFINE TRANSACTION(TEST)\n", encoding="utf-8")
            output = root / "inventory.json"
            subprocess.run([
                "python3", str(INVENTORY_SCRIPT), "--root", str(source), "--output", str(output), "--hash",
            ], check=True)
            payload = json.loads(output.read_text(encoding="utf-8"))
        by_path = {item["path"]: item for item in payload["artifacts"]}
        self.assertEqual((by_path["shared.inc"]["language"], by_path["shared.inc"]["disposition"]), ("pli-include", "eligible"))
        self.assertEqual((by_path["transactions.csd"]["language"], by_path["transactions.csd"]["disposition"]), ("cics-csd", "eligible"))

    def test_dashboard_stage_requires_validated_lifecycle_qa(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state = coordinator.plan_state(args(self.write_inventory(root)))
            for stage in ("analysis_slices", "synthesis", "requirements", "specifications"):
                state["lifecycle"][stage]["status"] = "VALIDATED"
            state_path = root / "state.json"
            state_path.write_text(json.dumps(state), encoding="utf-8")
            stage_args = argparse.Namespace(
                state=state_path, stage="dashboard", status="VALIDATED", evidence_id=[], reason=None,
                qa_result=None,
            )
            with self.assertRaisesRegex(coordinator.AnalysisStateError, "requires an independent lifecycle-QA"):
                coordinator.advance_stage(stage_args)
            qa_path = root / "dashboard-qa.json"
            qa_path.write_text(json.dumps({
                "status": "PASS", "lifecycle_status": "VALIDATED",
                "fingerprints": {"html": "h", "design": "d", "data": "x"},
            }), encoding="utf-8")
            stage_args.qa_result = qa_path
            advanced = coordinator.advance_stage(stage_args)
        self.assertEqual(advanced["lifecycle"]["dashboard"]["status"], "VALIDATED")
        self.assertEqual(advanced["lifecycle"]["dashboard"]["qa_fingerprints"]["html"], "h")

    def test_mixed_language_synthesis_requires_explicit_equivalence_and_unknowns_result(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state = coordinator.plan_state(args(self.write_inventory(root)))
            for record in state["coverage"]["artifacts"]:
                if not record["assigned_slice"]:
                    continue
                record.update(deep_packet(record))
            coordinator.recompute(state)
            state_path = root / "state.json"
            state_path.write_text(json.dumps(state), encoding="utf-8")
            stage_args = argparse.Namespace(
                state=state_path, stage="synthesis", status="VALIDATED", evidence_id=["EVID-SYN"], reason=None,
                qa_result=None, stage_result=None,
            )
            with self.assertRaisesRegex(coordinator.AnalysisStateError, "cross-language"):
                coordinator.advance_stage(stage_args)

            stage_result = root / "synthesis-result.json"
            stage_result.write_text(json.dumps({
                "status": "PASS",
                "cross_language_comparison": {
                    "status": "VALIDATED",
                    "languages": ["cobol", "pli", "java"],
                    "classifications": {
                        "EQUIVALENT": 2, "PARTIALLY_EQUIVALENT": 1, "DIVERGENT": 1,
                        "MISSING": 0, "UNKNOWN": 1,
                    },
                    "evidence_ids": ["EVID-X-LANG"],
                },
                "unknowns": [{"id": "UNKNOWN-001", "statement": "Production authentication is external."}],
                "defect_candidates": [{
                    "id": "DEFECT-001", "observed_behavior": "PL/I and COBOL differ on empty input.",
                    "decision": "DECISION_REQUIRED", "evidence_ids": ["EVID-X-LANG"],
                }],
            }), encoding="utf-8")
            stage_args.stage_result = stage_result
            advanced = coordinator.advance_stage(stage_args)

        synthesis = advanced["lifecycle"]["synthesis"]
        self.assertEqual(synthesis["status"], "VALIDATED")
        self.assertEqual(synthesis["cross_language_comparison"]["classifications"]["DIVERGENT"], 1)
        self.assertEqual(synthesis["unknown_count"], 1)
        self.assertEqual(synthesis["defect_candidate_count"], 1)


if __name__ == "__main__":
    unittest.main()
