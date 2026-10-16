#!/usr/bin/env python3
"""Validate, fingerprint, and render evidence-derived brand profiles."""

from __future__ import annotations

import base64
import binascii
import copy
import hashlib
import html
import json
import re
from typing import Any
from urllib.parse import urlparse


SCHEMA_VERSION = 2
STATUSES = {"resolved", "unresolved", "blocked"}
CONFIDENCE = {"high", "medium", "low"}
RESOLUTION_METHODS = {"css-custom-properties", "semantic-css", "manual-evidence"}
HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
CSS_LENGTH = re.compile(r"^(?:0|[0-9]+(?:\.[0-9]+)?(?:px|rem))$")
SAFE_FONT_STACK = re.compile(r"^[A-Za-z0-9 ,.'\"-]+$")
SAFE_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9-]{1,63}$")

REQUIRED_COLOR_KEYS = (
    "ink", "ink_subtle", "paper", "surface", "surface_subtle", "card", "line", "line_strong",
    "accent", "accent_soft", "secondary", "risk", "risk_soft", "good", "muted", "focus", "link",
    "header", "on_dark",
)
REQUIRED_THEME_KEYS = {
    "colors": REQUIRED_COLOR_KEYS,
    "typography": ("display", "body", "data"),
    "geometry": ("radius", "border_width"),
    "signature": ("style", "color", "thickness"),
}
REQUIRED_ASSET_ROLES = ("favicon", "logo")
SEMANTIC_ROLE_TOKENS = {
    "primary": "theme.colors.accent",
    "secondary": "theme.colors.secondary",
    "highlight": "theme.signature.color",
    "danger": "theme.colors.risk",
    "success": "theme.colors.good",
    "focus": "theme.colors.focus",
    "header": "theme.colors.header",
}


