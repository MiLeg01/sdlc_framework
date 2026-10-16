from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AGGREGATOR = ROOT / "tools" / "evals" / "aggregate_results.py"
sys.path.insert(0, str(ROOT / "tools" / "evals"))

from aggregate_results import discover_shards, git_change_impact  # noqa: E402
from quality_reporting import _reproduction_command  # noqa: E402


def result(
    capability: str,
    status: str = "PASS",
    *,
    subject_kind: str = "skill",
    scenario: str = "contract",
    run: int = 1,
    metrics: dict | None = None,
    duration: float = 0.01,
    tokens: int | None = None,
    score: float | None = None,
    threshold: float | None = 1.0,
    reason: str | None = None,
) -> dict:
    return {
        "capability": capability,
        "subject_kind": subject_kind,
        "scenario": scenario,
        "level": 1,
        "run": run,
        "deterministic": True,
        "status": status,
        "severity": status,
        "score": score if score is not None else (1.0 if status == "PASS" else None),
        "threshold": threshold,
        "duration_seconds": duration,
        "tokens": tokens,
        "reason": reason if status != "PASS" else None,
        "failure_reason": reason if status != "PASS" else None,
        "metrics": metrics or {},
        "performance_metrics": {
            name: "not_available"
            for name in (
                "llm_calls",
                "input_tokens",
                "output_tokens",
                "subagents_launched",
                "context_compactions",
                "source_files_read",
                "duplicate_source_reads",
                "dashboard_renders",
                "external_searches",
            )
        },
    }


