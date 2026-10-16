"""Public v1 baseline invariants for the canonical repository."""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class PublicBaselineTests(unittest.TestCase):
    def test_release_metadata_stays_on_v1_and_matches_the_changelog(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertRegex(version, r"^1\.\d+\.\d+$")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn(f"## v{version}", changelog)
        self.assertNotIn("## " + str(2) + ".0.0", changelog)

    def test_development_archaeology_is_not_part_of_the_product_tree(self) -> None:
        reports = sorted(path.name for path in (ROOT / "reports").glob("*.md"))
        self.assertEqual(
            reports,
            [
                "mutation-testing-and-tdd-quality.md",
                "project-memory-and-deep-analysis.md",
                "v1-dashboard-discovery-and-git-governance-hardening.md",
            ],
        )
        self.assertFalse((ROOT / "provenance").exists())
        index = json.loads((ROOT / "external" / "index" / "capabilities.json").read_text(encoding="utf-8"))
        self.assertEqual(index["candidates"], [])
        reviews = sorted(path.name for path in (ROOT / "external" / "reviews").glob("*.md"))
        self.assertEqual(reviews, ["README.md"])

    def test_tracked_product_has_no_private_or_project_specific_identity(self) -> None:
        tracked = subprocess.run(
            ["git", "ls-files"], cwd=ROOT, check=True, capture_output=True, text=True
        ).stdout.splitlines()
        text = "\n".join(
            (ROOT / relative).read_text(encoding="utf-8", errors="replace")
            for relative in tracked
            if (ROOT / relative).is_file()
        ).lower()
        prohibited = [
            "idea" + "projects",
            "/users/" + "paul." + "curcean",
            "bundes" + "kanzleramt",
        ]
        for token in prohibited:
            self.assertNotIn(token, text)

    def test_presentation_contains_only_the_current_visual_system(self) -> None:
        html = (ROOT / "presentation" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-visual-thesis="agent-commons-ultraviolet"', html)
        self.assertNotIn("max-width:0px", html)


if __name__ == "__main__":
    unittest.main()
