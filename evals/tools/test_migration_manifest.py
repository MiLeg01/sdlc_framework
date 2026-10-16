#!/usr/bin/env python3

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "migrate-code-with-evidence" / "scripts" / "validate_migration_manifest.py"
FIXTURES = ROOT / "evals" / "fixtures" / "code-migration"


class MigrationManifestTest(unittest.TestCase):
    def test_valid_manifest_preserves_traceability_and_safe_boundaries(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(FIXTURES / "valid-manifest.json")],
            check=True,
            capture_output=True,
            text=True,
        )
        summary = json.loads(result.stdout)
        self.assertEqual(1, summary["sliceCount"])
        self.assertEqual(1, summary["acceptanceScenarioCount"])
        self.assertEqual("isolated-target", summary["writeBoundary"])

    def test_unsafe_manifest_rejects_shared_roots_secrets_and_destructive_commands(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(FIXTURES / "unsafe-manifest.json")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("source.root and target.root must be distinct", result.stderr)
        self.assertIn("credential-like key is forbidden", result.stderr)
        self.assertIn("unsafe validation command", result.stderr)

    def test_target_nested_inside_source_is_rejected(self) -> None:
        manifest = json.loads((FIXTURES / "valid-manifest.json").read_text())
        manifest["target"]["root"] = "source-system/generated"
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory) / "nested-target.json"
            temporary.write_text(json.dumps(manifest))
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(temporary)],
                capture_output=True,
                text=True,
            )
        self.assertEqual(2, result.returncode)
        self.assertIn("target.root must not be inside source.root", result.stderr)


if __name__ == "__main__":
    unittest.main()
