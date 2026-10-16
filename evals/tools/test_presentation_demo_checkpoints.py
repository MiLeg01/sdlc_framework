from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "presentation" / "validate-demo-checkpoints.py"
CONTRACT = ROOT / "presentation" / "demo-checkpoints.json"


def load_validator():
    spec = importlib.util.spec_from_file_location("presentation_demo_validator", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load presentation demo validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PresentationDemoCheckpointTest(unittest.TestCase):
    def test_source_fingerprint_is_portable_across_roots(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            first_source = Path(first) / "client_input" / "nested"
            second_source = Path(second) / "client_input" / "nested"
            first_source.mkdir(parents=True)
            second_source.mkdir(parents=True)
            (first_source / "sample.txt").write_text("same source\n", encoding="utf-8")
            (second_source / "sample.txt").write_text("same source\n", encoding="utf-8")

            self.assertEqual(
                validator.source_fingerprint(Path(first)),
                validator.source_fingerprint(Path(second)),
            )

    def test_contract_declares_the_four_lifecycle_stages(self) -> None:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(
            list(contract["stages"]),
            ["01-fresh", "02-initialized", "03-analyzed", "04-spec-ready"],
        )
        self.assertEqual(contract["source"]["license"], "Apache-2.0")


if __name__ == "__main__":
    unittest.main()
