#!/usr/bin/env python3

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "estimate-adm-modernization" / "scripts" / "summarize_adm_estimate.py"
FIXTURES = ROOT / "evals" / "fixtures" / "adm-estimation"


class AdmEstimateTest(unittest.TestCase):
    def test_adm_migration_is_traced_across_commons_surfaces(self) -> None:
        catalog = json.loads((ROOT / "catalog" / "capabilities.yaml").read_text())
        interfaces = json.loads((ROOT / "adapters" / "codex" / "skill-interfaces.yaml").read_text())["interfaces"]
        skill_evals = (ROOT / "evals" / "skills" / "scenarios.yaml").read_text()
        archetypes = "\n".join(path.read_text() for path in (ROOT / "archetypes").rglob("*.yaml"))
        self.assertEqual("skills/estimate-adm-modernization/SKILL.md", catalog["skills"]["estimate-adm-modernization"]["path"])
        self.assertEqual(
            "skills/estimate-adm-modernization/scripts/summarize_adm_estimate.py",
            catalog["tools"]["summarize-adm-estimate"]["path"],
        )
        self.assertIn("estimate-adm-modernization", interfaces)
        self.assertIn("  estimate-adm-modernization:", skill_evals)
        self.assertIn('"estimate-adm-modernization"', archetypes)

    def test_valid_package_aggregates_pert_and_preserves_unknowns(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(FIXTURES / "valid-package.json")],
            check=True,
            capture_output=True,
            text=True,
        )
        summary = json.loads(result.stdout)
        self.assertEqual(5.33, summary["totals"]["expected"])
        self.assertEqual(["UNIT-2"], summary["unestimatedUnitIds"])
        self.assertTrue(any("unknown complexity drivers: volume" in warning for warning in summary["warnings"]))

    def test_invalid_range_and_false_calibration_confidence_fail(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(FIXTURES / "invalid-range.json")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("expected 0 <= optimistic <= mostLikely <= pessimistic", result.stderr)
        self.assertIn("unavailable calibration requires LOW confidence", result.stderr)


if __name__ == "__main__":
    unittest.main()
