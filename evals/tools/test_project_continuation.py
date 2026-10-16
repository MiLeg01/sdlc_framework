from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "continue-project" / "scripts" / "resolve_project_continuation.py"
SPEC = importlib.util.spec_from_file_location("resolve_project_continuation", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def manifest(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "scopes": ["development"],
        "requirements_required": False,
        "specification_method": "openspec",
        "specifications_required": True,
        "implementation_method": "test-driven-development",
        "implementation_phase": "active",
        "source_inventory_complete": True,
        "requires_user_choice": False,
        "dashboard_enabled": True,
    }
    value.update(overrides)
    return value


def state(*, requirements: list[dict] | None = None, specifications: list[dict] | None = None,
          relationships: list[dict] | None = None, project: dict | None = None) -> dict:
    return {
        "schema_version": 2,
        "project": project or {},
        "requirements": requirements or [],
        "specifications": specifications or [],
        "acceptance_criteria": [],
        "implementation_items": [],
        "tests": [],
        "evidence": [],
        "relationships": relationships or [],
    }


def requirement(identifier: str = "REQ-023", status: str = "approved", **extra: object) -> dict:
    return {"id": identifier, "title": identifier, "status": status, **extra}


def specification(identifier: str = "SPEC-007", readiness: str = "ready",
                  implementation_status: str = "not-started", validation_status: str = "PARTIAL",
                  **extra: object) -> dict:
    return {
        "id": identifier,
        "title": identifier,
        "status": "active",
        "readiness": readiness,
        "implementation_status": implementation_status,
        "validation_status": validation_status,
        **extra,
    }


class ProjectContinuationTests(unittest.TestCase):
    def test_manifest_loads_selected_canonical_skill_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".agent-commons.yaml").write_text(
                """project:
  scopes:
    - legacy-migration
commons:
  skills:
    - inventory-codebase
    - analyze-legacy-system
""",
                encoding="utf-8",
            )
            loaded = MODULE.load_manifest(root)
        self.assertEqual(loaded["selected_skills"], ["inventory-codebase", "analyze-legacy-system"])

    def test_capability_resolution_is_manifest_aware_and_non_automatic(self) -> None:
        configured = manifest(
            scopes=["legacy-migration"],
            requirements_required=True,
            source_inventory_complete=False,
            specifications_required=False,
            specification_method="none",
            implementation_phase="none",
            selected_skills=["inventory-codebase", "analyze-legacy-system"],
        )
        next_action = MODULE.resolve_next_action(configured, state())
        resolution = MODULE.describe_capability_resolution(configured, next_action)
        self.assertEqual(resolution["stable_id"], "analyze-legacy-system")
        self.assertTrue(resolution["selected_in_manifest"])
        self.assertEqual(resolution["source"], "canonical-agent-commons")
        self.assertFalse(resolution["automatic_execution"])

    def test_initialized_analysis_project_routes_to_analysis_entry_point(self) -> None:
        result = MODULE.resolve_next_action(
            manifest(scopes=["legacy-migration"], requirements_required=True,
                     source_inventory_complete=False, specifications_required=False,
                     specification_method="none", implementation_phase="none"),
            state(),
        )
        self.assertEqual(result["command"], "$analyze-legacy-system")

    def test_analysis_complete_requirements_missing(self) -> None:
        result = MODULE.resolve_next_action(
            manifest(scopes=["legacy-migration"], requirements_required=True,
                     specifications_required=False, specification_method="none", implementation_phase="none"),
            state(project={"analysis_status": "complete"}),
        )
        self.assertEqual(result["capability"], "derive-modernization-requirements")

    def test_top_level_full_analysis_projection_controls_lifecycle_routing(self) -> None:
        data = state(requirements=[requirement()], specifications=[specification(readiness="not-ready")],
                     relationships=[{"type": "specified-by", "source": "REQ-023", "target": "SPEC-007"}])
        data["analysis"] = {
            "target_mode": "FULL", "status": "COMPLETE",
            "coverage": {"relevant": 12, "accounted": 12, "unaccounted": 0, "blocked": 0},
        }
        result = MODULE.resolve_next_action(manifest(scopes=["legacy-migration"]), data)
        self.assertEqual(result["command"], "$review-openspec-change SPEC-007")

    def test_requirements_without_specs_route_to_specification(self) -> None:
        result = MODULE.resolve_next_action(manifest(requirements_required=True), state(
            requirements=[requirement()], project={"analysis_status": "complete"},
        ))
        self.assertEqual(result["command"], "$specify-openspec-change REQ-023")

    def test_requirement_with_ready_spec_uses_requirement_entry_point(self) -> None:
        data = state(
            requirements=[requirement()], specifications=[specification()],
            relationships=[{"type": "specified-by", "source": "REQ-023", "target": "SPEC-007"}],
        )
        subject = MODULE.resolve_subject(Path.cwd(), data, "REQ-023")
        result = MODULE.resolve_next_action(manifest(), data, subject)
        self.assertEqual(result["command"], "$implement-ready-slice REQ-023")
        self.assertIn("SPEC-007", result["reason"])

    def test_requirement_without_spec_never_routes_to_code(self) -> None:
        data = state(requirements=[requirement()])
        result = MODULE.resolve_next_action(manifest(), data, MODULE.resolve_subject(Path.cwd(), data, "REQ-023"))
        self.assertEqual(result["capability"], "specify-openspec-change")

    def test_requirement_with_multiple_specs_requires_choice(self) -> None:
        data = state(
            requirements=[requirement()],
            specifications=[specification(), specification("SPEC-011")],
            relationships=[
                {"type": "specified-by", "source": "REQ-023", "target": "SPEC-007"},
                {"type": "specified-by", "source": "REQ-023", "target": "SPEC-011"},
            ],
        )
        result = MODULE.resolve_next_action(manifest(), data, MODULE.resolve_subject(Path.cwd(), data, "REQ-023"))
        self.assertEqual(result["status"], "choice-required")
        self.assertEqual([item["id"] for item in result["choices"]], ["SPEC-007", "SPEC-011"])

    def test_requirement_with_multiple_specs_honors_prerequisite_order(self) -> None:
        data = state(
            requirements=[requirement()],
            specifications=[specification(), specification("SPEC-011", dependency_ids=["SPEC-007"])],
            relationships=[
                {"type": "specified-by", "source": "REQ-023", "target": "SPEC-007"},
                {"type": "specified-by", "source": "REQ-023", "target": "SPEC-011"},
            ],
        )
        result = MODULE.resolve_next_action(manifest(), data, MODULE.resolve_subject(Path.cwd(), data, "REQ-023"))
        self.assertEqual(result["command"], "$implement-ready-slice REQ-023")
        self.assertIn("SPEC-007", result["reason"])

    def test_ready_spec_routes_to_openspec_implementation(self) -> None:
        data = state(specifications=[specification()])
        result = MODULE.resolve_next_action(manifest(), data, MODULE.resolve_subject(Path.cwd(), data, "SPEC-007"))
        self.assertEqual(result["command"], "$implement-openspec-change SPEC-007")

    def test_implemented_spec_routes_to_verification(self) -> None:
        data = state(specifications=[specification(implementation_status="implemented")])
        result = MODULE.resolve_next_action(manifest(), data, MODULE.resolve_subject(Path.cwd(), data, "SPEC-007"))
        self.assertEqual(result["command"], "$verify-openspec-implementation SPEC-007")

    def test_everything_complete_has_no_required_action(self) -> None:
        data = state(specifications=[specification(implementation_status="validated", validation_status="PASS")])
        result = MODULE.resolve_next_action(manifest(), data)
        self.assertFalse(result["required"])
        self.assertIsNone(result["command"])

    def test_analysis_only_stops_after_requirements(self) -> None:
        result = MODULE.resolve_next_action(
            manifest(scopes=["legacy-migration"], requirements_required=True, specification_method="none",
                     specifications_required=False, implementation_phase="none"),
            state(requirements=[requirement()], project={"analysis_status": "complete"}),
        )
        self.assertFalse(result["required"])

    def test_migration_preparation_reaches_specs_but_not_code_without_spec(self) -> None:
        result = MODULE.resolve_next_action(
            manifest(scopes=["legacy-migration"], requirements_required=True, implementation_phase="planned"),
            state(requirements=[requirement()], project={"analysis_status": "complete"}),
        )
        self.assertEqual(result["capability"], "specify-openspec-change")

    def test_dependency_selects_only_unblocked_ready_spec(self) -> None:
        data = state(
            specifications=[
                specification("SPEC-001", implementation_status="validated", validation_status="PASS"),
                specification("SPEC-002", dependency_ids=["SPEC-001"]),
                specification("SPEC-003", dependency_ids=["SPEC-999"]),
            ],
        )
        result = MODULE.resolve_next_action(manifest(), data)
        self.assertEqual(result["command"], "$implement-openspec-change SPEC-002")

    def test_safe_openspec_path_resolves_specification(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "openspec/changes/customer-correction").mkdir(parents=True)
            data = state(specifications=[specification(source="openspec/changes/customer-correction")])
            resolved = MODULE.resolve_subject(root, data, "openspec/changes/customer-correction")
            self.assertEqual(resolved[0], "specification")
            self.assertEqual(resolved[1]["id"], "SPEC-007")

    def test_path_escape_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaises(MODULE.ContinuationError):
                MODULE.resolve_subject(root, state(), "../outside")

    def test_projection_keeps_dashboard_actions_synchronized(self) -> None:
        data = state(
            requirements=[requirement()], specifications=[specification()],
            relationships=[{"type": "specified-by", "source": "REQ-023", "target": "SPEC-007"}],
        )
        MODULE.apply_action_projection(manifest(), data)
        self.assertEqual(data["project"]["next_action"]["command"], "$implement-openspec-change SPEC-007")
        self.assertEqual(data["requirements"][0]["next_action"]["command"], "$implement-ready-slice REQ-023")
        self.assertEqual(data["specifications"][0]["next_action"]["command"], "$implement-openspec-change SPEC-007")

    def test_compact_memory_status_routes_stale_legacy_knowledge_to_selective_analysis(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            memory_root = root / ".agent-commons/memory"
            memory_root.mkdir(parents=True)
            (memory_root / "state.json").write_text(json.dumps({
                "schema_version": 1,
                "project": {"next_action": "Reanalyze changed COBOL validation flow"},
            }), encoding="utf-8")
            (memory_root / "index.json").write_text(json.dumps({
                "schema_version": 1,
                "storage_root": ".agent-commons/memory",
                "project_summary_path": ".agent-commons/memory/project-summary.md",
                "stale_record_count": 2,
                "conflicting_record_count": 1,
                "records": [
                    {"id": "COMP-001", "status": "STALE"},
                    {"id": "FLOW-002", "status": "CONFLICTING"},
                ],
                "checkpoints": [{"id": "INVENTORY_COMPLETE", "status": "VALIDATED"}],
                "source_inventory_fingerprint": "inventory-v2",
            }), encoding="utf-8")
            status = MODULE.load_memory_status(root)
            result = MODULE.resolve_next_action(
                manifest(scopes=["legacy-migration"], requirements_required=True),
                state(project={"analysis_status": "complete"}),
                memory_status=status,
            )

        self.assertTrue(status["available"])
        self.assertEqual(status["stale_record_ids"], ["COMP-001"])
        self.assertEqual(status["conflicting_record_ids"], ["FLOW-002"])
        self.assertEqual(status["latest_checkpoint"], "INVENTORY_COMPLETE")
        self.assertEqual(result["command"], "$analyze-legacy-system")
        self.assertIn("stale", result["reason"].lower())

    def test_enabled_lazy_memory_can_be_absent_before_first_substantial_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            status = MODULE.load_memory_status(Path(temporary))
        self.assertFalse(status["available"])
        self.assertEqual(status["stale_record_ids"], [])


if __name__ == "__main__":
    unittest.main()
