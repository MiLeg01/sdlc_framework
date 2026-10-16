from __future__ import annotations

import contextlib
import io
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "tools" / "sync_presentation.py"
SPEC = importlib.util.spec_from_file_location("sync_presentation", MODULE_PATH)
assert SPEC and SPEC.loader
sync_presentation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync_presentation)


class PresentationSyncTests(unittest.TestCase):
    @contextlib.contextmanager
    def fixture_repository(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for relative in (
                "skills",
                "agents",
                "tools",
                "templates",
                "archetypes/overlays",
                "adapters",
                "catalog",
                "presentation/assets",
                "evals/skills",
                "evals/agents",
                "evals/archetypes",
                "evals/external",
                "evals/initialization",
                "external/index",
            ):
                (root / relative).mkdir(parents=True, exist_ok=True)
            (root / "VERSION").write_text("0.0.0\n", encoding="utf-8")
            (root / "catalog/capabilities.yaml").write_text(
                json.dumps({"skills": {}, "agents": {}, "tools": {}, "templates": {}}),
                encoding="utf-8",
            )
            for relative, key in (
                ("evals/skills/scenarios.yaml", "skills"),
                ("evals/agents/scenarios.yaml", "agents"),
                ("evals/archetypes/scenarios.yaml", "archetypes"),
                ("evals/external/scenarios.yaml", "scenarios"),
                ("evals/initialization/scenarios.yaml", "scenarios"),
                ("evals/initialization/natural-language-scenarios.yaml", "scenarios"),
            ):
                (root / relative).write_text(f"{key}:\n", encoding="utf-8")
            (root / "external/sources.yaml").write_text('{"sources": []}\n', encoding="utf-8")
            (root / "external/index/capabilities.json").write_text(
                '{"candidates": []}\n', encoding="utf-8"
            )
            for identifier in (
                "initialize-project",
                "search-external-capabilities",
                "review-external-capability",
            ):
                self.write_skill(root, identifier)
            required_ids = (
                "network-search",
                "capability-graph",
                "network-reset",
                "capability-search",
                "capability-types",
                "capability-list",
                "capability-preview",
                "capability-source-preview",
                "diagram-capability-title",
            )
            controls = "".join(f'<div id="{identifier}"></div>' for identifier in required_ids)
            (root / "presentation/index.html").write_text(
                f'<!doctype html><html><body>{controls}<script src="assets/library-data.js"></script></body></html>',
                encoding="utf-8",
            )
            with mock.patch.multiple(
                sync_presentation,
                ROOT=root,
                CATALOG_PATH=root / "catalog/capabilities.yaml",
                VERSION_PATH=root / "VERSION",
                PRESENTATION_PATH=root / "presentation/index.html",
                DATA_PATH=root / "presentation/assets/library-data.js",
                STANDALONE_PATH=root / "presentation/agent-commons.html",
            ):
                yield root

    def write_skill(self, root: Path, identifier: str, extra: str = "") -> Path:
        path = root / "skills" / identifier / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "---\n"
            f"name: {identifier}\n"
            f"description: Perform {identifier} deterministically. Use for fixture verification. Do not use for unrelated work.\n"
            "---\n\n"
            f"# {identifier}\n\n{extra}\n",
            encoding="utf-8",
        )
        return path

    def write_agent(self, root: Path, identifier: str) -> Path:
        path = root / "agents" / f"{identifier}.yaml"
        path.write_text(
            json.dumps(
                {
                    "id": identifier,
                    "description": f"Review {identifier} evidence. Use for fixture review. Do not use for implementation.",
                    "responsibility": "Independent fixture review.",
                    "expected_inputs": ["evidence"],
                    "expected_outputs": ["findings"],
                }
            ),
            encoding="utf-8",
        )
        return path

    def test_payload_is_catalog_driven_and_exposes_promotion_gate(self) -> None:
        payload = sync_presentation.build_payload()
        catalog = json.loads((ROOT / "catalog" / "capabilities.yaml").read_text(encoding="utf-8"))
        skill_nodes = [entry for entry in payload["nodes"] if entry["type"] == "skill"]
        self.assertEqual(len(skill_nodes), len(catalog["skills"]))
        self.assertEqual(payload["stats"]["agents"], len(catalog["agents"]))
        self.assertEqual(payload["stats"]["tools"], len(catalog["tools"]))
        self.assertIn("skill:promote-to-commons", {entry["key"] for entry in skill_nodes})
        edges = {(edge["source"], edge["target"], edge["relationship"]) for edge in payload["edges"]}
        self.assertIn(
            ("skill:promote-to-commons", "skill:review-for-commons", "works with"),
            edges,
        )

    def test_payload_exposes_composition_validation_and_source_previews(self) -> None:
        payload = sync_presentation.build_payload()
        by_key = {entry["key"]: entry for entry in payload["nodes"]}
        self.assertIn("archetype:development", by_key)
        self.assertIn("overlay:branded-html", by_key)
        self.assertIn("adapter:codex", by_key)
        self.assertIn("eval:skill-evaluations", by_key)
        self.assertIn("external:anthropic-official-plugins", by_key)
        self.assertIn("# Practice test-driven development", by_key["skill:test-driven-development"]["source_preview"])
        self.assertNotIn("/Users/", json.dumps(payload))

    def test_payload_exposes_technical_diagram_family_and_overlay_links(self) -> None:
        payload = sync_presentation.build_payload()
        by_key = {entry["key"]: entry for entry in payload["nodes"]}
        for key in (
            "skill:create-technical-diagram",
            "skill:create-system-landscape-diagram",
            "skill:create-component-architecture-diagram",
            "skill:create-class-diagram",
            "skill:create-er-diagram",
            "skill:create-sequence-diagram",
            "skill:create-data-flow-diagram",
            "overlay:architecture-documentation",
        ):
            self.assertIn(key, by_key)
        edges = {(edge["source"], edge["target"], edge["relationship"]) for edge in payload["edges"]}
        self.assertIn(
            ("overlay:architecture-documentation", "skill:create-technical-diagram", "uses"),
            edges,
        )
        self.assertIn(
            ("overlay:architecture-documentation", "skill:create-er-diagram", "uses"),
            edges,
        )
        self.assertIn(
            ("skill:create-er-diagram", "archetype:development", "available in"),
            edges,
        )
        presentation = (ROOT / "presentation" / "index.html").read_text(encoding="utf-8")
        self.assertIn("One source of truth", presentation)
        self.assertIn("The evidence stays the same. The view changes for the audience.", presentation)

    def test_legacy_use_case_explains_post_initialization_runtime_sequence(self) -> None:
        presentation = (ROOT / "presentation" / "index.html").read_text(encoding="utf-8")
        for expected in (
            "$analyze-legacy-system",
            "From invocation to validated completion.",
            "01 / USER → RUNTIME",
            "Invoke $analyze-legacy-system",
            "02 / AGENT → PROJECT",
            "Load governance, manifest, state, memory",
            "03 / AGENT → INVENTORY",
            "Resolve mode + establish coverage",
            "04 / COORD. → WORKERS",
            "Assign bounded independent slices",
            "05 / WORKERS → COORD.",
            "Return validated evidence packets",
            "06 / COORD. → OUTPUTS",
            "Synthesize + refresh configured artifacts",
            "07 / GATE → USER",
            "Validate completeness + return next action",
            "One coordinator controls scope and shared state",
            "Archetype selects defaults → .agent-commons.yaml records capability IDs and constraints",
            "workers return evidence packets only",
            "No implementation begins.",
        ):
            self.assertIn(expected, presentation)

    def test_hero_explains_the_starting_point_in_one_glance(self) -> None:
        presentation = (ROOT / "presentation" / "index.html").read_text(encoding="utf-8")
        for expected in (
            "Start with the work.",
            "Not the",
            "Share the method. Keep project context local.",
            "Without Commons",
            "Rebuild the setup.",
            "Rules · tools · validation",
            "Share once",
            "With Commons",
            "Start the work.",
            "Goal · evidence · outcome",
        ):
            self.assertIn(expected, presentation)

    def test_company_value_slide_shows_independent_projects_and_shared_promotion(self) -> None:
        presentation = (ROOT / "presentation" / "index.html").read_text(encoding="utf-8")
        for expected in (
            "One Commons. Independent projects.",
            "Projects can run in parallel.",
            "Agent Commons vN",
            "Projects start independently from the same baseline",
            "Runs independently",
            "may propose learning",
            "ONE GOVERNANCE GATE",
            "Review → generalize → validate → promote",
            "vN++",
            "Future projects start with the updated validated baseline",
            "No project-to-project dependency",
            "No automatic promotion",
        ):
            self.assertIn(expected, presentation)
        self.assertNotIn("Project B inherits Method A only after Project A finishes", presentation)
        self.assertNotIn("Agent Commons vN+1", presentation)

    def test_initialization_explains_archetype_to_runtime_handoff(self) -> None:
        presentation = (ROOT / "presentation" / "index.html").read_text(encoding="utf-8")
        for expected in (
            "Which archetype or combination describes the project?",
            "Archetype at initialization. Skills at runtime.",
            "Select archetype(s)",
            "Resolve capabilities",
            "archetypes + overlays → deduplicated stable IDs",
            "At runtime, the agent invokes a canonical skill; the archetype remains configuration and provenance.",
            "Before runtime:",
            "The archetype does not execute.",
        ):
            self.assertIn(expected, presentation)

    def test_payload_exposes_localization_capability_and_overlay_links(self) -> None:
        payload = sync_presentation.build_payload()
        by_key = {entry["key"]: entry for entry in payload["nodes"]}
        localized = by_key["skill:localize-client-artifact"]
        self.assertIn("Austrian German", localized["tags"])
        self.assertIn("overlay:bilingual-client-delivery", by_key)
        edges = {(edge["source"], edge["target"], edge["relationship"]) for edge in payload["edges"]}
        self.assertIn(
            ("overlay:bilingual-client-delivery", "skill:localize-client-artifact", "uses"),
            edges,
        )

    def test_rendered_block_is_deterministic_and_current(self) -> None:
        first = sync_presentation.rendered_block()
        second = sync_presentation.rendered_block()
        self.assertEqual(first, second)
        self.assertEqual(sync_presentation.validate(), [])

    def test_standalone_render_embeds_generated_data_without_local_dependencies(self) -> None:
        with self.fixture_repository() as root:
            asset = sync_presentation.rendered_asset()
            standalone = sync_presentation.rendered_standalone(
                (root / "presentation/index.html").read_text(encoding="utf-8"),
                asset,
            )
            self.assertNotIn('src="assets/library-data.js"', standalone)
            self.assertIn("window.AGENT_COMMONS_DATA =", standalone)
            self.assertEqual(standalone.count("window.AGENT_COMMONS_DATA ="), 1)
            self.assertNotRegex(standalone, r'<(?:script|img|source|video|audio)\b[^>]*\bsrc=["\'](?!data:)')
            self.assertNotRegex(standalone, r'<link\b[^>]*\bhref=["\'](?!data:)')

    def test_sync_writes_current_standalone_presentation(self) -> None:
        with self.fixture_repository() as root:
            self.assertTrue(sync_presentation.sync())
            standalone_path = root / "presentation/agent-commons.html"
            self.assertTrue(standalone_path.exists())
            self.assertEqual(
                standalone_path.read_text(encoding="utf-8"),
                sync_presentation.rendered_standalone(
                    (root / "presentation/index.html").read_text(encoding="utf-8"),
                    (root / "presentation/assets/library-data.js").read_text(encoding="utf-8"),
                ),
            )

    def test_invalid_related_skill_is_rejected(self) -> None:
        catalog = json.loads((ROOT / "catalog" / "capabilities.yaml").read_text(encoding="utf-8"))
        catalog["skills"]["promote-to-commons"]["related"] = ["missing-skill"]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "capabilities.json"
            path.write_text(json.dumps(catalog), encoding="utf-8")
            with mock.patch.object(sync_presentation, "CATALOG_PATH", path):
                with self.assertRaisesRegex(sync_presentation.PresentationSyncError, "invalid related"):
                    sync_presentation.build_payload()

    def test_new_and_removed_skill_follow_the_source_tree_without_html_edits(self) -> None:
        with self.fixture_repository() as root:
            skill_path = self.write_skill(root, "example")
            payload = sync_presentation.build_payload()
            by_key = {entry["key"]: entry for entry in payload["nodes"]}
            self.assertIn("skill:example", by_key)
            self.assertIn("example", by_key["skill:example"]["search_terms"])

            skill_path.unlink()
            skill_path.parent.rmdir()
            keys = {entry["key"] for entry in sync_presentation.build_payload()["nodes"]}
            self.assertNotIn("skill:example", keys)

    def test_new_agent_is_discovered_without_manual_presentation_data(self) -> None:
        with self.fixture_repository() as root:
            self.write_agent(root, "requirements-auditor")
            by_key = {entry["key"]: entry for entry in sync_presentation.build_payload()["nodes"]}
            self.assertEqual(by_key["agent:requirements-auditor"]["type"], "agent")
            self.assertEqual(by_key["agent:requirements-auditor"]["path"], "agents/requirements-auditor.yaml")

    def test_archetype_relationship_is_derived_and_broken_reference_fails(self) -> None:
        with self.fixture_repository() as root:
            self.write_skill(root, "example")
            archetype_path = root / "archetypes/development/archetype.yaml"
            archetype_path.parent.mkdir(parents=True)
            archetype = {
                "id": "development",
                "title": "Development",
                "purpose": "Fixture composition.",
                "capabilities": {"required": {"skills": ["example"]}},
            }
            archetype_path.write_text(json.dumps(archetype), encoding="utf-8")
            edges = {
                (entry["source"], entry["target"], entry["relationship"])
                for entry in sync_presentation.build_payload()["edges"]
            }
            self.assertIn(("archetype:development", "skill:example", "uses"), edges)

            archetype["capabilities"]["required"]["skills"] = ["missing"]
            archetype_path.write_text(json.dumps(archetype), encoding="utf-8")
            with self.assertRaisesRegex(sync_presentation.PresentationSyncError, "missing node"):
                sync_presentation.build_payload()

    def test_overlay_condition_links_capability_to_compatible_archetype(self) -> None:
        with self.fixture_repository() as root:
            self.write_skill(root, "example")
            archetype_path = root / "archetypes/development/archetype.yaml"
            archetype_path.parent.mkdir(parents=True)
            archetype_path.write_text(
                json.dumps({"id": "development", "title": "Development", "purpose": "Fixture composition."}),
                encoding="utf-8",
            )
            overlay_path = root / "archetypes/overlays/architecture/overlay.yaml"
            overlay_path.parent.mkdir(parents=True)
            overlay_path.write_text(
                json.dumps(
                    {
                        "id": "architecture",
                        "title": "Architecture",
                        "purpose": "Fixture overlay.",
                        "compatible_archetypes": ["development"],
                        "conditions": [
                            {
                                "id": "diagram",
                                "when": "a diagram is requested",
                                "capabilities": {"skills": ["example"]},
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            edges = {
                (entry["source"], entry["target"], entry["relationship"])
                for entry in sync_presentation.build_payload()["edges"]
            }
            self.assertIn(("overlay:architecture", "skill:example", "uses"), edges)
            self.assertIn(("skill:example", "archetype:development", "available in"), edges)

    def test_duplicate_tool_id_is_rejected(self) -> None:
        with self.fixture_repository() as root:
            (root / "tools/cataloged.py").write_text('"""Cataloged tool."""\n', encoding="utf-8")
            (root / "tools/helper.py").write_text('"""Discovered tool."""\n', encoding="utf-8")
            catalog = {"skills": {}, "agents": {}, "templates": {}, "tools": {
                "helper": {"version": 1, "path": "tools/cataloged.py"}
            }}
            (root / "catalog/capabilities.yaml").write_text(json.dumps(catalog), encoding="utf-8")
            with self.assertRaisesRegex(sync_presentation.PresentationSyncError, "duplicate tool ID"):
                sync_presentation.build_payload()

    def test_check_mode_is_read_only_for_current_and_stale_data(self) -> None:
        with self.fixture_repository() as root:
            skill_path = self.write_skill(root, "example")
            self.assertTrue(sync_presentation.sync())
            asset_path = root / "presentation/assets/library-data.js"
            current = asset_path.read_bytes()
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(sync_presentation.main(["--check"]), 0)
            self.assertIn("CURRENT", output.getvalue())

            skill_path.write_text(skill_path.read_text(encoding="utf-8") + "Changed.\n", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(sync_presentation.main(["--check"]), 1)
            self.assertIn("STALE", output.getvalue())
            self.assertEqual(asset_path.read_bytes(), current)

    def test_refresh_is_idempotent(self) -> None:
        with self.fixture_repository() as root:
            self.write_skill(root, "example")
            self.assertTrue(sync_presentation.sync())
            first = (root / "presentation/assets/library-data.js").read_bytes()
            self.assertFalse(sync_presentation.sync())
            self.assertEqual((root / "presentation/assets/library-data.js").read_bytes(), first)

    def test_source_preview_redacts_confidential_paths_and_secret_assignments(self) -> None:
        with self.fixture_repository() as root:
            self.write_skill(root, "example", "/Users/private/client/source.py\napi_key = do-not-expose")
            node = next(
                entry for entry in sync_presentation.build_payload()["nodes"] if entry["key"] == "skill:example"
            )
            self.assertNotIn("/Users/", node["source_preview"])
            self.assertNotIn("do-not-expose", node["source_preview"])
            self.assertIn("[redacted]", node["source_preview"])


if __name__ == "__main__":
    unittest.main()