def _relative_luminance(color: str) -> float:
    channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4 for channel in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast(first: str, second: str) -> float:
    lighter, darker = sorted((_relative_luminance(first), _relative_luminance(second)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)

GENERIC_VISIBLE_COLORS = {
    "#172326", "#39484b", "#f4f6f3", "#ffffff", "#edf1ed", "#d5ddd8", "#a9b6af",
    "#006b57", "#e7f2ed", "#a23c2c", "#fbebe8", "#277451", "#63716e", "#202a2b",
    "#008e5c", "#174a5b", "#e0643a", "#122126", "#52666c", "#bdc9cc", "#82979c",
}

GENERIC_THEME = {
    "colors": {
        "ink": "#172326", "ink_subtle": "#39484b", "paper": "#f4f6f3", "surface": "#ffffff",
        "surface_subtle": "#edf1ed", "card": "#ffffff", "line": "#d5ddd8",
        "line_strong": "#a9b6af", "accent": "#006b57", "accent_soft": "#e7f2ed",
        "secondary": "#008e5c", "risk": "#a23c2c", "risk_soft": "#fbebe8", "good": "#277451",
        "muted": "#63716e", "focus": "#008e5c", "link": "#006b57", "header": "#202a2b",
        "on_dark": "#ffffff",
    },
    "typography": {
        "display": "Arial Narrow, Arial, sans-serif",
        "body": "Arial, sans-serif",
        "data": "Courier New, monospace",
    },
    "geometry": {"radius": "2px", "border_width": "1px"},
    "signature": {"style": "rule", "color": "#006b57", "thickness": "4px"},
}

ACCENTURE_FALLBACK_THEME = {
    "colors": {
        "ink": "#161616", "ink_subtle": "#4b4b4b", "paper": "#f7f7f7", "surface": "#ffffff",
        "surface_subtle": "#f0f0f0", "card": "#ffffff", "line": "#d4d4d4",
        "line_strong": "#8c8c8c", "accent": "#a100ff", "accent_soft": "#f3e5ff",
        "secondary": "#7500c0", "risk": "#b42318", "risk_soft": "#fee4e2", "good": "#067647",
        "muted": "#666666", "focus": "#a100ff", "link": "#7500c0", "header": "#000000",
        "on_dark": "#ffffff",
    },
    "typography": {
        "display": "Arial Narrow, Arial, sans-serif",
        "body": "Arial, sans-serif",
        "data": "Courier New, monospace",
    },
    "geometry": {"radius": "0px", "border_width": "1px"},
    "signature": {"style": "rule", "color": "#a100ff", "thickness": "4px"},
}


def accenture_fallback_css() -> str:
    """Return the deterministic organization fallback without claiming client-brand fidelity."""
    colors = ACCENTURE_FALLBACK_THEME["colors"]
    typography = ACCENTURE_FALLBACK_THEME["typography"]
    geometry = ACCENTURE_FALLBACK_THEME["geometry"]
    signature = ACCENTURE_FALLBACK_THEME["signature"]
    variables = {
        "--ink": colors["ink"], "--ink-2": colors["ink_subtle"], "--paper": colors["paper"],
        "--surface": colors["surface"], "--surface-2": colors["surface_subtle"], "--card": colors["card"],
        "--line": colors["line"], "--line-strong": colors["line_strong"], "--accent": colors["accent"],
        "--accent-soft": colors["accent_soft"], "--secondary": colors["secondary"], "--risk": colors["risk"],
        "--risk-soft": colors["risk_soft"], "--good": colors["good"], "--muted": colors["muted"],
        "--focus": colors["focus"], "--link": colors["link"], "--charcoal": colors["header"],
        "--on-dark": colors["on_dark"], "--display": typography["display"], "--body": typography["body"],
        "--data": typography["data"], "--radius": geometry["radius"],
        "--border-width": geometry["border_width"], "--signature": signature["color"],
        "--signature-thickness": signature["thickness"], "--highlight": signature["color"],
        "--brand-primary": colors["accent"], "--brand-accent": colors["secondary"],
        "--canvas": colors["paper"], "--rule": colors["line"], "--strong-rule": colors["line_strong"],
    }
    declarations = ";".join(f"{key}:{value}" for key, value in variables.items())
    return f'html[data-brand-id="accenture-fallback"]{{{declarations}}}'


def accenture_fallback_attributes() -> str:
    return (
        'data-brand-id="accenture-fallback" data-brand-status="fallback" '
        'data-brand-profile-fingerprint="" data-brand-theme-fingerprint="" data-brand-asset-fingerprint=""'
    )


def accenture_fallback_favicon() -> str:
    return (
        '<link rel="icon" type="image/svg+xml" sizes="any" '
        'href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 64 64%27%3E'
        '%3Cpath d=%27M8 8h24l24 24-24 24H8l24-24z%27 fill=%27%23a100ff%27/%3E%3C/svg%3E">'
    )


def accenture_fallback_logo(css_class: str = "brand-logo") -> str:
    return (
        f'<svg class="{html.escape(css_class)}" role="img" aria-label="Accenture" '
        'viewBox="0 0 180 48" width="180" height="48">'
        '<title>Accenture</title><text x="0" y="34" fill="currentColor" '
        'font-family="Arial, sans-serif" font-size="30" font-weight="700">accenture</text>'
        '<path d="M142 3h20l16 10-16 10h-20l16-10z" fill="#a100ff"/></svg>'
    )


def _fingerprint(value: object) -> str:
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def theme_fingerprint(theme: dict[str, object]) -> str:
    return _fingerprint(theme)


def asset_fingerprint(assets: dict[str, object]) -> str:
    canonical = {
        role: {key: record.get(key) for key in ("role", "source_url", "source_kind", "media_type", "sha256", "target")}
        for role, record in sorted(assets.items()) if isinstance(record, dict)
    }
    return _fingerprint(canonical)


def _profile_fingerprint(profile: dict[str, object]) -> str:
    canonical = {
        key: value for key, value in profile.items()
        if key not in {"profile_fingerprint", "theme_fingerprint", "asset_fingerprint"}
    }
    return _fingerprint(canonical)


def _semantic_brand_roles(
    profile: dict[str, object], observed_by_value: dict[str, list[str]], evidence_ids: set[str]
) -> dict[str, object]:
    theme = profile["theme"]
    colors = theme["colors"]
    role_values = {
        "primary": colors["accent"],
        "secondary": colors["secondary"],
        "highlight": theme["signature"]["color"],
        "danger": colors["risk"],
        "success": colors["good"],
        "focus": colors["focus"],
        "header": colors["header"],
    }
    mappings = {item["token"]: item for item in profile["mappings"]}
    roles: dict[str, object] = {}
    for role, token in SEMANTIC_ROLE_TOKENS.items():
        value = role_values[role]
        roles[role] = {
            "token": token,
            "value": value,
            "observed_usages": observed_by_value.get(value, []),
            "evidence_ids": mappings.get(token, {}).get("evidence_ids", []),
            "mapping_rationale": mappings.get(token, {}).get("rationale", ""),
            "confidence": mappings.get(token, {}).get("confidence", ""),
        }
    roles["identity"] = {
        "asset_roles": list(REQUIRED_ASSET_ROLES),
        "asset_fingerprint": asset_fingerprint(profile["assets"]),
        "evidence_ids": sorted(evidence_ids),
    }
    return roles


def _has_usage(usages: list[str], terms: set[str]) -> bool:
    text = " ".join(usages).casefold()
    return any(term in text for term in terms)


def _validate_semantic_brand_roles(roles: dict[str, object]) -> None:
    primary = roles["primary"]
    header = roles["header"]
    danger = roles["danger"]
    success = roles["success"]
    focus = roles["focus"]
    if not _has_usage(primary["observed_usages"], {"primary", "brand", "navigation", "header", "link", "accent"}):
        raise ValueError("brand primary color lacks evidence for a global product role")
    if _has_usage(primary["observed_usages"], {"logo", "wordmark", "icon", "highlight"}) and not _has_usage(
        primary["observed_usages"], {"primary", "navigation", "header", "link", "background", "surface"}
    ):
        raise ValueError("logo-only or highlight-only color cannot become the global primary color")
    if not _has_usage(header["observed_usages"], {"header", "navigation", "background", "surface", "text", "primary"}):
        raise ValueError("brand header color lacks evidence for a global header or navigation role")
    if primary["value"] == danger["value"] or header["value"] == danger["value"]:
        raise ValueError("danger must remain semantically distinguishable from global brand accents")
    if success["value"] == danger["value"]:
        raise ValueError("success must remain semantically distinguishable from danger")
    danger_evidence = [*danger["observed_usages"], str(danger.get("mapping_rationale", ""))]
    if not _has_usage(danger_evidence, {"danger", "risk", "error", "failure", "critical"}):
        raise ValueError("brand danger color lacks danger or risk usage evidence")
    success_evidence = [*success["observed_usages"], str(success.get("mapping_rationale", ""))]
    if not _has_usage(success_evidence, {"success", "good", "pass", "positive", "complete"}):
        raise ValueError("brand success color lacks success usage evidence")
    focus_evidence = [*focus["observed_usages"], str(focus.get("mapping_rationale", ""))]
    if not _has_usage(focus_evidence, {"focus", "keyboard", "outline"}):
        raise ValueError("brand focus color lacks focus usage evidence")


def _mapping_paths() -> set[str]:
    return {
        f"theme.{group}.{key}"
        for group, keys in REQUIRED_THEME_KEYS.items()
        for key in keys
    }


def _validate_capture_record(record: object, label: str) -> dict[str, str]:
    if not isinstance(record, dict):
        raise ValueError(f"brand profile {label} must be an object")
    normalized = copy.deepcopy(record)
    for field in ("url", "media_type", "sha256"):
        value = normalized.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"brand profile {label}.{field} must be non-empty")
    normalized["sha256"] = normalized["sha256"].lower()
    if not SHA256.fullmatch(normalized["sha256"]):
        raise ValueError(f"brand profile {label}.sha256 must be a SHA-256 hex digest")
    return normalized


