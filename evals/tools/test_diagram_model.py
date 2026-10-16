from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "skills" / "create-technical-diagram" / "scripts" / "validate_diagram_model.py"
SPEC = importlib.util.spec_from_file_location("validate_diagram_model", MODULE_PATH)
assert SPEC and SPEC.loader
diagram_model = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(diagram_model)


def base_model() -> dict[str, object]:
    return {
        "schema_version": 1,
        "diagram": {
            "type": "component-architecture",
            "title": "Synthetic service",
            "purpose": "Explain one verified dependency.",
            "audience": ["engineering"],
            "scope": "Selected service",
            "status": "CURRENT",
        },
        "evidence": [{"id": "E-1", "source": "src/service.py", "locator": "Service.run"}],
        "nodes": [
            {"id": "api", "label": "API", "kind": "component", "confidence": "VERIFIED", "evidence_ids": ["E-1"]},
            {"id": "store", "label": "Store", "kind": "database", "confidence": "VERIFIED", "evidence_ids": ["E-1"]},
        ],
        "relationships": [
            {"id": "writes", "source": "api", "target": "store", "label": "writes", "confidence": "VERIFIED", "evidence_ids": ["E-1"]}
        ],
        "views": [{"id": "overview", "title": "Overview", "node_ids": ["api", "store"], "relationship_ids": ["writes"]}],
    }


class DiagramModelTests(unittest.TestCase):
    def test_valid_evidence_backed_model_passes(self) -> None:
        errors, warnings, counts = diagram_model.validate(base_model())
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        self.assertEqual(counts["included_relationships"], 1)

    def test_verified_relationship_without_evidence_fails(self) -> None:
        model = base_model()
        model["relationships"][0]["evidence_ids"] = []
        errors, _, _ = diagram_model.validate(model)
        self.assertTrue(any("VERIFIED but has no evidence_ids" in error for error in errors))

    def test_unknown_relationship_cannot_render_as_normal_edge(self) -> None:
        model = base_model()
        relationship = model["relationships"][0]
        relationship.update({"confidence": "UNKNOWN", "evidence_ids": [], "annotation": "Runtime route unresolved"})
        errors, _, _ = diagram_model.validate(model)
        self.assertTrue(any("must set include=false" in error for error in errors))

    def test_relationship_endpoint_must_exist(self) -> None:
        model = base_model()
        model["relationships"][0]["target"] = "missing"
        errors, _, _ = diagram_model.validate(model)
        self.assertTrue(any("unknown target node" in error for error in errors))

    def test_large_model_requires_decomposition(self) -> None:
        model = base_model()
        model["relationships"] = []
        model["views"] = []
        model["nodes"] = [
            {"id": f"n-{index}", "label": f"Node {index}", "kind": "system", "confidence": "VERIFIED", "evidence_ids": ["E-1"]}
            for index in range(41)
        ]
        errors, _, _ = diagram_model.validate(model)
        self.assertTrue(any("large model requires overview/drilldown views" in error for error in errors))

    def test_large_model_passes_with_bounded_views(self) -> None:
        model = base_model()
        model["relationships"] = []
        model["nodes"] = [
            {"id": f"n-{index}", "label": f"Node {index}", "kind": "system", "confidence": "VERIFIED", "evidence_ids": ["E-1"]}
            for index in range(41)
        ]
        model["views"] = [
            {"id": "overview", "title": "Overview", "node_ids": [f"n-{index}" for index in range(20)], "relationship_ids": []},
            {"id": "drilldown", "title": "Drilldown", "node_ids": [f"n-{index}" for index in range(20, 41)], "relationship_ids": []},
        ]
        errors, _, _ = diagram_model.validate(model)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
