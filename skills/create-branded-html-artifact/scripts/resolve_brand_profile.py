#!/usr/bin/env python3
"""Resolve an official website into the canonical offline brand-profile contract."""

from __future__ import annotations

import argparse
import base64
import binascii
import colorsys
import gzip
import hashlib
import io
import json
import math
import mimetypes
import re
import sys
import zlib
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import unquote_to_bytes, urljoin, urlparse
from urllib.request import Request, urlopen


BRAND_SCRIPTS = Path(__file__).resolve().parents[2] / "build-living-dashboard" / "scripts"
sys.path.insert(0, str(BRAND_SCRIPTS))
from brand_profile import REQUIRED_THEME_KEYS, validate_brand_profile  # noqa: E402


MAX_CAPTURE_BYTES = 8 * 1024 * 1024
HEX = re.compile(r"#[0-9a-fA-F]{3,8}(?![0-9a-fA-F])")
RGB = re.compile(r"rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})(?:\s*,\s*([01](?:\.\d+)?))?\s*\)", re.I)
CUSTOM_PROPERTY = re.compile(r"(--[a-zA-Z0-9_-]+)\s*:\s*([^;}{]+)")
CSS_RULE = re.compile(r"([^{}]+)\{([^{}]*)\}", re.S)
CSS_DECLARATION = re.compile(r"([\w-]+)\s*:\s*([^;{}]+)")
CSS_LENGTH_VALUE = re.compile(r"(?<![\w.-])([0-9]+(?:\.[0-9]+)?(?:px|rem))(?![\w.-])", re.I)
CSS_VARIABLE_REFERENCE = re.compile(r"var\(\s*(--[\w-]+)(?:\s*,\s*([^()]*))?\s*\)", re.I)
CSS_IMAGE_DECLARATION = re.compile(
    r"((?:background(?:-image)?|content|mask(?:-image)?|-webkit-mask(?:-image)?))\s*:\s*"
    r"url\(\s*(?:\"([^\"]*)\"|'([^']*)'|([^)]*))\s*\)",
    re.I | re.S,
)
INLINE_SVG = re.compile(br"<svg\b[^>]*>.*?</svg\s*>", re.I | re.S)
HTML_ATTRIBUTE = re.compile(r"([:\w-]+)\s*=\s*(['\"])(.*?)\2", re.S)

COLOR_VARIABLES = {
    "ink": "--brand-ink", "ink_subtle": "--brand-ink-subtle", "paper": "--brand-paper",
    "surface": "--brand-surface", "surface_subtle": "--brand-surface-subtle", "card": "--brand-card",
    "line": "--brand-line", "line_strong": "--brand-line-strong", "accent": "--brand-primary",
    "accent_soft": "--brand-accent-soft", "secondary": "--brand-secondary", "risk": "--brand-danger",
    "risk_soft": "--brand-risk-soft", "good": "--brand-success", "muted": "--brand-muted",
    "focus": "--brand-focus", "link": "--brand-link", "header": "--brand-header",
    "on_dark": "--brand-on-dark",
}
TYPOGRAPHY_VARIABLES = {
    "display": "--brand-font-display", "body": "--brand-font-body", "data": "--brand-font-data",
}
GEOMETRY_VARIABLES = {"radius": "--brand-radius", "border_width": "--brand-border-width"}

SEMANTIC_TERMS = {
    "danger": ("danger", "error", "invalid", "critical", "failure", "alert"),
    "success": ("success", "positive", "complete", "confirmation", "confirmed"),
    "focus": (":focus", "focus-visible", "focus-within", "keyboard"),
    "header": ("header", "navigation", "navbar", "nav-", "nav_", "nav ", "footer"),
    "primary": ("primary", "cta", "brand-accent", "brand-primary", "highlight"),
    "button": ("button", "btn", "submit"),
    "link": ("link", "breadcrumb"),
    "card": ("card", "panel", "tile", "teaser", "box", "modal"),
    "muted": ("muted", "subtle", "secondary", "metadata", "placeholder", "disabled", "caption"),
    "logo": ("logo", "wordmark"),
}


class BrandResolutionError(ValueError):
    """A fail-closed brand resolution error with actionable diagnostics."""

    def __init__(self, diagnostics: list[str]) -> None:
        self.diagnostics = list(dict.fromkeys(diagnostics))
        super().__init__("; ".join(self.diagnostics))


@dataclass
class ColorEvidence:
    value: str
    count: int = 0
    usages: set[str] = field(default_factory=set)
    sources: set[str] = field(default_factory=set)
    categories: Counter[str] = field(default_factory=Counter)
    role_properties: Counter[str] = field(default_factory=Counter)


@dataclass
class CssAnalysis:
    properties: dict[str, str] = field(default_factory=dict)
    property_sources: dict[str, str] = field(default_factory=dict)
    colors: dict[str, ColorEvidence] = field(default_factory=dict)
    fonts: list[tuple[str, str, str]] = field(default_factory=list)
    radii: list[tuple[str, str, str]] = field(default_factory=list)
    border_widths: list[tuple[str, str, str]] = field(default_factory=list)
    logo_candidates: list[dict[str, object]] = field(default_factory=list)
    source_refs: set[str] = field(default_factory=set)


class DiscoveryParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.icons: list[dict[str, str]] = []
        self.stylesheets: list[str] = []
        self.inline_styles: list[str] = []
        self.manifest: str | None = None
        self.logos: list[dict[str, object]] = []
        self.metadata_logos: list[str] = []
        self.linked_logos: list[str] = []
        self.json_ld_blocks: list[str] = []
        self.preview_images: list[str] = []
        self.theme_colors: list[str] = []
        self.title_parts: list[str] = []
        self.visible_tokens: set[str] = set()
        self._title = False
        self._style = False
        self._style_parts: list[str] = []
        self._json_ld = False
        self._json_ld_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        self.visible_tokens.add(tag.lower())
        self.visible_tokens.update(f".{name}" for name in values.get("class", "").split() if name)
        if values.get("id"):
            self.visible_tokens.add(f"#{values['id']}")
        if values.get("style"):
            self.inline_styles.append(f"{tag}[style]{{{values['style']}}}")
        if tag == "link":
            relations = {part.lower() for part in values.get("rel", "").split()}
            if relations & {"icon", "shortcut", "apple-touch-icon", "mask-icon"} and values.get("href"):
                self.icons.append({
                    "href": values["href"], "type": values.get("type", ""),
                    "sizes": values.get("sizes", ""), "rel": values.get("rel", ""),
                })
            if "stylesheet" in relations and values.get("href"):
                self.stylesheets.append(values["href"])
            if "manifest" in relations and values.get("href"):
                self.manifest = values["href"]
            if relations & {"logo", "brand"} and values.get("href"):
                self.linked_logos.append(values["href"])
        elif tag == "meta":
            key = (values.get("name") or values.get("property") or "").lower()
            if key in {"theme-color", "msapplication-tilecolor"} and values.get("content"):
                self.theme_colors.append(values["content"])
            if key in {"og:image", "twitter:image"} and values.get("content"):
                self.preview_images.append(values["content"])
            if key in {"logo", "og:logo", "twitter:logo", "application-logo", "organization-logo"} and values.get("content"):
                self.metadata_logos.append(values["content"])
        elif tag in {"img", "source"} and (values.get("src") or values.get("srcset")):
            source = values.get("src") or values.get("srcset", "").split(",", 1)[0].strip().split(" ", 1)[0]
            identity = " ".join((values.get("class", ""), values.get("id", ""), values.get("alt", ""), source)).lower()
            score = identity.count("logo") * 4 + identity.count("wordmark") * 4 + (1 if "brand" in identity else 0)
            if "header" in identity:
                score += 4
            if any(term in identity for term in ("facebook", "linkedin", "twitter", "instagram", "youtube", "social")):
                score -= 20
            if score:
                self.logos.append({"src": source, "alt": values.get("alt") or "Official brand logo", "score": score})
        elif tag == "title":
            self._title = True
        elif tag == "style":
            self._style = True
            self._style_parts = []
        elif tag == "script" and values.get("type", "").casefold() == "application/ld+json":
            self._json_ld = True
            self._json_ld_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._title = False
        elif tag == "style" and self._style:
            self.inline_styles.append("".join(self._style_parts))
            self._style = False
            self._style_parts = []
        elif tag == "script" and self._json_ld:
            self.json_ld_blocks.append("".join(self._json_ld_parts))
            self._json_ld = False
            self._json_ld_parts = []

    def handle_data(self, data: str) -> None:
        if self._title:
            self.title_parts.append(data)
        if self._style:
            self._style_parts.append(data)
        if self._json_ld:
            self._json_ld_parts.append(data)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def media_type(url: str, supplied: str | None) -> str:
    value = (supplied or "").split(";", 1)[0].strip().lower()
    if value and value != "application/octet-stream":
        return value
    path = url.split("?", 1)[0]
    if path.lower().endswith(".webmanifest"):
        return "application/manifest+json"
    return mimetypes.guess_type(path)[0] or "application/octet-stream"


def _validate_fetch_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https", "file"}:
        raise ValueError(f"unsafe or unsupported URL scheme: {parsed.scheme or 'missing'}")
    if parsed.username or parsed.password:
        raise ValueError("URLs containing credentials are unsafe")