def _decode_asset_data(record: dict[str, object], label: str) -> bytes:
    data_uri = record.get("data_uri")
    if not isinstance(data_uri, str) or not data_uri.startswith("data:") or "," not in data_uri:
        raise ValueError(f"brand profile assets.{label}.data_uri must be an embedded data URI")
    header, payload = data_uri.split(",", 1)
    if ";base64" not in header:
        raise ValueError(f"brand profile assets.{label}.data_uri must use base64")
    try:
        decoded = base64.b64decode(payload, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise ValueError(f"brand profile assets.{label}.data_uri is invalid") from exc
    if not decoded:
        raise ValueError(f"brand profile assets.{label} is empty")
    return decoded


def _validate_image_payload(payload: bytes, media_type: str, label: str) -> None:
    lowered = payload.lstrip().lower()
    sniffed = None
    if lowered.startswith((b"<svg", b"<?xml")) and b"<svg" in lowered[:4096]:
        sniffed = "image/svg+xml"
    elif payload.startswith(b"\x89PNG\r\n\x1a\n"):
        sniffed = "image/png"
    elif payload.startswith(b"\xff\xd8\xff"):
        sniffed = "image/jpeg"
    elif payload.startswith((b"GIF87a", b"GIF89a")):
        sniffed = "image/gif"
    elif payload.startswith(b"RIFF") and payload[8:12] == b"WEBP":
        sniffed = "image/webp"
    elif payload.startswith(b"\x00\x00\x01\x00"):
        sniffed = "image/x-icon"
    compatible_icon = {media_type, sniffed} <= {"image/x-icon", "image/vnd.microsoft.icon"}
    if sniffed is None or (media_type != sniffed and not compatible_icon):
        raise ValueError(f"brand profile assets.{label} bytes do not match media_type {media_type}")
    if sniffed != "image/svg+xml":
        return
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"brand profile assets.{label} SVG encoding is unsafe") from exc
    unsafe_patterns = (
        r"<\s*script\b", r"\bon[a-z]+\s*=", r"<\s*foreignobject\b", r"<!\s*(?:doctype|entity)\b",
        r"\b(?:href|src)\s*=\s*['\"]\s*(?!#|data:)[^'\"]+",
        r"url\(\s*['\"]?\s*(?!#|data:)[^)]+",
    )
    if any(re.search(pattern, text, re.I) for pattern in unsafe_patterns):
        raise ValueError(f"brand profile assets.{label} contains unsafe SVG content")


