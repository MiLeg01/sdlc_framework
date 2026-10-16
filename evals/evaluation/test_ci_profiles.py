from __future__ import annotations

import sys
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "evals"))

from run_evals import (  # noqa: E402
    canonical_profile,
    default_repeat_for_profile,
    is_retryable_infrastructure_failure,
    select_capabilities_by_kind,
)


class CiProfileTests(unittest.TestCase):
    def test_cost_profiles_have_explicit_names_and_compatible_aliases(self) -> None:
        defaults = {"nightly_repeat": 3, "weekly_repeat": 5}

        self.assertEqual(canonical_profile("fast"), "fast")
        self.assertEqual(canonical_profile("standard"), "standard")
        self.assertEqual(canonical_profile("full"), "full")
        self.assertEqual(canonical_profile("deep"), "deep")
        self.assertEqual(canonical_profile("smoke"), "fast")
        self.assertEqual(canonical_profile("pr"), "fast")
        self.assertEqual(canonical_profile("nightly"), "full")
        self.assertEqual(canonical_profile("weekly"), "deep")

        self.assertEqual(default_repeat_for_profile("fast", defaults), 1)
        self.assertEqual(default_repeat_for_profile("standard", defaults), 1)
        self.assertEqual(default_repeat_for_profile("full", defaults), 3)
        self.assertEqual(default_repeat_for_profile("deep", defaults), 5)
        self.assertEqual(default_repeat_for_profile("smoke", defaults), 1)

    def test_parallel_jobs_can_select_capabilities_by_kind(self) -> None:
        contracts = {
            "one-skill": {"kind": "skill"},
            "one-agent": {"kind": "agent"},
            "one-tool": {"kind": "tool"},
        }

        self.assertEqual(
            select_capabilities_by_kind(contracts, ["skill", "tool"]),
            ["one-skill", "one-tool"],
        )

    def test_only_transient_executor_failures_are_retryable(self) -> None:
        rate_limited = subprocess.CompletedProcess([], 1, stdout="", stderr="HTTP 429 rate limit")
        assertion_failed = subprocess.CompletedProcess([], 1, stdout="", stderr="assertion failed")

        self.assertTrue(is_retryable_infrastructure_failure(rate_limited))
        self.assertFalse(is_retryable_infrastructure_failure(assertion_failed))


if __name__ == "__main__":
    unittest.main()