class CiAggregationTests(unittest.TestCase):
    def test_shard_discovery_ignores_repository_contract_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            contract = root / "source" / "evals" / "contracts"
            contract.mkdir(parents=True)
            (contract / "capabilities.json").write_text(
                json.dumps({"capabilities": {"synthetic": {}}}),
                encoding="utf-8",
            )
            shard = root / "quality-skills-a"
            shard.mkdir()
            (shard / "capabilities.json").write_text(
                json.dumps([result("one-skill")]),
                encoding="utf-8",
            )
            (shard / "summary.json").write_text(
                json.dumps({"selection": {"capabilities": ["one-skill"]}}),
                encoding="utf-8",
            )

            self.assertEqual(discover_shards(root, root / "aggregate", []), [shard])

    def test_git_change_impact_correlates_changed_tools_to_their_capability(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            subprocess.run(["git", "init", "-b", "main"], cwd=repository, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Eval Test"], cwd=repository, check=True)
            subprocess.run(["git", "config", "user.email", "eval@example.invalid"], cwd=repository, check=True)
            changed_path = repository / "tools" / "evals" / "run_evals.py"
            changed_path.parent.mkdir(parents=True)
            changed_path.write_text("first\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=repository, check=True)
            subprocess.run(["git", "commit", "-m", "Initial"], cwd=repository, check=True, capture_output=True)
            baseline = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=repository, check=True, capture_output=True, text=True,
            ).stdout.strip()
            changed_path.write_text("second\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=repository, check=True)
            subprocess.run(["git", "commit", "-m", "Update evaluation runner"], cwd=repository, check=True, capture_output=True)
            current = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=repository, check=True, capture_output=True, text=True,
            ).stdout.strip()

            impact = git_change_impact(baseline, current, repository)

            self.assertEqual(impact["status"], "AVAILABLE")
            self.assertIn("run-evaluations", impact["changed_capabilities"])
            self.assertTrue(any(item["commit"] == current for item in impact["commits"]))

    def test_shards_are_aggregated_and_weekly_diagnostics_are_rendered(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, item in (("skills", result("one-skill")), ("agents", result("one-agent", "WARNING"))):
                shard = root / name
                shard.mkdir()
                (shard / "capabilities.json").write_text(json.dumps([item]), encoding="utf-8")
                (shard / "summary.json").write_text(
                    json.dumps({
                        "selection": {
                            "capabilities": [item["capability"]],
                            "workflows": [],
                            "changed_files": [],
                            "impact": None,
                        }
                    }),
                    encoding="utf-8",
                )
            output = root / "aggregate"
            completed = subprocess.run(
                [
                    "python3",
                    str(AGGREGATOR),
                    "--input-root",
                    str(root),
                    "--output",
                    str(output),
                    "--profile",
                    "deep",
                    "--branch",
                    "main",
                    "--weekly-report",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            summary = json.loads((output / "quality-summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["selection"]["profile"], "deep")
            self.assertEqual(summary["overall"], "WARN")
            token_trend = next(row for row in summary["quality_trend"] if row["metric"] == "tokens")
            self.assertEqual(token_trend["current"], "not_available")
            report = (output / "weekly-quality-report.html").read_text(encoding="utf-8")
            for heading in (
                "7-day trend",
                "Mutation score",
                "Flaky scenarios",
                "Pass-rate variance",
                "Runtime trends",
                "Token trends",
                "Worst capability regression",
                "Top unstable capability",
            ):
                self.assertIn(heading, report)

    def test_nightly_dashboard_exposes_trends_impact_classification_and_diagnostics(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shard = root / "skills"
            shard.mkdir()
            results = [
                result(
                    "run-evaluations",
                    run=1,
                    scenario="behavior",
                    metrics={"correctness": 0.98, "completeness": 0.97, "evidence_grounding": 0.99},
                    duration=10.0,
                    tokens=1000,
                ),
                result(
                    "run-evaluations",
                    "REGRESSION_FAIL",
                    run=2,
                    scenario="behavior",
                    metrics={"correctness": 0.88, "completeness": 0.90, "evidence_grounding": 0.96},
                    duration=14.0,
                    tokens=1300,
                    score=0.88,
                    threshold=None,
                    reason="correctness fell below the accepted threshold",
                ),
                result(
                    "run-evaluations",
                    scenario="contract",
                    metrics={},
                    duration=0.01,
                    tokens=None,
                ),
            ]
            (shard / "capabilities.json").write_text(json.dumps(results), encoding="utf-8")
            (shard / "summary.json").write_text(json.dumps({
                "selection": {
                    "capabilities": ["run-evaluations"],
                    "workflows": ["commons-governance"],
                    "changed_files": ["tools/evals/run_evals.py"],
                    "impact": {
                        "changed_capabilities": ["run-evaluations"],
                        "direct_dependents": ["validate-commons"],
                        "critical_transitive_dependents": [],
                        "workflows": ["commons-governance"],
                    },
                }
            }), encoding="utf-8")

            baseline = root / "baseline.json"
            baseline.write_text(json.dumps({
                "schema_version": 1,
                "version": "1.0.0",
                "status": "accepted",
                "baseline_commit": "abcdef1",
                "created_at": "2026-08-20T00:00:00Z",
                "accepted_run": {"id": "nightly-1", "branch": "main", "profile": "full"},
                "capabilities": {},
                "scenarios": {
                    "run-evaluations:behavior": {
                        "scenario": "run-evaluations:behavior",
                        "runs": 2,
                        "pass_rate": 1.0,
                        "score_mean": 0.99,
                        "score_worst": 0.98,
                        "score_variance": 0.0,
                        "duration_mean_seconds": 10.0,
                        "duration_worst_seconds": 11.0,
                        "tokens_mean": 1000.0,
                        "tokens_worst": 1100.0,
                        "metrics_mean": {
                            "correctness": 0.98,
                            "completeness": 0.97,
                            "evidence_grounding": 0.99,
                        },
                        "metrics_worst": {
                            "correctness": 0.97,
                            "completeness": 0.96,
                            "evidence_grounding": 0.98,
                        },
                        "metrics_variance": {
                            "correctness": 0.0,
                            "completeness": 0.0,
                            "evidence_grounding": 0.0,
                        },
                        "performance_metrics": {},
                    },
                    "run-evaluations:contract": {
                        "scenario": "run-evaluations:contract",
                        "runs": 1,
                        "pass_rate": 1.0,
                        "score_mean": 1.0,
                        "score_worst": 1.0,
                        "score_variance": 0.0,
                        "duration_mean_seconds": 0.01,
                        "duration_worst_seconds": 0.01,
                        "tokens_mean": "not_available",
                        "tokens_worst": "not_available",
                        "metrics_mean": {},
                        "metrics_worst": {},
                        "metrics_variance": {},
                        "performance_metrics": {},
                    }
                },
            }), encoding="utf-8")

            mutation = root / "mutation-report.json"
            mutation.write_text(json.dumps({
                "status": "FAIL",
                "mutation_score": 1 / 3,
                "detected_harmful_mutations": 1,
                "total_harmful_mutations": 3,
                "critical_survivors": ["remove-quality-gate"],
                "results": [
                    {
                        "id": "preserve-quality-gate",
                        "critical": True,
                        "expected_failure": "quality gate rejects the mutation",
                        "status": "DETECTED",
                    },
                    {
                        "id": "remove-quality-gate",
                        "critical": True,
                        "expected_failure": "quality gate rejects the mutation",
                        "status": "SURVIVED",
                    },
                    {
                        "id": "broken-detector",
                        "critical": True,
                        "expected_failure": "detector rejects the mutation",
                        "status": "ERROR",
                    }
                ],
            }), encoding="utf-8")

            visual_dir = root / "visual"
            (visual_dir / "screenshots").mkdir(parents=True)
            (visual_dir / "screenshots" / "dashboard-overview.png").write_bytes(b"png")
            visual = visual_dir / "visual-report.json"
            visual.write_text(json.dumps({
                "status": "FAIL",
                "results": [{
                    "id": "dashboard-overview",
                    "screenshot": "evals/fixtures/visual-regression/screenshots/dashboard-overview.png",
                    "status": "FAIL",
                    "checks": {"visual_difference_within_tolerance": False},
                }],
            }), encoding="utf-8")

            history = root / "history" / "previous"
            history.mkdir(parents=True)
            generated_at = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat().replace("+00:00", "Z")
            (history / "quality-summary.json").write_text(json.dumps({
                "generated_at": generated_at,
                "overall": "PASS",
                "current_commit": "1234567",
                "performance": [{
                    "scenario": "run-evaluations:behavior",
                    "runs": 3,
                    "pass_rate": 2 / 3,
                    "score_worst": 0.8,
                    "score_variance": 0.01,
                    "duration_mean_seconds": 9.0,
                    "tokens_mean": 900.0,
                    "metrics_mean": {"correctness": 0.95},
                    "metrics_variance": {"correctness": 0.01},
                }],
                "mutation": {"mutation_score": 1.0},
            }), encoding="utf-8")

            output = root / "aggregate"
            completed = subprocess.run(
                [
                    "python3", str(AGGREGATOR),
                    "--input", str(shard),
                    "--output", str(output),
                    "--profile", "full",
                    "--branch", "main",
                    "--baseline", str(baseline),
                    "--mutation-report", str(mutation),
                    "--visual-report", str(visual),
                    "--history-dir", str(root / "history"),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 2, completed.stdout + completed.stderr)
            summary = json.loads((output / "quality-summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["build"]["name"], "Nightly")
            expected_version = f"v{(ROOT / 'VERSION').read_text(encoding='utf-8').strip()}"
            self.assertEqual(summary["build"]["version"], expected_version)
            self.assertEqual(summary["change_impact"]["changed_capabilities"], ["run-evaluations"])
            capability = next(item for item in summary["capabilities"] if item["capability"] == "run-evaluations")
            self.assertEqual(capability["impact"], "CHANGED")
            correctness = next(row for row in summary["quality_trend"] if row["metric"] == "correctness")
            self.assertEqual(correctness["baseline"], 0.98)
            self.assertAlmostEqual(correctness["current"], 0.93)
            self.assertAlmostEqual(correctness["delta"], -0.05)
            tokens = next(row for row in summary["quality_trend"] if row["metric"] == "tokens")
            self.assertEqual(tokens["baseline"], 1000.0)
            self.assertEqual(tokens["current"], 1150.0)
            self.assertEqual(tokens["coverage"], "1/2")
            self.assertTrue(tokens["partial"])
            self.assertEqual(capability["token_coverage"], "1/2")
            self.assertEqual(summary["history"]["30_day"][0]["commit"], "1234567")
            self.assertEqual(len(summary["history"]["7_day"]), 1)
            flaky = next(item for item in summary["flakiness"] if item["scenario"] == "run-evaluations:behavior")
            self.assertEqual(flaky["consecutive_failures"], 1)
            self.assertEqual(flaky["consecutive_failure_basis"], "ordered_evaluation_runs")
            survived = next(
                row for row in summary["mutation_view"]["rows"]
                if row["mutation"] == "remove-quality-gate"
            )
            self.assertEqual(survived["actual_detection"], "SURVIVED")
            self.assertEqual(summary["visual_failures"][0]["thumbnail"], "screenshots/dashboard-overview.png")
            self.assertTrue((output / "screenshots" / "dashboard-overview.png").is_file())
            classifications = {item["classification"] for item in summary["classified_regressions"]}
            self.assertIn("QUALITY_REGRESSION", classifications)
            self.assertIn("VISUAL_REGRESSION", classifications)
            self.assertIn("CONTRACT_REGRESSION", classifications)
            self.assertIn("INFRASTRUCTURE_FAILURE", classifications)
            self.assertEqual(summary["critical_regressions"], 3)
            diagnostic = next(item for item in summary["diagnostics"] if item["capability"] == "run-evaluations")
            self.assertIn("--capability run-evaluations", diagnostic["local_reproduction_command"])
            self.assertEqual(diagnostic["likely_impacted_by"], ["run-evaluations"])
            self.assertEqual(diagnostic["expected"]["status"], "PASS")
            self.assertEqual(diagnostic["expected"]["metric_minimums"]["correctness"], 0.95)
            self.assertEqual(diagnostic["actual"]["metrics"]["correctness"], 0.88)
            self.assertAlmostEqual(diagnostic["delta"]["metrics"]["correctness"], -0.07)

            html = (output / "quality-summary.html").read_text(encoding="utf-8")
            for heading in (
                "AGENT COMMONS QUALITY",
                "Current vs baseline",
                "Capability impact",
                "Flakiness",
                "Mutation diagnostics",
                "Mutation score trend",
                "Visual regressions",
                "Developer diagnostics",
            ):
                self.assertIn(heading, html)
            azure = (output / "azure-summary.md").read_text(encoding="utf-8")
            self.assertIn("Regression classes", azure)
            self.assertIn("Inspect first", azure)

    def test_reproduction_commands_use_the_subject_kind_and_real_entrypoints(self) -> None:
        workflow = _reproduction_command("commons-governance", "workflow", "full")
        aggregate = _reproduction_command("ci-aggregation", "suite", "full")

        self.assertIn("--workflow commons-governance", workflow)
        self.assertNotIn("--capability commons-governance", workflow)
        self.assertIn("aggregate_results.py --input-root", aggregate)
        self.assertNotIn("--help", aggregate)
        visual = _reproduction_command("visual-regression", "suite", "full")
        self.assertIn("playwright@1.62.1", visual)
        self.assertIn("--node-modules output/visual-deps/node_modules", visual)

    def test_mutation_execution_error_is_only_infrastructure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shard = root / "skills"
            shard.mkdir()
            (shard / "capabilities.json").write_text(json.dumps([result("one-skill")]), encoding="utf-8")
            mutation = root / "mutation-report.json"
            mutation.write_text(json.dumps({
                "status": "FAIL",
                "mutation_score": 0.0,
                "detected_harmful_mutations": 0,
                "total_harmful_mutations": 1,
                "evaluated_harmful_mutations": 0,
                "critical_survivors": [],
                "infrastructure_errors": ["detector-crash"],
                "results": [{
                    "id": "detector-crash",
                    "critical": True,
                    "expected_failure": "detector rejects the mutation",
                    "status": "ERROR",
                }],
            }), encoding="utf-8")
            output = root / "aggregate"

            completed = subprocess.run([
                "python3", str(AGGREGATOR), "--input", str(shard), "--output", str(output),
                "--profile", "deep", "--branch", "main", "--mutation-report", str(mutation),
            ], cwd=ROOT, capture_output=True, text=True)

            self.assertEqual(completed.returncode, 2, completed.stdout + completed.stderr)
            summary = json.loads((output / "quality-summary.json").read_text(encoding="utf-8"))
            self.assertEqual(
                {item["classification"] for item in summary["classified_regressions"]},
                {"INFRASTRUCTURE_FAILURE"},
            )
            self.assertEqual(summary["critical_regressions"], 0)
            self.assertEqual(summary["mutation_view"]["score"], "not_available")
            self.assertEqual(summary["mutation_view"]["critical_survivors"], [])
            self.assertEqual(summary["mutation_view"]["infrastructure_errors"], ["detector-crash"])

    def test_missing_required_shard_is_infrastructure_not_quality(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "aggregate"
            completed = subprocess.run(
                [
                    "python3", str(AGGREGATOR),
                    "--output", str(output),
                    "--profile", "full",
                    "--branch", "main",
                    "--required-shard", "quality-skills",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 2, completed.stdout + completed.stderr)
            summary = json.loads((output / "quality-summary.json").read_text(encoding="utf-8"))
            classifications = [item["classification"] for item in summary["classified_regressions"]]
            self.assertIn("INFRASTRUCTURE_FAILURE", classifications)
            self.assertNotIn("QUALITY_REGRESSION", classifications)

    def test_downloaded_required_shard_is_recognized_by_its_artifact_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "workspace"
            shard = workspace / "quality-skills-foundation"
            shard.mkdir(parents=True)
            (shard / "capabilities.json").write_text(
                json.dumps([result("one-skill")]),
                encoding="utf-8",
            )
            (shard / "summary.json").write_text(
                json.dumps({"selection": {"capabilities": ["one-skill"]}}),
                encoding="utf-8",
            )
            output = Path(temporary) / "aggregate"
            completed = subprocess.run(
                [
                    "python3", str(AGGREGATOR),
                    "--input-root", str(workspace),
                    "--output", str(output),
                    "--profile", "full",
                    "--branch", "main",
                    "--required-shard", "quality-skills-foundation",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            summary = json.loads((output / "quality-summary.json").read_text(encoding="utf-8"))
            reasons = [str(item.get("reason")) for item in summary["classified_regressions"]]
            self.assertFalse(
                [reason for reason in reasons if "missing required shard" in reason],
                summary["classified_regressions"],
            )


if __name__ == "__main__":
    unittest.main()