def _validate_asset(record: object, role: str, required: bool) -> dict[str, object]:
    if not isinstance(record, dict):
        raise ValueError(f"brand profile assets.{role} must be an object")
    normalized = copy.deepcopy(record)
    for field in ("role", "source_url", "source_kind", "media_type", "sha256", "target", "data_uri"):
        if not isinstance(normalized.get(field), str) or not str(normalized[field]).strip():
            raise ValueError(f"brand profile assets.{role}.{field} must be non-empty")
    if normalized["role"] != role:
        raise ValueError(f"brand profile assets.{role}.role must be {role}")
    if normalized["target"] != "embedded":
        raise ValueError(f"brand profile assets.{role}.target must be embedded")
    parsed = urlparse(str(normalized["source_url"]))
    if required and (normalized["source_kind"] != "official" or parsed.scheme not in {"http", "https", "file"}):
        raise ValueError(f"brand profile assets.{role} must come from an official resolvable source")
    if not str(normalized["media_type"]).startswith("image/"):
        raise ValueError(f"brand profile assets.{role}.media_type must be an image type")
    normalized["sha256"] = str(normalized["sha256"]).lower()
    if not SHA256.fullmatch(str(normalized["sha256"])):
        raise ValueError(f"brand profile assets.{role}.sha256 must be a SHA-256 hex digest")
    decoded = _decode_asset_data(normalized, role)
    if hashlib.sha256(decoded).hexdigest() != normalized["sha256"]:
        raise ValueError(f"brand profile assets.{role} embedded bytes do not match sha256")
    declared_media = str(normalized["data_uri"]).split(";", 1)[0][5:]
    if declared_media != normalized["media_type"]:
        raise ValueError(f"brand profile assets.{role} data URI media type differs")
    _validate_image_payload(decoded, str(normalized["media_type"]), role)
    return normalized


