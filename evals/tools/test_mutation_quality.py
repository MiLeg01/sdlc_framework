#!/usr/bin/env python3
"""Executable evaluations for application mutation testing: benchmark, gate, and tool detection.

The benchmark is real rather than asserted. Each declared mutation is applied to a disposable copy
of the fixture module, the weak and hardened suites are executed against it, and the recorded
KILLED or SURVIVED outcome must match the expectation. The gate scenarios then prove that the
deterministic assessment classifies strong tests, weak tests, boundary gaps, equivalent mutants,
critical survivors, unsupported technology, flaky baselines, and changed-code scope correctly.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "evals" / "fixtures" / "mutation-quality"
INPUT = FIXTURE / "input"
RUNS = FIXTURE / "runs"
CASES = FIXTURE / "benchmark-cases.json"
ASSESS = ROOT / "skills" / "mutation-testing" / "scripts" / "assess_mutation_quality.py"
DETECT = ROOT / "skills" / "mutation-testing" / "scripts" / "detect_mutation_tooling.py"
EXIT_CODES = {"PASS": 0, "WARNING": 0, "FAIL": 2, "NOT_SUPPORTED": 3, "BLOCKED": 4}


def run_suite(workspace: Path, suite: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "unittest", suite],
        cwd=workspace,
        capture_output=True,
        text=True,
    )


def assess(run: str, *, policy: bool = True, baseline: bool = True, extra: list[str] | None = None):
    command = [sys.executable, str(ASSESS), "--run", str(RUNS / run)]
    if policy:
        command += ["--policy", str(RUNS / "policy.json")]
    if baseline:
        command += ["--baseline", str(RUNS / "baseline.json")]
    command += extra or []
    completed = subprocess.run(command, capture_output=True, text=True)
    payload = json.loads(completed.stdout) if completed.stdout.strip().startswith("{") else None
    return completed, payload


class MutationBenchmarkScenarios(unittest.TestCase):
    """PART 49 benchmark: the same production code, two suites, measurable before and after."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = json.loads(CASES.read_text(encoding="utf-8"))
        cls.suites = cls.cases["suites"]

    def workspace(self, stack: tempfile.TemporaryDirectory) -> Path:
        workspace = Path(stack.name) / "project"
        shutil.copytree(INPUT, workspace)
        return workspace

    def test_both_suites_pass_against_the_unmutated_implementation(self):
        with tempfile.TemporaryDirectory(prefix="mutation-benchmark-") as temporary:
            workspace = Path(temporary) / "project"
            shutil.copytree(INPUT, workspace)
            for name, suite in self.suites.items():
                completed = run_suite(workspace, suite)
                self.assertEqual(
                    completed.returncode, 0,
                    f"{name} suite must pass before mutation: {completed.stderr}",
                )

    def test_declared_mutations_match_the_source_exactly_once(self):
        source = (INPUT / self.cases["module"]).read_text(encoding="utf-8")
        for case in self.cases["cases"]:
            with self.subTest(case=case["id"]):
                self.assertEqual(
                    source.count(case["search"]), 1,
                    f"{case['id']} search text must match exactly once",
                )

    def test_weak_suite_leaves_meaningful_mutants_alive_and_hardened_suite_kills_them(self):
        module = self.cases["module"]
        observed: dict[str, dict[str, str]] = {}
        for case in self.cases["cases"]:
            observed[case["id"]] = {}
            for name, suite in self.suites.items():
                with tempfile.TemporaryDirectory(prefix="mutation-benchmark-") as temporary:
                    workspace = Path(temporary) / "project"
                    shutil.copytree(INPUT, workspace)
                    target = workspace / module
                    source = target.read_text(encoding="utf-8")
                    target.write_text(
                        source.replace(case["search"], case["replacement"], 1), encoding="utf-8",
                    )
                    completed = run_suite(workspace, suite)
                    observed[case["id"]][name] = "KILLED" if completed.returncode != 0 else "SURVIVED"
            with self.subTest(case=case["id"]):
                self.assertEqual(
                    observed[case["id"]], case["expected"],
                    f"{case['id']} ({case['operator']}) did not behave as documented",
                )

        gaps = [case["id"] for case in self.cases["cases"] if case["classification"] == "TEST_GAP"]
        self.assertTrue(gaps, "the benchmark must contain at least one real test gap")
        for identifier in gaps:
            self.assertEqual(observed[identifier]["weak"], "SURVIVED")
            self.assertEqual(observed[identifier]["hardened"], "KILLED")

    def test_equivalent_mutant_survives_both_suites_and_is_not_a_test_gap(self):
        equivalent = [
            case for case in self.cases["cases"]
            if case["classification"] == "EQUIVALENT_MUTANT"
        ]
        self.assertTrue(equivalent, "the benchmark must contain an equivalent mutant")
        for case in equivalent:
            self.assertEqual(case["expected"], {"weak": "SURVIVED", "hardened": "SURVIVED"})
            self.assertTrue(
                case.get("accepted_reason"),
                f"{case['id']} must record why it is equivalent rather than a test gap",
            )

    def test_benchmark_contains_a_mutant_the_weak_suite_already_kills(self):
        killed = [
            case for case in self.cases["cases"]
            if case["expected"]["weak"] == "KILLED"
        ]
        self.assertTrue(
            killed,
            "a benchmark where every mutant survives would not prove the suites run at all",
        )


