#!/usr/bin/env python3
"""Regression tests for canonical Agent Commons commit-message governance."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import commit_policy  # noqa: E402


class CommitPolicyTests(unittest.TestCase):
    def test_main_branch_keeps_meaningful_message_without_type_prefix(self) -> None:
        self.assertEqual(
            commit_policy.compose_message("Improve dashboard rendering", "main"),
            "Improve dashboard rendering",
        )
        self.assertEqual([], commit_policy.validate_message("Improve dashboard rendering"))
        self.assertTrue(commit_policy.validate_message("feat: Improve dashboard rendering"))

    def test_ticket_branch_adds_reliable_ticket_prefix(self) -> None:
        self.assertEqual(
            commit_policy.compose_message("Improve dashboard rendering", "feature/ABC-123-dashboard"),
            "[ABC-123] Improve dashboard rendering",
        )

    def test_ambiguous_number_is_not_treated_as_ticket(self) -> None:
        self.assertIsNone(commit_policy.ticket_from_branch("experiment-2026-dashboard"))
        self.assertEqual(
            commit_policy.compose_message("Improve dashboard rendering", "experiment-2026-dashboard"),
            "Improve dashboard rendering",
        )

    def test_coauthor_and_agent_attribution_trailers_are_rejected(self) -> None:
        for trailer in (
            "Co-authored-by: Agent <agent@example.invalid>",
            "co-authored-by: Agent <agent@example.invalid>",
            "Generated-by: Codex",
            "Created-by: AI agent",
            "Assisted-by: automation",
        ):
            with self.subTest(trailer=trailer):
                errors = commit_policy.validate_message(f"Improve dashboard rendering\n\n{trailer}")
                self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
