#!/usr/bin/env python3
"""Behavioral tests for fact scoring and last-green quality baselines."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "evals"))

from eval_common import load_thresholds  # noqa: E402
from run_evals import (  # noqa: E402
    HARD_FAIL,
    REGRESSION_FAIL,
    WARNING,
    bounded_evidence_contents,
    calculate_fact_metrics,
    classify_assertion_failures,
    compare_performance_to_baseline,
    directory_snapshot,
    invalid_workspace_changes,
    normalize_performance_metrics,
)


class QualityBaselineTests(unittest.TestCase):
    def test_recall_precision_and_unsupported_findings_are_calculated(self) -> None:
        golden = {
            "expected_facts": [
                {"id": "fact-a", "severity": "CRITICAL", "text": "A"},
                {"id": "fact-b", "severity": "MAJOR", "text": "B"},
            ]
        }
        judgement = {
            "assertions": [
                {"assertion": "fact-a", "status": "PASS"},
                {"assertion": "fact-b", "status": "FAIL"},
            ],
            "unsupported_findings": ["invented-c"],
        }

        metrics = calculate_fact_metrics(judgement, golden)

        self.assertEqual(metrics["expected_facts"], 2)
        self.assertEqual(metrics["correct_findings"], 1)
        self.assertEqual(metrics["unsupported_findings"], 1)
        self.assertEqual(metrics["recall"], 0.5)
        self.assertEqual(metrics["precision"], 0.5)

    def test_missing_critical_fact_hard_fails_even_with_high_aggregate_recall(self) -> None:
        golden = {
            "expected_facts": [
                {"id": "critical-transaction", "severity": "CRITICAL", "text": "critical"},
                *[
                    {"id": f"minor-{index}", "severity": "MINOR", "text": "minor"}
                    for index in range(20)
                ],
            ]
        }

        self.assertEqual(
            classify_assertion_failures({"critical-transaction"}, golden),
            HARD_FAIL,
        )

    def test_baseline_comparison_exposes_current_baseline_delta_threshold(self) -> None:
        baseline = {
            "schema_version": 1,
            "status": "accepted",
            "baseline_commit": "abc123",
            "created_at": "2030-01-01T00:00:00Z",
            "accepted_run": {"id": "nightly-1", "branch": "main", "profile": "nightly"},
            "scenarios": {
                "legacy-modernization:e2e": {
                    "pass_rate": 1.0,
                    "metrics_mean": {"completeness": 0.941},
                    "duration_mean_seconds": 820.0,
                    "tokens_mean": 184000.0,
                }
            },
        }
        current = [{
            "scenario": "legacy-modernization:e2e",
            "pass_rate": 1.0,
            "metrics_mean": {"completeness": 0.882},
            "duration_mean_seconds": 610.0,
            "tokens_mean": 131000.0,
        }]

        comparison, results = compare_performance_to_baseline(
            current, baseline, load_thresholds()
        )

        row = next(item for item in comparison["rows"] if item["metric"] == "completeness")
        self.assertEqual(row["baseline"], 0.941)
        self.assertEqual(row["current"], 0.882)
        self.assertAlmostEqual(row["delta"], -0.059)
        self.assertEqual(row["threshold"], 0.03)
        self.assertEqual(row["status"], REGRESSION_FAIL)
        self.assertTrue(any(item["status"] == REGRESSION_FAIL for item in results))

    def test_bootstrap_baseline_is_reported_as_unavailable_not_green(self) -> None:
        comparison, results = compare_performance_to_baseline(
            [{"scenario": "legacy-modernization:e2e"}],
            {"status": "bootstrap", "baseline_commit": "not_available", "scenarios": {}},
            load_thresholds(),
        )

        self.assertEqual(comparison["status"], "NOT_AVAILABLE")
        self.assertEqual(results[0]["status"], WARNING)

    def test_missing_observability_is_not_available_not_fabricated(self) -> None:
        metrics = normalize_performance_metrics({})

        self.assertEqual(metrics["llm_calls"], "not_available")
        self.assertEqual(metrics["input_tokens"], "not_available")
        self.assertEqual(metrics["duplicate_source_reads"], "not_available")
        self.assertEqual(metrics["external_searches"], "not_available")

    def test_fixture_workspace_policy_allows_tdd_edits_but_not_unrelated_writes(self) -> None:
        fixture = json.loads((
            ROOT / "evals/fixtures/projects/development-delivery/input/scenario.json"
        ).read_text(encoding="utf-8"))
        source = fixture["source_artifacts"][2]
        generated = "evals/fixtures/projects/development-delivery/input/build/test-results.xml"

        self.assertEqual(invalid_workspace_changes([source, generated], fixture), [])
        self.assertEqual(invalid_workspace_changes(["outside.txt"], fixture), ["outside.txt"])

    def test_semantic_fixture_policies_allow_only_declared_generated_outputs(self) -> None:
        scenarios = json.loads((
            ROOT / "evals/fixtures/evaluation/scenarios.json"
        ).read_text(encoding="utf-8"))
        expected_changes = {
            "initialize-project": [
                ".agent-commons.yaml",
                ".agent-commons/memory/README.md",
                ".gitignore",
                "README.md",
            ],
            "maintain-project-memory": [
                ".agent-commons/memory/state.json",
            ],
            "test-driven-development": ["synthetic.py", "synthetic_test.py"],
            "create-branded-html-artifact": ["artifact/index.html"],
            "legacy-discovery-specialist": ["worker-result.json"],
            "commons-governance": [
                "catalog/capabilities.yaml",
                "skills/synthetic-release-verification/SKILL.md",
            ],
        }

        for identifier, changed in expected_changes.items():
            with self.subTest(identifier=identifier):
                self.assertEqual(invalid_workspace_changes(changed, scenarios[identifier]), [])
                self.assertEqual(
                    invalid_workspace_changes(["outside-policy.txt"], scenarios[identifier]),
                    ["outside-policy.txt"],
                )

    def test_project_fixture_policies_allow_declared_delivery_outputs(self) -> None:
        expected_changes = {
            "legacy-modernization": ["outputs/legacy-modernization/analysis.json"],
            "dashboard-quality": ["dashboard/index.html"],
            "public-sector-delivery": ["delivery/presentation/index.html"],
        }

        for identifier, changed in expected_changes.items():
            fixture = json.loads((
                ROOT / f"evals/fixtures/projects/{identifier}/input/scenario.json"
            ).read_text(encoding="utf-8"))
            with self.subTest(identifier=identifier):
                self.assertEqual(invalid_workspace_changes(changed, fixture), [])
                self.assertEqual(
                    invalid_workspace_changes(["outside-policy.txt"], fixture),
                    ["outside-policy.txt"],
                )

    def test_all_isolated_workspace_files_are_bounded_evidence_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            capability = workspace / "skills/example/scripts/helper.py"
            capability.parent.mkdir(parents=True)
            capability.write_text("first\nsecond\n", encoding="utf-8")
            contents = bounded_evidence_contents(
                workspace,
                {"skills/example/scripts/helper.py": "snapshot"},
                {"artifact/report.md": b"result\n"},
            )

        self.assertEqual(
            set(contents),
            {"skills/example/scripts/helper.py", "artifact/report.md"},
        )
        self.assertEqual(contents["skills/example/scripts/helper.py"], "first\nsecond\n")
        self.assertEqual(contents["artifact/report.md"], "result\n")

    def test_review_scenarios_supply_their_named_synthetic_inputs(self) -> None:
        scenarios = json.loads((
            ROOT / "evals/fixtures/evaluation/scenarios.json"
        ).read_text(encoding="utf-8"))
        named_inputs = {
            "architecture-reviewer": ["design", "evidence"],
            "privacy-security-reviewer": ["data_flow"],
            "test-behavior-reviewer": ["test_evidence"],
            "specify-openspec-change": ["existing_spec"],
            "sales-storytelling": ["evidence"],
        }

        for identifier, fields in named_inputs.items():
            scenario = scenarios[identifier]
            sources = set(scenario["source_artifacts"])
            for field in fields:
                with self.subTest(identifier=identifier, field=field):
                    path = scenario["inputs"][field]
                    self.assertIn(path, sources)
                    self.assertTrue((ROOT / path).is_file(), path)

    def test_dashboard_scenarios_include_runtime_dependencies_as_read_only_sources(self) -> None:
        required = {
            "skills/continue-project/scripts/resolve_project_continuation.py",
            "skills/localize-client-artifact/assets/bilingual-runtime.js",
        }
        capability_scenarios = json.loads((
            ROOT / "evals/fixtures/evaluation/scenarios.json"
        ).read_text(encoding="utf-8"))
        project_scenario = json.loads((
            ROOT / "evals/fixtures/projects/dashboard-quality/input/scenario.json"
        ).read_text(encoding="utf-8"))

        self.assertTrue(required <= set(capability_scenarios["build-living-dashboard"]["source_artifacts"]))
        self.assertTrue(required <= set(project_scenario["source_artifacts"]))

    def test_workspace_snapshot_ignores_python_bytecode_caches(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "package/module.py"
            bytecode = root / "package/__pycache__/module.cpython-311.pyc"
            source.parent.mkdir(parents=True)
            bytecode.parent.mkdir(parents=True)
            source.write_text("VALUE = 1\n", encoding="utf-8")
            bytecode.write_bytes(b"python-bytecode")

            snapshot = directory_snapshot(root)

            self.assertIn("package/module.py", snapshot)
            self.assertNotIn("package/__pycache__/module.cpython-311.pyc", snapshot)

    def test_promote_baseline_requires_explicit_accepted_green_main_run(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run = root / "run"
            run.mkdir()
            (run / "quality-summary.json").write_text(json.dumps({
                "schema_version": 1,
                "status": "PASS",
                "current_commit": "abc123",
                "counts": {"warnings": 0, "regression_failures": 0, "hard_failures": 0},
                "selection": {"profile": "full", "branch": "main"},
            }), encoding="utf-8")
            (run / "performance.json").write_text(json.dumps([{
                "scenario": "legacy-modernization:e2e", "runs": 1, "pass_rate": 1.0,
                "score_mean": 0.98, "score_worst": 0.98, "score_variance": 0.0,
                "metrics_mean": {"correctness": 0.98}, "metrics_worst": {"correctness": 0.98},
                "metrics_variance": {"correctness": 0.0},
                "duration_mean_seconds": 10.0, "duration_worst_seconds": 10.0,
                "tokens_mean": "not_available", "tokens_worst": "not_available",
                "performance_metrics": {"llm_calls": "not_available"},
            }]), encoding="utf-8")
            output = root / "last-green.json"
            command = [
                "python3", str(ROOT / "tools/evals/promote_baseline.py"),
                "--run-dir", str(run), "--output", str(output),
                "--accepted-run", "nightly-42", "--branch", "main",
            ]

            accepted = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)

            self.assertEqual(accepted.returncode, 0, accepted.stdout + accepted.stderr)
            baseline = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(baseline["baseline_commit"], "abc123")
            self.assertEqual(baseline["accepted_run"]["id"], "nightly-42")
            self.assertEqual(baseline["accepted_run"]["branch"], "main")
            self.assertEqual(baseline["accepted_run"]["profile"], "full")

            rejected = subprocess.run(
                command[:-2] + ["--branch", "feature"], cwd=ROOT, capture_output=True, text=True,
            )
            self.assertNotEqual(rejected.returncode, 0)

            summary = json.loads((run / "quality-summary.json").read_text(encoding="utf-8"))
            summary["selection"].pop("branch")
            (run / "quality-summary.json").write_text(json.dumps(summary), encoding="utf-8")
            missing_provenance = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertNotEqual(missing_provenance.returncode, 0)

            summary["selection"] = {"profile": "pr", "branch": "main"}
            (run / "quality-summary.json").write_text(json.dumps(summary), encoding="utf-8")
            wrong_profile = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertNotEqual(wrong_profile.returncode, 0)

    def test_legacy_executor_workspace_excludes_hidden_answer_key(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            executor = root / "executor.py"
            judge = root / "judge.py"
            output = root / "output"
            executor.write_text(
                "import json, sys\nfrom pathlib import Path\n"
                "request=json.load(sys.stdin)\n"
                "assert 'expected' not in request\n"
                "assert not list(Path('.').rglob('golden/*'))\n"
                "source=request['scenario_input']['source_artifacts'][0]\n"
                "print(json.dumps({'generated_result': {}, 'evidence': [{'id':'E1','source':source,'locator':'fixture:1'}]}))\n",
                encoding="utf-8",
            )
            judge.write_text(
                "import json, sys\nrequest=json.load(sys.stdin)\nrequired=[]\n"
                "for field in ('expected_facts','invariants','required_sequence','hard_assertions'):\n"
                "  for item in request['expected'].get(field,[]): required.append(item.get('id') if isinstance(item,dict) else item)\n"
                "assertions=[{'assertion':item,'status':'PASS','confidence':1.0,'reason':'covered','evidence':'E1'} for item in dict.fromkeys(required)]\n"
                "metrics={name:1.0 for name in ('correctness','completeness','evidence_grounding','traceability','scope_discipline','handoff_quality','consistency')}\n"
                "print(json.dumps({'assertions':assertions,'metrics':metrics,'unsupported_findings':[]}))\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    "python3", str(ROOT / "tools/evals/run_evals.py"),
                    "--workflow", "legacy-modernization", "--repeat", "1",
                    "--executor-command", f"python3 {executor}",
                    "--judge-command", f"python3 {judge}", "--require-semantic",
                    "--output", str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            results = json.loads((output / "capabilities.json").read_text(encoding="utf-8"))
            e2e = next(item for item in results if item["capability"] == "legacy-modernization" and item["scenario"] == "e2e")
            self.assertEqual(e2e["metrics"]["recall"], 1.0)
            self.assertEqual(e2e["metrics"]["precision"], 1.0)

    def test_development_judge_receives_content_addressed_red_green_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            executor = root / "executor.py"
            judge = root / "judge.py"
            output = root / "output"
            executor.write_text(
                "import json, subprocess, sys\nfrom pathlib import Path\n"
                "request=json.load(sys.stdin)\n"
                "base=Path('evals/fixtures/projects/development-delivery/input')\n"
                "red=subprocess.run([sys.executable,'session_service_acceptance.py'],cwd=base,capture_output=True,text=True)\n"
                "assert red.returncode != 0 and 'AssertionError' in red.stderr\n"
                "service=base/'session_service.py'\n"
                "service.write_text(service.read_text().replace('    return \"ACTIVE\"', "
                "'    return \"SESSION_EXPIRED\" if expires_at <= now else \"ACTIVE\"'))\n"
                "green=subprocess.run([sys.executable,'session_service_acceptance.py'],cwd=base,capture_output=True,text=True)\n"
                "assert green.returncode == 0, green.stderr\n"
                "log=base/'build/tdd-evidence.txt'; log.parent.mkdir(parents=True,exist_ok=True)\n"
                "log.write_text('RED expected SESSION_EXPIRED but observed ACTIVE\\nGREEN same focused test passed\\nREFACTOR no behavior change\\nVALIDATION PASS\\n')\n"
                "print(json.dumps({'generated_result': {'requirement':'REQ-AUTH-003','specification':'SPEC-AUTH-003','red':red.returncode,'green':green.returncode}, "
                "'evidence':[{'id':'E-IMPL','source':str(service),'locator':'line:5'},"
                "{'id':'E-RED-GREEN','source':str(log),'locator':'lines:1-4'}]}))\n",
                encoding="utf-8",
            )
            judge.write_text(
                "import json, sys\nfrom pathlib import Path\nrequest=json.load(sys.stdin)\n"
                "base=Path('evals/fixtures/projects/development-delivery/input')\n"
                "service=base/'session_service.py'; log=base/'build/tdd-evidence.txt'\n"
                "assert str(service) in request['executor_artifacts']['files']\n"
                "assert str(log) in request['executor_artifacts']['files']\n"
                "assert 'expires_at <= now' in service.read_text()\n"
                "evidence=log.read_text(); assert 'RED expected SESSION_EXPIRED' in evidence\n"
                "assert 'GREEN same focused test passed' in evidence and 'VALIDATION PASS' in evidence\n"
                "required=[]\nfor field in ('expected_facts','invariants','required_sequence','hard_assertions'):\n"
                "  for item in request['expected'].get(field,[]): required.append(item.get('id') if isinstance(item,dict) else item)\n"
                "assertions=[{'assertion':item,'status':'PASS','confidence':1.0,'reason':'verified from transferred artifacts','evidence':'E-RED-GREEN'} for item in dict.fromkeys(required)]\n"
                "metrics={name:1.0 for name in ('correctness','completeness','evidence_grounding','traceability','scope_discipline','handoff_quality','ownership_discipline','consistency')}\n"
                "print(json.dumps({'assertions':assertions,'metrics':metrics,'unsupported_findings':[]}))\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    "python3", str(ROOT / "tools/evals/run_evals.py"),
                    "--workflow", "development-delivery", "--repeat", "1",
                    "--executor-command", f"python3 {executor}",
                    "--judge-command", f"python3 {judge}", "--require-semantic",
                    "--output", str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            results = json.loads((output / "capabilities.json").read_text(encoding="utf-8"))
            e2e = next(item for item in results if item["capability"] == "development-delivery" and item["scenario"] == "e2e")
            self.assertEqual(e2e["status"], "PASS")
            self.assertEqual(e2e["metrics"]["recall"], 1.0)
            self.assertEqual(e2e["metrics"]["precision"], 1.0)


if __name__ == "__main__":
    unittest.main()
