#!/usr/bin/env python3
"""Executable regressions for hierarchical evidence-backed project memory."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "maintain-project-memory" / "scripts" / "manage_project_memory.py"
SPEC = importlib.util.spec_from_file_location("manage_project_memory", SCRIPT)
assert SPEC and SPEC.loader
memory = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(memory)


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class ProjectMemoryScenarios(unittest.TestCase):
    @staticmethod
    def project() -> dict:
        return {
            "goal": "Understand and modernize the mixed legacy estate",
            "mode": "legacy-migration",
            "source_roots": ["client_input"],
            "protected_paths": ["client_input"],
            "target_technology": ["Java 21", "Spring Boot"],
            "languages": ["COBOL", "PL/I", "Java"],
            "architecture": "Mainframe request path with a Java API boundary",
            "lifecycle_stage": "analysis",
            "major_decisions": ["DEC-001"],
            "critical_blockers": [],
            "next_action": "Analyze COBOL request flow",
        }

    def test_initializes_hierarchy_merges_verified_knowledge_and_builds_bounded_context(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "analysis/cobol").mkdir(parents=True)
            (root / "analysis/java").mkdir(parents=True)
            (root / "client_input").mkdir()
            cobol_source = "IDENTIFICATION DIVISION.\nPROGRAM-ID. BAQHRBKZ.\n"
            java_source = "final class Resource {}\n"
            (root / "client_input/BAQHRBKZ.cbl").write_text(cobol_source, encoding="utf-8")
            (root / "client_input/Resource.java").write_text(java_source, encoding="utf-8")
            (root / "analysis/cobol/BAQHRBKZ.json").write_text("{}\n", encoding="utf-8")
            (root / "analysis/java/Resource.json").write_text("{}\n", encoding="utf-8")

            initialized = memory.initialize_memory(root, self.project())
            self.assertEqual(initialized["storage_root"], ".agent-commons/memory")

            result = memory.merge_proposal(root, {
                "schema_version": 1,
                "producer": {"id": "legacy-worker", "validation_status": "PASS"},
                "domains": [
                    {"id": "cobol", "summary": "COBOL request validation and host calls."},
                    {"id": "java", "summary": "Java resource and service boundary."},
                ],
                "records": [
                    {
                        "id": "COMP-COBOL-001",
                        "layer": "L2",
                        "domain": "cobol",
                        "entity": {"id": "BAQHRBKZ", "type": "COBOL_PROGRAM"},
                        "statement": "BAQHRBKZ validates the request before invoking the host service.",
                        "confidence": "VERIFIED",
                        "canonical_refs": [{"path": "analysis/cobol/BAQHRBKZ.json", "id": "FLOW-001"}],
                        "evidence": [{
                            "path": "client_input/BAQHRBKZ.cbl", "lines": "1-2", "sha256": digest(cobol_source),
                        }],
                        "relationships": [],
                        "tags": ["request", "validation"],
                    },
                    {
                        "id": "COMP-JAVA-001",
                        "layer": "L2",
                        "domain": "java",
                        "entity": {"id": "Resource", "type": "JAVA_CLASS"},
                        "statement": "Resource exposes the modernization API boundary.",
                        "confidence": "VERIFIED",
                        "canonical_refs": [{"path": "analysis/java/Resource.json", "id": "API-001"}],
                        "evidence": [{
                            "path": "client_input/Resource.java", "lines": "1", "sha256": digest(java_source),
                        }],
                        "relationships": [],
                        "tags": ["api"],
                    },
                ],
                "checkpoint": {
                    "id": "INVENTORY_COMPLETE", "status": "VALIDATED",
                    "canonical_refs": [{"path": "analysis/cobol/BAQHRBKZ.json"}],
                },
            })
            self.assertEqual(result["merged_records"], 2)
            self.assertEqual(memory.validate_memory(root)["status"], "PASS")

            package = memory.build_context_package(root, {
                "task": "analyze-cobol",
                "domains": ["cobol"],
                "entities": ["BAQHRBKZ"],
                "dependency_depth": 1,
                "max_records": 20,
            })

        self.assertEqual(package["project"]["goal"], "Understand and modernize the mixed legacy estate")
        self.assertEqual([item["id"] for item in package["domains"]], ["cobol"])
        self.assertEqual([item["id"] for item in package["records"]], ["COMP-COBOL-001"])
        self.assertEqual(package["selection"]["policy"], "MINIMUM_SUFFICIENT_VERIFIED_CONTEXT")
        self.assertIn("COMP-JAVA-001", package["selection"]["irrelevant_record_ids"])
        self.assertLess(package["metrics"]["package_bytes"], package["metrics"]["available_memory_bytes"])

    def test_context_retrieval_follows_dependencies_in_both_directions_and_bounds_checkpoints(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "analysis").mkdir()
            (root / "client_input").mkdir()
            (root / "analysis/program.json").write_text("{}\n", encoding="utf-8")
            (root / "analysis/flow.json").write_text("{}\n", encoding="utf-8")
            source = "PROGRAM-ID. REQUEST.\n"
            (root / "client_input/program.cbl").write_text(source, encoding="utf-8")
            memory.initialize_memory(root, self.project())
            records = [
                {
                    "id": "COMP-001", "layer": "L2", "domain": "cobol",
                    "entity": {"id": "REQUEST", "type": "COBOL_PROGRAM"},
                    "statement": "The program validates the request.", "confidence": "VERIFIED",
                    "canonical_refs": [{"path": "analysis/program.json"}],
                    "evidence": [{"path": "client_input/program.cbl", "sha256": digest(source)}],
                    "relationships": [], "tags": ["validation"],
                },
                {
                    "id": "FLOW-001", "layer": "L2", "domain": "flows",
                    "entity": {"id": "REQUEST-FLOW", "type": "BUSINESS_FLOW"},
                    "statement": "The flow depends on the request program.", "confidence": "VERIFIED",
                    "canonical_refs": [{"path": "analysis/flow.json"}],
                    "evidence": [{"path": "client_input/program.cbl", "sha256": digest(source)}],
                    "relationships": [{"type": "DEPENDS_ON", "target": "COMP-001"}], "tags": ["flow"],
                },
            ]
            for order in range(1, 6):
                memory.merge_proposal(root, {
                    "schema_version": 1,
                    "producer": {"id": "coordinator", "validation_status": "PASS"},
                    "domains": [
                        {"id": "cobol", "summary": "COBOL behavior."},
                        {"id": "flows", "summary": "Request flow."},
                    ],
                    "records": records if order == 1 else [],
                    "checkpoint": {"id": f"PHASE-{order}", "order": order, "status": "VALIDATED"},
                })
            package = memory.build_context_package(root, {
                "task": "review-program", "domains": ["cobol"], "entities": ["REQUEST"],
                "dependency_depth": 1, "max_records": 10, "max_checkpoints": 2,
            })

        self.assertEqual({record["id"] for record in package["records"]}, {"COMP-001", "FLOW-001"})
        self.assertEqual([checkpoint["id"] for checkpoint in package["checkpoints"]], ["PHASE-4", "PHASE-5"])
        self.assertEqual(package["metrics"]["included_checkpoints"], 2)

    def test_conflicting_worker_findings_are_preserved_for_synthesis(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "analysis").mkdir()
            (root / "client_input").mkdir()
            source = "PROGRAM-ID. BAQHRBKZ.\n"
            (root / "client_input/program.cbl").write_text(source, encoding="utf-8")
            (root / "analysis/program.json").write_text("{}\n", encoding="utf-8")
            memory.initialize_memory(root, self.project())

            base = {
                "id": "COMP-001", "layer": "L2", "domain": "cobol",
                "entity": {"id": "BAQHRBKZ", "type": "COBOL_PROGRAM"},
                "confidence": "VERIFIED",
                "canonical_refs": [{"path": "analysis/program.json", "id": "FLOW-001"}],
                "evidence": [{"path": "client_input/program.cbl", "lines": "1", "sha256": digest(source)}],
                "relationships": [], "tags": ["request"],
            }
            for producer, statement in (
                ("worker-a", "The program rejects an empty request."),
                ("worker-b", "The program accepts an empty request and substitutes a default."),
            ):
                memory.merge_proposal(root, {
                    "schema_version": 1,
                    "producer": {"id": producer, "validation_status": "PASS"},
                    "domains": [{"id": "cobol", "summary": "COBOL request behavior."}],
                    "records": [{**base, "statement": statement}],
                })

            record = json.loads((root / ".agent-commons/memory/entities/COMP-001.json").read_text())
            validation = memory.validate_memory(root)

        self.assertEqual(record["confidence"], "CONFLICTING")
        self.assertEqual(len(record["variants"]), 2)
        self.assertEqual(validation["status"], "PASS")

    def test_source_change_selectively_invalidates_direct_and_dependency_linked_memory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "analysis").mkdir()
            (root / "client_input").mkdir()
            old_cobol = "PROGRAM-ID. BAQHRBKZ.\n"
            new_cobol = old_cobol + "PROCEDURE DIVISION.\n"
            java = "final class Resource {}\n"
            (root / "client_input/program.cbl").write_text(old_cobol, encoding="utf-8")
            (root / "client_input/Resource.java").write_text(java, encoding="utf-8")
            for name in ("program.json", "flow.json", "java.json"):
                (root / "analysis" / name).write_text("{}\n", encoding="utf-8")
            memory.initialize_memory(root, self.project())
            memory.merge_proposal(root, {
                "schema_version": 1,
                "producer": {"id": "synthesis", "validation_status": "PASS"},
                "domains": [
                    {"id": "cobol", "summary": "COBOL behavior."},
                    {"id": "flows", "summary": "Cross-component flows."},
                    {"id": "java", "summary": "Java API behavior."},
                ],
                "records": [
                    {
                        "id": "COMP-COBOL", "layer": "L2", "domain": "cobol",
                        "entity": {"id": "BAQHRBKZ", "type": "COBOL_PROGRAM"},
                        "statement": "The program validates the request.", "confidence": "VERIFIED",
                        "canonical_refs": [{"path": "analysis/program.json"}],
                        "evidence": [{"path": "client_input/program.cbl", "sha256": digest(old_cobol)}],
                        "relationships": [], "tags": ["validation"],
                    },
                    {
                        "id": "FLOW-001", "layer": "L2", "domain": "flows",
                        "entity": {"id": "REQUEST-FLOW", "type": "BUSINESS_FLOW"},
                        "statement": "The flow depends on the COBOL validation result.", "confidence": "VERIFIED",
                        "canonical_refs": [{"path": "analysis/flow.json"}],
                        "evidence": [{"path": "client_input/Resource.java", "sha256": digest(java)}],
                        "relationships": [{"type": "DEPENDS_ON", "target": "COMP-COBOL"}], "tags": ["flow"],
                    },
                    {
                        "id": "COMP-JAVA", "layer": "L2", "domain": "java",
                        "entity": {"id": "Resource", "type": "JAVA_CLASS"},
                        "statement": "The resource exposes the API.", "confidence": "VERIFIED",
                        "canonical_refs": [{"path": "analysis/java.json"}],
                        "evidence": [{"path": "client_input/Resource.java", "sha256": digest(java)}],
                        "relationships": [], "tags": ["api"],
                    },
                ],
            })
            (root / "client_input/program.cbl").write_text(new_cobol, encoding="utf-8")
            result = memory.invalidate_memory(root, {
                "schema_version": 1,
                "fingerprint": "inventory-revision-2",
                "artifacts": [
                    {"id": "ART-CBL", "path": "client_input/program.cbl", "sha256": digest(new_cobol)},
                    {"id": "ART-JAVA", "path": "client_input/Resource.java", "sha256": digest(java)},
                ],
            })
            validation = memory.validate_memory(root)
            compacted = memory.compact_memory(root)

            records = {
                path.stem: json.loads(path.read_text())
                for path in (root / ".agent-commons/memory/entities").glob("*.json")
            }

        self.assertEqual(result["directly_invalidated_record_ids"], ["COMP-COBOL"])
        self.assertEqual(result["dependency_invalidated_record_ids"], ["FLOW-001"])
        self.assertEqual(records["COMP-COBOL"]["status"], "STALE")
        self.assertEqual(records["FLOW-001"]["status"], "STALE")
        self.assertEqual(records["COMP-JAVA"]["status"], "CURRENT")
        self.assertEqual(validation["status"], "PASS")
        self.assertEqual(compacted["preserved_records"], 3)

    def test_context_benchmark_reports_measured_bytes_and_no_fake_token_precision(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "analysis").mkdir()
            (root / "client_input").mkdir()
            cobol = "MOVE A TO B.\n" * 2000
            java = "final class Resource {}\n" * 1000
            (root / "client_input/program.cbl").write_text(cobol, encoding="utf-8")
            (root / "client_input/Resource.java").write_text(java, encoding="utf-8")
            (root / "analysis/program.json").write_text("{}\n", encoding="utf-8")
            (root / "analysis/java.json").write_text("{}\n", encoding="utf-8")
            memory.initialize_memory(root, self.project())
            memory.merge_proposal(root, {
                "schema_version": 1,
                "producer": {"id": "workers", "validation_status": "PASS"},
                "domains": [
                    {"id": "cobol", "summary": "COBOL details."},
                    {"id": "java", "summary": "Java details."},
                ],
                "records": [
                    {
                        "id": "COMP-CBL", "layer": "L2", "domain": "cobol",
                        "entity": {"id": "PROGRAM", "type": "COBOL_PROGRAM"},
                        "statement": "The program transforms the request.", "confidence": "VERIFIED",
                        "canonical_refs": [{"path": "analysis/program.json"}],
                        "evidence": [{"path": "client_input/program.cbl", "sha256": digest(cobol)}],
                        "relationships": [], "tags": ["transform"],
                    },
                    {
                        "id": "COMP-JAVA", "layer": "L2", "domain": "java",
                        "entity": {"id": "Resource", "type": "JAVA_CLASS"},
                        "statement": "The resource exposes the API.", "confidence": "VERIFIED",
                        "canonical_refs": [{"path": "analysis/java.json"}],
                        "evidence": [{"path": "client_input/Resource.java", "sha256": digest(java)}],
                        "relationships": [], "tags": ["api"],
                    },
                ],
            })
            package = memory.build_context_package(root, {
                "task": "implement-java-api", "domains": ["java"], "entities": ["Resource"],
                "dependency_depth": 0, "max_records": 10,
            })
            benchmark = memory.benchmark_context(
                root, package, ["client_input/program.cbl", "client_input/Resource.java"],
            )

        self.assertGreater(benchmark["repeated_context_reduction_percent"], 30)
        self.assertEqual(benchmark["measurement"], "UTF-8 bytes")
        self.assertNotIn("tokens", benchmark)

    def test_rebuild_regenerates_hot_summary_from_l0_without_summary_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            memory.initialize_memory(root, self.project())
            summary = root / ".agent-commons/memory/project-summary.md"
            summary.write_text("# Third-generation summary of a summary\n\nIncorrect.\n", encoding="utf-8")

            rebuilt = memory.rebuild_memory(root)
            text = summary.read_text(encoding="utf-8")

        self.assertEqual(rebuilt["status"], "REBUILT")
        self.assertIn("Understand and modernize the mixed legacy estate", text)
        self.assertNotIn("Third-generation", text)


if __name__ == "__main__":
    unittest.main()