def _decode_http_content(payload: bytes, content_encoding: str, url: str) -> bytes:
    """Decode common HTTP transfer encodings with the same bounded capture limit."""
    decoded = payload
    encodings = [part.strip().casefold() for part in content_encoding.split(",") if part.strip()]
    for encoding in reversed(encodings):
        try:
            if encoding in {"", "identity"}:
                continue
            if encoding in {"gzip", "x-gzip"}:
                with gzip.GzipFile(fileobj=io.BytesIO(decoded)) as stream:
                    decoded = stream.read(MAX_CAPTURE_BYTES + 1)
            elif encoding == "deflate":
                compressed = decoded
                last_error: zlib.error | None = None
                for window_bits in (zlib.MAX_WBITS, -zlib.MAX_WBITS):
                    try:
                        decompressor = zlib.decompressobj(window_bits)
                        decoded = decompressor.decompress(compressed, MAX_CAPTURE_BYTES + 1)
                        if decompressor.unconsumed_tail:
                            raise ValueError("decoded response exceeds the capture limit")
                        remaining = MAX_CAPTURE_BYTES + 1 - len(decoded)
                        if remaining > 0:
                            decoded += decompressor.flush(remaining)
                        last_error = None
                        break
                    except zlib.error as exc:
                        last_error = exc
                if last_error is not None:
                    raise last_error
            else:
                raise ValueError(f"unsupported HTTP content encoding {encoding}: {url}")
        except (OSError, EOFError, zlib.error) as exc:
            raise ValueError(f"invalid {encoding}-encoded response: {url}") from exc
        if len(decoded) > MAX_CAPTURE_BYTES:
            raise ValueError(f"decoded capture exceeds {MAX_CAPTURE_BYTES} bytes: {url}")
    return decoded


def fetch(url: str) -> tuple[str, str, bytes]:
    _validate_fetch_url(url)
    request = Request(url, headers={"User-Agent": "Agent-Commons-Brand-Resolver/2", "Accept-Encoding": "identity"})
    with urlopen(request, timeout=20) as response:
        final_url = response.geturl()
        _validate_fetch_url(final_url)
        payload = response.read(MAX_CAPTURE_BYTES + 1)
        if len(payload) > MAX_CAPTURE_BYTES:
            raise ValueError(f"capture exceeds {MAX_CAPTURE_BYTES} bytes: {final_url}")
        payload = _decode_http_content(payload, response.headers.get("Content-Encoding", ""), final_url)
        return final_url, media_type(final_url, response.headers.get_content_type()), payload


def capture(url: str, supplied_type: str | None = None) -> tuple[dict[str, str], bytes]:
    final_url, detected_type, payload = fetch(url)
    resolved_type = supplied_type or detected_type
    return {"url": final_url, "media_type": media_type(final_url, resolved_type), "sha256": sha256(payload)}, payload


def _validate_image_bytes(role: str, media: str, payload: bytes) -> None:
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
    compatible = {media, sniffed} <= {"image/x-icon", "image/vnd.microsoft.icon"}
    if sniffed is None or (media != sniffed and not compatible):
        raise ValueError(f"identity.{role}: bytes do not match declared media type {media}")
    if sniffed == "image/svg+xml":
        try:
            text = payload.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"identity.{role}: unsafe SVG encoding") from exc
        if "<svg" not in text.lower():
            raise ValueError(f"identity.{role}: declared SVG is not an SVG document")
        unsafe_patterns = (
            r"<\s*script\b", r"\bon[a-z]+\s*=", r"<\s*foreignobject\b", r"<!\s*(?:doctype|entity)\b",
            r"\b(?:href|src)\s*=\s*['\"]\s*(?!#|data:)[^'\"]+",
            r"url\(\s*['\"]?\s*(?!#|data:)[^)]+",
        )
        if any(re.search(pattern, text, re.I) for pattern in unsafe_patterns):
            raise ValueError(f"identity.{role}: unsafe active or externally referenced SVG content")
        return
    if media not in {"image/png", "image/jpeg", "image/gif", "image/webp", "image/x-icon", "image/vnd.microsoft.icon"}:
        raise ValueError(f"identity.{role}: unsupported image media type {media}")


def asset(role: str, url: str, supplied_type: str | None = None) -> dict[str, str]:
    record, payload = capture(url, supplied_type)
    if not record["media_type"].startswith("image/"):
        raise ValueError(f"identity.{role}: asset did not resolve to an image: {record['media_type']}")
    _validate_image_bytes(role, record["media_type"], payload)
    return {
        "role": role, "source_url": record["url"], "source_kind": "official",
        "media_type": record["media_type"], "sha256": record["sha256"], "target": "embedded",
        "data_uri": f"data:{record['media_type']};base64,{base64.b64encode(payload).decode('ascii')}",
    }


def asset_from_bytes(role: str, source_url: str, media: str, payload: bytes) -> dict[str, str]:
    """Validate and embed bytes already captured from an official HTML document."""
    _validate_image_bytes(role, media, payload)
    return {
        "role": role, "source_url": source_url, "source_kind": "official",
        "media_type": media, "sha256": sha256(payload), "target": "embedded",
        "data_uri": f"data:{media};base64,{base64.b64encode(payload).decode('ascii')}",
    }


def _inline_svg_logo_candidates(html_bytes: bytes, base_url: str) -> list[dict[str, object]]:
    """Return exact, identity-labelled inline SVG fragments without interpreting their artwork."""
    candidates: list[dict[str, object]] = []
    for index, match in enumerate(INLINE_SVG.finditer(html_bytes), start=1):
        fragment = match.group(0)
        opening = fragment[:fragment.find(b">") + 1].decode("utf-8", errors="replace")
        attributes = {name.casefold(): value for name, _, value in HTML_ATTRIBUTE.findall(opening)}
        context = html_bytes[max(0, match.start() - 480):match.start()].decode("utf-8", errors="replace")
        identity = " ".join((context, opening, attributes.get("aria-label", ""), attributes.get("title", ""))).casefold()
        score = identity.count("logo") * 6 + identity.count("wordmark") * 6 + identity.count("brand") * 2
        score += 3 if "header" in identity else 0
        score += 2 if attributes.get("role", "").casefold() == "img" and attributes.get("aria-label") else 0
        if any(term in identity for term in ("facebook", "linkedin", "twitter", "instagram", "youtube", "social")):
            score -= 30
        if score < 5:
            continue
        candidates.append({
            "source_url": f"{base_url}#inline-svg-logo-{index}",
            "media_type": "image/svg+xml", "payload": fragment,
            "alt": attributes.get("aria-label") or attributes.get("title") or "Official brand logo",
            "score": score, "fallback": False,
        })
    return candidates


def normalize_color(value: str) -> str | None:
    value = value.strip().lower()
    if value.startswith("#"):
        digits = value[1:]
        if len(digits) == 3:
            return "#" + "".join(character * 2 for character in digits)
        if len(digits) == 6:
            return value
        if len(digits) == 8 and digits[6:] == "ff":
            return "#" + digits[:6]
        return None
    match = RGB.fullmatch(value)
    if not match or (match.group(4) is not None and float(match.group(4)) != 1.0):
        return None
    channels = [int(match.group(index)) for index in range(1, 4)]
    if any(channel > 255 for channel in channels):
        return None
    return "#" + "".join(f"{channel:02x}" for channel in channels)


def colors_in(value: str) -> list[str]:
    matches: list[tuple[int, str]] = []
    for match in HEX.finditer(value):
        normalized = normalize_color(match.group(0))
        if normalized:
            matches.append((match.start(), normalized))
    for match in RGB.finditer(value):
        normalized = normalize_color(match.group(0))
        if normalized:
            matches.append((match.start(), normalized))
    return [color for _, color in sorted(matches)]


def _selector_matches_visible(selector: str, visible_tokens: set[str]) -> bool:
    normalized_visible = {token.casefold() for token in visible_tokens}
    qualified_tokens = {token.casefold() for token in re.findall(r"[.#][A-Za-z_][\w-]*", selector)}
    if qualified_tokens:
        return bool(qualified_tokens & normalized_visible)
    element_tokens = {token.casefold() for token in re.findall(r"(?:^|[\s>+~,])([A-Za-z][\w-]*)", selector)}
    return bool(element_tokens & normalized_visible)


def _functional_subject_text(selector: str, prop: str) -> str:
    """Limit status semantics to the styled subject, not an unrelated page ancestor."""
    if prop.startswith("--"):
        return prop.casefold()
    subjects: list[str] = []
    for member in selector.split(","):
        expanded = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", member.strip())
        subject = re.split(r"\s+|>", expanded)[-1]
        if subject:
            subjects.append(subject.casefold())
    return " ".join(subjects)


def _functional_term_present(text: str, term: str) -> bool:
    return re.search(rf"(?<![a-z]){re.escape(term)}(?![a-z])", text) is not None


