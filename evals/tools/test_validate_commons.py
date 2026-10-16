"""Focused checks for repository-wide deterministic validation."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import validate_commons  # noqa: E402


class ValidateCommonsTests(unittest.TestCase):
    def test_yaml_duplicate_mapping_keys_reports_nested_duplicate(self) -> None:
        text = """version: 1
skills:
  synthetic:
    scenarios:
      missing_evidence:
        expected: [first]
        expected: [second]
      valid:
        expected: [third]
"""

        self.assertEqual(
            validate_commons.yaml_duplicate_mapping_key_errors(text, "scenarios.yaml"),
            [
                "scenarios.yaml:7: duplicate mapping key "
                "skills.synthetic.scenarios.missing_evidence.expected (first at line 6)"
            ],
        )

    def test_local_markdown_links_accept_files_and_heading_fragments(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "guide.md").write_text("# Guide\n\nSee [setup](docs/setup.md#quick-start).\n", encoding="utf-8")
            (root / "docs").mkdir()
            (root / "docs" / "setup.md").write_text("# Setup\n\n## Quick start\n", encoding="utf-8")
            self.assertEqual(validate_commons.local_markdown_link_errors(root), [])

    def test_local_markdown_links_report_missing_targets(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "guide.md").write_text("See [missing](docs/missing.md).\n", encoding="utf-8")
            self.assertEqual(
                validate_commons.local_markdown_link_errors(root),
                ["guide.md: missing local link target docs/missing.md"],
            )


if __name__ == "__main__":
    unittest.main()
