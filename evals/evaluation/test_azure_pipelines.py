from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AZURE = ROOT / ".azuredevops"


class AzurePipelineContractTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        path = AZURE / relative
        self.assertTrue(path.is_file(), f"missing Azure pipeline file: {path.relative_to(ROOT)}")
        return path.read_text(encoding="utf-8")

    def test_four_entry_pipelines_use_distinct_cost_profiles(self) -> None:
        expected = {
            "commons-pr-validation.yml": ("fast", "trigger: none", "pr:"),
            "commons-main-validation.yml": ("standard", "trigger:", "pr: none"),
            "commons-nightly-quality.yml": ("full", "schedules:", "cron:"),
            "commons-weekly-deep-eval.yml": ("deep", "schedules:", "cron:"),
        }
        for filename, (profile, trigger_marker, second_marker) in expected.items():
            with self.subTest(filename=filename):
                text = self.read(filename)
                self.assertIn(f"name: evalProfile\n  value: {profile}", text)
                if filename == "commons-pr-validation.yml":
                    self.assertNotIn("group: agent-commons-evals", text)
                else:
                    self.assertIn("group: agent-commons-evals", text)
                self.assertIn(trigger_marker, text)
                self.assertIn(second_marker, text)
                self.assertIn("templates/", text)

    def test_pr_is_changed_impact_only_and_never_promotes_baseline(self) -> None:
        text = self.read("commons-pr-validation.yml")
        setup = self.read("templates/setup.yml")
        self.assertIn("trigger: none\npr: none", text)
        self.assertIn("select_impacted_evals.py", text)
        self.assertIn("--changed", text)
        self.assertNotIn("promoteBaseline: true", text)
        self.assertNotIn("--all", text)
        self.assertIn("baselineSource: bootstrap", text)
        self.assertIn("persistCredentials", setup)
        self.assertIn("persistCredentials: true", text)

    def test_nightly_and_weekly_encode_required_repetition_and_depth(self) -> None:
        nightly = self.read("commons-nightly-quality.yml")
        weekly = self.read("commons-weekly-deep-eval.yml")
        aggregate = self.read("templates/aggregate-quality.yml")

        self.assertIn("repeat: 3", nightly)
        self.assertIn("promoteBaseline: true", nightly)
        for job in (
            "skills_foundation",
            "skills_delivery",
            "skills_visual",
            "skills_governance",
            "agents",
            "workflows_delivery",
            "workflows_governance",
        ):
            self.assertIn(f"jobName: {job}", nightly)
        self.assertIn("templates/visual-validation.yml", nightly)
        self.assertIn("templates/aggregate-quality.yml", nightly)
        self.assertIn("historyDays: 30", nightly)

        self.assertIn("repeat: 5", weekly)
        self.assertIn("runMutations: true", weekly)
        self.assertIn("weekly-quality-report.html", weekly)
        self.assertIn("historyDays: 30", weekly)
        self.assertIn("--max-builds '${{ parameters.historyDays }}'", aggregate)
        self.assertIn("--history-dir '$(Pipeline.Workspace)/quality-history'", aggregate)
        self.assertIn('history_definition="$BASELINE_PIPELINE_DEFINITION_ID"', aggregate)
        for shard in (
            "quality-skills-foundation",
            "quality-skills-delivery",
            "quality-skills-visual",
            "quality-skills-governance",
            "quality-agents",
            "quality-workflows-delivery",
            "quality-workflows-governance",
        ):
            self.assertIn(f"--required-shard {shard}", aggregate)

    def test_main_splits_the_complete_critical_scope_into_bounded_parallel_jobs(self) -> None:
        text = self.read("commons-main-validation.yml")
        contracts = json.loads(
            (ROOT / "evals/contracts/capabilities.json").read_text(encoding="utf-8")
        )["capabilities"]
        contracts.update(json.loads(
            (ROOT / "evals/contracts/agents.json").read_text(encoding="utf-8")
        )["capabilities"])
        workflows = json.loads(
            (ROOT / "evals/workflows/contracts.json").read_text(encoding="utf-8")
        )["workflows"]
        expected_capabilities = {
            identifier for identifier, contract in contracts.items()
            if contract.get("criticality") == "critical"
        }
        expected_workflows = {
            identifier for identifier, workflow in workflows.items()
            if workflow.get("criticality") == "critical"
        }

        self.assertIn("trigger:\n  batch: true", text)
        self.assertIn("- refs/heads/main", text)
        self.assertNotIn("selectionArguments: '--critical'", text)
        self.assertEqual(
            set(re.findall(r"--capability ([a-z0-9-]+)", text)),
            expected_capabilities,
        )
        self.assertEqual(
            set(re.findall(r"--workflow ([a-z0-9-]+)", text)),
            expected_workflows,
        )
        for job in (
            "critical_foundation",
            "critical_delivery",
            "critical_visual",
            "critical_governance",
            "critical_agents",
            "critical_workflows_delivery",
            "critical_workflows_governance",
        ):
            self.assertIn(f"jobName: {job}", text)
            block = text[text.index(f"jobName: {job}"):]
            next_job = block.find("jobName:", len(f"jobName: {job}"))
            if next_job >= 0:
                block = block[:next_job]
            selections = re.findall(r"--(?:capability|workflow) ([a-z0-9-]+)", block)
            self.assertGreater(len(selections), 0)
            self.assertLessEqual(len(selections), 6)

    def test_shard_artifact_names_match_the_shards_aggregation_requires(self) -> None:
        shard_template = self.read("templates/quality-shard.yml")
        aggregate = self.read("templates/aggregate-quality.yml")
        required = set(re.findall(r"--required-shard (\S+)", aggregate))

        self.assertIn(
            "artifactName: 'quality-${{ replace(parameters.jobName, ''_'', ''-'') }}'",
            shard_template,
        )
        for filename in ("commons-nightly-quality.yml", "commons-weekly-deep-eval.yml"):
            published = {
                "quality-" + job.replace("_", "-")
                for job in re.findall(r"jobName: (\w+)", self.read(filename))
            }
            with self.subTest(filename=filename):
                self.assertEqual(published, required)

    def test_setup_requires_yaml_trigger_ownership_in_azure(self) -> None:
        setup = self.read("SETUP.md")

        self.assertIn("Override the YAML continuous integration trigger", setup)
        self.assertIn("Disable implied YAML CI trigger", setup)
        self.assertIn("Processing of new run requests", setup)

    def test_split_skill_shards_select_every_and_only_registered_skill(self) -> None:
        contracts = json.loads(
            (ROOT / "evals/contracts/capabilities.json").read_text(encoding="utf-8")
        )["capabilities"]
        registered_skills = {
            identifier for identifier, contract in contracts.items()
            if contract.get("kind") == "skill"
        }

        for filename in ("commons-nightly-quality.yml", "commons-weekly-deep-eval.yml"):
            selected = re.findall(r"--capability ([a-z0-9-]+)", self.read(filename))
            with self.subTest(filename=filename):
                self.assertEqual(set(selected), registered_skills)
                self.assertEqual(len(selected), len(set(selected)))

    def test_templates_use_repository_semantic_entrypoints_and_guard_credentials(self) -> None:
        runner = self.read("templates/run-evals.yml")
        publisher = self.read("templates/publish-results.yml")
        visual = self.read("templates/visual-validation.yml")
        quality_shard = self.read("templates/quality-shard.yml")
        static = self.read("templates/static-validation.yml")

        self.assertIn("semanticPolicy", runner)
        self.assertNotIn("EVAL_EXECUTOR_COMMAND", runner)
        self.assertNotIn("EVAL_JUDGE_COMMAND", runner)
        self.assertIn("--check-config", runner)
        self.assertIn("--require-semantic", runner)
        self.assertIn("Evaluation failures:", runner)
        self.assertIn("failure.get('reason')", runner)
        self.assertIn("EVAL_PROVIDER", runner)
        self.assertIn("EVAL_EXECUTOR_PROVIDER", runner)
        self.assertIn("EVAL_API_VERSION", runner)
        self.assertIn("EVAL_APIM_ALLOWED_HOST", runner)
        self.assertIn("EVAL_APIM_SUBSCRIPTION_KEY", runner)
        self.assertIn("EVAL_APIM_CLIENT_USER_KEY", runner)
        self.assertIn("EVAL_APIM_CLIENT_USERNAME", runner)
        self.assertIn("EVAL_EXECUTOR_MODEL", runner)
        self.assertIn("EVAL_JUDGE_MODEL", runner)
        self.assertIn("EVAL_JUDGE_MODEL", runner)
        self.assertIn("PublishTestResults@2", publisher)
        self.assertIn("junit.xml", publisher)
        self.assertIn("PublishPipelineArtifact@1", publisher)
        self.assertIn("quality-summary.html", publisher)
        self.assertIn("screenshots", publisher)
        self.assertIn('--output "$output/screenshots"', visual)
        self.assertNotIn("cp -R evals/fixtures/visual-regression/screenshots", visual)
        setup = self.read("templates/setup.yml")
        self.assertIn("Configure Codex Linux sandbox", setup)
        self.assertIn("bubblewrap apparmor-profiles apparmor-utils", setup)
        self.assertIn("bwrap-userns-restrict", setup)
        self.assertIn("apparmor_parser -r", setup)
        self.assertIn("bwrap --unshare-net --ro-bind / / true", setup)
        self.assertNotIn("apparmor_restrict_unprivileged_userns=0", setup)
        self.assertIn("pixelmatch@7.1.0", setup)
        self.assertIn("pngjs@7.0.0", setup)
        self.assertIn(
            'key: \'playwright | "$(Agent.OS)" | "1.62.1-pixelmatch-7.1.0-pngjs-7.0.0"\'',
            setup,
        )
        self.assertIn("@openai/codex@0.150.1", setup)
        self.assertIn("AGENT_COMMONS_NODE_MODULES", setup)
        self.assertIn("AGENT_COMMONS_NODE_MODULES", runner)
        self.assertIn("installBrowser: ${{ parameters.installBrowser }}", quality_shard)
        self.assertNotIn('= "1.0.0"', static)
        self.assertIn("VERSION must contain a semantic version", static)
        self.assertIn("CHANGELOG.md does not contain", static)

    def test_setup_uses_supported_node_installer_tasks(self) -> None:
        setup = self.read("templates/setup.yml")

        self.assertNotIn("NodeTool@0", setup)
        self.assertEqual(setup.count("task: UseNode@1"), 2)
        self.assertEqual(setup.count("version: '22.14.0'"), 2)

    def test_semantic_jobs_with_visual_capabilities_install_the_browser_runtime(self) -> None:
        required_jobs = {
            "commons-pr-validation.yml": ["targeted"],
            "commons-main-validation.yml": [
                "critical_visual",
                "critical_workflows_delivery",
                "critical_workflows_governance",
            ],
            "commons-nightly-quality.yml": [
                "skills_visual", "workflows_delivery", "workflows_governance",
            ],
            "commons-weekly-deep-eval.yml": [
                "skills_visual", "workflows_delivery", "workflows_governance",
            ],
        }

        for filename, jobs in required_jobs.items():
            text = self.read(filename)
            for job in jobs:
                with self.subTest(filename=filename, job=job):
                    marker = f"jobName: {job}"
                    block = text[text.index(marker):]
                    next_job = block.find("jobName:", len(marker))
                    if next_job >= 0:
                        block = block[:next_job]
                    self.assertIn("installBrowser: true", block)

    def test_production_quality_pipelines_fail_early_through_semantic_smoke(self) -> None:
        smoke = self.read("templates/semantic-smoke.yml")
        self.assertIn("--capability inventory-codebase", smoke)
        self.assertIn("evalProfile: smoke", smoke)
        self.assertIn("semanticPolicy: required", smoke)
        self.assertIn("mode: resolve", smoke)
        self.assertIn("compareBaseline: true", smoke)
        self.assertIn("verify_azure_pipeline_access.py", smoke)
        self.assertIn("--expected-yaml-path '.azuredevops/commons-nightly-quality.yml'", smoke)
        for filename in ("commons-nightly-quality.yml", "commons-weekly-deep-eval.yml"):
            with self.subTest(filename=filename):
                text = self.read(filename)
                self.assertIn("stage: SemanticSmoke", text)
                self.assertIn("dependsOn: SemanticSmoke", text)

    def test_pr_and_main_are_deterministic_and_never_install_the_codex_runtime(self) -> None:
        shard = self.read("templates/quality-shard.yml")
        self.assertIn("- name: installSemanticRuntime", shard)
        self.assertIn(
            "installSemanticRuntime: ${{ parameters.installSemanticRuntime }}", shard,
        )

        for filename in ("commons-pr-validation.yml", "commons-main-validation.yml"):
            with self.subTest(filename=filename):
                text = self.read(filename)
                shard_count = text.count("template: templates/quality-shard.yml")
                self.assertEqual(text.count("installSemanticRuntime: false"), shard_count)
                self.assertEqual(text.count("semanticPolicy: optional"), shard_count)
                self.assertNotIn("semanticPolicy: required", text)
                self.assertNotIn("stage: SemanticSmoke", text)
                self.assertNotIn("templates/semantic-smoke.yml", text)

        for filename in ("commons-nightly-quality.yml", "commons-weekly-deep-eval.yml"):
            with self.subTest(filename=filename):
                text = self.read(filename)
                self.assertIn("semanticPolicy: required", text)
                self.assertNotIn("installSemanticRuntime: false", text)

    def test_last_green_is_resolved_from_nightly_artifact_and_only_green_runs_promote(self) -> None:
        baseline = self.read("templates/baseline.yml")

        self.assertIn("resolve_azure_baseline.py", baseline)
        self.assertNotIn("continueOnError: true", baseline)
        self.assertIn('--definition "$BASELINE_PIPELINE_DEFINITION_ID"', baseline)
        self.assertNotIn("--definition '$(baselinePipelineDefinitionId)'", baseline)
        self.assertIn("BASELINE_PIPELINE_DEFINITION_ID: $(baselinePipelineDefinitionId)", baseline)
        self.assertIn("last-green-baseline", baseline)
        self.assertIn("promote_baseline.py", baseline)
        self.assertIn("condition: succeeded()", baseline)
        self.assertIn("System.AccessToken", baseline)
        self.assertNotIn("Update build information", baseline)

    def test_nightly_definition_is_the_single_baseline_and_history_source(self) -> None:
        aggregate = self.read("templates/aggregate-quality.yml")
        runner = self.read("templates/run-evals.yml")

        self.assertNotIn("qualityHistoryPipelineDefinitionId", aggregate)
        self.assertIn("BASELINE_PIPELINE_DEFINITION_ID", runner)
        self.assertNotIn("QUALITY_HISTORY_PIPELINE_DEFINITION_ID", runner)
        self.assertIn('history_definition="$BASELINE_PIPELINE_DEFINITION_ID"', aggregate)
        self.assertIn("BASELINE_PIPELINE_DEFINITION_ID: $(baselinePipelineDefinitionId)", aggregate)

    def test_operational_setup_guide_covers_all_pipeline_configuration(self) -> None:
        setup = self.read("SETUP.md")
        for name, path in (
            ("Agent Commons - PR Validation", ".azuredevops/commons-pr-validation.yml"),
            ("Agent Commons - Main Validation", ".azuredevops/commons-main-validation.yml"),
            ("Agent Commons - Nightly Quality", ".azuredevops/commons-nightly-quality.yml"),
            ("Agent Commons - Weekly Deep Eval", ".azuredevops/commons-weekly-deep-eval.yml"),
        ):
            with self.subTest(name=name):
                self.assertIn(name, setup)
                self.assertIn(path, setup)
        for required in (
            "agent-commons-evals",
            "EVAL_PROVIDER",
            "EVAL_ENDPOINT",
            "EVAL_EXECUTOR_MODEL",
            "EVAL_JUDGE_MODEL",
            "AZURE_OPENAI_API_KEY",
            "EVAL_EXECUTOR_PROVIDER",
            "azure_openai_apim",
            "EVAL_API_VERSION",
            "EVAL_APIM_ALLOWED_HOST",
            "2025-04-01-preview",
            "EVAL_APIM_SUBSCRIPTION_KEY",
            "EVAL_APIM_CLIENT_USER_KEY",
            "EVAL_APIM_CLIENT_USERNAME",
            "gpt-5.6-sol",
            ".codex/config.toml",
            "baselinePipelineDefinitionId",
            "SYSTEM_ACCESSTOKEN: $(System.AccessToken)",
            "Build Service",
            "View build pipeline",
            "View builds",
            "credential-free",
            "01:00 UTC",
            "03:00 CEST / 02:00 CET",
            "02:00 UTC",
            "04:00 CEST / 03:00 CET",
            "Branch policies",
            "Microsoft-hosted",
            "--profile smoke",
            "Pipeline cannot access variable group",
            "Azure OpenAI 429",
            "What you need to configure",
        ):
            with self.subTest(required=required):
                self.assertIn(required, setup)
        self.assertNotIn("EVAL_EXECUTOR_COMMAND", setup)
        self.assertNotIn("EVAL_JUDGE_COMMAND", setup)
        self.assertNotIn("quality-baseline", setup)
        self.assertNotIn("Update build information", setup)
        self.assertNotIn("<your model>", setup.lower())


if __name__ == "__main__":
    unittest.main()