def _semantic_categories(selector: str, prop: str, visible: bool = False) -> set[str]:
    selector_text = f"{selector} {prop if prop.startswith('--') else ''}".casefold()
    categories = {
        name for name, terms in SEMANTIC_TERMS.items()
        if name not in {"danger", "success"} and any(term in selector_text for term in terms)
    }
    functional_subject = _functional_subject_text(selector, prop)
    for name in ("danger", "success"):
        if any(_functional_term_present(functional_subject, term) for term in SEMANTIC_TERMS[name]):
            categories.add(name)
    if re.search(r"(?:^|[\s>+~,])a(?=[:.#\[]|[\s>+~,]|$)", selector_text):
        categories.add("link")
    if re.search(r"(?:^|[\s>+~,])h[1-6](?=[:.#\[]|[\s>+~,]|$)", selector_text):
        categories.add("heading")
    if re.search(r"(?:^|[\s>+~,])body(?=[:.#\[]|[\s>+~,]|$)", selector_text):
        categories.add("body")
    if prop == "color":
        categories.add("text")
    if "background" in prop:
        categories.add("background")
    if "border" in prop or "outline" in prop:
        categories.add("border")
    if "outline" in prop:
        categories.add("focus")
    if re.search(r":(?:active|hover|focus|visited|disabled)\b|\.(?:active|selected|disabled)\b|\[aria-selected", selector_text):
        categories.add("state")
    if "header" in categories and "background" in categories:
        categories.add("header_background")
    if "primary" in categories and "background" in categories and "focus" not in categories:
        categories.add("primary_background")
    if visible:
        categories.add("visible")
    return categories


def _add_color(analysis: CssAnalysis, color: str, selector: str, prop: str, source_url: str, visible: bool = False) -> None:
    evidence = analysis.colors.setdefault(color, ColorEvidence(color))
    categories = _semantic_categories(selector, prop, visible)
    evidence.count += 1
    evidence.categories.update(categories)
    property_role = "token" if prop.startswith("--") else "text" if prop == "color" else "background" if "background" in prop else "border" if "border" in prop or "outline" in prop else "other"
    evidence.role_properties[property_role] += 1
    for category in categories:
        evidence.role_properties[f"{category}:{property_role}"] += 1
    selector_label = re.sub(r"\s+", " ", selector.strip())[:180]
    semantic = ",".join(sorted(categories)) or "unclassified"
    evidence.usages.add(f"{prop} on {selector_label} [semantic:{semantic}]")
    evidence.sources.add(f"{source_url}#{selector_label}[{prop}]")


def _css_logo_candidate(selector: str, prop: str, raw_url: str, source_url: str, visible: bool) -> dict[str, object] | None:
    selector_text = selector.casefold()
    if not any(term in selector_text for term in SEMANTIC_TERMS["logo"]):
        return None
    if re.search(r"::?(?:before|after)\b", selector_text):
        return None
    candidate_url = raw_url.strip()
    if not candidate_url or candidate_url.startswith("#"):
        return None
    score = 18 + (22 if visible else 0)
    if any(term in selector_text for term in ("site-logo", "sitelogo", "brand-logo", "wordmark")):
        score += 18
    if any(term in selector_text for term in ("chatbot", "cookie", "social", "partner", "sponsor")):
        score -= 20
    selector_label = re.sub(r"\s+", " ", selector.strip())[:180]
    evidence_url = f"{source_url}#{selector_label}[{prop}]"
    if candidate_url.casefold().startswith("data:"):
        try:
            header, encoded = candidate_url.split(",", 1)
            media = header[5:].split(";", 1)[0].casefold() or "text/plain"
            payload = base64.b64decode(encoded, validate=True) if ";base64" in header.casefold() else unquote_to_bytes(encoded)
        except (ValueError, binascii.Error):
            return None
        if not media.startswith("image/"):
            return None
        return {
            "source_url": evidence_url, "media_type": media, "payload": payload,
            "alt": "Official brand logo", "score": score, "fallback": False,
        }
    return {
        "source_url": urljoin(source_url, candidate_url), "media_type": None, "payload": None,
        "alt": "Official brand logo", "score": score, "fallback": False,
    }


def _expand_css_value(value: str, properties: dict[str, str], seen: set[str] | None = None) -> str:
    """Resolve ordinary CSS variable references while preserving unknown expressions for later diagnostics."""
    active = set(seen or ())

    def replace(match: re.Match[str]) -> str:
        variable = match.group(1).lower()
        fallback = (match.group(2) or "").strip()
        if variable in active:
            return fallback or match.group(0)
        raw = properties.get(variable)
        if raw is None:
            return fallback or match.group(0)
        return _expand_css_value(raw, properties, active | {variable})

    previous = value
    for _ in range(16):
        expanded = CSS_VARIABLE_REFERENCE.sub(replace, previous)
        if expanded == previous:
            return expanded
        previous = expanded
    return previous


def analyze_css(css_texts: list[tuple[str, str]], visible_tokens: set[str] | None = None) -> CssAnalysis:
    analysis = CssAnalysis()
    visible_tokens = visible_tokens or set()
    cleaned_sources: list[tuple[str, str]] = []
    for source_url, css in css_texts:
        analysis.source_refs.add(source_url)
        cleaned = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
        cleaned_sources.append((source_url, cleaned))
        for name, raw_value in CUSTOM_PROPERTY.findall(cleaned):
            normalized_name = name.lower()
            value = raw_value.strip()
            self_reference = re.fullmatch(
                rf"var\(\s*{re.escape(normalized_name)}(?:\s*,[^)]*)?\s*\)", value, re.I
            )
            if self_reference and normalized_name in analysis.properties:
                # Compiled utility CSS can redeclare a token as var(--same-token)
                # inside a scoped rule. It does not replace the concrete root value.
                continue
            analysis.properties[normalized_name] = value
            analysis.property_sources[normalized_name] = source_url
    for name, value in analysis.properties.items():
        source_url = analysis.property_sources[name]
        for color in colors_in(_expand_css_value(value, analysis.properties, {name})):
            _add_color(analysis, color, ":root", name, source_url)
    for source_url, cleaned in cleaned_sources:
        for selector, body in CSS_RULE.findall(cleaned):
            if selector.lstrip().startswith(("@font-face", "@keyframes", "@-webkit-keyframes")):
                continue
            selector = selector.strip()
            visible = _selector_matches_visible(selector, visible_tokens)
            for prop, double_quoted, single_quoted, unquoted in CSS_IMAGE_DECLARATION.findall(body):
                candidate = _css_logo_candidate(
                    selector, prop.lower(), double_quoted or single_quoted or unquoted, source_url, visible
                )
                if candidate:
                    analysis.logo_candidates.append(candidate)
            for prop, raw_value in CSS_DECLARATION.findall(body):
                prop = prop.lower()
                if prop.startswith("--"):
                    continue
                value = _expand_css_value(raw_value.strip(), analysis.properties)
                for color in colors_in(value):
                    _add_color(analysis, color, selector, prop, source_url, visible)
                if prop == "font-family" and re.fullmatch(r"[A-Za-z0-9 ,.'\"!-]+", value):
                    analysis.fonts.append((value.replace("!important", "").strip(), selector, source_url))
                if prop == "border-radius":
                    analysis.radii.extend((length.lower(), selector, source_url) for length in CSS_LENGTH_VALUE.findall(value))
                if prop == "border-width" or (prop.startswith("border") and prop != "border-radius"):
                    analysis.border_widths.extend((length.lower(), selector, source_url) for length in CSS_LENGTH_VALUE.findall(value))
    return analysis


def _resolve_variable(properties: dict[str, str], variable: str, seen: set[str] | None = None) -> str | None:
    raw = properties.get(variable)
    if raw is None:
        return None
    seen = set(seen or ())
    if variable in seen:
        return None
    seen.add(variable)
    match = re.fullmatch(r"var\(\s*(--[\w-]+)(?:\s*,[^)]*)?\s*\)", raw.strip())
    return _resolve_variable(properties, match.group(1).lower(), seen) if match else raw.strip()


def _variable_source(analysis: CssAnalysis, variable: str, seen: set[str] | None = None) -> str | None:
    raw = analysis.properties.get(variable)
    if raw is None:
        return None
    seen = set(seen or ())
    if variable in seen:
        return None
    seen.add(variable)
    match = re.fullmatch(r"var\(\s*(--[\w-]+)(?:\s*,[^)]*)?\s*\)", raw.strip())
    if match:
        return _variable_source(analysis, match.group(1).lower(), seen) or analysis.property_sources.get(variable)
    return analysis.property_sources.get(variable)


def _rgb_tuple(color: str) -> tuple[int, int, int]:
    return tuple(int(color[index:index + 2], 16) for index in (1, 3, 5))  # type: ignore[return-value]


