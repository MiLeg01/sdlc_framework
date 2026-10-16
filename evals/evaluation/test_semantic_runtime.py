from __future__ import annotations

import json
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
EVAL_TOOLS = ROOT / "tools" / "evals"
sys.path.insert(0, str(EVAL_TOOLS))

from semantic_provider import (  # noqa: E402
    AuthenticationError,
    OpenAICompatibleProvider,
    ProviderConfig,
    ProviderProtocolError,
    ProviderTransientError,
    default_transport,
    provider_config_from_environment,
)
from secure_http import CredentialSafeRedirectHandler  # noqa: E402
from semantic_runtime import (  # noqa: E402
    CodexExecutor,
    RuntimeConfigError,
    RuntimeExecutionError,
    executor_prompt,
    runtime_from_environment,
    sanitized_executor_environment,
)
from semantic_judge import (  # noqa: E402
    bounded_judge_payload,
    constrained_output_schema,
    environment_value,
    judge_instructions,
)
from semantic_executor import run_declared_browser_validations  # noqa: E402
from run_evals import (  # noqa: E402
    HARD_FAIL,
    INFRASTRUCTURE_FAILURE,
    PROTOCOL_FAILURE,
    QUALITY_REGRESSION,
    fixture_artifact_manifest,
    prepare_isolated_workspace,
    resolve_reference,
    result_record,
)