def validate_brand_profile(value: object) -> dict[str, object]:
    """Return a normalized profile or fail closed on unsupported or unproven branding."""
    if not isinstance(value, dict):
        raise ValueError("brand profile must be an object")
    profile = copy.deepcopy(value)
    if profile.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"brand profile schema_version must be {SCHEMA_VERSION}")
    identifier = profile.get("id")
    if not isinstance(identifier, str) or not SAFE_IDENTIFIER.fullmatch(identifier):
        raise ValueError("brand profile id must be a lowercase kebab-case identifier")
    name = profile.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("brand profile name must be non-empty")
    required = profile.get("required")
    if not isinstance(required, bool):
        raise ValueError("brand profile required must be boolean")
    status = profile.get("status")
    if status not in STATUSES:
        raise ValueError(f"brand profile status must use {sorted(STATUSES)}")
    if required and status != "resolved":
        raise ValueError(f"required brand profile is not resolved: {status}")
    resolution_method = profile.get("resolution_method")
    if resolution_method not in RESOLUTION_METHODS:
        raise ValueError(f"brand profile resolution_method must use {sorted(RESOLUTION_METHODS)}")

    source = profile.get("source")
    if not isinstance(source, dict):
        raise ValueError("brand profile source must be an object")
    for field in ("requested_url", "resolved_url", "captured_at"):
        if not isinstance(source.get(field), str) or not str(source[field]).strip():
            raise ValueError(f"brand profile source.{field} must be non-empty")
    if required:
        for field in ("requested_url", "resolved_url"):
            if urlparse(str(source[field])).scheme not in {"http", "https", "file"}:
                raise ValueError(f"brand profile source.{field} must be resolvable")
    source["html"] = _validate_capture_record(source.get("html"), "source.html")
    stylesheets = source.get("stylesheets")
    if not isinstance(stylesheets, list):
        raise ValueError("brand profile source.stylesheets must be an array")
    source["stylesheets"] = [
        _validate_capture_record(record, f"source.stylesheets[{index}]")
        for index, record in enumerate(stylesheets)
    ]
    if required and not source["stylesheets"]:
        raise ValueError("required brand profile needs captured stylesheet evidence")
    if source.get("manifest") is not None:
        source["manifest"] = _validate_capture_record(source["manifest"], "source.manifest")
    metadata = source.get("metadata")
    if required and not isinstance(metadata, dict):
        raise ValueError("required brand profile needs captured metadata")
    if isinstance(metadata, dict):
        if not isinstance(metadata.get("title"), str) or not str(metadata["title"]).strip():
            raise ValueError("brand profile source.metadata.title must be non-empty")
        if not isinstance(metadata.get("favicon_candidates"), list) or not metadata["favicon_candidates"]:
            raise ValueError("brand profile source.metadata.favicon_candidates must be non-empty")
        if not isinstance(metadata.get("logo_candidate"), str) or not str(metadata["logo_candidate"]).strip():
            raise ValueError("brand profile source.metadata.logo_candidate must be non-empty")
    source_fingerprint_value = _fingerprint({key: value for key, value in source.items() if key != "fingerprint"})
    if source.get("fingerprint") and source["fingerprint"] != source_fingerprint_value:
        raise ValueError("brand profile source fingerprint is stale")
    source["fingerprint"] = source_fingerprint_value
    profile["source"] = source

    assets = profile.get("assets")
    if not isinstance(assets, dict):
        raise ValueError("brand profile assets must be an object")
    missing_assets = set(REQUIRED_ASSET_ROLES) - assets.keys()
    if missing_assets:
        raise ValueError(f"brand profile assets are missing: {sorted(missing_assets)}")
    profile["assets"] = {role: _validate_asset(assets[role], role, bool(required)) for role in REQUIRED_ASSET_ROLES}

    identity = profile.get("identity")
    if not isinstance(identity, dict):
        raise ValueError("brand profile identity must be an object")
    for field in ("display_name", "logo_alt"):
        if not isinstance(identity.get(field), str) or not str(identity[field]).strip():
            raise ValueError(f"brand profile identity.{field} must be non-empty")

    observed = profile.get("observed_colors")
    if not isinstance(observed, list) or not observed:
        raise ValueError("brand profile observed_colors must be a non-empty array")
    observed_values: set[str] = set()
    observed_by_value: dict[str, list[str]] = {}
    for index, item in enumerate(observed):
        if not isinstance(item, dict):
            raise ValueError(f"brand profile observed_colors[{index}] must be an object")
        value_string = item.get("value")
        usages = item.get("usages")
        if not isinstance(value_string, str) or not HEX_COLOR.fullmatch(value_string):
            raise ValueError(f"brand profile observed_colors[{index}].value must be a six-digit hex color")
        item["value"] = value_string.lower()
        observed_values.add(item["value"])
        if not isinstance(usages, list) or not usages or any(not isinstance(entry, str) or not entry for entry in usages):
            raise ValueError(f"brand profile observed_colors[{index}].usages must be a non-empty string array")
        if not isinstance(item.get("source_ref"), str) or not str(item["source_ref"]).strip():
            raise ValueError(f"brand profile observed_colors[{index}].source_ref must be non-empty")
        if item.get("confidence") not in CONFIDENCE:
            raise ValueError(f"brand profile observed_colors[{index}].confidence must use {sorted(CONFIDENCE)}")
        observed_by_value.setdefault(item["value"], []).extend(usages)

    evidence = profile.get("evidence")
    if not isinstance(evidence, list) or any(not isinstance(item, dict) for item in evidence):
        raise ValueError("brand profile evidence must be an array of objects")
    evidence_ids: set[str] = set()
    for index, item in enumerate(evidence):
        evidence_id = item.get("id")
        if not isinstance(evidence_id, str) or not evidence_id.strip():
            raise ValueError(f"brand profile evidence[{index}].id must be non-empty")
        if evidence_id in evidence_ids:
            raise ValueError(f"duplicate brand evidence id: {evidence_id}")
        evidence_ids.add(evidence_id)
        for field in ("signal", "source_ref"):
            if not isinstance(item.get(field), str) or not str(item[field]).strip():
                raise ValueError(f"brand profile evidence[{index}].{field} must be non-empty")
        if item.get("confidence") not in CONFIDENCE:
            raise ValueError(f"brand profile evidence[{index}].confidence must use {sorted(CONFIDENCE)}")
    if status == "resolved" and not evidence:
        raise ValueError("resolved brand profile requires evidence")

    derived = profile.get("derived_tokens", [])
    if not isinstance(derived, list) or any(not isinstance(item, dict) for item in derived):
        raise ValueError("brand profile derived_tokens must be an array of objects")
    derived_by_token: dict[str, str] = {}
    for index, item in enumerate(derived):
        token = item.get("token")
        value_string = item.get("value")
        parents = item.get("derived_from")
        method = item.get("method")
        references = item.get("evidence_ids")
        if not isinstance(token, str) or token in derived_by_token:
            raise ValueError(f"brand profile derived_tokens[{index}].token must be unique")
        if not isinstance(value_string, str) or not HEX_COLOR.fullmatch(value_string):
            raise ValueError(f"brand profile derived_tokens[{index}].value must be a six-digit hex color")
        if not isinstance(parents, list) or not parents or any(parent.lower() not in observed_values for parent in parents):
            raise ValueError(f"brand profile derived_tokens[{index}].derived_from must reference observed colors")
        if not isinstance(method, str) or not method.strip():
            raise ValueError(f"brand profile derived_tokens[{index}].method must be non-empty")
        if item.get("confidence") not in CONFIDENCE:
            raise ValueError(f"brand profile derived_tokens[{index}].confidence must use {sorted(CONFIDENCE)}")
        if not isinstance(references, list) or not references or any(not isinstance(reference, str) for reference in references):
            raise ValueError(f"brand profile derived_tokens[{index}].evidence_ids must be a non-empty string array")
        unknown = sorted(set(references) - evidence_ids)
        if unknown:
            raise ValueError(f"brand profile derived_tokens[{index}] references unknown evidence: {unknown}")
        item["value"] = value_string.lower()
        derived_by_token[token] = item["value"]

    theme = profile.get("theme")
    if not isinstance(theme, dict):
        raise ValueError("brand profile theme must be an object")
    for group, keys in REQUIRED_THEME_KEYS.items():
        values = theme.get(group)
        if not isinstance(values, dict):
            raise ValueError(f"brand profile theme.{group} must be an object")
        missing = set(keys) - values.keys()
        extra = values.keys() - set(keys)
        if missing or extra:
            raise ValueError(f"brand profile theme.{group} keys invalid: missing={sorted(missing)} extra={sorted(extra)}")
    for key, color in theme["colors"].items():
        if not isinstance(color, str) or not HEX_COLOR.fullmatch(color):
            raise ValueError(f"brand profile theme.colors.{key} must be a six-digit hex color")
        normalized_color = color.lower()
        theme["colors"][key] = normalized_color
        token = f"theme.colors.{key}"
        if normalized_color not in observed_values and derived_by_token.get(token) != normalized_color:
            raise ValueError(f"brand profile {token} is neither observed nor explicitly derived")
    surface = theme["colors"]["surface"]
    for role in ("ink", "good", "link", "muted", "risk"):
        if _contrast(theme["colors"][role], surface) < 4.5:
            raise ValueError(f"brand profile theme.colors.{role} must meet 4.5:1 contrast against surface")
    if _contrast(theme["colors"]["focus"], surface) < 3.0:
        raise ValueError("brand profile theme.colors.focus must meet 3:1 contrast against surface")
    for background in ("header", "accent"):
        if _contrast(theme["colors"]["on_dark"], theme["colors"][background]) < 4.5:
            raise ValueError(f"brand profile theme.colors.on_dark must meet 4.5:1 contrast against {background}")
    for key, font_stack in theme["typography"].items():
        if not isinstance(font_stack, str) or not SAFE_FONT_STACK.fullmatch(font_stack):
            raise ValueError(f"brand profile theme.typography.{key} is not a safe local font stack")
    for key, length in theme["geometry"].items():
        if not isinstance(length, str) or not CSS_LENGTH.fullmatch(length):
            raise ValueError(f"brand profile theme.geometry.{key} must be a CSS length")
    signature = theme["signature"]
    if signature["style"] != "rule":
        raise ValueError("brand profile theme.signature.style must be rule")
    if not isinstance(signature["color"], str) or not HEX_COLOR.fullmatch(signature["color"]):
        raise ValueError("brand profile theme.signature.color must be a six-digit hex color")
    signature["color"] = signature["color"].lower()
    if signature["color"] not in observed_values:
        raise ValueError("brand profile theme.signature.color must be observed")
    if not isinstance(signature["thickness"], str) or not CSS_LENGTH.fullmatch(signature["thickness"]):
        raise ValueError("brand profile theme.signature.thickness must be a CSS length")

    mappings = profile.get("mappings")
    if not isinstance(mappings, list) or any(not isinstance(item, dict) for item in mappings):
        raise ValueError("brand profile mappings must be an array of objects")
    mapped_paths: set[str] = set()
    for index, mapping in enumerate(mappings):
        token = mapping.get("token")
        references = mapping.get("evidence_ids")
        if not isinstance(token, str) or token in mapped_paths:
            raise ValueError(f"brand profile mappings[{index}].token must be unique")
        if not isinstance(references, list) or not references or any(not isinstance(item, str) for item in references):
            raise ValueError(f"brand profile mappings[{index}].evidence_ids must be a non-empty string array")
        unknown = sorted(set(references) - evidence_ids)
        if unknown:
            raise ValueError(f"brand profile mapping {token} references unknown evidence: {unknown}")
        if mapping.get("decision") not in {"observed", "derived"}:
            raise ValueError(f"brand profile mappings[{index}].decision must be observed or derived")
        if mapping.get("confidence") not in CONFIDENCE:
            raise ValueError(f"brand profile mappings[{index}].confidence must use {sorted(CONFIDENCE)}")
        for field in ("rationale", "source_ref"):
            if not isinstance(mapping.get(field), str) or not str(mapping[field]).strip():
                raise ValueError(f"brand profile mappings[{index}].{field} must be non-empty")
        if str(token).startswith("theme.colors."):
            color_key = str(token).rsplit(".", 1)[-1]
            color_value = theme["colors"].get(color_key)
            if mapping["decision"] == "derived" and derived_by_token.get(str(token)) != color_value:
                raise ValueError(f"brand profile mapping {token} is derived without matching derivation provenance")
            if mapping["decision"] == "observed" and color_value not in observed_values:
                raise ValueError(f"brand profile mapping {token} is observed but its value was not observed")
        mapped_paths.add(token)
    expected_paths = _mapping_paths()
    if mapped_paths != expected_paths:
        raise ValueError(
            "brand profile mappings must prove every theme token: "
            f"missing={sorted(expected_paths - mapped_paths)} extra={sorted(mapped_paths - expected_paths)}"
        )

    computed_theme_fingerprint = theme_fingerprint(theme)
    if required and computed_theme_fingerprint == theme_fingerprint(GENERIC_THEME):
        raise ValueError("required client branding resolves to the generic dashboard fallback")
    profile["semantic_roles"] = _semantic_brand_roles(profile, observed_by_value, evidence_ids)
    _validate_semantic_brand_roles(profile["semantic_roles"])
    if profile.get("theme_fingerprint") and profile["theme_fingerprint"] != computed_theme_fingerprint:
        raise ValueError("brand profile theme fingerprint is stale")
    profile["theme_fingerprint"] = computed_theme_fingerprint

    computed_asset_fingerprint = asset_fingerprint(profile["assets"])
    if profile.get("asset_fingerprint") and profile["asset_fingerprint"] != computed_asset_fingerprint:
        raise ValueError("brand profile asset fingerprint is stale")
    profile["asset_fingerprint"] = computed_asset_fingerprint

    computed_profile_fingerprint = _profile_fingerprint(profile)
    if profile.get("profile_fingerprint") and profile["profile_fingerprint"] != computed_profile_fingerprint:
        raise ValueError("brand profile fingerprint is stale")
    profile["profile_fingerprint"] = computed_profile_fingerprint
    return profile


