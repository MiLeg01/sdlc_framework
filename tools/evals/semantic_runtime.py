#!/usr/bin/env python3
"""Runtime-neutral semantic executor interfaces and the production Codex adapter."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional

from secure_http import https_origin


class RuntimeConfigError(RuntimeError):
    """The configured semantic execution runtime is unavailable or incomplete."""


class RuntimeExecutionError(RuntimeError):
    """The semantic execution runtime failed to complete the requested scenario."""

    def __init__(self, message: str, *, transient: bool = False) -> None:
        super().__init__(message)
        self.transient = transient


@dataclass(frozen=True)
class RuntimeResult:
    output: dict[str, Any]
    model: str
    runtime: str
    duration_seconds: float
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    stdout: str = ""
    stderr: str = ""


@dataclass(frozen=True)
class CodexAPIMConfig:
    """Custom Codex provider settings for an Azure OpenAI endpoint behind APIM."""

    endpoint: str
    allowed_host: str
    api_version: str
    api_key: str
    subscription_key: str
    client_user_key: str
    client_username: str


class SemanticExecutor:
    """Interface implemented by an agent runtime that executes, but never judges, a scenario."""

    name = "abstract"

    def check_config(self) -> dict[str, str]:
        raise NotImplementedError

    def execute(self, request: dict[str, Any], workspace: Path) -> RuntimeResult:
        raise NotImplementedError


SAFE_EXECUTOR_ENVIRONMENT = {
    "PATH", "LANG", "LC_ALL", "LC_CTYPE", "TMPDIR", "TMP", "TEMP", "SHELL", "TERM",
    "HOME", "USER", "LOGNAME", "SSL_CERT_FILE", "SSL_CERT_DIR", "REQUESTS_CA_BUNDLE",
    "AGENT_COMMONS_NODE_MODULES",
}


def sanitized_executor_environment(environment: dict[str, str]) -> dict[str, str]:
    """Retain runtime essentials while excluding provider, pipeline, and unrelated credentials."""
    return {
        key: value
        for key, value in environment.items()
        if key in SAFE_EXECUTOR_ENVIRONMENT or key.startswith("LC_")
    }


def _find_usage(value: Any) -> dict[str, int]:
    usage: dict[str, int] = {}
    if isinstance(value, dict):
        candidate = value.get("usage")
        if isinstance(candidate, dict):
            for key in ("input_tokens", "output_tokens", "total_tokens"):
                metric = candidate.get(key)
                if isinstance(metric, int) and not isinstance(metric, bool) and metric >= 0:
                    usage[key] = metric
        for nested in value.values():
            for key, metric in _find_usage(nested).items():
                usage[key] = max(metric, usage.get(key, 0))
    elif isinstance(value, list):
        for nested in value:
            for key, metric in _find_usage(nested).items():
                usage[key] = max(metric, usage.get(key, 0))
    return usage


def parse_codex_jsonl(text: str) -> dict[str, Any]:
    """Extract non-secret observability fields from Codex JSONL events."""
    usage: dict[str, int] = {}
    model: Optional[str] = None
    events = 0
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        events += 1
        if isinstance(event, dict) and isinstance(event.get("model"), str):
            model = event["model"]
        for key, metric in _find_usage(event).items():
            usage[key] = max(metric, usage.get(key, 0))
    return {"events": events, "model": model, **usage}


def executor_prompt(request: dict[str, Any]) -> str:
    """Create the bounded executor prompt without Golden expectations or judge instructions."""
    scenario = request["scenario_input"]
    capability_path = request.get("canonical_source")
    capability_instruction = (
        f"Read and follow the capability definition at {capability_path}."
        if capability_path
        else "Use the Agent Commons capabilities available under skills/ and agents/."
    )
    return "\n".join([
        "Execute one isolated Agent Commons semantic evaluation scenario.",
        capability_instruction,
        "Work only inside the current workspace. Do not inspect parent directories or external repositories.",
        "Use only the supplied synthetic fixture and capability material.",
        "Inspect every declared source artifact and the selected capability's relevant bundled references, scripts, assets, and templates before deciding that evidence or tooling is missing.",
        "Do not judge or score your own work. Do not search for answer keys or expected results.",
        "Write files only where the scenario workspace policy explicitly permits it.",
        "Treat every supplied source and capability file as read-only unless its exact path is listed as writable.",
        "Return JSON matching the supplied executor output schema.",
        "Make generated_result.summary a complete standalone deliverable, not a description of work performed.",
        "Return the smallest complete result: include only observations explicitly required by the scenario prompt, inputs, and constraints; do not add unsolicited recommendations, benefits, risks, process narration, or general best-practice commentary.",
        "Use generated_result.observations to address every requested output and required reported finding. Satisfy operational constraints through the work itself; do not narrate them unless the scenario explicitly requests that reporting.",
        "When supplied inputs define stable IDs, dates, revisions, or other identifiers, preserve those identifiers exactly in the generated result. Do not invent aliases or unsupported metadata.",
        "Keep each observation to one independently verifiable claim. Each observation's evidence_id must directly support the full observation. Split claims across observations when they require different evidence, and do not claim that a command or validation ran unless its output was observed.",
        "Every evidence ID must be unique. Evidence sources must be relative workspace paths and locators must end in :LINE or :START-END.",
        "Copy evidence source paths exactly from declared source_artifacts or from files created inside the workspace; do not decorate, relabel, or rewrite those paths.",
        "Re-read every generated evidence file before returning and ensure each locator's final line is within the file's actual line count.",
        "Do not run inputs whose names end with browser_command inside the sandbox. Create their complete input artifacts; the trusted evaluation runner will execute those browser commands afterward and append authoritative browser evidence.",
        "Before returning, verify every scenario constraint and named input has been addressed. If the workspace policy permits outputs, create the required artifacts and run the available deterministic validation commands.",
        "Scenario request:",
        json.dumps({
            "capability": request["capability"],
            "subject_kind": request["subject_kind"],
            "scenario": request["scenario"],
            "prompt": scenario.get("prompt"),
            "inputs": scenario.get("inputs", {}),
            "constraints": scenario.get("constraints", []),
            "source_artifacts": scenario.get("source_artifacts", []),
            "workspace_policy": scenario.get("workspace_policy", {}),
        }, sort_keys=True),
    ])


class CodexExecutor(SemanticExecutor):
    """Production non-interactive Codex CLI semantic executor."""

    name = "codex"

    def __init__(
        self,
        *,
        model: str,
        executable: str = "codex",
        timeout_seconds: int = 1500,
        runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
        output_schema: Optional[Path] = None,
        apim_config: Optional[CodexAPIMConfig] = None,
    ) -> None:
        self.model = model.strip()
        self.executable = executable
        self.timeout_seconds = timeout_seconds
        self.runner = runner
        self.output_schema = output_schema
        self.apim_config = apim_config

    def _check_apim_config(self) -> None:
        if self.apim_config is None:
            return
        try:
            _, hostname, _ = https_origin(
                self.apim_config.endpoint,
                label="EVAL_ENDPOINT",
            )
        except ValueError as exc:
            raise RuntimeConfigError(str(exc)) from exc
        if not hostname.endswith(".azure-api.net"):
            raise RuntimeConfigError(
                "azure_openai_apim EVAL_ENDPOINT must use an Azure API Management *.azure-api.net host"
            )
        allowed_host = self.apim_config.allowed_host.strip().casefold()
        if not allowed_host or ":" in allowed_host or "/" in allowed_host:
            raise RuntimeConfigError("EVAL_APIM_ALLOWED_HOST must be one hostname without scheme or path")
        if hostname != allowed_host:
            raise RuntimeConfigError("EVAL_ENDPOINT host does not match EVAL_APIM_ALLOWED_HOST")
        required = {
            "EVAL_APIM_ALLOWED_HOST": self.apim_config.allowed_host,
            "EVAL_API_VERSION": self.apim_config.api_version,
            "AZURE_OPENAI_API_KEY": self.apim_config.api_key,
            "EVAL_APIM_SUBSCRIPTION_KEY": self.apim_config.subscription_key,
            "EVAL_APIM_CLIENT_USER_KEY": self.apim_config.client_user_key,
            "EVAL_APIM_CLIENT_USERNAME": self.apim_config.client_username,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise RuntimeConfigError(
                "Azure OpenAI APIM executor configuration is missing: " + ", ".join(missing)
            )

    def _apim_provider_override(self) -> str:
        if self.apim_config is None:
            raise RuntimeConfigError("APIM provider configuration is unavailable")
        endpoint = json.dumps(self.apim_config.endpoint)
        api_version = json.dumps(self.apim_config.api_version)
        return "".join([
            "model_providers.azure_apim={",
            'name="Azure OpenAI through APIM",',
            f"base_url={endpoint},",
            'env_key="AZURE_OPENAI_API_KEY",',
            'wire_api="responses",',
            f'query_params={{"api-version"={api_version}}},',
            "env_http_headers={",
            '"Ocp-Apim-Subscription-Key"="EVAL_APIM_SUBSCRIPTION_KEY",',
            '"x-client-userkey"="EVAL_APIM_CLIENT_USER_KEY",',
            '"x-client-username"="EVAL_APIM_CLIENT_USERNAME"',
            "}}",
        ])

    def _redact(self, text: str) -> str:
        if self.apim_config is None:
            return text
        redacted = text
        for value in (
            self.apim_config.endpoint,
            self.apim_config.api_key,
            self.apim_config.subscription_key,
            self.apim_config.client_user_key,
            self.apim_config.client_username,
        ):
            if value:
                redacted = redacted.replace(value, "[REDACTED]")
        for header in (
            "Authorization",
            "api-key",
            "Ocp-Apim-Subscription-Key",
            "x-client-userkey",
            "x-client-username",
        ):
            redacted = re.sub(
                rf"(?i)({re.escape(header)}\s*[:=]\s*)(Bearer\s+)?[^\s,;]+",
                rf"\1[REDACTED]",
                redacted,
            )
        return redacted

    def check_config(self, *, require_auth: bool = False) -> dict[str, str]:
        if not self.model:
            raise RuntimeConfigError("EVAL_EXECUTOR_MODEL is required for reproducible Codex execution")
        resolved = shutil.which(self.executable)
        if not resolved:
            raise RuntimeConfigError(f"Codex CLI executable is unavailable: {self.executable}")
        if self.apim_config is not None:
            self._check_apim_config()
            return {
                "runtime": self.name,
                "executable": resolved,
                "model": self.model,
                "provider": "azure_openai_apim",
                "authentication": "apim_bearer_and_headers",
            }
        authentication = "environment"
        environment_auth = any(
            value and not value.startswith("$(")
            for value in (os.environ.get("OPENAI_API_KEY"), os.environ.get("CODEX_ACCESS_TOKEN"))
        )
        if require_auth and not environment_auth:
            try:
                status = subprocess.run(
                    [resolved, "login", "status"],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise RuntimeConfigError(f"Codex authentication status is unavailable: {exc}") from exc
            if status.returncode != 0:
                raise RuntimeConfigError(
                    "Codex authentication is unavailable; run codex login or configure OPENAI_API_KEY"
                )
            authentication = "codex_login"
        return {
            "runtime": self.name,
            "executable": resolved,
            "model": self.model,
            "authentication": authentication,
        }

    def _command(
        self,
        workspace: Path,
        output_path: Path,
        denied_auth_root: Optional[Path] = None,
    ) -> list[str]:
        if self.output_schema is None:
            raise RuntimeConfigError("executor output schema path is not configured")
        command = [
            self.executable,
            "exec",
            "--strict-config",
            "--ephemeral",
            "--ignore-user-config",
            "--ignore-rules",
            "--skip-git-repo-check",
            "--cd",
            str(workspace),
            "--model",
            self.model,
            "--output-schema",
            str(self.output_schema),
            "--output-last-message",
            str(output_path),
            "--json",
            "--disable",
            "remote_plugin",
            "--disable",
            "apps",
            "--config",
            'approval_policy="never"',
            "--config",
            'default_permissions="eval-runtime"',
            "--config",
            'permissions.eval-runtime.extends=":workspace"',
            "--config",
            "permissions.eval-runtime.network.enabled=false",
            "--config",
            "features.multi_agent=false",
        ]
        if self.apim_config is not None:
            command.extend([
                "--config",
                'model_provider="azure_apim"',
                "--config",
                self._apim_provider_override(),
                "--config",
                'shell_environment_policy.filters={"AZURE_OPENAI_API_KEY"="exclude",'
                '"EVAL_APIM_SUBSCRIPTION_KEY"="exclude",'
                '"EVAL_APIM_CLIENT_USER_KEY"="exclude",'
                '"EVAL_APIM_CLIENT_USERNAME"="exclude"}',
            ])
        if denied_auth_root is not None:
            command.extend([
                "--config",
                "permissions.eval-runtime.filesystem={"
                f"{json.dumps(str(denied_auth_root))}=\"deny\""
                "}",
            ])
        command.append("-")
        return command

    def execute(self, request: dict[str, Any], workspace: Path) -> RuntimeResult:
        self.check_config()
        started = time.monotonic()
        with tempfile.TemporaryDirectory(prefix="agent-commons-codex-output-") as temporary:
            output_path = Path(temporary) / "executor-output.json"
            source_environment = {
                key: value for key, value in os.environ.items() if not value.startswith("$(")
            }
            api_key = source_environment.get("OPENAI_API_KEY")
            access_token = source_environment.get("CODEX_ACCESS_TOKEN")
            child_environment = sanitized_executor_environment(source_environment)
            runtime_home = Path(temporary) / "runtime-home"
            runtime_cache = runtime_home / "cache"
            runtime_config = runtime_home / "config"
            runtime_directory = runtime_home / "runtime"
            for directory in (runtime_home, runtime_cache, runtime_config, runtime_directory):
                directory.mkdir()
            runtime_directory.chmod(0o700)
            child_environment.update({
                "HOME": str(runtime_home),
                "XDG_CACHE_HOME": str(runtime_cache),
                "XDG_CONFIG_HOME": str(runtime_config),
                "XDG_RUNTIME_DIR": str(runtime_directory),
            })
            denied_auth_root: Optional[Path] = None
            if self.apim_config is not None:
                self._check_apim_config()
                codex_home = Path(temporary) / "codex-home"
                codex_home.mkdir()
                child_environment.update({
                    "CODEX_HOME": str(codex_home),
                    "AZURE_OPENAI_API_KEY": self.apim_config.api_key,
                    "EVAL_APIM_SUBSCRIPTION_KEY": self.apim_config.subscription_key,
                    "EVAL_APIM_CLIENT_USER_KEY": self.apim_config.client_user_key,
                    "EVAL_APIM_CLIENT_USERNAME": self.apim_config.client_username,
                })
                denied_auth_root = codex_home
            elif api_key or access_token:
                codex_home = Path(temporary) / "codex-home"
                codex_home.mkdir()
                child_environment["CODEX_HOME"] = str(codex_home)
                denied_auth_root = codex_home
                login_command = [
                    self.executable,
                    "login",
                    "--with-api-key" if api_key else "--with-access-token",
                ]
                try:
                    login = subprocess.run(
                        login_command,
                        cwd=workspace,
                        input=api_key or access_token,
                        capture_output=True,
                        text=True,
                        timeout=30,
                        env=child_environment,
                    )
                except (OSError, subprocess.TimeoutExpired) as exc:
                    raise RuntimeExecutionError(f"Codex authentication bootstrap failed: {exc}") from exc
                if login.returncode:
                    raise RuntimeExecutionError(
                        f"Codex authentication bootstrap exited {login.returncode}"
                    )
            elif source_environment.get("CODEX_HOME"):
                child_environment["CODEX_HOME"] = source_environment["CODEX_HOME"]
            command = self._command(workspace, output_path, denied_auth_root)
            try:
                completed = self.runner(
                    command,
                    cwd=workspace,
                    input=executor_prompt(request),
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds,
                    env=child_environment,
                )
            except subprocess.TimeoutExpired as exc:
                raise RuntimeExecutionError(
                    f"Codex execution timed out after {self.timeout_seconds} seconds",
                    transient=True,
                ) from exc
            except OSError as exc:
                raise RuntimeExecutionError(f"Codex execution could not start: {exc}") from exc
            if completed.returncode:
                detail = self._redact(
                    (completed.stderr or completed.stdout or "Codex execution failed")[-2000:]
                )
                lowered = detail.lower()
                transient = any(marker in lowered for marker in (
                    "429", "rate limit", "temporarily unavailable", "service unavailable",
                    "connection reset", "connection timed out", "timeout",
                ))
                raise RuntimeExecutionError(
                    f"Codex exited {completed.returncode}: {detail}", transient=transient,
                )
            if not output_path.is_file():
                raise RuntimeExecutionError("Codex did not write the schema-constrained final response")
            try:
                output = json.loads(output_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise RuntimeExecutionError(f"Codex final response was not valid JSON: {exc}") from exc
        observability = parse_codex_jsonl(completed.stdout)
        return RuntimeResult(
            output=output,
            runtime=self.name,
            model=str(observability.get("model") or self.model),
            duration_seconds=time.monotonic() - started,
            input_tokens=observability.get("input_tokens"),
            output_tokens=observability.get("output_tokens"),
            total_tokens=observability.get("total_tokens"),
            stdout=completed.stdout,
            stderr=completed.stderr,
        )


def runtime_from_environment(
    environment: Optional[dict[str, str]] = None,
    *,
    output_schema: Optional[Path] = None,
) -> SemanticExecutor:
    env = environment if environment is not None else os.environ
    def value(name: str, default: str = "") -> str:
        resolved = env.get(name, default).strip()
        return default if resolved.startswith("$(") else resolved

    runtime = value("EVAL_EXECUTOR_RUNTIME", "codex").lower()
    if runtime != "codex":
        raise RuntimeConfigError(f"unsupported semantic executor runtime: {runtime}")
    timeout = int(value("EVAL_EXECUTOR_TIMEOUT_SECONDS", "1500"))
    executor_provider = value("EVAL_EXECUTOR_PROVIDER", "openai").lower()
    if executor_provider not in {"openai", "azure_openai_apim"}:
        raise RuntimeConfigError(f"unsupported Codex executor provider: {executor_provider}")
    apim_config = None
    if executor_provider == "azure_openai_apim":
        apim_config = CodexAPIMConfig(
            endpoint=value("EVAL_EXECUTOR_ENDPOINT") or value("EVAL_ENDPOINT"),
            allowed_host=value("EVAL_APIM_ALLOWED_HOST"),
            api_version=value("EVAL_EXECUTOR_API_VERSION") or value("EVAL_API_VERSION"),
            api_key=value("EVAL_EXECUTOR_API_KEY") or value("AZURE_OPENAI_API_KEY"),
            subscription_key=(
                value("EVAL_EXECUTOR_APIM_SUBSCRIPTION_KEY")
                or value("EVAL_APIM_SUBSCRIPTION_KEY")
            ),
            client_user_key=(
                value("EVAL_EXECUTOR_APIM_CLIENT_USER_KEY")
                or value("EVAL_APIM_CLIENT_USER_KEY")
            ),
            client_username=(
                value("EVAL_EXECUTOR_APIM_CLIENT_USERNAME")
                or value("EVAL_APIM_CLIENT_USERNAME")
            ),
        )
    return CodexExecutor(
        model=value("EVAL_EXECUTOR_MODEL"),
        executable=value("EVAL_CODEX_BIN", "codex"),
        timeout_seconds=timeout,
        output_schema=output_schema,
        apim_config=apim_config,
    )