class SemanticRuntimeTests(unittest.TestCase):
    def request(self) -> dict:
        return {
            "schema_version": 1,
            "capability": "inventory-codebase",
            "subject_kind": "skill",
            "scenario": "semantic-smoke",
            "scenario_input": {
                "prompt": "Inspect the supplied synthetic file and report its language.",
                "source_artifacts": ["input/sample.py"],
                "inputs": {"root": "input"},
                "constraints": ["Use only supplied evidence"],
                "workspace_policy": {"writable_artifacts": [], "generated_prefixes": []},
            },
            "canonical_source": "skills/inventory-codebase/SKILL.md",
            "artifact_manifest": {"input/sample.py": "a" * 64},
            "workspace_root": ".",
        }

    def test_executor_output_schema_types_generated_result_for_responses_api(self) -> None:
        schema = json.loads(
            (ROOT / "evals" / "schemas" / "codex-executor-output.schema.json").read_text()
        )
        self.assertEqual(schema["properties"]["generated_result"]["type"], "object")
        self.assertFalse(schema["properties"]["generated_result"]["additionalProperties"])
        self.assertFalse(
            schema["properties"]["generated_result"]["properties"]["observations"]
            ["items"]["additionalProperties"]
        )

    def test_inventory_smoke_allows_only_its_required_inventory_artifact(self) -> None:
        scenarios = json.loads(
            (ROOT / "evals" / "fixtures" / "evaluation" / "scenarios.json").read_text()
        )
        self.assertEqual(
            scenarios["inventory-codebase"]["workspace_policy"],
            {"writable_artifacts": ["inventory.json"], "generated_prefixes": []},
        )
        self.assertTrue(any(
            "unreadable paths" in constraint
            for constraint in scenarios["inventory-codebase"]["constraints"]
        ))
        self.assertTrue(any(
            "symlinks" in constraint
            for constraint in scenarios["inventory-codebase"]["constraints"]
        ))

    def test_tdd_scenario_persists_red_green_and_broader_command_evidence(self) -> None:
        scenarios = json.loads(
            (ROOT / "evals" / "fixtures" / "evaluation" / "scenarios.json").read_text()
        )
        scenario = scenarios["test-driven-development"]

        self.assertEqual(scenario["inputs"]["evidence_log"], "tdd-command-results.txt")
        self.assertIn(
            "tdd-command-results.txt",
            scenario["workspace_policy"]["writable_artifacts"],
        )
        self.assertTrue(any(
            "RED, GREEN, and broader-gate command" in constraint
            for constraint in scenario["constraints"]
        ))

    def test_behavior_reviewer_scenario_bounds_findings_to_required_evidence(self) -> None:
        scenarios = json.loads(
            (ROOT / "evals" / "fixtures" / "evaluation" / "scenarios.json").read_text()
        )
        constraints = scenarios["test-behavior-reviewer"]["constraints"]

        self.assertTrue(any(
            "exactly three evidence-backed observations" in constraint
            for constraint in constraints
        ))
        self.assertTrue(any(
            "Do not add recommendations" in constraint
            for constraint in constraints
        ))

    def test_visual_semantic_scenarios_have_runnable_browser_outputs(self) -> None:
        scenarios = json.loads(
            (ROOT / "evals" / "fixtures" / "evaluation" / "scenarios.json").read_text()
        )
        visual = scenarios["validate-visual-artifact"]
        dashboard = scenarios["build-living-dashboard"]

        self.assertIn("visual-qa", visual["workspace_policy"]["generated_prefixes"])
        self.assertIn("capture_visual_matrix.mjs", visual["inputs"]["browser_command"])
        self.assertIn("validate_html.py", visual["inputs"]["static_validation_command"])
        self.assertEqual(
            visual["inputs"]["states"],
            "evals/fixtures/localization/visual-states.json",
        )
        state_fixture = json.loads((ROOT / visual["inputs"]["states"]).read_text())
        html_fixture = (ROOT / visual["inputs"]["artifact"]).read_text(encoding="utf-8")
        self.assertIn("overflow-wrap:anywhere", html_fixture)
        self.assertIn("select { width:100%; min-width:0; max-width:100%", html_fixture)
        self.assertIn("details { min-width:0; max-width:100%", html_fixture)
        capture_script = (
            ROOT / "skills/validate-visual-artifact/scripts/capture_visual_matrix.mjs"
        ).read_text(encoding="utf-8")
        self.assertIn("overflow_sources", capture_script)
        self.assertTrue(any(
            "exactly three evidence-backed observations" in constraint
            for constraint in visual["constraints"]
        ))
        self.assertTrue(any(
            "Do not include recommendations, next steps, limitations, assumptions"
            in constraint
            for constraint in visual["constraints"]
        ))
        for state in state_fixture["states"]:
            self.assertTrue(state["selector"].startswith("#"))
            self.assertIn(f'id="{state["selector"][1:]}"', html_fixture)
        self.assertIn(
            "skills/validate-visual-artifact/scripts/capture_visual_matrix.mjs",
            visual["source_artifacts"],
        )
        self.assertIn(
            "skills/validate-visual-artifact/scripts/validate_html.py",
            visual["source_artifacts"],
        )
        self.assertIn(
            "skills/localize-client-artifact/assets/bilingual-runtime.js",
            visual["source_artifacts"],
        )
        self.assertTrue(any(
            "trusted evaluation runner" in constraint
            for constraint in visual["constraints"]
        ))
        self.assertIn("dashboard", dashboard["workspace_policy"]["generated_prefixes"])
        self.assertIn("capture_dashboard_visual_qa.mjs", dashboard["inputs"]["browser_command"])
        self.assertIn(
            "skills/build-living-dashboard/scripts/capture_dashboard_visual_qa.mjs",
            dashboard["source_artifacts"],
        )

    def test_trusted_executor_runs_declared_browser_validation_after_artifact_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            script = workspace / "skills" / "validate-visual-artifact" / "scripts" / "capture.mjs"
            script.parent.mkdir(parents=True)
            script.write_text("// synthetic browser validator\n", encoding="utf-8")
            artifact = workspace / "artifact" / "index.html"
            artifact.parent.mkdir()
            artifact.write_text("<html></html>\n", encoding="utf-8")
            request = self.request()
            request["scenario_input"] = {
                "source_artifacts": [
                    "skills/validate-visual-artifact/scripts/capture.mjs",
                ],
                "inputs": {
                    "browser_command": (
                        "node skills/validate-visual-artifact/scripts/capture.mjs "
                        "--html artifact/index.html --output visual-qa/report.json"
                    ),
                },
                "workspace_policy": {
                    "writable_artifacts": [],
                    "generated_prefixes": ["visual-qa"],
                },
            }
            output = {
                "generated_result": {"summary": "Created the artifact.", "observations": []},
                "evidence": [],
            }
            captured: dict[str, object] = {}

            def run(command, **kwargs):
                captured["command"] = command
                captured["cwd"] = kwargs["cwd"]
                captured["environment"] = kwargs["env"]
                report = workspace / "visual-qa" / "report.json"
                report.parent.mkdir(parents=True)
                report.write_text(
                    json.dumps({"status": "PASS", "browser": {"engine": "chromium"}}, indent=2)
                    + "\n",
                    encoding="utf-8",
                )
                return subprocess.CompletedProcess(command, 0, stdout="captured\n", stderr="")

            with mock.patch.dict(os.environ, {
                "PATH": "/usr/bin",
                "AGENT_COMMONS_NODE_MODULES": "/tmp/synthetic-node-modules",
                "AZURE_OPENAI_API_KEY": "must-not-leak",
            }, clear=True):
                validations = run_declared_browser_validations(
                    request, workspace, output, runner=run,
                )

            self.assertEqual(len(validations), 1)
            self.assertEqual(captured["command"][0], "node")
            self.assertEqual(captured["cwd"], workspace)
            self.assertEqual(
                captured["environment"]["AGENT_COMMONS_NODE_MODULES"],
                "/tmp/synthetic-node-modules",
            )
            self.assertNotIn("AZURE_OPENAI_API_KEY", captured["environment"])
            self.assertEqual(output["generated_result"]["observations"], [])
            self.assertEqual(output["evidence"][0]["source"], "visual-qa/report.json")
            self.assertEqual(output["generated_result"]["summary"], "Created the artifact.")

    def test_trusted_executor_reports_failed_browser_checks(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            script = workspace / "skills" / "validate-visual-artifact" / "scripts" / "capture.mjs"
            script.parent.mkdir(parents=True)
            script.write_text("// synthetic browser validator\n", encoding="utf-8")
            request = self.request()
            request["scenario_input"] = {
                "source_artifacts": [str(script.relative_to(workspace))],
                "inputs": {
                    "browser_command": (
                        "node skills/validate-visual-artifact/scripts/capture.mjs "
                        "--output visual-qa/report.json"
                    ),
                },
                "workspace_policy": {
                    "writable_artifacts": [],
                    "generated_prefixes": ["visual-qa"],
                },
            }
            output = {
                "generated_result": {"summary": "Created the artifact.", "observations": []},
                "evidence": [],
            }

            def run(command, **kwargs):
                report = workspace / "visual-qa" / "report.json"
                report.parent.mkdir(parents=True)
                report.write_text(
                    json.dumps({"status": "FAIL", "states": [{"id": "mobile", "visible": False}]}),
                    encoding="utf-8",
                )
                return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

            with self.assertRaisesRegex(RuntimeExecutionError, '"visible": false'):
                run_declared_browser_validations(request, workspace, output, runner=run)

    def test_deep_research_fixture_requires_inline_citations_in_every_section(self) -> None:
        scenarios = json.loads(
            (ROOT / "evals" / "fixtures" / "evaluation" / "scenarios.json").read_text()
        )
        research = scenarios["deep-research"]
        requirement = " ".join([research["prompt"], *research["constraints"]]).lower()

        for section in ("summary", "observations", "alternatives", "risks", "recommendation"):
            self.assertIn(section, requirement)
        self.assertIn("inline", requirement)
        self.assertIn("conflict field as supplied synthesis", requirement)
        self.assertIn("never source fact", requirement)
        self.assertIn("every observation label identify both", requirement)

    def test_codex_executor_uses_noninteractive_schema_constrained_isolated_run(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            (workspace / "input").mkdir()
            (workspace / "input" / "sample.py").write_text("print('synthetic')\n", encoding="utf-8")
            (workspace / "skills" / "inventory-codebase").mkdir(parents=True)
            (workspace / "skills" / "inventory-codebase" / "SKILL.md").write_text(
                "# Inventory\n", encoding="utf-8"
            )
            captured: dict[str, object] = {}

            def run(command, **kwargs):
                captured["command"] = command
                captured["prompt"] = kwargs["input"]
                captured["environment"] = kwargs["env"]
                captured["runtime_directories_exist"] = all(
                    Path(kwargs["env"][name]).is_dir()
                    for name in ("HOME", "XDG_CACHE_HOME", "XDG_CONFIG_HOME", "XDG_RUNTIME_DIR")
                )
                output_path = Path(command[command.index("--output-last-message") + 1])
                output_path.write_text(
                    json.dumps({
                        "generated_result": {"language": "Python"},
                        "evidence": [{
                            "id": "E1",
                            "source": "input/sample.py",
                            "locator": "input/sample.py:1",
                            "claim": "The fixture uses Python syntax.",
                        }],
                    }),
                    encoding="utf-8",
                )
                events = "\n".join([
                    json.dumps({"type": "thread.started", "model": "gpt-test"}),
                    json.dumps({"type": "turn.completed", "usage": {
                        "input_tokens": 23, "output_tokens": 11, "total_tokens": 34,
                    }}),
                ])
                return subprocess.CompletedProcess(command, 0, stdout=events, stderr="")

            executor = CodexExecutor(
                model="gpt-test",
                executable="codex",
                runner=run,
                output_schema=ROOT / "evals" / "schemas" / "executor-output.schema.json",
            )
            with mock.patch.dict(os.environ, {"PATH": "/usr/bin"}, clear=True), mock.patch(
                "semantic_runtime.shutil.which", return_value="/fake/codex"
            ):
                result = executor.execute(self.request(), workspace)

            command = captured["command"]
            self.assertIn("exec", command)
            self.assertIn("--ephemeral", command)
            self.assertIn("--ignore-user-config", command)
            self.assertIn("--output-schema", command)
            self.assertIn("default_permissions=\"eval-runtime\"", command)
            self.assertIn("permissions.eval-runtime.network.enabled=false", command)
            self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", command)
            self.assertNotIn('"expected"', captured["prompt"])
            self.assertNotIn("golden", captured["prompt"].lower())
            self.assertIn("Every evidence ID must be unique", captured["prompt"])
            self.assertIn("Re-read every generated evidence file", captured["prompt"])
            self.assertIn("Do not run inputs whose names end with browser_command", captured["prompt"])
            self.assertIn("capability file as read-only", captured["prompt"])
            self.assertIn("Inspect every declared source artifact", captured["prompt"])
            self.assertIn("verify every scenario constraint", captured["prompt"])
            child_environment = captured["environment"]
            self.assertEqual(Path(child_environment["HOME"]).name, "runtime-home")
            self.assertEqual(Path(child_environment["XDG_CACHE_HOME"]).name, "cache")
            self.assertEqual(Path(child_environment["XDG_CONFIG_HOME"]).name, "config")
            self.assertEqual(Path(child_environment["XDG_RUNTIME_DIR"]).name, "runtime")
            self.assertTrue(captured["runtime_directories_exist"])
            self.assertEqual(result.output["generated_result"]["language"], "Python")
            self.assertEqual(result.input_tokens, 23)
            self.assertEqual(result.output_tokens, 11)
            self.assertEqual(result.total_tokens, 34)

    def test_codex_executor_rejects_missing_model_or_binary(self) -> None:
        with self.assertRaises(RuntimeConfigError):
            CodexExecutor(model="", executable="codex").check_config()
        with mock.patch("semantic_runtime.shutil.which", return_value=None):
            with self.assertRaises(RuntimeConfigError):
                CodexExecutor(model="gpt-test", executable="definitely-missing-codex").check_config()

    def test_codex_executor_uses_apim_provider_without_exposing_secrets_in_arguments(self) -> None:
        environment = {
            "EVAL_EXECUTOR_RUNTIME": "codex",
            "EVAL_EXECUTOR_PROVIDER": "azure_openai_apim",
            "EVAL_EXECUTOR_MODEL": "gpt-test",
            "EVAL_ENDPOINT": "https://synthetic-gateway.azure-api.net/team/openai",
            "EVAL_APIM_ALLOWED_HOST": "synthetic-gateway.azure-api.net",
            "EVAL_API_VERSION": "2025-04-01-preview",
            "AZURE_OPENAI_API_KEY": "backend-secret",
            "EVAL_APIM_SUBSCRIPTION_KEY": "subscription-secret",
            "EVAL_APIM_CLIENT_USER_KEY": "user-secret",
            "EVAL_APIM_CLIENT_USERNAME": "synthetic-user",
        }
        captured: dict[str, object] = {}

        def run(command, **kwargs):
            captured["command"] = command
            captured["environment"] = kwargs["env"]
            output_path = Path(command[command.index("--output-last-message") + 1])
            output_path.write_text(json.dumps({"generated_result": {}, "evidence": []}))
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        runtime = runtime_from_environment(
            environment,
            output_schema=ROOT / "evals" / "schemas" / "executor-output.schema.json",
        )
        with tempfile.TemporaryDirectory() as temporary, mock.patch(
            "semantic_runtime.shutil.which", return_value="/fake/codex"
        ), mock.patch.dict(os.environ, environment, clear=True), mock.patch(
            "semantic_runtime.subprocess.run"
        ) as login:
            runtime.runner = run
            runtime.execute(self.request(), Path(temporary))

        command_text = " ".join(captured["command"])
        child_environment = captured["environment"]
        self.assertIn('model_provider="azure_apim"', command_text)
        self.assertIn("model_providers.azure_apim", command_text)
        self.assertIn("env_http_headers", command_text)
        self.assertEqual(child_environment["AZURE_OPENAI_API_KEY"], "backend-secret")
        self.assertEqual(child_environment["EVAL_APIM_SUBSCRIPTION_KEY"], "subscription-secret")
        self.assertNotIn("backend-secret", command_text)
        self.assertNotIn("subscription-secret", command_text)
        self.assertNotIn("user-secret", command_text)
        self.assertIn("shell_environment_policy.filters", command_text)
        self.assertIn("permissions.eval-runtime.filesystem={", command_text)
        self.assertIn("--strict-config", captured["command"])
        login.assert_not_called()

    def test_codex_executor_redacts_apim_secrets_from_failures(self) -> None:
        environment = {
            "EVAL_EXECUTOR_PROVIDER": "azure_openai_apim",
            "EVAL_EXECUTOR_MODEL": "gpt-test",
            "EVAL_ENDPOINT": "https://synthetic-gateway.azure-api.net/team/openai",
            "EVAL_APIM_ALLOWED_HOST": "synthetic-gateway.azure-api.net",
            "EVAL_API_VERSION": "2025-04-01-preview",
            "AZURE_OPENAI_API_KEY": "backend-secret",
            "EVAL_APIM_SUBSCRIPTION_KEY": "subscription-secret",
            "EVAL_APIM_CLIENT_USER_KEY": "user-secret",
            "EVAL_APIM_CLIENT_USERNAME": "synthetic-user",
        }
        runtime = runtime_from_environment(
            environment,
            output_schema=ROOT / "evals" / "schemas" / "codex-executor-output.schema.json",
        )
        runtime.runner = lambda command, **kwargs: subprocess.CompletedProcess(
            command,
            1,
            stdout="",
            stderr="Authorization: Bearer backend-secret x-client-userkey=user-secret synthetic-user",
        )
        with tempfile.TemporaryDirectory() as temporary, mock.patch(
            "semantic_runtime.shutil.which", return_value="/fake/codex"
        ), mock.patch.dict(os.environ, environment, clear=True):
            with self.assertRaisesRegex(Exception, "REDACTED") as raised:
                runtime.execute(self.request(), Path(temporary))
        message = str(raised.exception)
        self.assertNotIn("backend-secret", message)
        self.assertNotIn("user-secret", message)
        self.assertNotIn("synthetic-user", message)

    def test_executor_environment_excludes_judge_and_pipeline_secrets(self) -> None:
        sanitized = sanitized_executor_environment({
            "PATH": "/usr/bin",
            "LANG": "C.UTF-8",
            "OPENAI_API_KEY": "executor-secret",
            "AZURE_OPENAI_API_KEY": "judge-secret",
            "EVAL_API_KEY": "judge-secret",
            "EVAL_BEARER_TOKEN": "judge-token",
            "SYSTEM_ACCESSTOKEN": "azure-token",
            "SSH_AUTH_SOCK": "/tmp/agent.sock",
            "AGENT_COMMONS_NODE_MODULES": "/opt/agent-commons-browser/node_modules",
        })

        self.assertEqual(sanitized, {
            "PATH": "/usr/bin",
            "LANG": "C.UTF-8",
            "AGENT_COMMONS_NODE_MODULES": "/opt/agent-commons-browser/node_modules",
        })

    def test_judge_instructions_bind_assertions_to_supplied_evidence_ids(self) -> None:
        instructions = judge_instructions(
            ["correctness", "completeness"],
            ["correctness"],
            ["E-SYN-001", "E-SYN-002"],
        )

        self.assertIn("E-SYN-001, E-SYN-002", instructions)
        self.assertIn("Never invent", instructions)
        self.assertIn("deterministic findings as authoritative", instructions)
        self.assertIn("Do not penalize visual_quality", instructions)

    def test_judge_schema_constrains_assertions_and_evidence_to_request_ids(self) -> None:
        schema = json.loads((ROOT / "evals/schemas/judge-output.schema.json").read_text())
        constrained = constrained_output_schema(
            schema,
            {
                "expected": {
                    "expected_facts": [{"id": "fact-one", "text": "Fact one"}],
                    "invariants": ["source-read-only"],
                    "required_sequence": ["inventory"],
                    "hard_assertions": ["scope-complete"],
                }
            },
            ["E-SYN-001", "E-SYN-002"],
        )
        properties = constrained["properties"]["assertions"]["items"]["properties"]

        self.assertEqual(
            properties["assertion"]["enum"],
            ["fact-one", "source-read-only", "inventory", "scope-complete"],
        )
        self.assertEqual(properties["evidence"]["enum"], ["E-SYN-001", "E-SYN-002"])

    def test_isolated_workspace_exposes_complete_capability_without_golden_data(self) -> None:
        contract = {
            "path": "skills/maintain-project-memory/SKILL.md",
            "capabilities": [],
        }
        fixture = {
            "source_artifacts": ["evals/fixtures/trace-graph-valid.json"],
        }
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            prepare_isolated_workspace(workspace, contract, fixture)

            self.assertTrue((workspace / "skills/maintain-project-memory/SKILL.md").is_file())
            self.assertTrue((workspace / "skills/maintain-project-memory/references/memory-contract.md").is_file())
            self.assertTrue((workspace / "skills/maintain-project-memory/scripts/manage_project_memory.py").is_file())
            self.assertFalse(any("golden" in path.parts for path in workspace.rglob("*")))

    def test_isolated_workspace_instructions_support_stable_line_evidence(self) -> None:
        contract = {"path": "skills/continue-project/SKILL.md"}
        fixture = {"source_artifacts": ["evals/fixtures/queue.json"]}
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            prepare_isolated_workspace(workspace, contract, fixture)
            lines = (workspace / "AGENTS.md").read_text(encoding="utf-8").splitlines()

        self.assertGreaterEqual(len(lines), 6)
        self.assertEqual(lines[0], "# Isolated semantic evaluation workspace")
        self.assertIn("Use only files in this workspace.", lines)

    def test_isolated_workspace_copies_support_dependencies_without_treating_them_as_sources(self) -> None:
        contract = {"path": "skills/maintain-project-memory/SKILL.md"}
        fixture = {
            "source_artifacts": ["evals/fixtures/trace-graph-valid.json"],
            "workspace_dependencies": ["tools/evals/secure_http.py"],
        }
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            prepare_isolated_workspace(workspace, contract, fixture)

            self.assertTrue((workspace / "tools/evals/secure_http.py").is_file())
            self.assertNotIn(
                "tools/evals/secure_http.py",
                fixture_artifact_manifest(contract, fixture),
            )

    def test_presentation_fixture_dependencies_preserve_generated_catalog_facts(self) -> None:
        contracts = json.loads(
            (ROOT / "evals/contracts/capabilities.json").read_text(encoding="utf-8")
        )["capabilities"]
        contract = contracts["update-commons-presentation"]
        scenario = next(item for item in contract["scenarios"] if item["id"] == "behavior")
        fixture = resolve_reference(scenario["fixture"], "fixture")
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            prepare_isolated_workspace(workspace, contract, fixture)

            completed = subprocess.run(
                ["python3", "tools/refresh_commons_presentation.py"],
                cwd=workspace,
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertEqual(
                (workspace / "presentation/assets/library-data.js").read_text(encoding="utf-8"),
                (ROOT / "presentation/assets/library-data.js").read_text(encoding="utf-8"),
            )

    def test_dashboard_quality_fixture_build_command_succeeds_in_isolation(self) -> None:
        workflows = json.loads(
            (ROOT / "evals/workflows/contracts.json").read_text(encoding="utf-8")
        )["workflows"]
        contract = workflows["dashboard-quality"]
        scenario = next(item for item in contract["scenarios"] if item["id"] == "e2e")
        fixture = resolve_reference(scenario["fixture"], "fixture")
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            prepare_isolated_workspace(workspace, contract, fixture)
            completed = subprocess.run(
                fixture["inputs"]["build_command"].split(),
                cwd=workspace,
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertTrue((workspace / "dashboard/index.html").is_file())

    def test_commons_governance_fixture_contains_presentation_runtime(self) -> None:
        workflows = json.loads(
            (ROOT / "evals/workflows/contracts.json").read_text(encoding="utf-8")
        )["workflows"]
        contract = workflows["commons-governance"]
        scenario = next(item for item in contract["scenarios"] if item["id"] == "e2e")
        fixture = resolve_reference(scenario["fixture"], "fixture")
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            prepare_isolated_workspace(workspace, contract, fixture)

            for relative in (
                "presentation/index.html",
                "presentation/assets/library-data.js",
                "tools/sync_presentation.py",
            ):
                with self.subTest(relative=relative):
                    self.assertTrue((workspace / relative).is_file(), relative)

    def test_executor_prompt_requires_complete_outputs_and_exact_supplied_identifiers(self) -> None:
        prompt = executor_prompt(self.request())

        self.assertIn("complete standalone deliverable", prompt)
        self.assertIn("Return the smallest complete result", prompt)
        self.assertIn("do not add unsolicited recommendations", prompt)
        self.assertIn("one independently verifiable claim", prompt)
        self.assertIn("Satisfy operational constraints through the work itself", prompt)
        self.assertIn("do not narrate them", prompt)
        self.assertIn("preserve those identifiers exactly", prompt)
        self.assertIn("Do not invent aliases", prompt)
        self.assertIn("directly support the full observation", prompt)
        self.assertIn("Copy evidence source paths exactly", prompt)

    def test_provider_builds_openai_responses_request_and_extracts_metrics(self) -> None:
        captured: dict[str, object] = {}

        def transport(request, timeout):
            captured["url"] = request.full_url
            captured["headers"] = dict(request.header_items())
            captured["payload"] = json.loads(request.data)
            body = {
                "id": "resp_test",
                "status": "completed",
                "model": "judge-test",
                "usage": {"input_tokens": 101, "output_tokens": 29, "total_tokens": 130},
                "output": [{
                    "type": "message",
                    "content": [{
                        "type": "output_text",
                        "text": json.dumps({
                            "assertions": [{
                                "assertion": "known-language",
                                "status": "PASS",
                                "confidence": 1.0,
                                "reason": "The result identifies Python.",
                                "evidence": "E1",
                            }],
                            "metrics": {"correctness": 1.0},
                            "unsupported_findings": [],
                        }),
                    }],
                }],
            }
            return 200, {}, json.dumps(body).encode("utf-8")

        provider = OpenAICompatibleProvider(
            ProviderConfig(
                provider="openai",
                endpoint="https://api.openai.com/v1",
                model="judge-test",
                api_key="secret-test-key",
                timeout_seconds=30,
            ),
            transport=transport,
        )
        result = provider.judge(
            {"scenario": {}, "expected": {}, "generated_result": {}, "evidence": [], "executor_artifacts": {}},
            {"type": "object"},
            "Judge independently.",
        )

        self.assertEqual(captured["url"], "https://api.openai.com/v1/responses")
        self.assertEqual(captured["headers"]["Authorization"], "Bearer secret-test-key")
        self.assertEqual(captured["payload"]["model"], "judge-test")
        self.assertEqual(captured["payload"]["text"]["format"]["type"], "json_schema")
        self.assertEqual(result.output["assertions"][0]["status"], "PASS")
        self.assertEqual(result.input_tokens, 101)
        self.assertEqual(result.total_tokens, 130)

    def test_provider_classifies_auth_transient_and_protocol_failures(self) -> None:
        with self.assertRaises(AuthenticationError):
            OpenAICompatibleProvider(ProviderConfig(
                provider="openai", endpoint="https://api.openai.com/v1", model="judge", api_key=None,
            )).check_config()

        def rate_limited(request, timeout):
            return 429, {}, b'{"error":{"message":"rate limited"}}'

        provider = OpenAICompatibleProvider(ProviderConfig(
            provider="openai", endpoint="https://api.openai.com/v1", model="judge", api_key="test",
        ), transport=rate_limited)
        with self.assertRaises(ProviderTransientError):
            provider.judge({}, {"type": "object"}, "Judge.")

        def malformed(request, timeout):
            return 200, {}, b'{"status":"completed","output":[]}'

        provider = OpenAICompatibleProvider(ProviderConfig(
            provider="openai", endpoint="https://api.openai.com/v1", model="judge", api_key="test",
        ), transport=malformed)
        with self.assertRaises(ProviderProtocolError):
            provider.judge({}, {"type": "object"}, "Judge.")

    def test_azure_provider_uses_v1_endpoint_and_api_key_header(self) -> None:
        captured: dict[str, object] = {}

        def transport(request, timeout):
            captured["url"] = request.full_url
            captured["headers"] = dict(request.header_items())
            return 200, {}, json.dumps({
                "status": "completed",
                "model": "judge-deployment",
                "output": [{"type": "message", "content": [{
                    "type": "output_text",
                    "text": json.dumps({
                        "assertions": [{
                            "assertion": "A1", "status": "PASS", "confidence": 1.0,
                            "reason": "verified", "evidence": "E1",
                        }],
                        "metrics": {"correctness": 1.0},
                    }),
                }]}],
            }).encode("utf-8")

        provider = OpenAICompatibleProvider(ProviderConfig(
            provider="azure_openai",
            endpoint="https://synthetic-resource.openai.azure.com",
            model="judge-deployment",
            api_key="synthetic-key",
        ), transport=transport)
        provider.judge({}, {"type": "object"}, "Judge.")

        self.assertEqual(
            captured["url"],
            "https://synthetic-resource.openai.azure.com/openai/v1/responses",
        )
        self.assertEqual(captured["headers"]["Api-key"], "synthetic-key")

    def test_apim_provider_reproduces_codex_custom_provider_contract(self) -> None:
        captured: dict[str, object] = {}

        def transport(request, timeout):
            captured["url"] = request.full_url
            captured["headers"] = {
                key.casefold(): value for key, value in request.header_items()
            }
            return 200, {}, json.dumps({
                "status": "completed",
                "model": "gpt-test",
                "output": [{"type": "message", "content": [{
                    "type": "output_text",
                    "text": json.dumps({
                        "assertions": [{
                            "assertion": "A1", "status": "PASS", "confidence": 1.0,
                            "reason": "verified", "evidence": "E1",
                        }],
                        "metrics": {"correctness": 1.0},
                    }),
                }]}],
            }).encode("utf-8")

        config = provider_config_from_environment({
            "EVAL_PROVIDER": "azure_openai_apim",
            "EVAL_ENDPOINT": "https://synthetic-gateway.azure-api.net/team/openai",
            "EVAL_APIM_ALLOWED_HOST": "synthetic-gateway.azure-api.net",
            "EVAL_API_VERSION": "2025-04-01-preview",
            "EVAL_JUDGE_MODEL": "gpt-test",
            "AZURE_OPENAI_API_KEY": "backend-secret",
            "EVAL_APIM_SUBSCRIPTION_KEY": "subscription-secret",
            "EVAL_APIM_CLIENT_USER_KEY": "user-secret",
            "EVAL_APIM_CLIENT_USERNAME": "synthetic-user",
        })
        provider = OpenAICompatibleProvider(config, transport=transport)
        provider.judge({}, {"type": "object"}, "Judge.")

        self.assertEqual(
            captured["url"],
            "https://synthetic-gateway.azure-api.net/team/openai/responses?api-version=2025-04-01-preview",
        )
        self.assertEqual(captured["headers"]["authorization"], "Bearer backend-secret")
        self.assertEqual(captured["headers"]["ocp-apim-subscription-key"], "subscription-secret")
        self.assertEqual(captured["headers"]["x-client-userkey"], "user-secret")
        self.assertEqual(captured["headers"]["x-client-username"], "synthetic-user")

    def test_apim_provider_adds_gateway_headers_with_explicit_bearer_token(self) -> None:
        provider = OpenAICompatibleProvider(provider_config_from_environment({
            "EVAL_PROVIDER": "azure_openai_apim",
            "EVAL_ENDPOINT": "https://synthetic-gateway.azure-api.net/team/openai",
            "EVAL_APIM_ALLOWED_HOST": "synthetic-gateway.azure-api.net",
            "EVAL_API_VERSION": "2025-04-01-preview",
            "EVAL_JUDGE_MODEL": "gpt-test",
            "EVAL_BEARER_TOKEN": "bearer-secret",
            "EVAL_APIM_SUBSCRIPTION_KEY": "subscription-secret",
            "EVAL_APIM_CLIENT_USER_KEY": "user-secret",
            "EVAL_APIM_CLIENT_USERNAME": "synthetic-user",
        }))
        headers = provider._authorization_headers()
        self.assertEqual(headers["Authorization"], "Bearer bearer-secret")
        self.assertEqual(headers["Ocp-Apim-Subscription-Key"], "subscription-secret")

    def test_provider_timeout_is_transient(self) -> None:
        request = urllib.request.Request("https://api.openai.com/v1/responses")
        with mock.patch(
            "semantic_provider.secure_urlopen",
            side_effect=urllib.error.URLError("timed out"),
        ):
            with self.assertRaises(ProviderTransientError):
                default_transport(request, 1)

    def test_provider_rejects_insecure_or_untrusted_credential_destinations(self) -> None:
        with self.assertRaises(ProviderProtocolError):
            OpenAICompatibleProvider(ProviderConfig(
                provider="azure_openai",
                endpoint="http://synthetic-resource.openai.azure.com",
                model="judge",
                api_key="test",
            )).check_config()
        with self.assertRaises(ProviderProtocolError):
            OpenAICompatibleProvider(provider_config_from_environment({
                "EVAL_PROVIDER": "azure_openai_apim",
                "EVAL_ENDPOINT": "https://attacker.example/team/openai",
                "EVAL_APIM_ALLOWED_HOST": "synthetic-gateway.azure-api.net",
                "EVAL_API_VERSION": "2025-04-01-preview",
                "EVAL_JUDGE_MODEL": "judge",
                "AZURE_OPENAI_API_KEY": "backend-secret",
                "EVAL_APIM_SUBSCRIPTION_KEY": "subscription-secret",
                "EVAL_APIM_CLIENT_USER_KEY": "user-secret",
                "EVAL_APIM_CLIENT_USERNAME": "synthetic-user",
            })).check_config()
        with self.assertRaises(ProviderProtocolError):
            OpenAICompatibleProvider(provider_config_from_environment({
                "EVAL_PROVIDER": "azure_openai_apim",
                "EVAL_ENDPOINT": "https://attacker-controlled.azure-api.net/team/openai",
                "EVAL_APIM_ALLOWED_HOST": "synthetic-gateway.azure-api.net",
                "EVAL_API_VERSION": "2025-04-01-preview",
                "EVAL_JUDGE_MODEL": "judge",
                "AZURE_OPENAI_API_KEY": "backend-secret",
                "EVAL_APIM_SUBSCRIPTION_KEY": "subscription-secret",
                "EVAL_APIM_CLIENT_USER_KEY": "user-secret",
                "EVAL_APIM_CLIENT_USERNAME": "synthetic-user",
            })).check_config()
        with self.assertRaises(ProviderProtocolError):
            OpenAICompatibleProvider(ProviderConfig(
                provider="azure_openai",
                endpoint="https://attacker.example",
                model="judge",
                api_key="test",
            )).check_config()

    def test_cross_origin_redirect_strips_sensitive_headers(self) -> None:
        request = urllib.request.Request(
            "https://dev.azure.com/example/artifact",
            headers={
                "Authorization": "Bearer secret",
                "api-key": "secret-key",
                "Ocp-Apim-Subscription-Key": "subscription-secret",
                "x-client-userkey": "user-secret",
                "x-client-username": "synthetic-user",
            },
        )
        redirected = CredentialSafeRedirectHandler().redirect_request(
            request,
            None,
            302,
            "Found",
            {},
            "https://signed.blob.core.windows.net/archive.zip",
        )

        self.assertIsNotNone(redirected)
        self.assertIsNone(redirected.get_header("Authorization"))
        self.assertIsNone(redirected.get_header("api-key"))
        self.assertIsNone(redirected.get_header("Ocp-Apim-Subscription-Key"))
        self.assertIsNone(redirected.get_header("x-client-userkey"))
        self.assertIsNone(redirected.get_header("x-client-username"))

    def test_judge_payload_contains_only_declared_files_and_verifies_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            source = workspace / "input" / "sample.py"
            artifact = workspace / "artifacts" / "report.md"
            source.parent.mkdir()
            artifact.parent.mkdir()
            source.write_text("print('synthetic')\n", encoding="utf-8")
            artifact.write_text("# Result\n", encoding="utf-8")
            (workspace / "unrelated-secret.txt").write_text("must not leave workspace", encoding="utf-8")
            artifact_hash = hashlib.sha256(artifact.read_bytes()).hexdigest()
            request = {
                "scenario": {"input": {"source_artifacts": ["input/sample.py"]}},
                "evidence": [{"id": "E1", "source": "artifacts/report.md", "locator": "artifacts/report.md:1"}],
                "executor_artifacts": {"files": {"artifacts/report.md": artifact_hash}},
            }

            payload = bounded_judge_payload(request, workspace, 1000)

            self.assertEqual(
                set(payload["workspace_evidence"]),
                {"input/sample.py", "artifacts/report.md"},
            )
            self.assertNotIn("unrelated-secret.txt", payload["workspace_evidence"])
            request["executor_artifacts"]["files"]["artifacts/report.md"] = "0" * 64
            with self.assertRaises(ProviderProtocolError):
                bounded_judge_payload(request, workspace, 1000)

    def test_judge_payload_prioritizes_cited_report_over_large_screenshot(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            screenshot = workspace / "a" / "screenshot.png"
            report = workspace / "z" / "visual-qa.json"
            screenshot.parent.mkdir()
            report.parent.mkdir()
            screenshot.write_bytes(b"\x89PNG" + b"x" * 500)
            report.write_text('{"status":"PASS"}\n', encoding="utf-8")
            request = {
                "scenario": {"input": {"source_artifacts": []}},
                "evidence": [{
                    "id": "E-BROWSER",
                    "source": "z/visual-qa.json",
                    "locator": "z/visual-qa.json:1",
                }],
                "executor_artifacts": {"files": {
                    "a/screenshot.png": hashlib.sha256(screenshot.read_bytes()).hexdigest(),
                    "z/visual-qa.json": hashlib.sha256(report.read_bytes()).hexdigest(),
                }},
            }

            payload = bounded_judge_payload(request, workspace, 40)

            cited = payload["workspace_evidence"]["z/visual-qa.json"]
            self.assertEqual(cited["content"], '{"status":"PASS"}\n')
            self.assertFalse(cited["truncated"])

    def test_judge_environment_uses_default_for_unresolved_azure_macro(self) -> None:
        self.assertEqual(
            environment_value(
                "EVAL_JUDGE_MAX_EVIDENCE_BYTES",
                "500000",
                {"EVAL_JUDGE_MAX_EVIDENCE_BYTES": "$(EVAL_JUDGE_MAX_EVIDENCE_BYTES)"},
            ),
            "500000",
        )

    def test_judge_instructions_require_every_scenario_metric(self) -> None:
        instructions = judge_instructions(
            ["correctness", "handoff_quality", "visual_quality"],
            ["handoff_quality", "visual_quality"],
        )

        self.assertIn(
            "Return every required metric exactly once: handoff_quality, visual_quality.",
            instructions,
        )

    def test_config_check_does_not_execute_a_model_call(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            marker = directory / "model-called"
            codex = directory / "codex"
            codex.write_text(
                "#!/bin/sh\n"
                "if [ \"$1\" = exec ]; then touch \"$EVAL_TEST_MODEL_MARKER\"; exit 99; fi\n"
                "exit 0\n",
                encoding="utf-8",
            )
            codex.chmod(0o755)
            environment = {
                "PATH": f"{directory}:{os.environ.get('PATH', '')}",
                "EVAL_TEST_MODEL_MARKER": str(marker),
                "EVAL_EXECUTOR_RUNTIME": "codex",
                "EVAL_EXECUTOR_MODEL": "executor-test",
                "EVAL_PROVIDER": "openai",
                "EVAL_ENDPOINT": "https://api.openai.com/v1",
                "EVAL_JUDGE_MODEL": "judge-test",
                "OPENAI_API_KEY": "test-key",
                "BASELINE_PIPELINE_DEFINITION_ID": "42",
            }
            completed = subprocess.run(
                [
                    sys.executable,
                    str(EVAL_TOOLS / "run_evals.py"),
                    "--check-config",
                    "--output",
                    str(directory / "results"),
                ],
                cwd=ROOT,
                env=environment,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertIn("Semantic evaluation configuration", completed.stdout)
            self.assertIn("Executor: available", completed.stdout)
            self.assertIn("Judge: available", completed.stdout)
            self.assertIn("Runner: available", completed.stdout)
            self.assertIn("Provider: available (openai)", completed.stdout)
            self.assertIn("Executor model: executor-test", completed.stdout)
            self.assertIn("Judge model: judge-test", completed.stdout)
            self.assertIn("Azure baseline: configured (definition 42)", completed.stdout)
            self.assertIn("Quality history: nightly definition 42", completed.stdout)
            self.assertIn("Result directory: writable", completed.stdout)
            self.assertNotIn("responses", completed.stdout.lower())
            self.assertNotIn("test-key", completed.stdout)
            self.assertFalse(marker.exists())

    def test_unresolved_azure_macros_use_runtime_defaults(self) -> None:
        runtime = runtime_from_environment({
            "EVAL_EXECUTOR_RUNTIME": "codex",
            "EVAL_EXECUTOR_MODEL": "executor-test",
            "EVAL_CODEX_BIN": "$(EVAL_CODEX_BIN)",
            "EVAL_EXECUTOR_TIMEOUT_SECONDS": "$(EVAL_EXECUTOR_TIMEOUT_SECONDS)",
        })
        provider = provider_config_from_environment({
            "EVAL_PROVIDER": "openai",
            "EVAL_ENDPOINT": "$(EVAL_ENDPOINT)",
            "EVAL_JUDGE_MODEL": "judge-test",
            "OPENAI_API_KEY": "test-key",
            "EVAL_JUDGE_TIMEOUT_SECONDS": "$(EVAL_JUDGE_TIMEOUT_SECONDS)",
        })

        self.assertEqual(runtime.executable, "codex")
        self.assertEqual(runtime.timeout_seconds, 1500)
        self.assertEqual(provider.endpoint, "https://api.openai.com/v1")
        self.assertEqual(provider.timeout_seconds, 180)

    def test_result_failure_types_distinguish_infrastructure_protocol_and_quality(self) -> None:
        infrastructure = result_record(
            "subject", "skill", "scenario", 2, 1, False, HARD_FAIL, 0.1,
            "infrastructure failure after 3 attempts", attempts={"executor": 3},
        )
        protocol = result_record(
            "subject", "skill", "scenario", 2, 1, False, HARD_FAIL, 0.1,
            "judge returned invalid JSON",
        )
        quality = result_record(
            "subject", "skill", "scenario", 2, 1, False, HARD_FAIL, 0.1,
            "required business rule was not satisfied",
        )

        self.assertEqual(infrastructure["failure_type"], INFRASTRUCTURE_FAILURE)
        self.assertEqual(infrastructure["attempts"], {"executor": 3})
        self.assertEqual(protocol["failure_type"], PROTOCOL_FAILURE)
        self.assertEqual(quality["failure_type"], QUALITY_REGRESSION)


if __name__ == "__main__":
    unittest.main()