def css_variables(profile: dict[str, object]) -> dict[str, str]:
    theme = profile["theme"]
    colors = theme["colors"]
    return {
        "--ink": colors["ink"], "--ink-2": colors["ink_subtle"], "--paper": colors["paper"],
        "--surface": colors["surface"], "--surface-2": colors["surface_subtle"], "--card": colors["card"],
        "--line": colors["line"], "--line-strong": colors["line_strong"], "--accent": colors["accent"],
        "--accent-soft": colors["accent_soft"], "--secondary": colors["secondary"], "--risk": colors["risk"],
        "--risk-soft": colors["risk_soft"], "--good": colors["good"], "--muted": colors["muted"],
        "--focus": colors["focus"], "--link": colors["link"], "--charcoal": colors["header"],
        "--on-dark": colors["on_dark"], "--display": theme["typography"]["display"],
        "--body": theme["typography"]["body"], "--data": theme["typography"]["data"],
        "--radius": theme["geometry"]["radius"], "--border-width": theme["geometry"]["border_width"],
        "--signature": theme["signature"]["color"], "--signature-thickness": theme["signature"]["thickness"],
        "--highlight": theme["signature"]["color"],
        "--brand-primary": colors["accent"], "--brand-accent": colors["secondary"],
        "--canvas": colors["paper"], "--rule": colors["line"], "--strong-rule": colors["line_strong"],
    }


