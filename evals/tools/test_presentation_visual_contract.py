from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "tools" / "check_presentation_visual_contract.py"
SPEC = importlib.util.spec_from_file_location("check_presentation_visual_contract", MODULE_PATH)
assert SPEC and SPEC.loader
visual_contract = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(visual_contract)


class PresentationVisualContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = (ROOT / "presentation" / "index.html").read_text(encoding="utf-8")
        cls.contract = json.loads(
            (ROOT / "presentation" / "visual-contract.json").read_text(encoding="utf-8")
        )

    def test_current_presentation_matches_locked_contract(self) -> None:
        self.assertEqual(visual_contract.validate(self.html, self.contract), [])

    def test_text_content_can_change(self) -> None:
        changed = self.html.replace("Stop starting", "Keep building", 1)
        self.assertEqual(visual_contract.validate(changed, self.contract), [])

    def test_css_cannot_change(self) -> None:
        changed = self.html.replace("--void: #050008", "--void: #060009", 1)
        self.assertIn(
            "style_sha256 drifted from the locked visual system",
            visual_contract.validate(changed, self.contract),
        )

    def test_structure_cannot_change(self) -> None:
        changed = self.html.replace('class="page hero-grid"', 'class="page hero-grid redesigned"', 1)
        self.assertIn(
            "structure_sha256 drifted from the locked visual system",
            visual_contract.validate(changed, self.contract),
        )

    def test_runtime_cannot_change(self) -> None:
        changed = self.html.replace("var nav =", "var changedNav =", 1)
        self.assertIn(
            "behavior_sha256 drifted from the locked visual system",
            visual_contract.validate(changed, self.contract),
        )


if __name__ == "__main__":
    unittest.main()