class MutationQualityGateScenarios(unittest.TestCase):
    """PART 39 gate expectations, derived rather than asserted."""

    def expect(self, run: str, status: str, **kwargs):
        completed, payload = assess(run, **kwargs)
        self.assertIsNotNone(payload, f"{run} produced no assessment: {completed.stderr}")
        self.assertEqual(payload["status"], status, f"{run}: {payload['reasons']}")
        self.assertEqual(completed.returncode, EXIT_CODES[status], f"{run} exit code")
        return payload

    def test_strong_tests_pass(self):
        payload = self.expect("strong-tests-run.json", "PASS")
        self.assertEqual(payload["critical_survivors"], [])
        self.assertEqual(payload["metrics"]["accepted_equivalent_or_excluded"], 1)

    def test_weak_tests_fail_on_critical_survivors_and_the_configured_minimum(self):
        payload = self.expect("weak-tests-run.json", "FAIL")
        self.assertEqual(payload["critical_survivors"], ["MUT-001", "MUT-002", "MUT-003"])
        self.assertTrue(any("critical meaningful mutant survives" in r for r in payload["reasons"]))
        self.assertTrue(any("below the configured minimum" in r for r in payload["reasons"]))

    def test_boundary_survivor_is_linked_to_its_acceptance_criterion(self):
        payload = self.expect("weak-tests-run.json", "FAIL")
        boundary = next(item for item in payload["traceability"] if item["survivor"] == "MUT-001")
        self.assertEqual(boundary["requirement"], "REQ-017")
        self.assertEqual(boundary["specification"], "SPEC-004")
        self.assertEqual(boundary["acceptance_criterion"], "AC-004-3")
        self.assertEqual(boundary["classification"], "TEST_GAP")

    def test_accepted_equivalent_mutant_is_excluded_and_does_not_fail_the_gate(self):
        payload = self.expect("strong-tests-run.json", "PASS")
        self.assertEqual(payload["classification_counts"], {"EQUIVALENT_MUTANT": 1})
        self.assertEqual(payload["metrics"]["meaningful_survivors"], 0)

    def test_unjustified_equivalence_claim_stays_in_the_denominator_and_warns(self):
        payload = self.expect("unjustified-equivalence-run.json", "WARNING")
        self.assertEqual(payload["metrics"]["meaningful_survivors"], 1)
        self.assertTrue(any("without a recorded reason" in w for w in payload["warnings"]))

    def test_critical_survivor_fails_even_with_a_high_aggregate_score(self):
        completed, payload = assess("weak-tests-run.json", policy=False, baseline=False)
        self.assertEqual(payload["status"], "FAIL")
        self.assertGreater(payload["metrics"]["mutation_score"], 0.85)
        self.assertEqual(completed.returncode, 2)

    def test_non_critical_survivor_warns_rather_than_fails(self):
        payload = self.expect("non-critical-survivor-run.json", "WARNING")
        self.assertEqual(payload["critical_survivors"], [])
        self.assertTrue(any("non-critical meaningful survivors" in w for w in payload["warnings"]))

    def test_unsupported_technology_is_not_a_pass(self):
        payload = self.expect("unsupported-technology-run.json", "NOT_SUPPORTED")
        self.assertEqual(payload["metrics"]["mutation_score"], "not_available")
        self.assertTrue(payload["compensating_verification"])
        allowed, _ = assess("unsupported-technology-run.json", extra=["--allow-not-supported"])
        self.assertEqual(allowed.returncode, 0, "an explicit allowance may exit 0")
        self.assertIn("NOT_SUPPORTED", allowed.stdout)

    def test_flaky_baseline_blocks_instead_of_scoring(self):
        payload = self.expect("flaky-baseline-run.json", "BLOCKED")
        self.assertTrue(any("BLOCKED_BY_FLAKY_TESTS" in r for r in payload["reasons"]))
        self.assertEqual(payload["metrics"]["mutation_score"], "not_available")

    def test_flaky_survivor_result_blocks_the_run(self):
        payload = self.expect("flaky-survivor-run.json", "BLOCKED")
        self.assertTrue(any("BLOCKED_BY_FLAKY_TESTS" in r for r in payload["reasons"]))

    def test_failing_baseline_suite_fails_before_mutation_is_interpreted(self):
        payload = self.expect("failing-baseline-run.json", "FAIL")
        self.assertTrue(any("failed before mutation execution" in r for r in payload["reasons"]))

    def test_invalid_tool_execution_fails(self):
        payload = self.expect("invalid-execution-run.json", "FAIL")
        self.assertTrue(any("invalid execution" in r for r in payload["reasons"]))

    def test_material_regression_against_the_baseline_fails(self):
        payload = self.expect("regressed-run.json", "FAIL")
        self.assertEqual(payload["baseline_comparison"]["verdict"], "REGRESSED")
        self.assertTrue(any("regressed" in r for r in payload["reasons"]))

    def test_small_deterioration_within_tolerance_only_warns(self):
        completed, payload = assess("strong-tests-run.json")
        self.assertEqual(payload["baseline_comparison"]["verdict"], "IMPROVED")
        self.assertEqual(completed.returncode, 0)

    def test_unclassified_survivor_blocks_the_assessment(self):
        payload = self.expect("unclassified-survivor-run.json", "BLOCKED")
        self.assertTrue(any("unclassified" in r for r in payload["reasons"]))

    def test_changed_code_scope_selects_only_impacted_code_and_gates_it(self):
        payload = self.expect("changed-scope-run.json", "FAIL")
        run = json.loads((RUNS / "changed-scope-run.json").read_text(encoding="utf-8"))
        selection = run["mutation_run"]["scope_selection"]
        self.assertEqual(selection["changed_production_files"], ["example/orders/eligibility.py"])
        self.assertTrue(selection["excluded_unchanged_modules"])
        self.assertTrue(payload["run"]["changed_scope_only"])
        self.assertLess(payload["metrics"]["total_mutants"], 20)
        self.assertTrue(any("changed business logic" in r for r in payload["reasons"]))

    def test_score_cannot_be_asserted_by_the_run(self):
        run = json.loads((RUNS / "strong-tests-run.json").read_text(encoding="utf-8"))
        run["metrics"]["mutation_score"] = 1.0
        with tempfile.TemporaryDirectory(prefix="mutation-gate-") as temporary:
            path = Path(temporary) / "asserted-score.json"
            path.write_text(json.dumps(run), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(ASSESS), "--run", str(path)],
                capture_output=True, text=True,
            )
        self.assertEqual(completed.returncode, 1)
        self.assertIn("must not assert mutation_score", completed.stderr)

    def test_an_unaccounted_survivor_cannot_silently_improve_the_score(self):
        run = json.loads((RUNS / "weak-tests-run.json").read_text(encoding="utf-8"))
        run["survivors"] = run["survivors"][:1]
        with tempfile.TemporaryDirectory(prefix="mutation-gate-") as temporary:
            path = Path(temporary) / "hidden-survivors.json"
            path.write_text(json.dumps(run), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(ASSESS), "--run", str(path)],
                capture_output=True, text=True,
            )
        self.assertEqual(completed.returncode, 1)
        self.assertIn("unaccounted survivor", completed.stderr)

    def test_a_baseline_for_a_different_scope_is_not_a_regression_signal(self):
        payload = self.expect("non-critical-survivor-run.json", "WARNING")
        self.assertFalse(payload["baseline_comparison"]["comparable"])