def _luminance(color: str) -> float:
    channels = []
    for channel in _rgb_tuple(color):
        value = channel / 255
        channels.append(value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def _contrast(first: str, second: str) -> float:
    light, dark = sorted((_luminance(first), _luminance(second)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def _hls(color: str) -> tuple[float, float, float]:
    red, green, blue = (channel / 255 for channel in _rgb_tuple(color))
    return colorsys.rgb_to_hls(red, green, blue)


def _color_distance(first: str, second: str) -> float:
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(_rgb_tuple(first), _rgb_tuple(second))))


def _mix(foreground: str, background: str, foreground_ratio: float) -> str:
    mixed = [round(a * foreground_ratio + b * (1 - foreground_ratio)) for a, b in zip(_rgb_tuple(foreground), _rgb_tuple(background))]
    return "#" + "".join(f"{channel:02x}" for channel in mixed)


def _accessible_variant(color: str, surface: str, target_ratio: float) -> str:
    """Minimally adjust an evidenced color toward black or white until it is safe for text/focus use."""
    if _contrast(color, surface) >= target_ratio:
        return color
    target = "#000000" if _luminance(surface) >= 0.45 else "#ffffff"
    for percentage in range(1, 101):
        candidate = _mix(target, color, percentage / 100)
        if _contrast(candidate, surface) >= target_ratio:
            return candidate
    return target


def _rank_colors(analysis: CssAnalysis, scorer: Callable[[ColorEvidence], float], exclude: set[str] | None = None) -> list[tuple[float, ColorEvidence]]:
    excluded = exclude or set()
    ranked = [(float(scorer(item)), item) for value, item in analysis.colors.items() if value not in excluded]
    return sorted((entry for entry in ranked if entry[0] > 0), key=lambda entry: (-entry[0], -entry[1].count, entry[1].value))


def _choose(analysis: CssAnalysis, scorer: Callable[[ColorEvidence], float], exclude: set[str] | None = None) -> ColorEvidence | None:
    ranked = _rank_colors(analysis, scorer, exclude)
    return ranked[0][1] if ranked else None


def _category(item: ColorEvidence, name: str) -> int:
    return item.categories[name]


def _role_use(item: ColorEvidence, semantic_role: str, property_role: str) -> int:
    return item.role_properties[f"{semantic_role}:{property_role}"]


def _hue_distance(first: str, second: str) -> float:
    difference = abs(_hls(first)[0] - _hls(second)[0])
    return min(difference, 1 - difference)


def _semantic_palette(analysis: CssAnalysis) -> tuple[dict[str, str], list[dict[str, object]], dict[str, dict[str, str]], list[str]]:
    diagnostics: list[str] = []
    decisions: dict[str, dict[str, str]] = {}
    chosen: dict[str, str] = {}
    derived_tokens: list[dict[str, object]] = []

    def record(key: str, item: ColorEvidence | None, reason: str, confidence: str = "high") -> None:
        if item is None:
            diagnostics.append(f"theme.colors.{key}: missing {reason}")
            return
        chosen[key] = item.value
        decisions[f"theme.colors.{key}"] = {
            "decision": "observed", "confidence": confidence, "rationale": reason,
            "source_ref": sorted(item.sources)[0],
        }

    def derive(key: str, value: str, parents: list[str], reason: str, source_ref: str, confidence: str = "medium") -> None:
        chosen[key] = value
        decisions[f"theme.colors.{key}"] = {
            "decision": "derived", "confidence": confidence, "rationale": reason, "source_ref": source_ref,
        }
        derived_tokens.append({
            "token": f"theme.colors.{key}", "value": value,
            "derived_from": list(dict.fromkeys(parents)), "method": reason,
            "confidence": confidence, "evidence_ids": ["BRAND-EVID-CSS-SEMANTIC"],
        })

    risk = _choose(
        analysis,
        lambda item: (_category(item, "danger") * 50 + item.count + 10)
        if _category(item, "danger") and (_hls(item.value)[0] < 0.08 or _hls(item.value)[0] > 0.94) and _hls(item.value)[2] >= 0.25 else 0,
    )
    good = _choose(
        analysis,
        lambda item: (_category(item, "success") * 50 + item.count + 8)
        if _category(item, "success") and 0.18 < _hls(item.value)[0] < 0.48 and _hls(item.value)[2] >= 0.18 else 0,
    )
    focus = _choose(
        analysis,
        lambda item: (
            _role_use(item, "focus", "border") * 80
            + _role_use(item, "focus", "background") * 30
            + _role_use(item, "focus", "text") * 20
            + _role_use(item, "focus", "token") * 15
            + min(item.count, 20)
        ) if _category(item, "focus") else 0,
    )
    header = _choose(
        analysis,
        lambda item: (
            _role_use(item, "header", "background") * 120
            + _role_use(item, "primary", "background") * 35
            + _role_use(item, "header", "token") * 25
            + min(item.count, 20)
            + (1 - _luminance(item.value)) * 10
        ) if (
            item.role_properties["background"]
            and (_role_use(item, "header", "background") or _role_use(item, "primary", "background"))
            and _luminance(item.value) < 0.5
        ) else 0,
        {risk.value} if risk else set(),
    )
    def accent_score(item: ColorEvidence, allow_near_white: bool = False) -> float:
        if not allow_near_white and _luminance(item.value) > 0.92:
            return 0
        interface_use = (
            _role_use(item, "primary", "background")
            + _role_use(item, "button", "background")
            + _role_use(item, "link", "text")
            + _role_use(item, "primary", "border")
            + _role_use(item, "primary", "token")
        )
        if not interface_use:
            return 0
        return (
            _role_use(item, "primary", "background") * 90
            + _role_use(item, "button", "background") * 45
            + _role_use(item, "primary", "token") * 35
            + min(_role_use(item, "link", "text"), 6) * 20
            + _role_use(item, "primary", "border") * 12
            + _role_use(item, "visible", "background") * 8
            + min(item.count, 500)
            + _hls(item.value)[2] * 10
            - _role_use(item, "state", "background") * 15
            - _category(item, "danger") * 120
            - _category(item, "success") * 60
            - _role_use(item, "logo", "token") * 100
        )

    excluded_primary = {value for value in (risk.value if risk else None, good.value if good else None) if value}
    accent = _choose(analysis, accent_score, excluded_primary)
    if accent is None:
        accent = _choose(analysis, lambda item: accent_score(item, allow_near_white=True), excluded_primary)
    link = _choose(
        analysis,
        lambda item: (
            _role_use(item, "link", "text") * 70
            + _role_use(item, "visible", "text") * 5
            + _role_use(item, "link", "token") * 20
            + min(item.count, 20)
        ) if _role_use(item, "link", "text") or _role_use(item, "link", "token") else 0,
        {risk.value} if risk else set(),
    )
    excluded_secondary = {value for value in (accent.value if accent else None, header.value if header else None, risk.value if risk else None, good.value if good else None) if value}
    secondary = _choose(
        analysis,
        lambda item: (
            _role_use(item, "link", "text") * 22
            + _role_use(item, "primary", "background") * 16
            + _role_use(item, "primary", "token") * 14
            + _role_use(item, "heading", "text") * 12
            + _role_use(item, "header", "background") * 5
            + min(item.count, 24) + _hls(item.value)[2] * 6
            - _category(item, "danger") * 100 - _category(item, "success") * 40
        ) if _hls(item.value)[2] > 0.15 or _luminance(item.value) < 0.12 else 0,
        excluded_secondary,
    )
    ink = _choose(
        analysis,
        lambda item: (
            _role_use(item, "body", "text") * 160
            + _role_use(item, "heading", "text") * 35
            + item.role_properties["text"] * 10
            + _role_use(item, "visible", "text") * 6
            + min(item.count, 30)
            + (1 - _luminance(item.value)) * 24
            - _role_use(item, "button", "text") * 8
            - _category(item, "danger") * 100
            - _category(item, "success") * 60
        ) if item.role_properties["text"] and _luminance(item.value) < 0.55 else 0,
        {value for value in (accent.value if accent else None, risk.value if risk else None, good.value if good else None) if value},
    )
    surface = _choose(
        analysis,
        lambda item: (
            _role_use(item, "body", "background") * 160
            + _role_use(item, "card", "background") * 20
            + item.role_properties["background"] * 9
            + _role_use(item, "background", "token") * 5
            + min(item.count, 25)
            + _luminance(item.value) * 30
            - _role_use(item, "primary", "background") * 25
            - _role_use(item, "danger", "background") * 40
            - _role_use(item, "success", "background") * 25
        ) if (
            (item.role_properties["background"] or _role_use(item, "background", "token"))
            and _luminance(item.value) > 0.65
            and (_hls(item.value)[2] < 0.35 or _luminance(item.value) > 0.92)
        ) else 0,
    )
    if surface is None:
        surface = _choose(
            analysis,
            lambda item: item.role_properties["background"] * 8 + min(item.count, 20) + _luminance(item.value) * 20
            if item.role_properties["background"] and _luminance(item.value) > 0.65 else 0,
        )
    paper = _choose(
        analysis,
        lambda item: _role_use(item, "body", "background") * 80 + item.role_properties["background"] * 4 + _luminance(item.value) * 20
        if _role_use(item, "body", "background") and _luminance(item.value) > 0.65 else 0,
    )
    card = _choose(
        analysis,
        lambda item: _role_use(item, "card", "background") * 45 + item.role_properties["background"] * 5 + _luminance(item.value) * 20
        if (
            _role_use(item, "card", "background")
            and _luminance(item.value) > 0.60
            and (_hls(item.value)[2] < 0.40 or _luminance(item.value) > 0.92)
        ) else 0,
    )
    muted = _choose(
        analysis,
        lambda item: (
            _role_use(item, "muted", "text") * 70
            + item.role_properties["text"] * 8
            + _role_use(item, "visible", "text") * 4
            + min(item.count, 15)
            + (10 if _hls(item.value)[2] < 0.30 else 0)
        ) if (
            item.role_properties["text"]
            and 0.04 < _luminance(item.value) < 0.7
            and (_role_use(item, "muted", "text") or _hls(item.value)[2] < 0.30)
        ) else 0,
        {value for value in (accent.value if accent else None, risk.value if risk else None, good.value if good else None, ink.value if ink else None) if value},
    )
    line = _choose(
        analysis,
        lambda item: (item.role_properties["border"] * 12 + min(item.count, 16) + 12 - _hls(item.value)[2] * 20)
        if item.role_properties["border"] and 0.45 < _luminance(item.value) < 0.95 and _hls(item.value)[2] < 0.5 else 0,
        {value for value in (accent.value if accent else None, risk.value if risk else None, good.value if good else None) if value},
    )

    core_missing = []
    if accent is None:
        core_missing.append("theme.colors.accent: missing an exact non-danger color used for primary controls, navigation, or links")
    if ink is None:
        core_missing.append("theme.colors.ink: missing an exact dark color used for body or interface text")
    if not (surface or paper or card):
        core_missing.append("theme.colors.surface: missing an exact page, card, or panel background color")
    if core_missing:
        return {}, [], decisions, core_missing

    surface_from_background = surface is None
    surface = surface or paper or card
    paper_from_surface = paper is None
    paper = paper or surface
    card_from_surface = card is None
    card = card or surface
    header_from_accent = header is None
    header = header or accent
    link_from_accent = link is None
    link = link or accent
    secondary_from_core = secondary is None
    secondary = secondary or link or header or accent
    muted_from_ink = muted is None
    muted = muted or ink
    focus_from_core = focus is None
    focus = focus or header or accent

    text_surface = surface.value if surface else paper.value if paper else card.value if card else "#ffffff"
    link_reason = "an exact link color" if not link_from_accent else "observed primary interface color reused for links"
    link_confidence = "high" if not link_from_accent else "medium"
    if link and _contrast(link.value, text_surface) < 4.5:
        accessible_link = _choose(
            analysis,
            lambda item: (
                _role_use(item, "link", "text") * 80
                + _role_use(item, "visible", "text") * 6
                + min(item.count, 20)
            ) if (
                item.value != link.value
                and _role_use(item, "link", "text")
                and _contrast(item.value, text_surface) >= 4.5
                and not _category(item, "danger")
            ) else 0,
            {risk.value} if risk else set(),
        )
        if accessible_link:
            link = accessible_link
            link_reason = "an exact accessible color used by visible link selectors"
            link_confidence = "medium"
    focus_reason = "an exact focus color" if not focus_from_core else "observed core interface color reused for focus"
    focus_confidence = "high" if not focus_from_core else "medium"
    if focus and _contrast(focus.value, text_surface) < 3.0:
        accessible_focus = _choose(
            analysis,
            lambda item: (
                _role_use(item, "focus", "border") * 80
                + _role_use(item, "focus", "background") * 35
                + _role_use(item, "primary", "border") * 15
                + min(item.count, 20)
            ) if (
                item.value != focus.value
                and (_category(item, "focus") or _category(item, "primary"))
                and _contrast(item.value, text_surface) >= 3.0
                and not _category(item, "danger")
            ) else 0,
            {risk.value} if risk else set(),
        )
        if accessible_focus:
            focus = accessible_focus
            focus_reason = "an exact accessible focus or primary boundary color"
            focus_confidence = "medium"
    risk_original = risk
    good_original = good
    good_reason = "an exact color used by success, valid, positive, or confirmation selectors"
    good_confidence = "high"
    if good and _contrast(good.value, text_surface) < 4.5:
        accessible_green = _choose(
            analysis,
            lambda item: (
                35 - _hue_distance(item.value, good.value) * 180 + min(item.count, 12)
                + _category(item, "success") * 20 + _category(item, "text") * 4
            ) if (
                item.value != good.value
                and _hue_distance(item.value, good.value) <= 0.15
                and _contrast(item.value, text_surface) >= 4.5
                and not _category(item, "danger")
                and (_category(item, "background") or _category(item, "border") or _category(item, "text"))
            ) else 0,
        )
        if accessible_green:
            good = accessible_green
            good_reason = "an exact accessible official green nearest the observed success color"
            good_confidence = "medium"
    risk_reason = "an exact color used by danger, error, invalid, or critical selectors"
    risk_confidence = "high"
    if risk and _contrast(risk.value, text_surface) < 4.5:
        accessible_red = _choose(
            analysis,
            lambda item: (
                35 - _hue_distance(item.value, risk.value) * 180 + min(item.count, 12)
                + _category(item, "danger") * 20 + _category(item, "text") * 4
            ) if (
                item.value != risk.value
                and _hue_distance(item.value, risk.value) <= 0.10
                and _hls(item.value)[2] >= 0.25
                and _contrast(item.value, text_surface) >= 4.5
                and not _category(item, "success")
                and (_category(item, "background") or _category(item, "border") or _category(item, "text"))
            ) else 0,
        )
        if accessible_red:
            risk = accessible_red
            risk_reason = "an exact accessible official red nearest the observed danger color"
            risk_confidence = "medium"
    if muted and _contrast(muted.value, text_surface) < 4.5:
        accessible_muted = _choose(
            analysis,
            lambda item: (
                _category(item, "muted") * 40 + _category(item, "text") * 12
                + _category(item, "heading") * 4 + min(item.count, 20)
            ) if (
                item.value != (ink.value if ink else None)
                and _hls(item.value)[2] <= 0.30
                and 0.12 <= _luminance(item.value) < 0.35
                and _contrast(item.value, text_surface) >= 4.5
                and not _category(item, "danger")
            ) else 0,
            {value for value in (accent.value if accent else None, risk.value if risk else None, good.value if good else None, ink.value if ink else None) if value},
        )
        muted = accessible_muted or ink
        muted_from_ink = accessible_muted is None

    if risk_original and risk and _contrast(risk.value, text_surface) < 4.5:
        chosen["risk"] = _accessible_variant(risk.value, text_surface, 4.5)
        decisions["theme.colors.risk"] = {
            "decision": "derived", "confidence": "medium",
            "rationale": "lightness-adjusted from the observed danger color only far enough to meet 4.5:1 against the observed surface; the exact original remains recorded as observed evidence",
            "source_ref": sorted(risk_original.sources)[0],
        }
        derived_tokens.append({
            "token": "theme.colors.risk", "value": chosen["risk"],
            "derived_from": list(dict.fromkeys((risk_original.value, text_surface))),
            "method": decisions["theme.colors.risk"]["rationale"], "confidence": "medium",
            "evidence_ids": ["BRAND-EVID-CSS-SEMANTIC"],
        })
    elif risk is not None:
        record("risk", risk if risk and (_category(risk, "danger") or risk is not risk_original) else None, risk_reason, risk_confidence)
    else:
        derive(
            "risk", _accessible_variant("#b42318", text_surface, 4.5), [ink.value, surface.value],
            "accessible standard danger color supplied only because the website exposed no optional danger role; core client colors remain independently evidenced",
            sorted(surface.sources)[0], "low",
        )
    if good_original and good and _contrast(good.value, text_surface) < 4.5:
        chosen["good"] = _accessible_variant(good.value, text_surface, 4.5)
        decisions["theme.colors.good"] = {
            "decision": "derived", "confidence": "medium",
            "rationale": "lightness-adjusted from the observed success color only far enough to meet 4.5:1 against the observed surface; the exact original remains recorded as observed evidence",
            "source_ref": sorted(good_original.sources)[0],
        }
        derived_tokens.append({
            "token": "theme.colors.good", "value": chosen["good"],
            "derived_from": list(dict.fromkeys((good_original.value, text_surface))),
            "method": decisions["theme.colors.good"]["rationale"], "confidence": "medium",
            "evidence_ids": ["BRAND-EVID-CSS-SEMANTIC"],
        })
    elif good is not None:
        record("good", good, good_reason, good_confidence)
    else:
        derive(
            "good", _accessible_variant("#067647", text_surface, 4.5), [ink.value, surface.value],
            "accessible standard success color supplied only because the website exposed no optional success role; core client colors remain independently evidenced",
            sorted(surface.sources)[0], "low",
        )
    record("focus", focus, focus_reason, focus_confidence)
    record("header", header, "an exact header or navigation background" if not header_from_accent else "observed primary interface color reused for the header", "high" if not header_from_accent else "medium")
    record("accent", accent if accent and any(_category(accent, role) for role in ("primary", "button", "link", "header_background")) else None, "an exact non-danger color used for primary controls, navigation, or links")
    record("link", link, link_reason, link_confidence)
    record("secondary", secondary, "a distinct, repeatedly used secondary interface accent" if not secondary_from_core else "observed core interface accent reused for the secondary role", "medium")
    record("ink", ink if ink and _category(ink, "text") else None, "an exact dark color used for body or interface text")
    record("surface", surface, "an exact light background used by cards, panels, or page surfaces", "medium" if surface_from_background else "high")
    record("paper", paper, "an exact page background color" if not paper_from_surface else "observed interface surface reused as the page background", "medium" if paper_from_surface else "high")
    record("card", card, "an exact card or panel surface" if not card_from_surface else "observed interface surface reused for cards", "medium" if card_from_surface or not _category(card, "card") else "high")
    record("muted", muted, "an exact restrained text or metadata color" if not muted_from_ink else "observed body text color reused where no separate muted color was exposed", "medium")
    if line and _category(line, "border"):
        record("line", line, "an exact neutral border color")
    else:
        derive(
            "line", _mix(ink.value, surface.value, 0.20), [ink.value, surface.value],
            "20 percent sRGB mix of observed text over the observed surface because no separate border color was exposed",
            sorted(surface.sources)[0], "medium",
        )

    if risk and accent and risk.value == accent.value:
        diagnostics.append("theme.colors.accent: danger color cannot be the global primary color")
    if accent and _category(accent, "logo") and not any(_category(accent, role) for role in ("primary", "button", "link", "header")):
        diagnostics.append("theme.colors.accent: logo-only color lacks independent interface usage")
    if surface and ink and _contrast(surface.value, ink.value) < 4.5:
        diagnostics.append("theme.colors.ink: observed text and surface colors do not meet 4.5:1 contrast")
    for role, item in (("muted", muted),):
        if item and surface and _contrast(item.value, surface.value) < 4.5:
            diagnostics.append(f"theme.colors.{role}: observed color does not meet 4.5:1 contrast against the surface")
    if diagnostics:
        return {}, [], decisions, diagnostics

    chosen["ink_subtle"] = chosen["muted"]
    decisions["theme.colors.ink_subtle"] = {**decisions["theme.colors.muted"], "rationale": "observed restrained text color reused for secondary text"}
    chosen["surface_subtle"] = chosen["paper"]
    decisions["theme.colors.surface_subtle"] = {**decisions["theme.colors.paper"], "confidence": "medium", "rationale": "observed page surface reused for subtle regions"}
    light_candidates = [
        item for item in analysis.colors.values()
        if _luminance(item.value) > 0.65
        and item.value not in {chosen["surface"], chosen["paper"], chosen["card"]}
        and (_category(item, "background") or _category(item, "card"))
        and (_hue_distance(item.value, chosen["accent"]) <= 0.15 or _hls(item.value)[2] < 0.08)
    ]
    accent_soft_item = min(light_candidates, key=lambda item: (_color_distance(item.value, chosen["accent"]), item.value)) if light_candidates else None
    if accent_soft_item:
        record("accent_soft", accent_soft_item, "an observed light surface nearest the primary accent", "medium")
    else:
        chosen["accent_soft"] = _mix(chosen["accent"], chosen["surface"], 0.12)
        decisions["theme.colors.accent_soft"] = {"decision": "derived", "confidence": "medium", "rationale": "12 percent sRGB mix of the observed accent over the observed surface", "source_ref": decisions["theme.colors.accent"]["source_ref"]}
    risk_soft_parent = risk_original.value if risk_original else chosen["risk"]
    chosen["risk_soft"] = _mix(risk_soft_parent, chosen["surface"], 0.10)
    risk_soft_reason = (
        "10 percent sRGB mix of the exact observed danger color over the observed surface"
        if risk_original
        else "10 percent sRGB mix of the explicit low-confidence functional danger fallback over the observed surface"
    )
    decisions["theme.colors.risk_soft"] = {"decision": "derived", "confidence": "medium" if risk_original else "low", "rationale": risk_soft_reason, "source_ref": decisions["theme.colors.risk"]["source_ref"]}
    chosen["line_strong"] = chosen["muted"] if _contrast(chosen["muted"], chosen["surface"]) >= 2 else chosen["line"]
    decisions["theme.colors.line_strong"] = {**decisions["theme.colors.muted" if chosen["line_strong"] == chosen["muted"] else "theme.colors.line"], "confidence": "medium", "rationale": "observed stronger neutral boundary color"}
    on_dark = _choose(
        analysis,
        lambda item: (
            _category(item, "text") * 8
            + (_category(item, "header") + _category(item, "button")) * 6
            + min(item.count, 20)
            + 30
        ) if (
            _category(item, "text")
            and _contrast(item.value, chosen["header"]) >= 4.5
            and _contrast(item.value, chosen["accent"]) >= 4.5
        ) else 0,
    )
    if on_dark:
        record("on_dark", on_dark, "an exact foreground with accessible contrast on the observed header and primary fills")
    else:
        foreground = max(
            ("#ffffff", "#000000"),
            key=lambda candidate: min(_contrast(candidate, chosen["header"]), _contrast(candidate, chosen["accent"])),
        )
        if min(_contrast(foreground, chosen["header"]), _contrast(foreground, chosen["accent"])) < 4.5:
            chosen["header"] = chosen["accent"]
            decisions["theme.colors.header"] = {
                **decisions["theme.colors.accent"],
                "confidence": "medium",
                "rationale": "observed primary fill reused for the header because version 2 requires one accessible foreground across both branded fills",
            }
            foreground = "#ffffff" if _contrast("#ffffff", chosen["accent"]) >= 4.5 else "#000000"
        derive(
            "on_dark", foreground, [chosen["header"], chosen["accent"], chosen["surface"]],
            "black or white foreground selected deterministically for accessible contrast across the emitted header and primary fills",
            decisions["theme.colors.header"]["source_ref"], "medium",
        )
    if diagnostics:
        return {}, [], decisions, diagnostics

    for token in ("theme.colors.accent_soft", "theme.colors.risk_soft"):
        decision = decisions[token]
        if decision["decision"] != "derived":
            continue
        key = token.rsplit(".", 1)[-1]
        parent_values = (
            [chosen["accent"], chosen["surface"]]
            if key == "accent_soft"
            else ([risk_soft_parent, chosen["surface"]] if risk_original else [ink.value, surface.value])
        )
        derived_tokens.append({
            "token": token, "value": chosen[key], "derived_from": list(dict.fromkeys(parent_values)),
            "method": decision["rationale"], "confidence": decision["confidence"], "evidence_ids": ["BRAND-EVID-CSS-SEMANTIC"],
        })
    return chosen, derived_tokens, decisions, []


def _normalize_font_stack(value: str) -> str:
    names = [part.strip().strip("'\"") for part in value.split(",") if part.strip()]
    normalized: list[str] = []
    for name in names:
        lowered = name.casefold()
        if lowered in {"font-awesome", "amslaborant"} or any(term in lowered for term in ("icon", "glyph", "symbol")):
            continue
        if name.casefold() == "roboto-condensed":
            name = "Roboto Condensed"
        if name not in normalized:
            normalized.append(name)
    if not normalized:
        return ""
    if not any(name.casefold() in {"sans-serif", "serif", "monospace"} for name in normalized):
        normalized.extend(["Arial", "sans-serif"])
    return ", ".join(normalized)


def _semantic_typography(analysis: CssAnalysis) -> tuple[dict[str, str], dict[str, dict[str, str]], list[str]]:
    candidates = [
        (_normalize_font_stack(value), selector, source) for value, selector, source in analysis.fonts
        if not any(term in selector.casefold() for term in ("icon", "glyph", "symbol"))
    ]
    candidates = [entry for entry in candidates if entry[0]]
    if not candidates:
        source = sorted(analysis.source_refs)[0]
        values = {
            "display": "Arial, sans-serif", "body": "Arial, sans-serif", "data": "Courier New, monospace",
        }
        decisions = {
            f"theme.typography.{key}": {
                "decision": "derived", "confidence": "low",
                "rationale": "safe local fallback selected because the website exposed no usable font-family declaration",
                "source_ref": source,
            }
            for key in values
        }
        return values, decisions, []
    body_counts = Counter(value for value, selector, _ in candidates if "body" in selector.casefold()) or Counter(value for value, _, _ in candidates)
    display_counts = Counter(value for value, selector, _ in candidates if re.search(r"(?:^|[\s>+~,])h[1-6](?=[:.#\[]|[\s>+~,]|$)|heading|title|hero", selector.casefold()))
    display_pool = display_counts or body_counts
    display = sorted(display_pool, key=lambda value: ("condensed" not in value.casefold(), -display_pool[value], value))[0]
    body = sorted(body_counts, key=lambda value: (-body_counts[value], value))[0]
    data_counts = Counter(value for value, selector, _ in candidates if re.search(r"code|pre|data|metric|number", selector.casefold()))
    data = sorted(data_counts, key=lambda value: (-data_counts[value], value))[0] if data_counts else body
    values = {"display": display, "body": body, "data": data}
    decisions: dict[str, dict[str, str]] = {}
    for key, value in values.items():
        source = next(source for candidate, _, source in candidates if candidate == value)
        observed = key != "data" or bool(data_counts)
        decisions[f"theme.typography.{key}"] = {
            "decision": "observed" if observed else "derived", "confidence": "high" if observed else "medium",
            "rationale": "safe local font stack selected from observed semantic CSS usage" if observed else "observed body stack reused for data labels because no separate data face was evidenced",
            "source_ref": source,
        }
    return values, decisions, []


def _numeric_length(value: str) -> float:
    return float(re.match(r"[0-9.]+", value).group(0))  # type: ignore[union-attr]


def _semantic_geometry(analysis: CssAnalysis) -> tuple[dict[str, str], dict[str, dict[str, str]], dict[str, str], list[str]]:
    radii = [(value, selector, source) for value, selector, source in analysis.radii if _numeric_length(value) <= 12]
    borders = [(value, selector, source) for value, selector, source in analysis.border_widths if 0 < _numeric_length(value) <= 4]
    source = sorted(analysis.source_refs)[0]
    radius_counts = Counter(value for value, _, _ in radii)
    border_counts = Counter(value for value, _, _ in borders)
    radius = sorted(radius_counts, key=lambda value: (-radius_counts[value], _numeric_length(value), value))[0] if radii else "0px"
    border_width = sorted(border_counts, key=lambda value: (-border_counts[value], _numeric_length(value), value))[0] if borders else "1px"
    signature_candidates = [entry for entry in borders if any(term in entry[1].casefold() for term in ("message", "section", "signature", "active"))]
    signature_thickness = max(signature_candidates, key=lambda entry: (_numeric_length(entry[0]), entry[0]))[0] if signature_candidates else border_width
    geometry = {"radius": radius, "border_width": border_width}
    decisions: dict[str, dict[str, str]] = {}
    for key, value in geometry.items():
        evidence = radii if key == "radius" else borders
        observed = bool(evidence)
        value_source = next((item_source for candidate, _, item_source in evidence if candidate == value), source)
        decisions[f"theme.geometry.{key}"] = {
            "decision": "observed" if observed else "derived", "confidence": "high" if observed else "low",
            "rationale": f"representative restrained {key.replace('_', ' ')} selected from observed CSS" if observed else f"restrained {key.replace('_', ' ')} fallback selected because no usable declaration was exposed",
            "source_ref": value_source,
        }
    signature = {"style": "rule", "thickness": signature_thickness}
    signature_source = next((item_source for value, _, item_source in borders if value == signature_thickness), source)
    decisions["theme.signature.style"] = {"decision": "derived", "confidence": "medium", "rationale": "restrained rule treatment derived from observed border usage", "source_ref": signature_source}
    decisions["theme.signature.thickness"] = {
        "decision": "observed" if borders else "derived", "confidence": "high" if borders else "low",
        "rationale": "exact semantic border thickness reused for the signature rule" if borders else "restrained fallback thickness reused for the signature rule",
        "source_ref": signature_source,
    }
    return geometry, decisions, signature, []


def _observed_colors(analysis: CssAnalysis) -> list[dict[str, object]]:
    return [{"value": item.value, "usages": sorted(item.usages)[:16], "source_ref": sorted(item.sources)[0], "frequency": item.count, "confidence": "high"} for item in sorted(analysis.colors.values(), key=lambda entry: entry.value)]


def _custom_property_profile(analysis: CssAnalysis, source_ref: str) -> tuple[dict[str, object], list[dict[str, object]], dict[str, dict[str, str]], list[str]]:
    missing: list[str] = []
    colors: dict[str, str] = {}
    typography: dict[str, str] = {}
    geometry: dict[str, str] = {}
    decisions: dict[str, dict[str, str]] = {}
    for group, variables, output in (("colors", COLOR_VARIABLES, colors), ("typography", TYPOGRAPHY_VARIABLES, typography), ("geometry", GEOMETRY_VARIABLES, geometry)):
        for key, variable in variables.items():
            value = _resolve_variable(analysis.properties, variable)
            if not value:
                missing.append(f"theme.{group}.{key}: missing official CSS custom property {variable}")
                continue
            if group == "colors":
                normalized = normalize_color(value)
                if not normalized:
                    missing.append(f"theme.colors.{key}: {variable} is not an exact opaque color")
                    continue
                value = normalized
            output[key] = value
            decisions[f"theme.{group}.{key}"] = {"decision": "observed", "confidence": "high", "rationale": f"exact official CSS custom property {variable}", "source_ref": _variable_source(analysis, variable) or source_ref}
    thickness = _resolve_variable(analysis.properties, "--brand-signature-thickness")
    if not thickness:
        missing.append("theme.signature.thickness: missing official CSS custom property --brand-signature-thickness")
    if missing:
        return {}, [], decisions, missing
    theme = {"colors": colors, "typography": typography, "geometry": geometry, "signature": {"style": "rule", "color": colors["secondary"], "thickness": thickness}}
    thickness_source = _variable_source(analysis, "--brand-signature-thickness") or source_ref
    decisions["theme.signature.style"] = {"decision": "derived", "confidence": "high", "rationale": "rule treatment is explicitly encoded by the official signature thickness token", "source_ref": thickness_source}
    decisions["theme.signature.color"] = {**decisions["theme.colors.secondary"], "rationale": "official secondary color reused for the signature rule"}
    decisions["theme.signature.thickness"] = {"decision": "observed", "confidence": "high", "rationale": "exact official CSS custom property --brand-signature-thickness", "source_ref": thickness_source}
    return theme, [], decisions, []


def _semantic_theme(analysis: CssAnalysis) -> tuple[dict[str, object], list[dict[str, object]], dict[str, dict[str, str]], list[str]]:
    colors, derived, color_decisions, color_diagnostics = _semantic_palette(analysis)
    typography, typography_decisions, typography_diagnostics = _semantic_typography(analysis)
    geometry, geometry_decisions, signature, geometry_diagnostics = _semantic_geometry(analysis)
    diagnostics = color_diagnostics + typography_diagnostics + geometry_diagnostics
    if diagnostics:
        return {}, [], {**color_decisions, **typography_decisions, **geometry_decisions}, diagnostics
    signature["color"] = colors["secondary"]
    signature_decisions = {"theme.signature.color": {"decision": "observed", "confidence": "medium", "rationale": "observed secondary interface accent selected for the restrained signature rule", "source_ref": color_decisions["theme.colors.secondary"]["source_ref"]}}
    return {"colors": colors, "typography": typography, "geometry": geometry, "signature": signature}, derived, {**color_decisions, **typography_decisions, **geometry_decisions, **signature_decisions}, []


def _apply_optional_accessibility(
    theme: dict[str, object],
    derived_tokens: list[dict[str, object]],
    decisions: dict[str, dict[str, str]],
) -> None:
    """Remap evidenced functional colors to accessible rendered roles without losing the originals."""
    colors = theme.get("colors")
    if not isinstance(colors, dict) or not isinstance(colors.get("surface"), str):
        return
    surface = str(colors["surface"])
    existing = {str(item.get("token")) for item in derived_tokens}
    for key, ratio, label in (
        ("risk", 4.5, "danger"),
        ("good", 4.5, "success"),
        ("focus", 3.0, "focus"),
        ("link", 4.5, "link"),
    ):
        original = colors.get(key)
        token = f"theme.colors.{key}"
        if not isinstance(original, str) or _contrast(original, surface) >= ratio or token in existing:
            continue
        replacement = _accessible_variant(original, surface, ratio)
        prior = decisions[token]
        rationale = (
            f"lightness-adjusted from the exact observed {label} color only far enough to meet "
            f"{ratio:g}:1 against the observed surface; the original remains in observed evidence"
        )
        colors[key] = replacement
        decisions[token] = {**prior, "decision": "derived", "confidence": "medium", "rationale": rationale}
        derived_tokens.append({
            "token": token, "value": replacement, "derived_from": list(dict.fromkeys((original, surface))),
            "method": rationale, "confidence": "medium", "evidence_ids": ["BRAND-EVID-CSS-SEMANTIC"],
        })


def _select_favicon(parser: DiscoveryParser, base_url: str, manifest_payload: dict[str, object], manifest_url: str | None) -> list[tuple[str, str | None]]:
    candidates: list[tuple[int, str, str | None]] = []
    for icon in parser.icons:
        media = icon.get("type") or None
        sizes = icon.get("sizes", "")
        relation = icon.get("rel", "").casefold()
        priority = 30 if "32x32" in sizes else 20 if media == "image/svg+xml" or "any" in sizes else 10
        if "shortcut" in relation:
            priority -= 2
        candidates.append((priority, urljoin(base_url, icon["href"]), media))
    icons = manifest_payload.get("icons", []) if isinstance(manifest_payload, dict) else []
    for icon in icons if isinstance(icons, list) else []:
        if isinstance(icon, dict) and isinstance(icon.get("src"), str):
            supplied = icon.get("type") if isinstance(icon.get("type"), str) else None
            candidates.append((8, urljoin(manifest_url or base_url, icon["src"]), supplied))
    unique: dict[str, tuple[int, str, str | None]] = {}
    for candidate in candidates:
        unique.setdefault(candidate[1], candidate)
    return [(candidate_url, supplied) for _, candidate_url, supplied in sorted(unique.values(), key=lambda entry: (-entry[0], entry[1]))]


def _structured_logo_urls(blocks: list[str]) -> list[str]:
    urls: list[str] = []

    def visit(value: object, logo_context: bool = False) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                lowered = str(key).casefold()
                if lowered == "logo":
                    visit(child, True)
                elif logo_context and lowered in {"url", "contenturl"}:
                    visit(child, True)
                elif isinstance(child, (dict, list)):
                    visit(child, False)
        elif isinstance(value, list):
            for child in value:
                visit(child, logo_context)
        elif logo_context and isinstance(value, str) and value.strip():
            urls.append(value.strip())

    for block in blocks:
        try:
            visit(json.loads(block))
        except json.JSONDecodeError:
            continue
    return list(dict.fromkeys(urls))


def _select_logos(
    parser: DiscoveryParser,
    base_url: str,
    html_bytes: bytes,
    manifest_payload: dict[str, object],
    manifest_url: str | None,
    favicon_candidates: list[tuple[str, str | None]],
    css_candidates: list[dict[str, object]],
) -> list[dict[str, object]]:
    candidates = _inline_svg_logo_candidates(html_bytes, base_url)
    candidates.extend(css_candidates)
    candidates.extend({
        "source_url": urljoin(base_url, str(item["src"])), "media_type": None, "payload": None,
        "alt": str(item["alt"]), "score": int(item["score"]), "fallback": False,
    } for item in parser.logos)
    candidates.extend({
        "source_url": urljoin(base_url, candidate), "media_type": None, "payload": None,
        "alt": "Official brand logo", "score": 12, "fallback": False,
    } for candidate in parser.linked_logos)
    candidates.extend({
        "source_url": urljoin(base_url, candidate), "media_type": None, "payload": None,
        "alt": "Official brand logo", "score": 10, "fallback": False,
    } for candidate in [*parser.metadata_logos, *_structured_logo_urls(parser.json_ld_blocks)])
    manifest_icons = manifest_payload.get("icons", []) if isinstance(manifest_payload, dict) else []
    for icon in manifest_icons if isinstance(manifest_icons, list) else []:
        if isinstance(icon, dict) and isinstance(icon.get("src"), str):
            candidates.append({
                "source_url": urljoin(manifest_url or base_url, icon["src"]),
                "media_type": icon.get("type") if isinstance(icon.get("type"), str) else None,
                "payload": None, "alt": "Official application identity", "score": 4, "fallback": True,
            })
    candidates.extend({
        "source_url": candidate_url, "media_type": supplied_type, "payload": None,
        "alt": "Official site identity", "score": 2, "fallback": True,
    } for candidate_url, supplied_type in favicon_candidates)
    unique: dict[str, dict[str, object]] = {}
    for candidate in candidates:
        existing = unique.get(str(candidate["source_url"]))
        if existing is None or int(candidate["score"]) > int(existing["score"]):
            unique[str(candidate["source_url"])] = candidate
    return sorted(unique.values(), key=lambda item: (-int(item["score"]), str(item["source_url"])))


def _capture_first_asset(role: str, candidates: list[tuple[str, str | None]]) -> tuple[dict[str, str] | None, list[str]]:
    diagnostics: list[str] = []
    for candidate_url, supplied_type in candidates:
        try:
            return asset(role, candidate_url, supplied_type), []
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            diagnostics.append(f"identity.{role}: {candidate_url} could not be used ({exc})")
    if not candidates:
        diagnostics.append(f"identity.{role}: no official candidate was discovered in HTML metadata or manifest")
    return None, diagnostics


def _capture_first_logo(candidates: list[dict[str, object]]) -> tuple[dict[str, str] | None, str, list[str]]:
    diagnostics: list[str] = []
    explicit = [candidate for candidate in candidates if not candidate.get("fallback")]
    for candidate in explicit or candidates:
        candidate_url = str(candidate["source_url"])
        try:
            payload = candidate.get("payload")
            if isinstance(payload, bytes):
                resolved = asset_from_bytes("logo", candidate_url, str(candidate["media_type"]), payload)
            else:
                resolved = asset("logo", candidate_url, str(candidate["media_type"]) if candidate.get("media_type") else None)
            return resolved, str(candidate["alt"]), []
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            diagnostics.append(f"identity.logo: {candidate_url} could not be used ({exc})")
    if not candidates:
        diagnostics.append("identity.logo: no official logo or wordmark candidate was discovered in inline SVG, HTML images, visible CSS image declarations, metadata, manifest, or linked assets")
    return None, "", diagnostics


def build_profile(url: str, identifier: str, captured_at: str) -> dict[str, object]:
    html_record, html_bytes = capture(url)
    html_text = html_bytes.decode("utf-8", errors="replace")
    parser = DiscoveryParser()
    parser.feed(html_text)
    base_url = html_record["url"]

    stylesheet_records: list[dict[str, str]] = []
    css_texts: list[tuple[str, str]] = []
    stylesheet_diagnostics: list[str] = []
    for href in dict.fromkeys(parser.stylesheets):
        stylesheet_url = urljoin(base_url, href)
        try:
            record, payload = capture(stylesheet_url)
            if record["media_type"] not in {"text/css", "text/plain", "application/octet-stream"}:
                raise ValueError(f"unexpected stylesheet media type {record['media_type']}")
            stylesheet_records.append(record)
            css_texts.append((record["url"], payload.decode("utf-8", errors="replace")))
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            stylesheet_diagnostics.append(f"source.stylesheets: {stylesheet_url} could not be inspected ({exc})")
    for index, css in enumerate(parser.inline_styles):
        source_ref = f"{base_url}#inline-style-{index + 1}"
        stylesheet_records.append({"url": source_ref, "media_type": "text/css", "sha256": sha256(css.encode("utf-8"))})
        css_texts.append((source_ref, css))
    if not css_texts:
        raise BrandResolutionError(stylesheet_diagnostics or ["source.stylesheets: no official stylesheet or inline style was resolved"])

    manifest_record = None
    manifest_payload: dict[str, object] = {}
    manifest_diagnostics: list[str] = []
    if parser.manifest:
        try:
            manifest_record, payload = capture(urljoin(base_url, parser.manifest))
            manifest_record["media_type"] = "application/manifest+json"
            decoded = json.loads(payload.decode("utf-8"))
            if isinstance(decoded, dict):
                manifest_payload = decoded
        except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
            manifest_diagnostics.append(f"source.manifest: declared manifest could not be inspected ({exc})")

    analysis = analyze_css(css_texts, parser.visible_tokens)
    favicon_candidates = _select_favicon(parser, base_url, manifest_payload, manifest_record["url"] if manifest_record else None)
    logo_candidates = _select_logos(
        parser, base_url, html_bytes, manifest_payload, manifest_record["url"] if manifest_record else None,
        favicon_candidates, analysis.logo_candidates,
    )
    favicon, favicon_diagnostics = _capture_first_asset("favicon", favicon_candidates)
    logo_raw, logo_alt, logo_diagnostics = _capture_first_logo(logo_candidates)
    diagnostics = logo_diagnostics
    if favicon is None and favicon_candidates:
        diagnostics.extend(favicon_diagnostics)
    elif favicon is None and logo_raw is not None:
        favicon = {**logo_raw, "role": "favicon"}
        favicon_diagnostics.append("identity.favicon: no usable official favicon was found; the exact validated official logo bytes were reused as the offline icon")

    for color in parser.theme_colors:
        normalized = normalize_color(color)
        if normalized:
            _add_color(analysis, normalized, "meta[name=theme-color]", "content", base_url)
    custom_complete = all(_resolve_variable(analysis.properties, variable) for variable in (*COLOR_VARIABLES.values(), *TYPOGRAPHY_VARIABLES.values(), *GEOMETRY_VARIABLES.values(), "--brand-signature-thickness"))
    if custom_complete:
        theme, derived_tokens, decisions, theme_diagnostics = _custom_property_profile(analysis, stylesheet_records[0]["url"])
        resolution_method = "css-custom-properties"
    else:
        theme, derived_tokens, decisions, theme_diagnostics = _semantic_theme(analysis)
        resolution_method = "semantic-css"
    if theme:
        _apply_optional_accessibility(theme, derived_tokens, decisions)
    diagnostics.extend(theme_diagnostics)
    if favicon is None or logo_raw is None or diagnostics:
        diagnostics.append("Action: provide an accessible official website with a usable logo and defensible core interface palette, or use the Accenture fallback.")
        raise BrandResolutionError(diagnostics)

    title = " ".join(part.strip() for part in parser.title_parts if part.strip()) or identifier.replace("-", " ").title()
    evidence = [
        {"id": "BRAND-EVID-001", "source_ref": base_url, "signal": "Official website, redirects, metadata, stylesheet links, inline styles, and manifest candidates were inspected.", "confidence": "high"},
        {"id": "BRAND-EVID-CSS-SEMANTIC", "source_ref": stylesheet_records[0]["url"], "signal": f"Exact CSS declarations were mapped to theme roles using {resolution_method} evidence, selector semantics, frequency, contrast, and accessibility checks.", "confidence": "high" if resolution_method == "css-custom-properties" else "medium"},
        {"id": "BRAND-EVID-003", "source_ref": favicon["source_url"], "signal": "Official favicon or reused official identity bytes were captured unchanged, safety-checked, hashed, and embedded for offline use.", "confidence": "high"},
        {"id": "BRAND-EVID-004", "source_ref": logo_raw["source_url"], "signal": "Official image or static inline SVG logo bytes were captured unchanged, safety-checked, hashed, and embedded for offline use.", "confidence": "high"},
    ]
    mappings = []
    for group, keys in REQUIRED_THEME_KEYS.items():
        for key in keys:
            token = f"theme.{group}.{key}"
            decision = decisions[token]
            mappings.append({"token": token, "evidence_ids": ["BRAND-EVID-CSS-SEMANTIC"], **decision})

    profile = {
        "schema_version": 2, "id": identifier, "name": title, "required": True, "status": "resolved",
        "resolution_method": resolution_method,
        "source": {
            "requested_url": url, "resolved_url": base_url, "captured_at": captured_at, "html": html_record,
            "stylesheets": stylesheet_records, "manifest": manifest_record,
            "metadata": {
                "title": title,
                "theme_colors": sorted({color for raw in parser.theme_colors for color in colors_in(raw)}),
                "preview_images": [urljoin(base_url, candidate) for candidate in parser.preview_images],
                "favicon_candidates": [candidate for candidate, _ in favicon_candidates] or [favicon["source_url"]],
                "logo_candidates": [str(candidate["source_url"]) for candidate in logo_candidates],
                "logo_candidate": logo_raw["source_url"],
            },
            "capture_warnings": stylesheet_diagnostics + manifest_diagnostics + favicon_diagnostics,
        },
        "identity": {"display_name": title, "logo_alt": logo_alt},
        "assets": {"favicon": favicon, "logo": logo_raw},
        "observed_colors": _observed_colors(analysis), "derived_tokens": derived_tokens,
        "evidence": evidence, "theme": theme, "mappings": mappings,
    }
    return validate_brand_profile(profile)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--id", required=True)
    parser.add_argument("--captured-at", default=None)
    args = parser.parse_args()
    captured_at = args.captured_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    try:
        profile = build_profile(args.url, args.id, captured_at)
    except BrandResolutionError as exc:
        print("BRAND RESOLUTION BLOCKED", file=sys.stderr)
        for diagnostic in exc.diagnostics:
            print(f"- {diagnostic}", file=sys.stderr)
        return 1
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"BRAND RESOLUTION BLOCKED\n- source: {exc}\n- Action: verify the official URL and asset access, or use the Accenture fallback.", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(args.output)
    print(f"BRAND PROFILE RESOLVED: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
