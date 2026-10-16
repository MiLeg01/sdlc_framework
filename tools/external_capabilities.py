#!/usr/bin/env python3
"""Discover and maintain metadata for untrusted external agent capabilities."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from functools import lru_cache
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
SOURCES_PATH = ROOT / "external" / "sources.yaml"
INDEX_PATH = ROOT / "external" / "index" / "capabilities.json"
CATALOG_PATH = ROOT / "catalog" / "capabilities.yaml"
TRUSTS = {"OFFICIAL", "CURATED", "COMMUNITY", "UNTRUSTED"}
SOURCE_TYPES = {"github-repository", "github-organization", "github-search", "registry", "website", "web-discovery"}
STATUSES = {"DISCOVERED", "REVIEWED", "REJECTED", "PROMOTION-CANDIDATE", "INCORPORATED", "SUPERSEDED", "STALE"}
REVIEW_STATUSES = {"NOT_REVIEWED", "CURRENT", "OUTDATED"}
SECURITY_CLASSES = {"INSTRUCTIONS ONLY", "INSTRUCTIONS + SCRIPTS", "PLUGIN WITH HOOKS", "MCP/REMOTE TOOLING", "UNKNOWN"}
RELATIONSHIPS = {"COPIED", "ADAPTED", "INSPIRED-BY", "INDEPENDENT-REIMPLEMENTATION"}
REVIEW_FIELDS = {
    "schema_version", "id", "source_id", "repository", "path", "revision", "trust", "license",
    "license_scope", "security_class", "relationship", "status", "reviewed_at",
}
REVIEW_HEADINGS = {
    "## Provenance", "## License assessment", "## Security and supply-chain characteristics",
    "## Semantic comparison with current commons", "## Useful novel patterns",
    "## Rejected or non-canonical patterns", "## Promotion candidates",
    "## Required evaluations before promotion", "## Final recommendation",
}
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9.+#-]*")
STOPWORDS = {
    "a", "an", "and", "agent", "agents", "for", "from", "in", "of", "on", "or", "the", "to",
    "tool", "tools", "workflow", "workflows", "skill", "skills", "code", "with", "this", "that",
}
GENERIC_RELEVANCE_TERMS = {
    "agent", "agents", "code", "development", "java", "legacy", "migration", "modernization",
    "software", "test", "testing", "tool", "tools", "workflow", "workflows",
}
TECHNOLOGY_ANCHORS = {"cobol", "pli", "sas", "java-21", "spring", "mainframe", "copybook"}
SAFE_EXTERNAL_QUERY_TERMS = GENERIC_RELEVANCE_TERMS | TECHNOLOGY_ANCHORS | {
    "4.x", "acceptance", "analysis", "architecture", "aware", "business", "characterization",
    "c++", "c#", "data", "delivery", "dependency", "diagram", "dotnet", "evaluation", "evidence",
    "boot", "extraction", "go", "graph", "html", "javascript", "kotlin", "lineage", "mapping", "net", "parity", "php", "presentation", "python",
    "qa", "requirements", "review", "rule", "rules", "ruby", "rust", "scala", "security", "semantic",
    "spring", "sql", "standalone", "strategy", "target", "traceability", "typescript", "upgrade", "validation", "visual",
}
DISCOVERY_STATUSES = {"completed", "partial-rate-limited", "partial-source-failure", "failed"}
CAPABILITY_MARKERS = ("skill.md", "/skills/", "/agents/", "/commands/", "/workflows/", "mcp", "hook", "plugin")
PROJECT_TECHNOLOGIES = {
    ".cbl": "COBOL", ".cob": "COBOL", ".pli": "PL/I", ".java": "Java", ".kt": "Kotlin",
    ".cs": ".NET", ".fs": ".NET", ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
    ".tsx": "TypeScript", ".go": "Go", ".rs": "Rust", ".rb": "Ruby", ".php": "PHP",
    ".sql": "SQL", ".scala": "Scala", ".cpp": "C++", ".cc": "C++", ".c": "C",
}


class ExternalCapabilityError(ValueError):
    """External metadata or discovery input is invalid."""


class ProviderRequestError(ExternalCapabilityError):
    """A redacted, structured provider failure safe to persist."""

    def __init__(self, failure: dict[str, Any]) -> None:
        self.failure = failure
        super().__init__(f"{failure.get('provider', 'provider')} {failure.get('operation', 'request')} failed")


class DiscoveryLease:
    """Small project-local lease preventing duplicate discovery processes."""

    def __init__(self, path: Path, request_key: str, stale_seconds: int = 1800) -> None:
        self.path = path
        self.request_key = request_key
        self.stale_seconds = max(1, stale_seconds)
        self.acquired = False

    def acquire(self) -> bool:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"pid": os.getpid(), "request_key": self.request_key, "started_at": utc_now()}
        try:
            descriptor = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            try:
                age = max(0.0, time.time() - self.path.stat().st_mtime)
            except OSError:
                return False
            if age <= self.stale_seconds:
                return False
            try:
                self.path.unlink()
            except OSError:
                return False
            return self.acquire()
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, sort_keys=True)
            handle.write("\n")
        self.acquired = True
        return True

    def release(self) -> None:
        if not self.acquired:
            return
        try:
            current = load_json(self.path)
            if current.get("pid") == os.getpid() and current.get("request_key") == self.request_key:
                self.path.unlink(missing_ok=True)
        except (ExternalCapabilityError, OSError):
            pass
        self.acquired = False

    def __enter__(self) -> "DiscoveryLease":
        if not self.acquire():
            raise ExternalCapabilityError("matching external discovery is already running")
        return self

    def __exit__(self, *_: object) -> None:
        self.release()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ExternalCapabilityError(f"invalid JSON-compatible YAML/JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ExternalCapabilityError(f"expected object in {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def registry_fingerprint(registry: dict[str, Any]) -> str:
    encoded = json.dumps(registry, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def normalize_github(value: str) -> str:
    raw = value.strip()
    raw = re.sub(r"^git@github\.com:", "", raw, flags=re.I)
    raw = re.sub(r"^ssh://git@github\.com/", "", raw, flags=re.I)
    raw = re.sub(r"^https?://(?:www\.)?github\.com/", "", raw, flags=re.I)
    raw = raw.split("?", 1)[0].split("#", 1)[0].strip("/")
    if raw.endswith(".git"):
        raw = raw[:-4]
    parts = raw.split("/")
    if len(parts) < 2 or not all(re.fullmatch(r"[A-Za-z0-9_.-]+", part) for part in parts[:2]):
        raise ExternalCapabilityError(f"not a GitHub repository URL or owner/repository slug: {value}")
    return "/".join(parts[:2])


def normalize_topic(value: str) -> str:
    normalized = value.strip().casefold()
    normalized = re.sub(r"\b(?:pl\s*/\s*i|pl[- ]?1|pli)\b", "pl/i", normalized)
    normalized = re.sub(r"\bjava\s*[- ]?21\b", "java-21", normalized)
    normalized = re.sub(r"\bspring\s+boot\s+4(?:\.x)?\b", "spring boot 4.x", normalized)
    normalized = re.sub(r"\bmodernisation\b", "modernization", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip(" ,;|")
    return normalized


def validate_topic_privacy(values: list[str]) -> None:
    for raw in values:
        protected = re.sub(r"\bpl\s*/\s*i\b", "pli", str(raw), flags=re.I)
        if re.search(r"https?://|(?:^|\s)/(?:Users|home|private|var)/|[A-Za-z]:\\|\.git(?:/|\b)", protected, re.I):
            raise ExternalCapabilityError("search topic contains a URL or local path; use generic capability terms only")
        if re.search(r"\b(?:client|customer|repository|repo|project)\s*[:=]", protected, re.I):
            raise ExternalCapabilityError("search topic contains project-sensitive identifiers; use generic capability terms only")
        if re.search(r"\b[A-Za-z_][A-Za-z0-9_.-]*/[A-Za-z_][A-Za-z0-9_.-]*\b", protected):
            raise ExternalCapabilityError("search topic contains a repository identifier; use generic capability terms only")
        if any(marker in protected for marker in ("-----BEGIN", "api_key=", "token=", "password=")):
            raise ExternalCapabilityError("search topic contains credential-like or source content; use generic capability terms only")
        normalized_terms = set(terms(normalize_topic(protected).replace("pl/i", "pli")))
        unknown = normalized_terms - SAFE_EXTERNAL_QUERY_TERMS - STOPWORDS
        if unknown:
            raise ExternalCapabilityError("search topic contains non-allowlisted identifiers; use generic capability terms only")


def _specific_topic_terms(value: str) -> set[str]:
    normalized = normalize_topic(value).replace("pl/i", "pli")
    return {token for token in terms(normalized) if token not in GENERIC_RELEVANCE_TERMS}


def normalize_topics(values: list[str]) -> list[str]:
    candidates: list[tuple[str, set[str]]] = []
    for raw in values:
        normalized = normalize_topic(str(raw))
        if not normalized:
            continue
        specific = _specific_topic_terms(normalized)
        if not specific:
            continue
        duplicate = False
        for index, (current, current_specific) in enumerate(candidates):
            if normalized == current or (specific and specific == current_specific):
                preferred = min((current, normalized), key=lambda item: (len(item.split()), len(item), item))
                candidates[index] = (preferred, _specific_topic_terms(preferred))
                duplicate = True
                break
        if not duplicate:
            candidates.append((normalized, specific))
    return [value for value, _ in candidates[:8]]


def matched_capability_gaps(haystack: str, topics: list[str]) -> list[str]:
    normalized_haystack = normalize_topic(haystack).replace("pl/i", "pli")
    haystack_terms = set(terms(normalized_haystack))
    for token in tuple(haystack_terms):
        haystack_terms.update(part for part in token.split("-") if part)
    matched: list[str] = []
    for topic in topics:
        specific = _specific_topic_terms(topic)
        anchors = specific & TECHNOLOGY_ANCHORS
        capability_terms = specific - TECHNOLOGY_ANCHORS
        anchor_match = not anchors or bool(anchors & haystack_terms)
        capability_overlap = capability_terms & haystack_terms
        minimum_capability_matches = 0 if not capability_terms else min(2, len(capability_terms))
        capability_match = len(capability_overlap) >= minimum_capability_matches
        if specific and anchor_match and capability_match:
            matched.append(topic)
    return matched


def combined_community_query(topics: list[str]) -> str:
    phrases: list[str] = []
    for topic in topics:
        normalized = normalize_topic(topic).replace("pl/i", "pli")
        ordered = [token for token in terms(normalized) if token not in GENERIC_RELEVANCE_TERMS]
        if ordered:
            phrases.append(" ".join(ordered[:5]))
    unique = list(dict.fromkeys(phrases))[:6]
    if not unique:
        return ""
    expression = " OR ".join(unique)
    return f"({expression}) agent in:name,description,readme is:public"


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ExternalCapabilityError(f"missing or invalid review frontmatter: {path}")
    end = text.index("\n---\n", 4)
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            raise ExternalCapabilityError(f"invalid frontmatter line in {path}: {line}")
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values, text[end + 5:]


def validate_registry(registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if registry.get("schema_version") != 1:
        errors.append("external source registry schema_version must be 1")
    discovery = registry.get("discovery")
    expected_flags = {"official_sources", "curated_sources", "github_search", "general_web_search"}
    if not isinstance(discovery, dict) or set(discovery) != expected_flags or not all(isinstance(discovery.get(key), bool) for key in expected_flags):
        errors.append("external source registry discovery flags are invalid")
    github = registry.get("github")
    if not isinstance(github, dict):
        errors.append("external source registry github policy is missing")
    else:
        expected_github = {"minimum_remaining", "repository_cache_ttl_seconds", "stop_after_candidates"}
        if set(github) != expected_github or any(not isinstance(github.get(key), int) or github[key] < 0 for key in expected_github):
            errors.append("external source registry github policy is invalid")
        elif not 1 <= github["stop_after_candidates"] <= 20:
            errors.append("external source registry stop_after_candidates must be between 1 and 20")
    sources = registry.get("sources")
    if not isinstance(sources, list):
        return errors + ["external source registry sources must be a list"]
    ids: set[str] = set()
    expected_tier = {"OFFICIAL": 1, "CURATED": 2, "COMMUNITY": 3, "UNTRUSTED": 4}
    for index, source in enumerate(sources):
        label = f"sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{label} must be an object")
            continue
        identifier = source.get("id")
        if not isinstance(identifier, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", identifier):
            errors.append(f"{label} has invalid id")
        elif identifier in ids:
            errors.append(f"duplicate external source id: {identifier}")
        else:
            ids.add(identifier)
        trust = source.get("trust")
        if trust not in TRUSTS:
            errors.append(f"{label} has invalid trust")
        elif source.get("tier") != expected_tier[trust]:
            errors.append(f"{identifier}: tier does not match trust {trust}")
        if source.get("type") not in SOURCE_TYPES:
            errors.append(f"{identifier}: unsupported source type")
        if not isinstance(source.get("enabled"), bool):
            errors.append(f"{identifier}: enabled must be boolean")
        if not isinstance(source.get("description"), str) or len(source["description"]) < 20:
            errors.append(f"{identifier}: description is missing or too short")
        if not isinstance(source.get("capability_categories"), list) or not source["capability_categories"]:
            errors.append(f"{identifier}: capability_categories must be non-empty")
        if source.get("type") == "github-repository":
            try:
                repository = normalize_github(str(source.get("repository", "")))
                location = normalize_github(str(source.get("location", "")))
                if repository.lower() != location.lower():
                    errors.append(f"{identifier}: repository and location disagree")
            except ExternalCapabilityError as exc:
                errors.append(f"{identifier}: {exc}")
    if isinstance(discovery, dict) and discovery.get("general_web_search"):
        enabled_web = [source for source in sources if isinstance(source, dict) and source.get("type") == "web-discovery" and source.get("enabled")]
        if not enabled_web:
            errors.append("general_web_search is enabled without an enabled web-discovery source")
    return errors


def validate_review(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        metadata, body = parse_frontmatter(path)
    except (OSError, ExternalCapabilityError) as exc:
        return [str(exc)]
    missing = REVIEW_FIELDS - metadata.keys()
    extra = metadata.keys() - REVIEW_FIELDS
    if missing:
        errors.append(f"{path.name}: missing review fields {sorted(missing)}")
    if extra:
        errors.append(f"{path.name}: unexpected review fields {sorted(extra)}")
    if metadata.get("schema_version") != "1":
        errors.append(f"{path.name}: schema_version must be 1")
    if metadata.get("trust") not in TRUSTS:
        errors.append(f"{path.name}: invalid trust")
    if metadata.get("security_class") not in SECURITY_CLASSES:
        errors.append(f"{path.name}: invalid security_class")
    if metadata.get("relationship") not in RELATIONSHIPS:
        errors.append(f"{path.name}: invalid relationship")
    if metadata.get("status") not in STATUSES - {"DISCOVERED"}:
        errors.append(f"{path.name}: invalid reviewed status")
    if metadata.get("license", "").upper() in {"UNKNOWN", "LICENSE UNKNOWN"} and metadata.get("relationship") in {"COPIED", "ADAPTED"}:
        errors.append(f"{path.name}: unknown license prohibits copied or adapted relationship")
    missing_headings = sorted(heading for heading in REVIEW_HEADINGS if heading not in body)
    if missing_headings:
        errors.append(f"{path.name}: missing review sections {missing_headings}")
    return errors


def validate_index(index: dict[str, Any], registry: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if index.get("schema_version") != 1:
        errors.append("external index schema_version must be 1")
    expected_fingerprint = registry_fingerprint(registry)
    if index.get("source_registry_fingerprint") != expected_fingerprint:
        warnings.append("external index source registry fingerprint is stale")
    sources = {source["id"]: source for source in registry.get("sources", []) if isinstance(source, dict) and "id" in source}
    candidates = index.get("candidates")
    if not isinstance(candidates, list):
        return errors + ["external index candidates must be a list"], warnings
    ids: set[str] = set()
    for position, candidate in enumerate(candidates):
        label = f"candidates[{position}]"
        if not isinstance(candidate, dict):
            errors.append(f"{label} must be an object")
            continue
        identifier = candidate.get("id")
        if not isinstance(identifier, str) or not re.fullmatch(r"ext-[a-z0-9-]+", identifier):
            errors.append(f"{label} has invalid id")
        elif identifier in ids:
            errors.append(f"duplicate external candidate id: {identifier}")
        else:
            ids.add(identifier)
        source = sources.get(candidate.get("source_id"))
        if source is None:
            errors.append(f"{identifier}: unknown source_id {candidate.get('source_id')}")
        elif candidate.get("source_trust") != source.get("trust"):
            errors.append(f"{identifier}: source trust does not match registry")
        if candidate.get("status") not in STATUSES:
            errors.append(f"{identifier}: invalid status")
        if candidate.get("review_status") not in REVIEW_STATUSES:
            errors.append(f"{identifier}: invalid review_status")
        if candidate.get("security_class") not in SECURITY_CLASSES:
            errors.append(f"{identifier}: invalid security_class")
        relationship = candidate.get("relationship")
        if relationship is not None and relationship not in RELATIONSHIPS:
            errors.append(f"{identifier}: invalid relationship")
        license_data = candidate.get("license")
        if not isinstance(license_data, dict) or not license_data.get("status") or not license_data.get("copy_policy"):
            errors.append(f"{identifier}: incomplete license metadata")
        elif license_data.get("status") == "UNKNOWN" and relationship in {"COPIED", "ADAPTED"}:
            errors.append(f"{identifier}: unknown license prohibits copied or adapted relationship")
        review_path = candidate.get("review_path")
        if candidate.get("review_status") != "NOT_REVIEWED":
            if not review_path or not (ROOT / review_path).is_file():
                errors.append(f"{identifier}: reviewed candidate lacks review_path")
            else:
                try:
                    metadata, _ = parse_frontmatter(ROOT / review_path)
                    if metadata.get("id") != identifier or metadata.get("revision") != candidate.get("revision"):
                        errors.append(f"{identifier}: review metadata does not match index")
                except ExternalCapabilityError as exc:
                    errors.append(str(exc))
    return errors, warnings


class GitHubClient:
    def __init__(
        self,
        max_attempts: int = 3,
        backoff_seconds: float = 0.25,
        detect_auth: bool = True,
        minimum_remaining: int = 5,
    ) -> None:
        self.max_attempts = max(1, max_attempts)
        self.backoff_seconds = max(0.0, backoff_seconds)
        self.minimum_remaining = max(0, minimum_remaining)
        self.token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        self.transport = "token-api" if self.token else "anonymous-api"
        self.authenticated = bool(self.token)
        self.rate_limits: dict[str, dict[str, int | float | None]] = {}
        self.network_requests = 0
        self._lock = threading.Lock()
        if detect_auth and shutil.which("gh"):
            status = subprocess.run(
                ["gh", "auth", "status", "--hostname", "github.com"],
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                check=False,
            )
            if status.returncode == 0:
                self.transport = "gh-cli"
                self.authenticated = True

    def access_summary(self) -> dict[str, object]:
        return {"provider": "github", "transport": self.transport, "authenticated": self.authenticated}

    @staticmethod
    def _header_value(headers: Any, name: str) -> str | None:
        if headers is None:
            return None
        value = headers.get(name) if hasattr(headers, "get") else None
        if value in {None, ""} and isinstance(headers, dict):
            expected = name.casefold()
            value = next((candidate for key, candidate in headers.items() if str(key).casefold() == expected), None)
        return str(value) if value not in {None, ""} else None

    def observe_rate_limit(self, headers: Any, resource_override: str | None = None) -> None:
        resource = resource_override or self._header_value(headers, "X-RateLimit-Resource") or "core"
        remaining_raw = self._header_value(headers, "X-RateLimit-Remaining")
        reset_raw = self._header_value(headers, "X-RateLimit-Reset")
        retry_raw = self._header_value(headers, "Retry-After")
        with self._lock:
            state = self.rate_limits.setdefault(resource, {"remaining": None, "reset_epoch": None, "retry_after_seconds": None, "blocked_until": None})
            if remaining_raw and remaining_raw.isdigit():
                state["remaining"] = int(remaining_raw)
            if reset_raw and reset_raw.isdigit():
                state["reset_epoch"] = int(reset_raw)
            if retry_raw:
                try:
                    retry_seconds = max(0, int(float(retry_raw)))
                except ValueError:
                    retry_seconds = None
                state["retry_after_seconds"] = retry_seconds
                if retry_seconds is not None:
                    state["blocked_until"] = time.time() + retry_seconds

    def block_rate_limit(self, operation: str, headers: Any) -> None:
        header_resource = self._header_value(headers, "X-RateLimit-Resource")
        resource = header_resource or self._resource(operation)
        with self._lock:
            state = self.rate_limits.setdefault(resource, {"remaining": None, "reset_epoch": None, "retry_after_seconds": None, "blocked_until": None})
            if not isinstance(state.get("blocked_until"), (int, float)):
                reset_epoch = state.get("reset_epoch")
                state["blocked_until"] = max(time.time() + 60, float(reset_epoch)) if isinstance(reset_epoch, (int, float)) else time.time() + 60

    @staticmethod
    def _resource(operation: str) -> str:
        if operation == "code-search":
            return "code_search"
        return "search" if "search" in operation else "core"

    def can_schedule(self, operation: str) -> bool:
        resource = self._resource(operation)
        state = self.rate_limits.get(resource) or self.rate_limits.get("core") or {}
        blocked_until = state.get("blocked_until")
        if isinstance(blocked_until, (int, float)) and blocked_until > time.time():
            return False
        remaining = state.get("remaining")
        return not isinstance(remaining, int) or remaining > self.minimum_remaining

    @staticmethod
    def _iso_epoch(value: int | float | None) -> str | None:
        if not isinstance(value, (int, float)):
            return None
        return datetime.fromtimestamp(value, timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def rate_limit_failure(self, operation: str, status: int | None = None, category: str = "primary") -> dict[str, Any]:
        resource = self._resource(operation)
        state = self.rate_limits.get(resource) or self.rate_limits.get("core") or {}
        return {
            "provider": "github", "operation": operation, "http_status": status,
            "category": "rate-limit", "rate_limit_category": category,
            "remaining": state.get("remaining"), "reset_at": self._iso_epoch(state.get("reset_epoch")),
            "retry_after_seconds": state.get("retry_after_seconds"), "cached_results_used": False,
        }

    def _failure(self, operation: str, exc: Exception, body: str = "") -> ProviderRequestError:
        status = exc.code if isinstance(exc, urllib.error.HTTPError) else None
        headers = exc.headers if isinstance(exc, urllib.error.HTTPError) else None
        resource = self._header_value(headers, "X-RateLimit-Resource") or self._resource(operation)
        self.observe_rate_limit(headers, resource)
        remaining = self._header_value(headers, "X-RateLimit-Remaining")
        retry_after = self._header_value(headers, "Retry-After")
        text = body.casefold()
        is_rate_limit = status == 429 or (status == 403 and (remaining == "0" or "rate limit" in text or retry_after is not None))
        if is_rate_limit:
            category = "secondary" if status == 429 or retry_after is not None or "secondary" in text else "primary"
            self.block_rate_limit(operation, headers)
            return ProviderRequestError(self.rate_limit_failure(operation, status, category))
        return ProviderRequestError({
            "provider": "github", "operation": operation, "http_status": status,
            "category": "provider-error", "rate_limit_category": None, "remaining": None,
            "reset_at": None, "retry_after_seconds": None, "cached_results_used": False,
        })

    @staticmethod
    def _parse_gh_response(output: str) -> tuple[dict[str, str], Any]:
        normalized = output.replace("\r\n", "\n")
        blocks = normalized.split("\n\n")
        body_index = next((index for index, block in enumerate(blocks) if block.lstrip().startswith(("{", "["))), len(blocks) - 1)
        header_text = "\n\n".join(blocks[:body_index])
        body = "\n\n".join(blocks[body_index:])
        headers: dict[str, str] = {}
        for line in header_text.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip()] = value.strip()
        return headers, json.loads(body)

    def _gh_request(self, path: str, operation: str) -> Any:
        endpoint = path.removeprefix("https://api.github.com/").lstrip("/")
        completed = subprocess.run(
            ["gh", "api", "--include", endpoint], stdin=subprocess.DEVNULL,
            capture_output=True, text=True, check=False,
        )
        with self._lock:
            self.network_requests += 1
        if completed.returncode != 0:
            header_text = completed.stdout.replace("\r\n", "\n").split("\n\n", 1)[0]
            response_headers = {}
            for line in header_text.splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    response_headers[key.strip()] = value.strip()
            combined_error = f"{completed.stdout[:2000]}\n{completed.stderr[:2000]}"
            status_match = re.search(r"HTTP\s+(?:\d(?:\.\d)?\s+)?(\d{3})", combined_error, re.I)
            status = int(status_match.group(1)) if status_match else None
            synthetic = urllib.error.HTTPError("https://api.github.com", status or 500, "request failed", response_headers, None)
            raise self._failure(operation, synthetic, combined_error)
        headers, payload = self._parse_gh_response(completed.stdout)
        self.observe_rate_limit(headers, self._header_value(headers, "X-RateLimit-Resource") or self._resource(operation))
        return payload

    def request(self, path: str, operation: str = "api-request") -> Any:
        if not self.can_schedule(operation):
            raise ProviderRequestError(self.rate_limit_failure(operation))
        if self.transport == "gh-cli":
            return self._gh_request(path, operation)
        url = path if path.startswith("https://") else f"https://api.github.com{path}"
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "agent-commons-external-intelligence"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(url, headers=headers)
        last_error: Exception | None = None
        for attempt in range(self.max_attempts):
            try:
                with self._lock:
                    self.network_requests += 1
                with urllib.request.urlopen(request, timeout=25) as response:
                    self.observe_rate_limit(response.headers, self._header_value(response.headers, "X-RateLimit-Resource") or self._resource(operation))
                    return json.load(response)
            except urllib.error.HTTPError as exc:
                body = ""
                try:
                    body = exc.read(4096).decode("utf-8", errors="replace")
                except Exception:
                    pass
                failure = self._failure(operation, exc, body)
                if failure.failure["category"] == "rate-limit" or exc.code < 500:
                    raise failure from exc
                last_error = exc
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = exc
            if attempt + 1 < self.max_attempts:
                time.sleep(self.backoff_seconds * (2 ** attempt))
        raise self._failure(operation, last_error or RuntimeError("request failed")) from last_error

    def inspect_rate_limit(self) -> None:
        value = self.request("/rate_limit", operation="rate-limit-inspection")
        resources = value.get("resources", {}) if isinstance(value, dict) else {}
        for resource in ("core", "search", "code_search"):
            details = resources.get(resource)
            if not isinstance(details, dict):
                continue
            headers = {
                "X-RateLimit-Resource": resource,
                "X-RateLimit-Remaining": str(details.get("remaining", "")),
                "X-RateLimit-Reset": str(details.get("reset", "")),
            }
            self.observe_rate_limit(headers)

    def repository(self, slug: str) -> dict[str, Any]:
        value = self.request(f"/repos/{slug}", operation="repository-metadata")
        return value if isinstance(value, dict) else {}

    def revision(self, slug: str, branch: str) -> tuple[str, str | None]:
        value = self.request(f"/repos/{slug}/commits/{urllib.parse.quote(branch, safe='')}", operation="repository-revision")
        date = value.get("commit", {}).get("committer", {}).get("date") if isinstance(value, dict) else None
        return str(value.get("sha", "")), date

    def tree(self, slug: str, revision: str) -> list[str]:
        value = self.request(f"/repos/{slug}/git/trees/{revision}?recursive=1", operation="repository-tree")
        return [item["path"] for item in value.get("tree", []) if isinstance(item, dict) and item.get("type") == "blob" and isinstance(item.get("path"), str)]

    def search_repositories(self, query: str, limit: int) -> list[dict[str, Any]]:
        encoded = urllib.parse.urlencode({"q": query, "sort": "updated", "order": "desc", "per_page": min(limit, 30)})
        value = self.request(f"/search/repositories?{encoded}", operation="repository-search")
        return [item for item in value.get("items", []) if isinstance(item, dict)]

    def search_code(self, query: str, limit: int) -> list[dict[str, Any]]:
        if not self.authenticated:
            return []
        encoded = urllib.parse.urlencode({"q": query, "per_page": min(limit, 30)})
        value = self.request(f"/search/code?{encoded}", operation="code-search")
        return [item for item in value.get("items", []) if isinstance(item, dict)]


def terms(value: str) -> list[str]:
    return [token for token in TOKEN_RE.findall(value.lower()) if token not in STOPWORDS and len(token) > 1]


def capability_root(path: str) -> str:
    parts = path.split("/")
    for marker in ("plugins", "skills"):
        if marker in parts:
            index = parts.index(marker)
            if index + 1 < len(parts):
                return "/".join(parts[:index + 2])
    if any(marker in parts for marker in ("commands", "agents", "hooks", "workflows")):
        return path
    return str(Path(path).parent) if "/" in path else path


def score_path(path: str, topic_terms: list[str]) -> int:
    lower = path.lower()
    topic_score = sum(6 for token in topic_terms if token in lower)
    if not topic_score:
        return 0
    score = topic_score
    score += sum(2 for marker in CAPABILITY_MARKERS if marker in lower)
    if lower.endswith(("skill.md", ".md", ".yaml", ".yml", ".json")):
        score += 1
    return score


def detect_security(paths: list[str]) -> str:
    lowered = [path.lower() for path in paths]
    if any("mcp" in path for path in lowered):
        return "MCP/REMOTE TOOLING"
    if any("hook" in path for path in lowered) and any("plugin" in path or ".claude-plugin" in path for path in lowered):
        return "PLUGIN WITH HOOKS"
    if any(path.endswith((".py", ".js", ".ts", ".sh", ".ps1", ".rb", ".go")) for path in lowered):
        return "INSTRUCTIONS + SCRIPTS"
    if any(path.endswith((".md", ".txt", ".yaml", ".yml", ".json")) for path in lowered):
        return "INSTRUCTIONS ONLY"
    return "UNKNOWN"


def detect_runtime(source: dict[str, Any], paths: list[str]) -> str:
    text = " ".join([source.get("id", ""), source.get("description", ""), *paths]).lower()
    if "claude" in text or ".claude-plugin" in text:
        return "claude-code"
    if "codex" in text or ".agents/skills" in text:
        return "codex"
    if "cline" in text:
        return "cline"
    if "opencode" in text:
        return "opencode"
    return "runtime-neutral-or-other"


def detect_type(paths: list[str]) -> str:
    lowered = [path.lower() for path in paths]
    kinds = set()
    if any("/.claude-plugin/" in f"/{path}" or path.endswith("plugin.json") for path in lowered):
        kinds.add("plugin")
    for marker, name in (("/skills/", "skill/workflow"), ("/agents/", "agent"), ("/commands/", "command"), ("/hooks/", "hook"), ("mcp", "MCP"), ("/workflows/", "workflow")):
        if any(marker in f"/{path}" for path in lowered):
            kinds.add(name)
    if any(path.endswith((".py", ".js", ".ts", ".sh")) for path in lowered):
        kinds.add("script")
    if len(kinds) > 1:
        return "composite-package"
    return next(iter(kinds), "unknown")


def license_metadata(spdx: str | None, scope: str) -> dict[str, str]:
    normalized = spdx if spdx and spdx not in {"NOASSERTION", "OTHER"} else "UNKNOWN"
    if normalized == "UNKNOWN":
        return {"status": "UNKNOWN", "spdx": "LICENSE UNKNOWN", "scope": scope, "copy_policy": "PROHIBITED_UNTIL_LICENSE_RESOLVED"}
    return {"status": "DETECTED", "spdx": normalized, "scope": scope, "copy_policy": "REVIEW_LICENSE_TERMS_BEFORE_COPYING"}


@lru_cache(maxsize=1)
def commons_search_documents() -> tuple[tuple[str, frozenset[str]], ...]:
    try:
        catalog = load_json(CATALOG_PATH)
    except ExternalCapabilityError:
        return ()
    documents: list[tuple[str, frozenset[str]]] = []
    for identifier, entry in catalog.get("skills", {}).items():
        description = str(entry.get("description", "")) if isinstance(entry, dict) else ""
        if not description and isinstance(entry, dict):
            path = ROOT / entry.get("path", "")
            if path.is_file():
                try:
                    text = path.read_text(encoding="utf-8")
                    description = text.split("description:", 1)[1].splitlines()[0] if "description:" in text else ""
                except OSError:
                    pass
        documents.append((identifier, frozenset(terms(f"{identifier} {description}"))))
    return tuple(documents)


def commons_overlaps(name: str, purpose: str) -> list[str]:
    query = set(terms(f"{name} {purpose}"))
    scored: list[tuple[int, str]] = []
    for identifier, document_terms in commons_search_documents():
        overlap = len(query & document_terms)
        if overlap:
            scored.append((overlap, identifier))
    return [identifier for _, identifier in sorted(scored, key=lambda item: (-item[0], item[1]))[:5]]


def snapshot_repository(snapshot: dict[str, Any], slug: str) -> dict[str, Any] | None:
    value = snapshot.get("repositories", {}).get(slug)
    return value if isinstance(value, dict) else None


def repository_cache_path(cache_dir: Path | None, slug: str) -> Path | None:
    if cache_dir is None:
        return None
    return cache_dir / "repositories" / f"{hashlib.sha256(slug.encode()).hexdigest()}.json"


def cached_repository_evidence(cache_dir: Path | None, slug: str, ttl_seconds: int) -> dict[str, Any] | None:
    path = repository_cache_path(cache_dir, slug)
    if path is None or not path.is_file() or ttl_seconds <= 0:
        return None
    age = max(0.0, time.time() - path.stat().st_mtime)
    if age > ttl_seconds:
        return None
    value = load_json(path)
    if value.get("slug") != slug or not isinstance(value.get("evidence"), dict):
        return None
    evidence = dict(value["evidence"])
    evidence["_cache_hit"] = True
    return evidence


def store_repository_evidence(cache_dir: Path | None, slug: str, evidence: dict[str, Any]) -> None:
    path = repository_cache_path(cache_dir, slug)
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(path, {"schema_version": 1, "slug": slug, "cached_at": utc_now(), "evidence": evidence})


def repository_evidence(
    slug: str,
    client: GitHubClient,
    snapshot: dict[str, Any] | None,
    cache_dir: Path | None = None,
    cache_ttl_seconds: int = 86400,
) -> dict[str, Any]:
    if snapshot is not None:
        value = snapshot_repository(snapshot, slug)
        if value is None:
            raise ExternalCapabilityError(f"snapshot lacks repository {slug}")
        return value
    cached = cached_repository_evidence(cache_dir, slug, cache_ttl_seconds)
    if cached is not None:
        return cached
    metadata = client.repository(slug)
    branch = metadata.get("default_branch", "main")
    revision, commit_date = client.revision(slug, branch)
    evidence = {
        "full_name": metadata.get("full_name", slug),
        "html_url": metadata.get("html_url", f"https://github.com/{slug}"),
        "description": metadata.get("description") or "",
        "default_branch": branch,
        "license": (metadata.get("license") or {}).get("spdx_id"),
        "revision": revision,
        "updated_at": metadata.get("updated_at"),
        "pushed_at": metadata.get("pushed_at"),
        "last_commit_at": commit_date,
        "stars": metadata.get("stargazers_count", 0),
        "topics": metadata.get("topics", []),
        "tree": client.tree(slug, revision),
        "files": {},
    }
    store_repository_evidence(cache_dir, slug, evidence)
    return evidence


def purpose_from_files(slug: str, root: str, evidence: dict[str, Any], client: GitHubClient, snapshot: dict[str, Any] | None) -> str:
    files = evidence.get("files", {}) if isinstance(evidence.get("files"), dict) else {}
    candidates = [f"{root}/.claude-plugin/plugin.json", f"{root}/plugin.json", f"{root}/README.md", "README.md"]
    for path in candidates:
        content = str(files.get(path, ""))
        if not content:
            continue
        if path.endswith(".json"):
            try:
                description = json.loads(content).get("description")
                if isinstance(description, str) and description.strip():
                    return description.strip()
            except json.JSONDecodeError:
                pass
        for line in content.splitlines():
            cleaned = line.strip().lstrip("#").strip()
            if len(cleaned) >= 30 and not cleaned.startswith(("[", "<", "!")):
                return cleaned[:500]
    return str(evidence.get("description") or f"Potential reusable capability under {root}.")


def stable_candidate_id(source_id: str, root: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", f"{source_id}-{root}".lower()).strip("-")
    if len(slug) > 72:
        slug = slug[:63].rstrip("-") + "-" + hashlib.sha1(root.encode()).hexdigest()[:8]
    return f"ext-{slug}"


def search_configured_source(
    source: dict[str, Any], topics: list[str] | str, client: GitHubClient,
    snapshot: dict[str, Any] | None, limit: int, cache_dir: Path | None = None,
    repository_cache_ttl_seconds: int = 86400,
) -> list[dict[str, Any]]:
    topic_list = [topics] if isinstance(topics, str) else topics
    slug = normalize_github(source["repository"])
    evidence = repository_evidence(slug, client, snapshot, cache_dir, repository_cache_ttl_seconds)
    tree = [str(path) for path in evidence.get("tree", [])]
    query_terms = list(dict.fromkeys(
        token
        for topic in topic_list
        for token in terms(topic)
    ))
    roots: dict[str, int] = {}
    for path in tree:
        score = score_path(path, query_terms)
        if score or any(marker in f"/{path.lower()}" for marker in CAPABILITY_MARKERS):
            root = capability_root(path)
            roots[root] = max(roots.get(root, 0), score or 1)
    metadata_score = sum(4 for token in query_terms if token in str(evidence.get("description", "")).lower())
    if not roots and metadata_score:
        roots[slug] = metadata_score
    trust_bonus = 20 if source["trust"] == "OFFICIAL" else 12
    results: list[dict[str, Any]] = []
    for root, path_score in sorted(roots.items(), key=lambda item: (-item[1], item[0]))[:limit]:
        related = [path for path in tree if path == root or path.startswith(root.rstrip("/") + "/")]
        purpose = purpose_from_files(slug, root, evidence, client, snapshot)
        matched_gaps = matched_capability_gaps(f"{root} {purpose} {evidence.get('description', '')}", topic_list)
        if not matched_gaps:
            continue
        relevance_score = path_score + metadata_score + trust_bonus
        root_license = f"{root}/LICENSE" if f"{root}/LICENSE" in tree else "repository metadata"
        candidate = {
            "id": stable_candidate_id(source["id"], root),
            "name": Path(root).name if root != slug else slug.split("/")[-1],
            "source_id": source["id"],
            "repository": slug,
            "source_url": evidence.get("html_url", f"https://github.com/{slug}"),
            "path": root if root != slug else "",
            "revision": evidence.get("revision", "UNKNOWN"),
            "source_trust": source["trust"],
            "detected_runtime": detect_runtime(source, related),
            "capability_type": detect_type(related),
            "purpose": purpose,
            "relevance_score": relevance_score,
            "relevance": sorted(set(query_terms)),
            "matched_gaps": matched_gaps,
            "license": license_metadata(evidence.get("license"), root_license),
            "upstream": {"default_branch": evidence.get("default_branch"), "last_commit_at": evidence.get("last_commit_at") or evidence.get("pushed_at")},
            "why_useful": f"Matched configured {source['trust'].lower()} source for: {' | '.join(matched_gaps)}",
            "commons_overlap": commons_overlaps(Path(root).name, purpose),
            "review_recommendation": "REVIEW" if relevance_score >= 22 else "CONSIDER",
            "security_class": detect_security(related),
            "status": "DISCOVERED",
            "review_status": "NOT_REVIEWED",
            "discovered_at": utc_now(),
            "last_checked": utc_now(),
            "repository_metadata_cache_hit": bool(evidence.get("_cache_hit")),
        }
        results.append(candidate)
    return results


def community_results(
    topics: list[str] | str,
    client: GitHubClient,
    snapshot: dict[str, Any] | None,
    limit: int,
    retain_limit: int | None = None,
    failures: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    topic_list = [topics] if isinstance(topics, str) else topics
    if snapshot is not None:
        items = snapshot.get("community_search", [])
    else:
        query = combined_community_query(topic_list)
        if not query:
            return []
        items = client.search_repositories(query, limit)
    results: list[dict[str, Any]] = []
    query_terms = list(dict.fromkeys(token for topic in topic_list for token in terms(topic)))
    for item in items[:limit]:
        if not isinstance(item, dict):
            continue
        slug = item.get("full_name") or item.get("repository")
        if not isinstance(slug, str) or "/" not in slug:
            continue
        description = str(item.get("description") or "")
        topics = [str(value) for value in item.get("topics", [])]
        haystack = f"{slug} {description} {' '.join(topics)}".lower()
        matched_gaps = matched_capability_gaps(haystack, topic_list)
        if not matched_gaps:
            continue
        matched_specific = set().union(*(_specific_topic_terms(gap) for gap in matched_gaps))
        term_score = sum(7 for token in matched_specific if token in normalize_topic(haystack).replace("pl/i", "pli"))
        stars = int(item.get("stargazers_count", item.get("stars", 0)) or 0)
        update_value = str(item.get("pushed_at") or item.get("updated_at") or "")
        match = re.match(r"(\d{4})-", update_value)
        recent = bool(match and int(match.group(1)) >= datetime.now(timezone.utc).year - 2)
        quality_score = min(10, stars // 50) + (3 if recent else 0)
        score = term_score + quality_score
        recommendation = "REVIEW" if score >= 13 and matched_specific else "REJECT_LOW_SIGNAL"
        if recommendation == "REJECT_LOW_SIGNAL":
            continue
        spdx = item.get("license")
        if isinstance(spdx, dict):
            spdx = spdx.get("spdx_id")
        revision = item.get("revision", "UNPINNED")
        last_commit_at = item.get("pushed_at") or item.get("updated_at")
        matched_path = str(item.get("matched_path") or "")
        results.append({
            "id": stable_candidate_id("github-community-discovery", slug),
            "name": slug.split("/")[-1],
            "source_id": "github-community-discovery",
            "repository": slug,
            "source_url": item.get("html_url", f"https://github.com/{slug}"),
            "path": matched_path,
            "revision": revision,
            "source_trust": "COMMUNITY",
            "detected_runtime": "runtime-neutral-or-other",
            "capability_type": detect_type([matched_path]) if matched_path else "repository-candidate",
            "purpose": description or "Community repository discovered by GitHub search.",
            "relevance_score": score,
            "relevance": sorted(set(query_terms)),
            "matched_gaps": matched_gaps,
            "license": license_metadata(spdx, "repository metadata"),
            "upstream": {"default_branch": item.get("default_branch"), "last_commit_at": last_commit_at},
            "why_useful": f"Community discovery match for: {' | '.join(matched_gaps)}",
            "commons_overlap": commons_overlaps(slug, description),
            "review_recommendation": recommendation,
            "security_class": "UNKNOWN",
            "status": "DISCOVERED",
            "review_status": "NOT_REVIEWED",
            "discovered_at": utc_now(),
            "last_checked": utc_now(),
            "_default_branch": str(item.get("default_branch") or "main"),
        })
    retained = sorted(results, key=lambda item: (-item["relevance_score"], item["repository"]))[:retain_limit or limit]
    for candidate in retained:
        if snapshot is None:
            try:
                revision, commit_date = client.revision(candidate["repository"], candidate["_default_branch"])
                candidate["revision"] = revision
                candidate["upstream"]["last_commit_at"] = commit_date or candidate["upstream"]["last_commit_at"]
            except ProviderRequestError as exc:
                if failures is None:
                    raise
                failure = dict(exc.failure)
                failure["source_id"] = "github-community-discovery"
                failure["cached_results_used"] = False
                failures.append(failure)
                break
            except ExternalCapabilityError:
                if failures is not None:
                    failures.append(_structured_failure(
                        "github", "repository-revision", "source-failure",
                        source_id="github-community-discovery", cached_results_used=False,
                    ))
                break
    for candidate in retained:
        candidate.pop("_default_branch", None)
    return retained


def project_query(root: Path) -> dict[str, Any]:
    if not root.is_dir():
        raise ExternalCapabilityError(f"project root is not a directory: {root}")
    technologies: set[str] = set()
    paths_seen = 0
    inventory_path = root / "analysis" / "source-inventory.json"
    inventory_fingerprint: str | None = None
    inventory_reused = False
    if inventory_path.is_file():
        inventory = load_json(inventory_path)
        inventory_fingerprint = str(inventory.get("fingerprint") or "") or None
        for artifact in inventory.get("artifacts", []):
            if not isinstance(artifact, dict):
                continue
            paths_seen += 1
            language = str(artifact.get("language") or "")
            if language and language.casefold() != "unknown":
                technologies.add(language)
        inventory_reused = True
    else:
        for path in root.rglob("*"):
            if any(part in {".git", "node_modules", "vendor", "dist", "build", "target", ".venv", "output"} for part in path.parts):
                continue
            if path.is_file():
                paths_seen += 1
                technology = PROJECT_TECHNOLOGIES.get(path.suffix.lower())
                if technology:
                    technologies.add(technology)
                if paths_seen >= 800:
                    break
    scopes: set[str] = set()
    selected_capabilities: set[str] = set()
    manifest = root / ".agent-commons.yaml"
    manifest_text = manifest.read_text(encoding="utf-8", errors="replace") if manifest.is_file() else ""
    source_match = re.search(r"^\s*source_technology:\s*(?:\"([^\"]+)\"|([^\s#]+))", manifest_text, re.M)
    target_match = re.search(r"^\s*target_technology:\s*(?:\"([^\"]+)\"|([^\s#]+))", manifest_text, re.M)
    source_technology = next((value for value in source_match.groups() if value and value != "null"), "") if source_match else ""
    target_technology = next((value for value in target_match.groups() if value and value != "null"), "") if target_match else ""
    capability_state = manifest_text.partition("capability_state:")[2].partition("external_capabilities:")[0]
    capability_gaps = re.findall(r"^\s*- id:\s*\"([^\"]+)\"", capability_state, re.M)
    for scope in ("legacy-migration", "development", "presentation"):
        if re.search(rf"(?<![a-z0-9-]){re.escape(scope)}(?![a-z0-9-])", manifest_text):
            scopes.add(scope)
    try:
        catalog = load_json(CATALOG_PATH)
        for identifier in catalog.get("skills", {}):
            if re.search(rf"(?<![a-z0-9-]){re.escape(identifier)}(?![a-z0-9-])", manifest_text):
                selected_capabilities.add(identifier)
    except ExternalCapabilityError:
        pass
    concepts: list[str] = []
    for technology in sorted(technologies):
        if technology in {"COBOL", "PL/I"}:
            concepts.extend([
                f"{technology} semantic analysis",
                f"{technology} business rule dependency extraction",
            ])
        elif technology != "Java":
            concepts.append(f"{technology} agent workflow")
    if source_technology:
        concepts.extend([
            f"{source_technology} code semantic analysis agent skill",
            f"{source_technology} business rule dependency extraction workflow",
        ])
    if source_technology and target_technology:
        concepts.append(f"{source_technology} to {target_technology} migration mapping workflow")
    elif target_technology:
        concepts.append(f"{target_technology} target architecture agent workflow")
    if "legacy-migration" in scopes or technologies & {"COBOL", "PL/I"}:
        concepts.extend(["legacy modernization", "business rule extraction", "characterization testing", "dependency graph"])
    if "development" in scopes:
        concepts.extend(["agent software delivery", "acceptance testing"])
    if "presentation" in scopes:
        concepts.extend(["standalone HTML visual QA", "evidence aware presentation"])
    for gap in capability_gaps[:3]:
        concepts.append(gap.replace("-", " "))
    if "audit-delivery-traceability" in selected_capabilities:
        concepts.append("delivery traceability evaluation")
    unique: list[str] = []
    for concept in dict.fromkeys(concepts):
        try:
            validate_topic_privacy([concept])
        except ExternalCapabilityError:
            continue
        unique.append(concept)
        if len(unique) >= 8:
            break
    return {
        "project_root": ".",
        "terms": unique,
        "signals": {
            "technologies": sorted(technologies),
            "source_technology": source_technology or None,
            "target_technology": target_technology or None,
            "scopes": sorted(scopes),
            "capability_ids": sorted(selected_capabilities),
            "capability_gaps": capability_gaps,
            "source_inventory_fingerprint": inventory_fingerprint,
            "source_inventory_reused": inventory_reused,
        },
        "privacy": "Queries use allowlisted technologies, canonical scopes, and canonical capability IDs only; project names, goals, client details, paths, and source text are excluded.",
    }


def effective_source_policy(args: argparse.Namespace) -> tuple[set[str], bool]:
    selected_trust = set(getattr(args, "trust", None) or [])
    include_community = bool(getattr(args, "include_community", False))
    source_scope = getattr(args, "source_scope", "configured")
    if source_scope == "official":
        return {"OFFICIAL"}, False
    if source_scope == "official-curated":
        return {"OFFICIAL", "CURATED"}, False
    if source_scope == "all":
        return selected_trust, True
    return selected_trust, include_community


def source_revision_fingerprint(
    args: argparse.Namespace,
    registry: dict[str, Any],
    snapshot: dict[str, Any] | None,
) -> str:
    selected_ids = set(getattr(args, "source", None) or [])
    selected_trust, _ = effective_source_policy(args)
    revisions: dict[str, str] = {}
    for source in registry.get("sources", []):
        if not isinstance(source, dict) or source.get("type") != "github-repository" or not source.get("enabled"):
            continue
        if selected_ids and source.get("id") not in selected_ids:
            continue
        if selected_trust and source.get("trust") not in selected_trust:
            continue
        slug = normalize_github(str(source.get("repository", "")))
        if snapshot is not None:
            evidence = snapshot_repository(snapshot, slug)
        else:
            evidence = cached_repository_evidence(
                Path(args.cache_dir) if getattr(args, "cache_dir", None) else None,
                slug,
                int(getattr(args, "repository_cache_ttl_seconds", 86400)),
            )
        revisions[slug] = str((evidence or {}).get("revision") or "UNRESOLVED")
    encoded = json.dumps(revisions, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def search_cache_key(
    args: argparse.Namespace,
    registry: dict[str, Any],
    topics: list[str],
    source_revision: str | None = None,
) -> str:
    snapshot = getattr(args, "snapshot", None)
    snapshot_hash = hashlib.sha256(Path(snapshot).read_bytes()).hexdigest() if snapshot else None
    effective_trust, effective_community = effective_source_policy(args)
    material = {
        "registry": registry_fingerprint(registry),
        "topics": sorted(normalize_topics(topics)),
        "sources": sorted(getattr(args, "source", None) or []),
        "trust": sorted(effective_trust),
        "source_scope": getattr(args, "source_scope", None),
        "include_community": effective_community,
        "per_source_limit": int(getattr(args, "per_source_limit", 3)),
        "community_limit": int(getattr(args, "community_limit", 8)),
        "limit": int(getattr(args, "limit", 20)),
        "snapshot": snapshot_hash,
        "source_revision": source_revision or source_revision_fingerprint(args, registry, load_json(snapshot) if snapshot else None),
    }
    encoded = json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def cached_search(
    args: argparse.Namespace,
    registry: dict[str, Any],
    topics: list[str],
    source_revision: str,
) -> tuple[dict[str, Any] | None, Path | None]:
    cache_dir = getattr(args, "cache_dir", None)
    ttl = max(0, int(getattr(args, "cache_ttl_seconds", 0) or 0))
    if not cache_dir or ttl == 0:
        return None, None
    path = Path(cache_dir) / f"{search_cache_key(args, registry, topics, source_revision)}.json"
    if not path.is_file():
        return None, path
    age = max(0.0, time.time() - path.stat().st_mtime)
    if age > ttl:
        return None, path
    result = load_json(path)
    if result.get("status") == "failed":
        return None, path
    execution = result.setdefault("execution", {})
    previous_requests = int(execution.get("network_requests", 0) or 0)
    execution["cached_entry_network_requests"] = previous_requests
    execution["network_requests"] = 0
    result["cache"] = {
        "hit": True, "age_seconds": round(age, 3), "ttl_seconds": ttl,
        "entry_status": result.get("status"),
        "negative_entry": not bool(result.get("candidates")),
        "partial_entry": str(result.get("status", "")).startswith("partial-"),
    }
    for failure in result.get("failures", []):
        if isinstance(failure, dict):
            failure["cached_results_used"] = True
    return result, path


def _structured_failure(
    provider: str,
    operation: str,
    category: str,
    *,
    source_id: str | None = None,
    cached_results_used: bool = False,
) -> dict[str, Any]:
    return {
        "provider": provider, "operation": operation, "http_status": None,
        "category": category, "rate_limit_category": None, "remaining": None,
        "reset_at": None, "retry_after_seconds": None,
        "cached_results_used": cached_results_used, "source_id": source_id,
    }


def _cached_candidate_results_used(candidates: list[dict[str, Any]]) -> bool:
    return any(candidate.get("repository_metadata_cache_hit") is True for candidate in candidates)


def discovery_status(failures: list[dict[str, Any]], candidates: list[dict[str, Any]]) -> str:
    if not failures:
        return "completed"
    if any(failure.get("category") == "rate-limit" for failure in failures):
        return "partial-rate-limited" if candidates else "failed"
    return "partial-source-failure" if candidates else "failed"


def discovery_request_key(
    topics: list[str],
    source_scope: str,
    sources_path: Path = SOURCES_PATH,
    snapshot: Path | None = None,
) -> str:
    registry = load_json(sources_path)
    normalized = normalize_topics(topics)
    material = {
        "topics": sorted(normalized), "source_scope": source_scope,
        "registry": registry_fingerprint(registry),
        "snapshot": hashlib.sha256(snapshot.read_bytes()).hexdigest() if snapshot else None,
    }
    return hashlib.sha256(json.dumps(material, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _coverage_notes(topics: list[str], candidates: list[dict[str, Any]]) -> list[str]:
    notes: list[str] = []
    for label, patterns in (("COBOL", {"cobol"}), ("PL/I", {"pli"})):
        requested = any(patterns & _specific_topic_terms(topic) for topic in topics)
        found = any(
            patterns & set(terms(normalize_topic(f"{candidate.get('repository', '')} {candidate.get('purpose', '')}").replace("pl/i", "pli")))
            for candidate in candidates
        )
        if requested and not found:
            notes.append(f"No {label}-specific capability was found.")
    return notes


def search(args: argparse.Namespace, client: GitHubClient | None = None) -> dict[str, Any]:
    registry = load_json(args.sources)
    errors = validate_registry(registry)
    if errors:
        raise ExternalCapabilityError("; ".join(errors))
    raw_topics = args.topic if isinstance(args.topic, list) else [args.topic]
    topics = [str(value).strip() for value in raw_topics if value and str(value).strip()]
    project = project_query(args.project_root) if args.project_root else None
    if not topics and project:
        topics = [str(value) for value in project["terms"][:8]]
    if not topics:
        raise ExternalCapabilityError("search requires --topic or --project-root with discoverable generic terms")
    validate_topic_privacy(topics)
    topics = normalize_topics(topics)
    if not topics:
        raise ExternalCapabilityError("search topics contain only generic terms; provide a concrete capability gap")
    snapshot = load_json(args.snapshot) if getattr(args, "snapshot", None) else None
    revision_fingerprint = source_revision_fingerprint(args, registry, snapshot)
    cached, cache_path = cached_search(args, registry, topics, revision_fingerprint)
    if cached is not None:
        return cached
    topic = " | ".join(topics)
    github_config = registry.get("github", {}) if isinstance(registry.get("github"), dict) else {}
    client = client or GitHubClient(minimum_remaining=int(github_config.get("minimum_remaining", 5)))
    selected_ids = set(args.source or [])
    selected_trust, include_community = effective_source_policy(args)
    candidates: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    rate_limit_checked = snapshot is not None
    if snapshot is None:
        try:
            client.inspect_rate_limit()
            rate_limit_checked = True
        except ProviderRequestError as exc:
            failures.append(dict(exc.failure))
    sources = [source for source in registry["sources"] if source.get("enabled")]
    configured = [
        source for source in sources
        if (not selected_ids or source["id"] in selected_ids)
        and (not selected_trust or source["trust"] in selected_trust)
        and source["type"] == "github-repository"
        and source["trust"] in {"OFFICIAL", "CURATED"}
    ]
    jobs = configured
    workers = 1
    target_candidates = min(int(getattr(args, "limit", 20)), int(github_config.get("stop_after_candidates", 7)))
    source_tiers: dict[str, dict[str, object]] = {}
    community_attempted = False
    repository_cache_ttl = int(getattr(args, "repository_cache_ttl_seconds", github_config.get("repository_cache_ttl_seconds", 86400)))
    for trust in ("OFFICIAL", "CURATED"):
        tier_sources = [source for source in jobs if source["trust"] == trust]
        if not tier_sources:
            continue
        tier = source_tiers.setdefault(trust, {"configured": len(tier_sources), "completed": 0, "failed": 0, "status": "pending"})
        for source in tier_sources:
            if len(candidates) >= target_candidates:
                tier["status"] = "stopped-enough-candidates"
                break
            try:
                candidates.extend(search_configured_source(
                    source, topics, client, snapshot, args.per_source_limit,
                    Path(args.cache_dir) if getattr(args, "cache_dir", None) else None,
                    repository_cache_ttl,
                ))
                tier["completed"] = int(tier["completed"]) + 1
            except ProviderRequestError as exc:
                failure = dict(exc.failure)
                failure["source_id"] = source["id"]
                failure["cached_results_used"] = _cached_candidate_results_used(candidates)
                failures.append(failure)
                tier["failed"] = int(tier["failed"]) + 1
            except ExternalCapabilityError:
                failures.append(_structured_failure("github", "configured-repository", "source-failure", source_id=source["id"], cached_results_used=_cached_candidate_results_used(candidates)))
                tier["failed"] = int(tier["failed"]) + 1
        if tier["status"] == "pending":
            tier["status"] = "completed" if tier["failed"] == 0 else "partial"
    if include_community and len(candidates) < target_candidates and (not selected_trust or "COMMUNITY" in selected_trust):
        community_attempted = True
        community_tier = source_tiers.setdefault("COMMUNITY", {"configured": 1, "completed": 0, "failed": 0, "status": "pending"})
        if not registry["discovery"].get("github_search"):
            failures.append(_structured_failure("github", "repository-search", "disabled-source", source_id="github-community-discovery", cached_results_used=_cached_candidate_results_used(candidates)))
            community_tier.update({"failed": 1, "status": "failed"})
        elif snapshot is None and not client.can_schedule("repository-search"):
            failure = client.rate_limit_failure("repository-search")
            failure["source_id"] = "github-community-discovery"
            failure["cached_results_used"] = _cached_candidate_results_used(candidates)
            failures.append(failure)
            community_tier.update({"failed": 1, "status": "rate-limited"})
        else:
            try:
                failure_count = len(failures)
                candidates.extend(community_results(
                    topics,
                    client,
                    snapshot,
                    args.community_limit,
                    max(0, target_candidates - len(candidates)),
                    failures,
                ))
                new_failures = failures[failure_count:]
                if new_failures:
                    rate_limited = any(failure.get("category") == "rate-limit" for failure in new_failures)
                    community_tier.update({"failed": 1, "status": "rate-limited" if rate_limited else "partial"})
                else:
                    community_tier.update({"completed": 1, "status": "completed"})
            except ProviderRequestError as exc:
                failure = dict(exc.failure)
                failure["source_id"] = "github-community-discovery"
                failure["cached_results_used"] = _cached_candidate_results_used(candidates)
                failures.append(failure)
                community_tier.update({"failed": 1, "status": "rate-limited" if failure.get("category") == "rate-limit" else "failed"})
            except ExternalCapabilityError:
                failures.append(_structured_failure("github", "repository-search", "source-failure", source_id="github-community-discovery", cached_results_used=_cached_candidate_results_used(candidates)))
                community_tier.update({"failed": 1, "status": "failed"})
    deduplicated: dict[str, dict[str, Any]] = {}
    for candidate in candidates:
        current = deduplicated.get(candidate["id"])
        if current is None or candidate["relevance_score"] > current["relevance_score"]:
            deduplicated[candidate["id"]] = candidate
    candidates = [candidate for candidate in deduplicated.values() if candidate.get("matched_gaps") and candidate.get("review_recommendation") != "REJECT_LOW_SIGNAL"]
    trust_rank = {"OFFICIAL": 0, "CURATED": 1, "COMMUNITY": 2, "UNTRUSTED": 3}
    candidates.sort(key=lambda item: (trust_rank[item["source_trust"]], -item["relevance_score"], item["repository"], item["path"]))
    result = {
        "schema_version": 2,
        "query": topic,
        "queries": topics,
        "project_query": project,
        "priority_order": ["OFFICIAL", "CURATED", "COMMUNITY", "UNTRUSTED"],
        "general_web_discovery": "ENABLED" if registry["discovery"].get("general_web_search") else "DISABLED",
        "safety": {"installed": False, "executed_external_code": False, "mutated_commons": False},
        "candidates": candidates[:target_candidates],
        "candidate_count": len(candidates[:target_candidates]),
        "failures": failures,
        "completed_source_tiers": [trust for trust in ("OFFICIAL", "CURATED", "COMMUNITY", "UNTRUSTED") if source_tiers.get(trust, {}).get("status") in {"completed", "stopped-enough-candidates"}],
        "source_tiers": source_tiers,
        "coverage_notes": _coverage_notes(topics, candidates[:target_candidates]),
        "offline_snapshot": snapshot is not None,
        "provider_access": client.access_summary(),
        "execution": {
            "configured_source_branches": len(jobs),
            "configured_source_fetches": len(jobs),
            "topics_scored_per_fetch": len(topics),
            "max_workers": workers,
            "catalog_loads": 1,
            "parallel": False,
            "community_query_count": 1 if community_attempted and snapshot is None else 0,
            "legacy_community_query_estimate": len(topics) * (5 if client.authenticated else 3) if community_attempted and snapshot is None else 0,
            "network_requests": client.network_requests,
            "rate_limit_checked": rate_limit_checked,
            "stopped_after_enough_candidates": len(candidates) >= target_candidates,
        },
        "cache": {
            "hit": False,
            "age_seconds": 0,
            "ttl_seconds": max(0, int(getattr(args, "cache_ttl_seconds", 0) or 0)),
            "entry_status": None, "negative_entry": False, "partial_entry": False,
        },
    }
    result["status"] = discovery_status(failures, result["candidates"])
    if getattr(args, "cache_dir", None) and result["status"] != "failed":
        final_revision = source_revision_fingerprint(args, registry, snapshot)
        cache_path = Path(args.cache_dir) / f"{search_cache_key(args, registry, topics, final_revision)}.json"
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        write_json(cache_path, result)
    return result


def index_upsert(args: argparse.Namespace) -> None:
    registry = load_json(args.sources)
    index = load_json(args.index)
    results = load_json(args.results)
    incoming = results.get("candidates", [])
    if not isinstance(incoming, list):
        raise ExternalCapabilityError("search results candidates must be a list")
    merged = {candidate["id"]: candidate for candidate in index.get("candidates", []) if isinstance(candidate, dict) and "id" in candidate}
    for candidate in incoming:
        if isinstance(candidate, dict) and candidate.get("id"):
            merged[candidate["id"]] = candidate
    index["candidates"] = sorted(merged.values(), key=lambda candidate: candidate["id"])
    index["source_registry_fingerprint"] = registry_fingerprint(registry)
    index["updated_at"] = utc_now()
    write_json(args.index, index)


def current_revision(slug: str, client: GitHubClient, snapshot: dict[str, Any] | None) -> str:
    evidence = repository_evidence(slug, client, snapshot)
    return str(evidence.get("revision", "UNKNOWN"))


def check_stale(args: argparse.Namespace) -> dict[str, Any]:
    index = load_json(args.index)
    snapshot = load_json(args.snapshot) if args.snapshot else None
    client = GitHubClient()
    checked_at = utc_now()
    results: list[dict[str, Any]] = []
    failures: list[str] = []
    changed = False
    for candidate in index.get("candidates", []):
        if not isinstance(candidate, dict) or not candidate.get("repository") or not candidate.get("revision"):
            continue
        try:
            upstream = current_revision(candidate["repository"], client, snapshot)
        except ExternalCapabilityError as exc:
            failures.append(f"{candidate.get('id')}: {exc}")
            continue
        outdated = upstream not in {"", "UNKNOWN", candidate["revision"]}
        results.append({
            "id": candidate["id"], "pinned_revision": candidate["revision"], "upstream_revision": upstream,
            "review_status": "OUTDATED" if outdated else candidate.get("review_status", "NOT_REVIEWED"),
            "result": "REVIEW OUTDATED" if outdated else "CURRENT",
        })
        if args.write:
            candidate["last_checked"] = checked_at[:10]
            if outdated and candidate.get("review_status") != "NOT_REVIEWED":
                candidate["review_status"] = "OUTDATED"
                changed = True
    if args.write and (changed or results):
        index["updated_at"] = checked_at
        write_json(args.index, index)
    return {"schema_version": 1, "checked_at": checked_at, "results": results, "failures": failures, "reviews_overwritten": False}


def validate_all(args: argparse.Namespace) -> int:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        registry = load_json(args.sources)
        errors.extend(validate_registry(registry))
    except ExternalCapabilityError as exc:
        registry = {}
        errors.append(str(exc))
    try:
        index = load_json(args.index)
        index_errors, index_warnings = validate_index(index, registry)
        errors.extend(index_errors)
        warnings.extend(index_warnings)
    except ExternalCapabilityError as exc:
        errors.append(str(exc))
    for path in sorted((ROOT / "external" / "reviews").glob("*.md")):
        if path.name != "README.md":
            errors.extend(validate_review(path))
    for relative in (
        "external/schema/sources.schema.json", "external/schema/index.schema.json", "external/schema/review.schema.json",
        "external/schema/discovery-result.schema.json", "external/schema/discovery-state.schema.json",
    ):
        if not (ROOT / relative).is_file():
            errors.append(f"missing external schema: {relative}")
    payload = {"errors": errors, "warnings": warnings, "sources": len(registry.get("sources", [])), "candidates": len(index.get("candidates", [])) if 'index' in locals() else 0}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"sources={payload['sources']} candidates={payload['candidates']} errors={len(errors)} warnings={len(warnings)}")
        for warning in warnings:
            print(f"WARNING {warning}")
        for error in errors:
            print(f"ERROR {error}")
    return 1 if errors else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate")
    validate.add_argument("--sources", type=Path, default=SOURCES_PATH)
    validate.add_argument("--index", type=Path, default=INDEX_PATH)
    validate.add_argument("--json", action="store_true")

    normalize = subparsers.add_parser("normalize-github")
    normalize.add_argument("location")

    discover = subparsers.add_parser("search")
    discover.add_argument("--topic", action="append")
    discover.add_argument("--project-root", type=Path)
    discover.add_argument("--source", action="append")
    discover.add_argument("--trust", action="append", choices=["OFFICIAL", "CURATED", "COMMUNITY"])
    discover.add_argument("--include-community", action="store_true")
    discover.add_argument("--per-source-limit", type=int, default=3)
    discover.add_argument("--community-limit", type=int, default=8)
    discover.add_argument("--limit", type=int, default=20)
    discover.add_argument("--max-workers", type=int, default=4)
    discover.add_argument("--sources", type=Path, default=SOURCES_PATH)
    discover.add_argument("--snapshot", type=Path)
    discover.add_argument("--output", type=Path)
    discover.add_argument("--cache-dir", type=Path, default=ROOT / "external" / "cache" / "search")
    discover.add_argument("--cache-ttl-seconds", type=int, default=1800)
    discover.add_argument("--repository-cache-ttl-seconds", type=int, default=86400)
    discover.add_argument("--source-scope", choices=("configured", "official", "official-curated", "all"), default="configured")
    discover.add_argument("--lock-path", type=Path)
    discover.add_argument("--lease-stale-seconds", type=int, default=1800)

    project = subparsers.add_parser("project-query")
    project.add_argument("--root", type=Path, required=True)

    upsert = subparsers.add_parser("index-upsert")
    upsert.add_argument("--results", type=Path, required=True)
    upsert.add_argument("--sources", type=Path, default=SOURCES_PATH)
    upsert.add_argument("--index", type=Path, default=INDEX_PATH)

    stale = subparsers.add_parser("check-stale")
    stale.add_argument("--index", type=Path, default=INDEX_PATH)
    stale.add_argument("--snapshot", type=Path)
    stale.add_argument("--write", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "validate":
            return validate_all(args)
        if args.command == "normalize-github":
            print(normalize_github(args.location))
            return 0
        if args.command == "project-query":
            print(json.dumps(project_query(args.root), indent=2))
            return 0
        if args.command == "search":
            lease_path = args.lock_path or (args.project_root / ".agent-commons" / "external-discovery.lock" if args.project_root else None)
            lease = DiscoveryLease(
                lease_path,
                discovery_request_key(args.topic or project_query(args.project_root)["terms"], args.source_scope, args.sources, args.snapshot),
                args.lease_stale_seconds,
            ) if lease_path else None
            if lease and not lease.acquire():
                raise ExternalCapabilityError("matching external discovery is already running")
            try:
                result = search(args)
            finally:
                if lease:
                    lease.release()
            if args.output:
                write_json(args.output, result)
            else:
                print(json.dumps(result, indent=2))
            return 0
        if args.command == "index-upsert":
            index_upsert(args)
            return 0
        if args.command == "check-stale":
            print(json.dumps(check_stale(args), indent=2))
            return 0
    except (ExternalCapabilityError, OSError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