def render_brand_css(profile: dict[str, object]) -> str:
    declarations = ";".join(f"{key}:{value}" for key, value in css_variables(profile).items())
    return f'html[data-brand-id="{html.escape(str(profile["id"]))}"]{{{declarations}}}'


def favicon_markup(profile: dict[str, object]) -> str:
    record = profile["assets"]["favicon"]
    return (
        f'<link rel="icon" type="{html.escape(str(record["media_type"]))}" '
        f'href="{html.escape(str(record["data_uri"]), quote=True)}" '
        f'data-brand-asset="favicon" data-brand-asset-sha256="{record["sha256"]}">'
    )


def logo_markup(profile: dict[str, object], css_class: str = "brand-logo") -> str:
    record = profile["assets"]["logo"]
    return (
        f'<img class="{html.escape(css_class)}" data-brand-logo data-brand-asset="logo" '
        f'data-brand-asset-sha256="{record["sha256"]}" '
        f'src="{html.escape(str(record["data_uri"]), quote=True)}" '
        f'alt="{html.escape(str(profile["identity"]["logo_alt"]))}">'
    )


def brand_attributes(profile: dict[str, object]) -> str:
    return (
        f'data-brand-id="{html.escape(str(profile["id"]))}" data-brand-status="{profile["status"]}" '
        f'data-brand-profile-fingerprint="{profile["profile_fingerprint"]}" '
        f'data-brand-theme-fingerprint="{profile["theme_fingerprint"]}" '
        f'data-brand-asset-fingerprint="{profile["asset_fingerprint"]}"'
    )
