#!/usr/bin/env python3
"""Provider-neutral semantic judge transport with OpenAI-compatible implementations."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from dataclasses import dataclass
from typing import Any, Callable, Optional

from secure_http import https_origin, secure_urlopen


class ProviderError(RuntimeError):
    """Base semantic provider failure."""


class AuthenticationError(ProviderError):
    """No supported provider credential is configured."""


class ProviderTransientError(ProviderError):
    """A retryable provider or network failure."""


class ProviderProtocolError(ProviderError):
    """The provider response did not satisfy the expected protocol."""


@dataclass(frozen=True)
class ProviderConfig:
    provider: str
    endpoint: str
    model: str
    api_key: Optional[str] = None
    bearer_token: Optional[str] = None
    api_version: Optional[str] = None
    apim_allowed_host: Optional[str] = None
    apim_subscription_key: Optional[str] = None
    apim_client_user_key: Optional[str] = None
    apim_client_username: Optional[str] = None
    timeout_seconds: int = 180


@dataclass(frozen=True)
class ProviderResult:
    output: dict[str, Any]
    provider: str
    model: str
    duration_seconds: float
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


Transport = Callable[[urllib.request.Request, int], tuple[int, dict[str, str], bytes]]


class SemanticJudgeProvider:
    """Interface for an independent semantic judge model provider."""

    def check_config(self, *, resolve_auth: bool = True) -> dict[str, str]:
        raise NotImplementedError

    def judge(
        self,
        judge_input: dict[str, Any],
        output_schema: dict[str, Any],
        instructions: str,
    ) -> ProviderResult:
        raise NotImplementedError


def default_transport(
    request: urllib.request.Request,
    timeout: int,
) -> tuple[int, dict[str, str], bytes]:
    try:
        with secure_urlopen(request, timeout=timeout) as response:
            return response.status, dict(response.headers.items()), response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers.items()), exc.read()
    except (urllib.error.URLError, TimeoutError) as exc:
        raise ProviderTransientError(f"provider connection failed: {exc.reason if hasattr(exc, 'reason') else exc}") from exc


def _azure_access_token() -> Optional[str]:
    try:
        from azure.identity import DefaultAzureCredential  # type: ignore

        credential = DefaultAzureCredential(exclude_interactive_browser_credential=True)
        return credential.get_token("https://cognitiveservices.azure.com/.default").token
    except Exception:
        pass
    if shutil.which("az"):
        try:
            completed = subprocess.run(
                [
                    "az", "account", "get-access-token", "--resource",
                    "https://cognitiveservices.azure.com", "--query", "accessToken", "-o", "tsv",
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=20,
            )
        except (OSError, subprocess.TimeoutExpired):
            return None
        token = completed.stdout.strip()
        if completed.returncode == 0 and token:
            return token
    return None


def provider_config_from_environment(environment: Optional[dict[str, str]] = None) -> ProviderConfig:
    env = environment if environment is not None else os.environ
    def value(name: str, default: str = "") -> str:
        resolved = env.get(name, default).strip()
        return default if resolved.startswith("$(") else resolved

    provider = value("EVAL_PROVIDER", "azure_openai").lower()
    if provider not in {"azure_openai", "azure_openai_apim", "openai"}:
        raise ProviderProtocolError(f"unsupported semantic judge provider: {provider}")
    endpoint = value("EVAL_ENDPOINT")
    if provider == "openai" and not endpoint:
        endpoint = "https://api.openai.com/v1"
    model = value("EVAL_JUDGE_MODEL")
    api_key = value("EVAL_API_KEY") or (
        value("AZURE_OPENAI_API_KEY")
        if provider in {"azure_openai", "azure_openai_apim"}
        else value("OPENAI_API_KEY")
    )
    bearer = value("EVAL_BEARER_TOKEN")
    return ProviderConfig(
        provider=provider,
        endpoint=endpoint,
        model=model,
        api_key=api_key,
        bearer_token=bearer,
        api_version=value("EVAL_API_VERSION"),
        apim_allowed_host=value("EVAL_APIM_ALLOWED_HOST"),
        apim_subscription_key=value("EVAL_APIM_SUBSCRIPTION_KEY"),
        apim_client_user_key=value("EVAL_APIM_CLIENT_USER_KEY"),
        apim_client_username=value("EVAL_APIM_CLIENT_USERNAME"),
        timeout_seconds=int(value("EVAL_JUDGE_TIMEOUT_SECONDS", "180")),
    )


class OpenAICompatibleProvider(SemanticJudgeProvider):
    """Call the Responses API for OpenAI or Azure OpenAI v1 endpoints."""

    def __init__(self, config: ProviderConfig, *, transport: Transport = default_transport) -> None:
        self.config = config
        self.transport = transport

    def check_config(self, *, resolve_auth: bool = True) -> dict[str, str]:
        if not self.config.endpoint:
            raise ProviderProtocolError("EVAL_ENDPOINT is required for the configured provider")
        try:
            _, hostname, _ = https_origin(self.config.endpoint, label="EVAL_ENDPOINT")
        except ValueError as exc:
            raise ProviderProtocolError(str(exc)) from exc
        if self.config.provider == "openai" and hostname != "api.openai.com":
            raise ProviderProtocolError("openai EVAL_ENDPOINT must use api.openai.com")
        if self.config.provider == "azure_openai" and not hostname.endswith(".openai.azure.com"):
            raise ProviderProtocolError(
                "azure_openai EVAL_ENDPOINT must use an Azure OpenAI *.openai.azure.com host"
            )
        if self.config.provider == "azure_openai_apim":
            if not hostname.endswith(".azure-api.net"):
                raise ProviderProtocolError(
                    "azure_openai_apim EVAL_ENDPOINT must use an Azure API Management *.azure-api.net host"
                )
            allowed_host = (self.config.apim_allowed_host or "").strip().casefold()
            if not allowed_host or ":" in allowed_host or "/" in allowed_host:
                raise ProviderProtocolError(
                    "EVAL_APIM_ALLOWED_HOST must be one hostname without scheme or path"
                )
            if hostname != allowed_host:
                raise ProviderProtocolError(
                    "EVAL_ENDPOINT host does not match EVAL_APIM_ALLOWED_HOST"
                )
            required = {
                "EVAL_APIM_ALLOWED_HOST": self.config.apim_allowed_host,
                "EVAL_API_VERSION": self.config.api_version,
                "EVAL_APIM_SUBSCRIPTION_KEY": self.config.apim_subscription_key,
                "EVAL_APIM_CLIENT_USER_KEY": self.config.apim_client_user_key,
                "EVAL_APIM_CLIENT_USERNAME": self.config.apim_client_username,
            }
            missing = [name for name, value in required.items() if not value]
            if missing:
                raise ProviderProtocolError(
                    "Azure OpenAI APIM judge configuration is missing: " + ", ".join(missing)
                )
        if not self.config.model:
            raise ProviderProtocolError("EVAL_JUDGE_MODEL is required")
        auth = "api_key" if self.config.api_key else "bearer" if self.config.bearer_token else None
        if not auth and self.config.provider == "azure_openai" and resolve_auth:
            auth = "azure_identity" if _azure_access_token() else None
        if not auth and self.config.provider == "azure_openai" and not resolve_auth:
            if shutil.which("az"):
                auth = "azure_identity"
            else:
                try:
                    import azure.identity  # type: ignore  # noqa: F401
                    auth = "azure_identity"
                except ImportError:
                    auth = None
        if not auth:
            if self.config.provider == "azure_openai":
                variable = "AZURE_OPENAI_API_KEY/EVAL_API_KEY or Azure identity"
            elif self.config.provider == "azure_openai_apim":
                variable = "AZURE_OPENAI_API_KEY/EVAL_API_KEY"
            else:
                variable = "OPENAI_API_KEY/EVAL_API_KEY"
            raise AuthenticationError(f"judge authentication unavailable; configure {variable}")
        return {
            "provider": self.config.provider,
            "endpoint": self.config.endpoint,
            "model": self.config.model,
            "authentication": auth,
        }

    def _url(self) -> str:
        base = self.config.endpoint.rstrip("/")
        if self.config.provider == "azure_openai" and not base.endswith("/openai/v1"):
            base += "/openai/v1"
        if not base.endswith("/responses"):
            base += "/responses"
        if self.config.provider != "azure_openai_apim":
            return base
        parsed = urlsplit(base)
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))
        query["api-version"] = self.config.api_version or ""
        return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment))

    def _authorization_headers(self) -> dict[str, str]:
        headers: dict[str, str]
        if self.config.api_key:
            if self.config.provider == "azure_openai":
                headers = {"api-key": self.config.api_key}
            else:
                headers = {"Authorization": f"Bearer {self.config.api_key}"}
        else:
            token = self.config.bearer_token
            if not token and self.config.provider == "azure_openai":
                token = _azure_access_token()
            if not token:
                raise AuthenticationError("judge authentication became unavailable")
            headers = {"Authorization": f"Bearer {token}"}
        if self.config.provider == "azure_openai_apim":
            headers.update({
                "Ocp-Apim-Subscription-Key": self.config.apim_subscription_key or "",
                "x-client-userkey": self.config.apim_client_user_key or "",
                "x-client-username": self.config.apim_client_username or "",
            })
        return headers

    def judge(
        self,
        judge_input: dict[str, Any],
        output_schema: dict[str, Any],
        instructions: str,
    ) -> ProviderResult:
        self.check_config(resolve_auth=False)
        payload = {
            "model": self.config.model,
            "instructions": instructions,
            "input": json.dumps(judge_input, sort_keys=True),
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "agent_commons_semantic_judgement",
                    "strict": False,
                    "schema": output_schema,
                },
            },
        }
        headers = {"Content-Type": "application/json", **self._authorization_headers()}
        request = urllib.request.Request(
            self._url(), data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST",
        )
        started = time.monotonic()
        status, _, body = self.transport(request, self.config.timeout_seconds)
        if status in {408, 409, 429} or status >= 500:
            raise ProviderTransientError(f"provider returned transient HTTP {status}")
        if status in {401, 403}:
            raise AuthenticationError(f"provider authentication failed with HTTP {status}")
        if status < 200 or status >= 300:
            raise ProviderError(f"provider returned HTTP {status}")
        try:
            response = json.loads(body)
        except json.JSONDecodeError as exc:
            raise ProviderProtocolError(f"provider returned invalid JSON: {exc}") from exc
        if response.get("status") not in {None, "completed"}:
            raise ProviderProtocolError(f"provider response did not complete: {response.get('status')}")
        text: Optional[str] = response.get("output_text") if isinstance(response.get("output_text"), str) else None
        if text is None:
            for item in response.get("output", []):
                if not isinstance(item, dict):
                    continue
                for content in item.get("content", []):
                    if isinstance(content, dict) and content.get("type") == "refusal":
                        raise ProviderProtocolError("judge provider refused the evaluation request")
                    if isinstance(content, dict) and content.get("type") == "output_text":
                        text = content.get("text")
                        break
                if text is not None:
                    break
        if not isinstance(text, str) or not text.strip():
            raise ProviderProtocolError("provider response did not contain output text")
        try:
            output = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ProviderProtocolError(f"judge output text was not valid JSON: {exc}") from exc
        usage = response.get("usage", {}) if isinstance(response.get("usage"), dict) else {}
        return ProviderResult(
            output=output,
            provider=self.config.provider,
            model=str(response.get("model") or self.config.model),
            duration_seconds=time.monotonic() - started,
            input_tokens=usage.get("input_tokens") if isinstance(usage.get("input_tokens"), int) else None,
            output_tokens=usage.get("output_tokens") if isinstance(usage.get("output_tokens"), int) else None,
            total_tokens=usage.get("total_tokens") if isinstance(usage.get("total_tokens"), int) else None,
        )


def provider_from_environment(environment: Optional[dict[str, str]] = None) -> OpenAICompatibleProvider:
    return OpenAICompatibleProvider(provider_config_from_environment(environment))
