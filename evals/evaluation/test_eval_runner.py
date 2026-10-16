#!/usr/bin/env python3
"""Behavioral tests for the canonical evaluation runner."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "tools" / "evals" / "run_evals.py"
sys.path.insert(0, str(ROOT / "tools" / "evals"))

from eval_common import load_thresholds  # noqa: E402
from run_evals import (  # noqa: E402
    HARD_FAIL,
    PASS,
    REGRESSION_FAIL,
    WARNING,
    apply_baseline_comparison,
    deterministic_environment,
    evaluate_repeat_consistency,
    filter_required_judge_assertions,
    result_record,
    run_unittest_scenario,
    normalize_evidence_source,
    validate_evidence_locators,
)


class EvalRunnerTests(unittest.TestCase):
    def run_eval(self, *arguments: str) -> tuple[subprocess.CompletedProcess[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        output = Path(temporary.name)
        completed = subprocess.run(
            ["python3", str(RUNNER), *arguments, "--output", str(output)],
            cwd=ROOT,
            env=deterministic_environment(),
            capture_output=True,
            text=True,
        )
        return completed, output

    def test_capability_run_writes_machine_readable_and_junit_results(self) -> None:
        completed, output = self.run_eval("--capability", "maintain-project-memory")

        self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
        for name in (
            "summary.json",
            "capabilities.json",
            "failures.json",
            "performance.json",
            "quality-summary.json",
            "quality-summary.html",
            "junit.xml",
        ):
            self.assertTrue((output / name).is_file(), name)
        summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["selection"]["capabilities"], ["maintain-project-memory"])
        self.assertGreater(summary["counts"]["passed"], 0)
        quality = json.loads((output / "quality-summary.json").read_text(encoding="utf-8"))
        self.assertEqual(quality["overall"], "WARN")
        self.assertIn("current_commit", quality)
        self.assertIn("capability_scores", quality)
        self.assertEqual(quality["capability_scores"]["maintain-project-memory"]["score"], "not_available")
        self.assertIn("performance", quality)
        self.assertIn("visuals", quality)
        self.assertTrue(all(item["status"] == "NOT_VERIFIED" for item in quality["visuals"]))
        self.assertEqual(quality["mutation"], "not_available")
        ET.parse(output / "junit.xml")

    def test_changed_run_rejects_unapproved_golden_updates(self) -> None:
        completed, output = self.run_eval(
            "--changed-file",
            "evals/golden/critical-capabilities.json",
        )

        self.assertEqual(completed.returncode, 2)
        failures = json.loads((output / "failures.json").read_text(encoding="utf-8"))
        self.assertEqual(failures[0]["severity"], "HARD_FAIL")
        self.assertIn("protected", failures[0]["reason"].lower())

    def test_changed_run_rejects_uncontracted_canonical_capability(self) -> None:
        completed, output = self.run_eval(
            "--changed-file",
            "skills/review-code-change/SKILL.md",
        )

        self.assertEqual(completed.returncode, 2)
        failures = json.loads((output / "failures.json").read_text(encoding="utf-8"))
        self.assertIn("lacks an evaluation contract", failures[0]["reason"])

    def test_repeat_does_not_repeat_deterministic_checks(self) -> None:
        completed, output = self.run_eval(
            "--capability",
            "maintain-project-memory",
            "--repeat",
            "3",
        )

        self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
        results = json.loads((output / "capabilities.json").read_text(encoding="utf-8"))
        deterministic = [item for item in results if item["deterministic"]]
        self.assertTrue(deterministic)
        self.assertTrue(all(item["run"] == 1 for item in deterministic))

    def test_nightly_profile_uses_configured_repeat_default(self) -> None:
        completed, output = self.run_eval(
            "--capability",
            "maintain-project-memory",
            "--profile",
            "nightly",
        )

        self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
        results = json.loads((output / "capabilities.json").read_text(encoding="utf-8"))
        behavior = [item for item in results if item["scenario"] == "behavior"]
        self.assertEqual(len(behavior), 3)

    def test_python_interpreter_can_be_selected_for_deterministic_suites(self) -> None:
        completed, _ = self.run_eval(
            "--capability",
            "maintain-project-memory",
            "--python",
            sys.executable,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)

    def test_deterministic_suites_do_not_inherit_semantic_runtime_configuration(self) -> None:
        with mock.patch.dict(os.environ, {
            "EVAL_EXECUTOR_MODEL": "gpt-5.6-sol",
            "EVAL_CODEX_BIN": "/usr/bin/false",
            "EVAL_PROVIDER": "openai",
            "EVAL_JUDGE_MODEL": "gpt-5.6-sol",
            "OPENAI_API_KEY": "synthetic-test-key",
            "CODEX_ACCESS_TOKEN": "synthetic-access-token",
        }, clear=False):
            completed, _ = self.run_eval(
                "--capability",
                "maintain-project-memory",
            )

        self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)

    def test_deterministic_environment_removes_runtime_credentials(self) -> None:
        sanitized = deterministic_environment({
            "PATH": "/usr/bin",
            "EVAL_PROVIDER": "openai",
            "AZURE_OPENAI_API_KEY": "azure-secret",
            "OPENAI_API_KEY": "openai-secret",
            "CODEX_ACCESS_TOKEN": "codex-secret",
            "SYSTEM_ACCESSTOKEN": "pipeline-secret",
        })

        self.assertEqual(sanitized, {"PATH": "/usr/bin"})

    def test_baseline_pass_rate_regression_returns_one(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        baseline = Path(temporary.name) / "baseline.json"
        baseline.write_text(json.dumps({
            "schema_version": 1,
            "status": "accepted",
            "scenarios": {
                "maintain-project-memory:behavior": {
                    "pass_rate": 1.0,
                    "duration_mean_seconds": 0.0,
                    "tokens_mean": None,
                }
            },
        }), encoding="utf-8")

        completed, output = self.run_eval(
            "--capability",
            "maintain-project-memory",
            "--compare-baseline",
            str(baseline),
        )

        self.assertEqual(completed.returncode, 1, completed.stderr + completed.stdout)
        failures = json.loads((output / "failures.json").read_text(encoding="utf-8"))
        self.assertTrue(any(item["severity"] == "REGRESSION_FAIL" for item in failures))
        performance = json.loads((output / "performance.json").read_text(encoding="utf-8"))
        behavior = next(item for item in performance if item["scenario"] == "maintain-project-memory:behavior")
        self.assertEqual(behavior["runs"], 1)

    def test_baseline_regression_cannot_replace_accepted_baseline(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name)
        baseline = directory / "baseline.json"
        replacement = directory / "replacement.json"
        executor = directory / "executor.py"
        judge = directory / "judge.py"
        executor.write_text(
            "import json, sys\nrequest = json.load(sys.stdin)\n"
            "print(json.dumps({'generated_result': {}, 'evidence': [{'id': 'E1', "
            "'source': request['scenario_input']['source_artifacts'][0], 'locator': 'synthetic:1'}]}))\n",
            encoding="utf-8",
        )
        judge.write_text(
            "import json, sys\nrequest = json.load(sys.stdin)\n"
            "required = []\n"
            "for field in ('expected_facts', 'invariants', 'required_sequence', 'hard_assertions'):\n"
            "    required.extend(request['expected'].get(field, []))\n"
            "assertions = [{'assertion': item, 'status': 'PASS', 'confidence': 1.0, "
            "'reason': 'covered', 'evidence': request['evidence'][0]['id']} for item in required]\n"
            "print(json.dumps({'assertions': assertions, 'metrics': {'correctness': 0.96, "
            "'completeness': 1.0, 'evidence_grounding': 1.0, 'traceability': 1.0, "
            "'scope_discipline': 1.0, 'handoff_quality': 1.0}}))\n",
            encoding="utf-8",
        )
        baseline.write_text(json.dumps({
            "schema_version": 1,
            "status": "accepted",
            "scenarios": {
                "maintain-project-memory:behavior": {
                    "pass_rate": 1.0,
                    "duration_mean_seconds": 0.0,
                    "tokens_mean": None,
                    "metrics_mean": {"correctness": 1.0},
                }
            },
        }), encoding="utf-8")

        completed, _ = self.run_eval(
            "--capability",
            "maintain-project-memory",
            "--compare-baseline",
            str(baseline),
            "--write-baseline",
            str(replacement),
            "--executor-command",
            f"python3 {executor}",
            "--judge-command",
            f"python3 {judge}",
            "--require-semantic",
        )

        self.assertEqual(completed.returncode, 2, completed.stderr + completed.stdout)
        self.assertFalse(replacement.exists())

    def test_green_runner_still_cannot_promote_last_green_baseline(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        replacement = Path(temporary.name) / "replacement.json"

        completed, output = self.run_eval(
            "--capability", "validate-commons", "--write-baseline", str(replacement),
        )

        self.assertEqual(completed.returncode, 2, completed.stderr + completed.stdout)
        self.assertFalse(replacement.exists())
        failures = json.loads((output / "failures.json").read_text(encoding="utf-8"))
        self.assertTrue(any("never promotes" in (item.get("reason") or "") for item in failures))

    def test_failed_visual_report_is_a_hard_failure(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        report = Path(temporary.name) / "visual-report.json"
        report.write_text(json.dumps({"status": "FAIL", "results": []}), encoding="utf-8")

        completed, output = self.run_eval(
            "--capability", "validate-commons", "--visual-report", str(report),
        )

        self.assertEqual(completed.returncode, 2, completed.stderr + completed.stdout)
        failures = json.loads((output / "failures.json").read_text(encoding="utf-8"))
        self.assertTrue(any(item["capability"] == "visual-regression" for item in failures))

    def test_minor_visual_baseline_decrease_is_warning(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        baseline = Path(temporary.name) / "baseline.json"
        baseline.write_text(json.dumps({
            "schema_version": 1,
            "status": "accepted",
            "scenarios": {
                "visual-capability:behavior": {
                    "pass_rate": 1.0,
                    "duration_mean_seconds": 0.0,
                    "tokens_mean": None,
                    "metrics_mean": {"visual_quality": 0.96},
                }
            },
        }), encoding="utf-8")
        performance = [{
            "scenario": "visual-capability:behavior",
            "pass_rate": 1.0,
            "duration_mean_seconds": 0.0,
            "tokens_mean": None,
            "score_mean": 0.95,
            "metrics_mean": {"visual_quality": 0.95},
        }]

        results = apply_baseline_comparison([], performance, baseline, load_thresholds())

        self.assertEqual(results[0]["status"], WARNING)
        self.assertIn("within tolerance", results[0]["reason"])

    def test_reused_unittest_module_preserves_its_failure(self) -> None:
        scenario = {
            "id": "shared-test",
            "level": 3,
            "deterministic": True,
            "execution": {"kind": "unittest", "modules": ["does.not.exist"]},
        }
        cache: dict[str, dict[str, object]] = {}

        first = run_unittest_scenario("first", "workflow", scenario, sys.executable, cache)
        second = run_unittest_scenario("second", "workflow", scenario, sys.executable, cache)

        self.assertEqual(first["status"], HARD_FAIL)
        self.assertEqual(second["status"], HARD_FAIL)
        self.assertIn("does.not.exist", second["reason"])

    def test_repeated_semantic_variance_is_a_regression(self) -> None:
        scenario = {"id": "behavior", "level": 2}
        repeated = [
            result_record("sample", "skill", "behavior", 2, 1, False, PASS, 0.1, metrics={"consistency": 0.8}),
            result_record("sample", "skill", "behavior", 2, 2, False, PASS, 0.1, metrics={"consistency": 1.0}),
        ]

        result = evaluate_repeat_consistency(
            "sample", "skill", scenario, repeated, load_thresholds(),
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["status"], REGRESSION_FAIL)
        self.assertIn("variance", result["reason"])

    def test_external_executor_and_independent_judge_repeat_stochastic_scenario(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name)
        executor = directory / "executor.py"
        judge = directory / "judge.py"
        executor.write_text(
            "import json, sys\nfrom pathlib import Path\n"
            "request = json.load(sys.stdin)\n"
            "assert 'expected' not in request\n"
            "assert request['scenario_input']['prompt']\n"
            "assert request['workspace_root'] == '.'\n"
            "assert all(Path(item).is_file() for item in request['scenario_input']['source_artifacts'])\n"
            "print(json.dumps({'generated_result': {'capability': request['capability']}, "
            "'evidence': [{'id': 'E1', 'source': request['scenario_input']['source_artifacts'][0], "
            "'locator': 'synthetic:1'}], 'tokens': 250}))\n",
            encoding="utf-8",
        )
        judge.write_text(
            "import hashlib, json, sys\n"
            "request = json.load(sys.stdin)\n"
            "assert set(request) == {'scenario', 'expected', 'generated_result', 'evidence', 'executor_artifacts', 'deterministic_findings', 'required_metrics'}\n"
            "assert 'handoff_quality' in request['required_metrics']\n"
            "assert any(item['scenario'] == 'workspace-policy' and item['status'] == 'PASS' "
            "for item in request['deterministic_findings'])\n"
            "from pathlib import Path\n"
            "assert all(Path(item).is_file() for item in request['scenario']['input']['source_artifacts'])\n"
            "assert all(hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest "
            "for path, digest in request['scenario']['artifact_manifest'].items())\n"
            "required = []\n"
            "for field in ('expected_facts', 'invariants', 'required_sequence', 'hard_assertions'):\n"
            "    required.extend(request['expected'].get(field, []))\n"
            "assertions = [{'assertion': item, 'status': 'PASS', 'confidence': 1.0, "
            "'reason': 'synthetic fixture satisfies the contract', 'evidence': request['evidence'][0]['id']} "
            "for item in required]\n"
            "print(json.dumps({'assertions': assertions, 'metrics': {'correctness': 1.0, "
            "'completeness': 1.0, 'evidence_grounding': 1.0, 'traceability': 1.0, "
            "'scope_discipline': 1.0, 'handoff_quality': 1.0}}))\n",
            encoding="utf-8",
        )

        completed, output = self.run_eval(
            "--capability",
            "maintain-project-memory",
            "--repeat",
            "3",
            "--executor-command",
            f"python3 {executor}",
            "--judge-command",
            f"python3 {judge}",
            "--require-semantic",
        )

        self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
        results = json.loads((output / "capabilities.json").read_text(encoding="utf-8"))
        behavior = [item for item in results if item["scenario"] == "behavior"]
        self.assertEqual(len(behavior), 3)
        self.assertTrue(all(item["status"] == "PASS" for item in behavior))

    def test_failed_hard_assertion_returns_two(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name)
        executor = directory / "executor.py"
        judge = directory / "judge.py"
        executor.write_text(
            "import json, sys\nrequest = json.load(sys.stdin)\n"
            "assert 'expected' not in request\n"
            "print(json.dumps({'generated_result': {}, 'evidence': [{'id': 'E1', "
            "'source': request['scenario_input']['source_artifacts'][0], 'locator': 'synthetic:1'}]}))\n",
            encoding="utf-8",
        )
        judge.write_text(
            "import json, sys\nrequest = json.load(sys.stdin)\n"
            "required = []\n"
            "for field in ('expected_facts', 'invariants', 'required_sequence', 'hard_assertions'):\n"
            "    required.extend(request['expected'].get(field, []))\n"
            "assertions = [{'assertion': item, "
            "'status': 'FAIL' if item == 'red_evidence_present' else 'PASS', 'confidence': 1.0, "
            "'reason': 'no failing test was observed' if item == 'red_evidence_present' else 'covered', "
            "'evidence': request['evidence'][0]['id']} for item in required]\n"
            "print(json.dumps({'assertions': assertions, "
            "'metrics': {'correctness': 1.0, 'completeness': 1.0, 'evidence_grounding': 1.0, "
            "'traceability': 1.0, 'scope_discipline': 1.0, 'handoff_quality': 1.0}}))\n",
            encoding="utf-8",
        )

        completed, output = self.run_eval(
            "--capability",
            "test-driven-development",
            "--executor-command",
            f"python3 {executor}",
            "--judge-command",
            f"python3 {judge}",
            "--require-semantic",
        )

        self.assertEqual(completed.returncode, 2, completed.stderr + completed.stdout)
        failures = json.loads((output / "failures.json").read_text(encoding="utf-8"))
        self.assertTrue(any(item["severity"] == "HARD_FAIL" for item in failures))

    def test_incomplete_judge_assertion_coverage_returns_two(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name)
        executor = directory / "executor.py"
        judge = directory / "judge.py"
        executor.write_text(
            "import json, sys\nrequest = json.load(sys.stdin)\n"
            "print(json.dumps({'generated_result': {}, 'evidence': [{'id': 'E1', "
            "'source': request['scenario_input']['source_artifacts'][0], 'locator': 'synthetic:1'}]}))\n",
            encoding="utf-8",
        )
        judge.write_text(
            "import json, sys\nrequest = json.load(sys.stdin)\n"
            "print(json.dumps({'assertions': [{'assertion': request['expected']['expected_facts'][0], "
            "'status': 'PASS', 'confidence': 1.0, 'reason': 'only one fact checked', "
            "'evidence': request['evidence'][0]['id']}], 'metrics': {'correctness': 1.0, "
            "'completeness': 1.0, 'evidence_grounding': 1.0, 'traceability': 1.0, "
            "'scope_discipline': 1.0, 'handoff_quality': 1.0}}))\n",
            encoding="utf-8",
        )

        completed, output = self.run_eval(
            "--capability",
            "maintain-project-memory",
            "--executor-command",
            f"python3 {executor}",
            "--judge-command",
            f"python3 {judge}",
            "--require-semantic",
        )

        self.assertEqual(completed.returncode, 2, completed.stderr + completed.stdout)
        failures = json.loads((output / "failures.json").read_text(encoding="utf-8"))
        self.assertTrue(any("missing required assertion coverage" in item["reason"] for item in failures))

    def test_applicable_consistency_metric_cannot_be_omitted(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name)
        executor = directory / "executor.py"
        judge = directory / "judge.py"
        executor.write_text(
            "import json, sys\nrequest = json.load(sys.stdin)\n"
            "print(json.dumps({'generated_result': {}, 'evidence': [{'id': 'E1', "
            "'source': request['scenario_input']['source_artifacts'][0], 'locator': 'synthetic:1'}]}))\n",
            encoding="utf-8",
        )
        judge.write_text(
            "import json, sys\nrequest = json.load(sys.stdin)\n"
            "required = []\n"
            "for field in ('expected_facts', 'invariants', 'required_sequence', 'hard_assertions'):\n"
            "    required.extend(request['expected'].get(field, []))\n"
            "assertions = [{'assertion': item, 'status': 'PASS', 'confidence': 1.0, "
            "'reason': 'covered', 'evidence': request['evidence'][0]['id']} for item in required]\n"
            "print(json.dumps({'assertions': assertions, 'metrics': {'correctness': 1.0, "
            "'completeness': 1.0, 'evidence_grounding': 1.0, 'precision': 1.0, "
            "'traceability': 1.0, 'scope_discipline': 1.0, 'handoff_quality': 1.0}}))\n",
            encoding="utf-8",
        )

        completed, output = self.run_eval(
            "--capability",
            "analyze-legacy-system",
            "--repeat",
            "3",
            "--executor-command",
            f"python3 {executor}",
            "--judge-command",
            f"python3 {judge}",
            "--require-semantic",
        )

        self.assertEqual(completed.returncode, 2, completed.stderr + completed.stdout)
        failures = json.loads((output / "failures.json").read_text(encoding="utf-8"))
        self.assertTrue(any("consistency" in item["reason"] for item in failures))

    def test_invalid_executor_token_count_is_a_structured_hard_failure(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name)
        executor = directory / "executor.py"
        judge = directory / "judge.py"
        executor.write_text(
            "import json, sys\njson.load(sys.stdin)\n"
            "print(json.dumps({'generated_result': {}, 'evidence': [], 'tokens': True}))\n",
            encoding="utf-8",
        )
        judge.write_text("raise SystemExit('judge must not run')\n", encoding="utf-8")

        completed, output = self.run_eval(
            "--capability",
            "maintain-project-memory",
            "--executor-command",
            f"python3 {executor}",
            "--judge-command",
            f"python3 {judge}",
            "--require-semantic",
        )

        self.assertEqual(completed.returncode, 2, completed.stderr + completed.stdout)
        failures = json.loads((output / "failures.json").read_text(encoding="utf-8"))
        self.assertTrue(any("tokens" in item["reason"] for item in failures))

    def test_unbounded_executor_evidence_is_a_hard_failure(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name)
        executor = directory / "executor.py"
        judge = directory / "judge.py"
        executor.write_text(
            "import json, sys\njson.load(sys.stdin)\n"
            "print(json.dumps({'generated_result': {}, 'evidence': [{'id': 'E1', "
            "'source': 'not-in-the-fixture.txt', 'locator': 'line:1'}]}))\n",
            encoding="utf-8",
        )
        judge.write_text("raise SystemExit('judge must not run')\n", encoding="utf-8")

        completed, output = self.run_eval(
            "--capability",
            "maintain-project-memory",
            "--executor-command",
            f"python3 {executor}",
            "--judge-command",
            f"python3 {judge}",
            "--require-semantic",
        )

        self.assertEqual(completed.returncode, 2, completed.stderr + completed.stdout)
        failures = json.loads((output / "failures.json").read_text(encoding="utf-8"))
        self.assertTrue(any("unbounded sources" in item["reason"] for item in failures))

    def test_executor_evidence_locator_must_resolve_in_the_source(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name)
        executor = directory / "executor.py"
        judge = directory / "judge.py"
        executor.write_text(
            "import json, sys\nrequest = json.load(sys.stdin)\n"
            "source = request['scenario_input']['source_artifacts'][0]\n"
            "print(json.dumps({'generated_result': {'claim': 'unsupported'}, 'evidence': "
            "[{'id': 'E1', 'source': source, 'locator': 'line:999999'}]}))\n",
            encoding="utf-8",
        )
        judge.write_text("raise SystemExit('judge must not run')\n", encoding="utf-8")

        completed, output = self.run_eval(
            "--capability", "maintain-project-memory",
            "--executor-command", f"python3 {executor}",
            "--judge-command", f"python3 {judge}",
            "--require-semantic",
        )

        self.assertEqual(completed.returncode, 2, completed.stderr + completed.stdout)
        failures = json.loads((output / "failures.json").read_text(encoding="utf-8"))
        self.assertTrue(any("locators do not resolve" in item["reason"] for item in failures))

    def test_bare_executor_line_range_resolves_against_its_declared_source(self) -> None:
        failures = validate_evidence_locators(
            [{"id": "E1", "source": "input/sample.py", "locator": "2-3"}],
            {"input/sample.py": "one\ntwo\nthree\n"},
        )

        self.assertEqual(failures, [])

    def test_executor_evidence_sources_normalize_safe_relative_variants(self) -> None:
        self.assertEqual(
            normalize_evidence_source(" ./evals/fixtures/input.md "),
            "evals/fixtures/input.md",
        )
        self.assertIsNone(normalize_evidence_source("../outside.md"))
        self.assertIsNone(normalize_evidence_source("/absolute/outside.md"))

    def test_judge_assertion_filter_discards_non_golden_criteria(self) -> None:
        judgement = {
            "assertions": [
                {"assertion": "required fact", "status": "PASS"},
                {"assertion": "scenario prompt", "status": "PASS"},
            ],
            "metrics": {"correctness": 1.0},
        }

        filtered = filter_required_judge_assertions(judgement, {"required fact"})

        self.assertEqual(
            filtered["assertions"],
            [{"assertion": "required fact", "status": "PASS"}],
        )
        self.assertEqual(filtered["metrics"], {"correctness": 1.0})

    def test_duplicate_executor_evidence_ids_are_a_hard_failure(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name)
        executor = directory / "executor.py"
        judge = directory / "judge.py"
        executor.write_text(
            "import json, sys\nrequest = json.load(sys.stdin)\n"
            "source = request['scenario_input']['source_artifacts'][0]\n"
            "print(json.dumps({'generated_result': {}, 'evidence': ["
            "{'id': 'E1', 'source': source, 'locator': 'line:1'}, "
            "{'id': 'E1', 'source': source, 'locator': 'line:2'}]}))\n",
            encoding="utf-8",
        )
        judge.write_text("raise SystemExit('judge must not run')\n", encoding="utf-8")

        completed, output = self.run_eval(
            "--capability", "maintain-project-memory",
            "--executor-command", f"python3 {executor}",
            "--judge-command", f"python3 {judge}",
            "--require-semantic",
        )

        self.assertEqual(completed.returncode, 2, completed.stderr + completed.stdout)
        failures = json.loads((output / "failures.json").read_text(encoding="utf-8"))
        self.assertTrue(any("duplicate evidence IDs" in item["reason"] for item in failures))

    def test_external_executor_repository_write_is_a_hard_failure(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name)
        executor = directory / "executor.py"
        judge = directory / "judge.py"
        probe = ROOT / "evals" / "fixtures" / "evaluation" / "executor-write-probe.txt"
        self.addCleanup(lambda: probe.unlink(missing_ok=True))
        executor.write_text(
            "import json, sys\nfrom pathlib import Path\njson.load(sys.stdin)\n"
            f"Path({str(probe)!r}).write_text('unexpected write', encoding='utf-8')\n"
            "print(json.dumps({'generated_result': {}, 'evidence': []}))\n",
            encoding="utf-8",
        )
        judge.write_text("raise SystemExit('judge must not run')\n", encoding="utf-8")

        completed, output = self.run_eval(
            "--capability",
            "maintain-project-memory",
            "--executor-command",
            f"python3 {executor}",
            "--judge-command",
            f"python3 {judge}",
            "--require-semantic",
        )

        self.assertEqual(completed.returncode, 2, completed.stderr + completed.stdout)
        failures = json.loads((output / "failures.json").read_text(encoding="utf-8"))
        self.assertTrue(any("modified repository paths" in item["reason"] for item in failures))

    def test_external_executor_cannot_modify_isolated_source_fixture(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name)
        executor = directory / "executor.py"
        judge = directory / "judge.py"
        executor.write_text(
            "import json, sys\nfrom pathlib import Path\nrequest = json.load(sys.stdin)\n"
            "Path(request['scenario_input']['source_artifacts'][0]).write_text('changed', encoding='utf-8')\n"
            "print(json.dumps({'generated_result': {}, 'evidence': []}))\n",
            encoding="utf-8",
        )
        judge.write_text("raise SystemExit('judge must not run')\n", encoding="utf-8")

        completed, output = self.run_eval(
            "--capability",
            "maintain-project-memory",
            "--executor-command",
            f"python3 {executor}",
            "--judge-command",
            f"python3 {judge}",
            "--require-semantic",
        )

        self.assertEqual(completed.returncode, 2, completed.stderr + completed.stdout)
        failures = json.loads((output / "failures.json").read_text(encoding="utf-8"))
        self.assertTrue(any("modified isolated fixture paths" in item["reason"] for item in failures))

    def test_external_executor_cannot_change_isolated_source_mode(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name)
        executor = directory / "executor.py"
        judge = directory / "judge.py"
        executor.write_text(
            "import json, os, sys\nrequest = json.load(sys.stdin)\n"
            "os.chmod(request['scenario_input']['source_artifacts'][0], 0o600)\n"
            "print(json.dumps({'generated_result': {}, 'evidence': []}))\n",
            encoding="utf-8",
        )
        judge.write_text("raise SystemExit('judge must not run')\n", encoding="utf-8")

        completed, output = self.run_eval(
            "--capability", "maintain-project-memory",
            "--executor-command", f"python3 {executor}",
            "--judge-command", f"python3 {judge}",
            "--require-semantic",
        )

        self.assertEqual(completed.returncode, 2, completed.stderr + completed.stdout)
        failures = json.loads((output / "failures.json").read_text(encoding="utf-8"))
        self.assertTrue(any("modified isolated fixture paths" in item["reason"] for item in failures))


if __name__ == "__main__":
    unittest.main()
