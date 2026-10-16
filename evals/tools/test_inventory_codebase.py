#!/usr/bin/env python3
"""Executable regressions for deterministic codebase inventory behavior."""

from __future__ import annotations

import contextlib
import errno
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "inventory-codebase" / "scripts" / "inventory_codebase.py"
SPEC = importlib.util.spec_from_file_location("inventory_codebase", SCRIPT)
assert SPEC and SPEC.loader
inventory_codebase = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inventory_codebase)


class InventoryCodebaseScenarios(unittest.TestCase):
    def test_directory_traversal_errors_are_visible_relative_failures(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            unreadable = root / "restricted"

            def walk_with_error(path: Path, *, topdown: bool, followlinks: bool, onerror):
                self.assertEqual(Path(path), root)
                self.assertTrue(topdown)
                self.assertFalse(followlinks)
                onerror(PermissionError(errno.EACCES, "Permission denied", str(unreadable)))
                return iter([(str(root), [], [])])

            stdout = io.StringIO()
            argv = ["inventory_codebase.py", "--root", str(root)]
            with mock.patch.object(inventory_codebase.os, "walk", side_effect=walk_with_error), \
                    mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(stdout):
                status = inventory_codebase.main()

        payload = json.loads(stdout.getvalue())
        self.assertEqual(status, 1)
        self.assertEqual(payload["counts"]["failures"], 1)
        self.assertEqual(
            payload["failures"],
            [{"path": "restricted", "error": "PermissionError"}],
        )


if __name__ == "__main__":
    unittest.main()
