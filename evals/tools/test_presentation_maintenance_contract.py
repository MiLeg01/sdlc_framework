from __future__ import annotations

import unittest
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class PresentationMaintenanceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.update_skill = (ROOT / "skills" / "update-commons-presentation" / "SKILL.md").read_text(encoding="utf-8")
        cls.promote_skill = (ROOT / "skills" / "promote-to-commons" / "SKILL.md").read_text(encoding="utf-8")
        cls.promotion_contract = (
            ROOT / "skills" / "promote-to-commons" / "references" / "promotion-contract.md"
        ).read_text(encoding="utf-8")
        cls.scenarios = (ROOT / "evals" / "skills" / "scenarios.yaml").read_text(encoding="utf-8")
        cls.presentation = (ROOT / "presentation" / "index.html").read_text(encoding="utf-8")

    def test_update_skill_refreshes_before_classification(self) -> None:
        refresh_position = self.update_skill.index("python3 tools/refresh_commons_presentation.py")
        classification_position = self.update_skill.index("## Classify narrative impact")
        self.assertLess(refresh_position, classification_position)
        for classification in ("FACTUAL ONLY", "MINOR NARRATIVE IMPACT", "MAJOR NARRATIVE IMPACT"):
            self.assertIn(classification, self.update_skill)

    def test_update_skill_preserves_style_and_requires_visual_qa(self) -> None:
        for phrase in (
            "The visual system is immutable",
            "Only generated facts and authored textual content may change",
            "Do not update or rebaseline `presentation/visual-contract.json`",
            "python3 tools/check_presentation_visual_contract.py",
            "validate-visual-artifact",
            "desktop, laptop, and mobile widths",
            "Do not present planned capabilities",
        ):
            self.assertIn(phrase, self.update_skill)

    def test_promotion_automatically_refreshes_facts_without_rewriting_story(self) -> None:
        combined = re.sub(r"\s+", " ", f"{self.promote_skill}\n{self.promotion_contract}")
        for phrase in (
            "python3 tools/refresh_commons_presentation.py",
            "requires no separate user confirmation",
            "Do not rewrite the hero, sales narrative, architecture story",
            "recommend the `update-commons-presentation` workflow",
        ):
            self.assertIn(phrase, combined)

    def test_required_narrative_scenarios_exist(self) -> None:
        block = self.scenarios.split("  update-commons-presentation:\n", 1)[1].split(
            "\n  validate-visual-artifact:", 1
        )[0]
        for scenario in (
            "factual_only",
            "minor_narrative",
            "major_architecture",
            "keep_existing_style",
            "new_agent",
            "new_skill",
            "stale_presentation",
        ):
            self.assertIn(f"      {scenario}:", block)

    def test_locked_visual_system_preserves_authored_chapter_order(self) -> None:
        section_ids = re.findall(r'<section class="chapter[^>]*\sid="([^"]+)"', self.presentation)
        self.assertEqual(section_ids, [
            "start", "tax", "engine", "inside", "network", "architecture",
            "initialize", "compose", "external", "trust", "payoff",
            "closing",
        ])
        self.assertIn('data-visual-thesis="agent-commons-ultraviolet"', self.presentation)
        self.assertIn('href="#payoff" aria-label="Go to chapter 11"', self.presentation)
        # The closing chapter is a chapter: it is reachable from the rail and
        # counted by the progress indicator like every other section.
        self.assertIn('href="#closing" aria-label="Go to chapter 12"', self.presentation)
        self.assertEqual(len(re.findall(r'<a href="#[^"]+" aria-label="Go to chapter', self.presentation)), len(section_ids))

    def test_presentation_accessibility_contract_is_first_class(self) -> None:
        for marker in (
            '<main id="main" tabindex="-1">',
            'aria-labelledby="capability-tab-overview"',
            'aria-controls="scope-panel"',
            'wireKeyboardTabs(previewTabs)',
            'wireKeyboardTabs(scopeTabs)',
            'wireKeyboardTabs(useTabs)',
            '@media (prefers-reduced-motion: reduce)',
            '@media (forced-colors: active)',
        ):
            self.assertIn(marker, self.presentation)

    def test_graph_nodes_are_operable_not_hidden(self) -> None:
        # Graph nodes carry click, focus and keydown handlers. They previously
        # shipped as tabindex="-1" aria-hidden="true", which made every one of
        # those handlers unreachable and hid the diagram from assistive tech.
        self.assertNotIn('tabindex: "-1", "aria-hidden": "true"', self.presentation)
        for marker in (
            'role: "button"',
            'function setNetworkTabStop(',
            'function moveNetworkTabStop(',
            '.graph-node:focus-visible',
            '<desc id="network-description">',
            'graph.querySelector("desc")',
        ):
            self.assertIn(marker, self.presentation)

    def test_presenter_hardware_can_drive_the_deck(self) -> None:
        # Clickers emit PageDown/PageUp or the horizontal arrows, never j/k.
        for marker in ("ArrowRight", "ArrowLeft", "PageDown", "PageUp", "Home", "End"):
            self.assertIn(marker, self.presentation)
        # ArrowUp/ArrowDown and Space stay unbound so ordinary keyboard
        # scrolling of this long document keeps working.
        self.assertNotIn("ArrowDown: 1", self.presentation)
        self.assertNotIn("ArrowUp: 1", self.presentation)


if __name__ == "__main__":
    unittest.main()