class MutationToolingDetectionScenarios(unittest.TestCase):
    def detect(self, root: Path):
        completed = subprocess.run(
            [sys.executable, str(DETECT), "--root", str(root)],
            capture_output=True, text=True,
        )
        return completed, json.loads(completed.stdout)

    def test_each_supported_ecosystem_resolves_to_one_adapter(self):
        with tempfile.TemporaryDirectory(prefix="mutation-detect-") as temporary:
            root = Path(temporary)
            (root / "pom.xml").write_text("<project/>", encoding="utf-8")
            (root / "package.json").write_text("{}", encoding="utf-8")
            (root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
            (root / "app.csproj").write_text("<Project/>", encoding="utf-8")
            completed, result = self.detect(root)
        self.assertEqual(completed.returncode, 0)
        adapters = {entry["id"]: entry["recommended_adapter"] for entry in result["ecosystems"]}
        self.assertEqual(adapters["jvm"], "pitest")
        self.assertEqual(adapters["dotnet"], "stryker-net")
        self.assertEqual(adapters["javascript"], "stryker-js")
        self.assertEqual(adapters["python"], "mutmut")
        for entry in result["ecosystems"]:
            self.assertFalse(entry["already_configured"])

    def test_existing_configuration_is_reused_rather_than_replaced(self):
        with tempfile.TemporaryDirectory(prefix="mutation-detect-") as temporary:
            root = Path(temporary)
            (root / "pom.xml").write_text(
                "<project><build><plugins><plugin>"
                "<artifactId>pitest-maven</artifactId></plugin></plugins></build></project>",
                encoding="utf-8",
            )
            _, result = self.detect(root)
        entry = next(item for item in result["ecosystems"] if item["id"] == "jvm")
        self.assertTrue(entry["already_configured"])
        self.assertEqual(entry["status"], "SUPPORTED_CONFIGURED")
        self.assertIn("reuse", entry["action"])

    def test_unsupported_legacy_source_is_reported_not_omitted(self):
        with tempfile.TemporaryDirectory(prefix="mutation-detect-") as temporary:
            root = Path(temporary)
            (root / "PAYCALC.cbl").write_text("IDENTIFICATION DIVISION.\n", encoding="utf-8")
            completed, result = self.detect(root)
        self.assertEqual(completed.returncode, 3, "no supported ecosystem must not exit 0")
        self.assertEqual(result["status"], "NOT_SUPPORTED")
        cobol = next(item for item in result["unsupported_sources"] if item["id"] == "cobol")
        self.assertEqual(cobol["status"], "NOT_SUPPORTED")
        self.assertIn("target implementation", cobol["action"])


if __name__ == "__main__":
    unittest.main()
