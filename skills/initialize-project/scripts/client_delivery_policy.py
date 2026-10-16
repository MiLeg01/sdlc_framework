#!/usr/bin/env python3
"""Resolve conservative client sector, geography, locale, and delivery defaults."""

from __future__ import annotations

import re
from urllib.parse import urlparse


CONFIRMED = "CONFIRMED"
HIGH_CONFIDENCE = "HIGH_CONFIDENCE"
UNCERTAIN = "UNCERTAIN"
NOT_PUBLIC_SECTOR = "NOT_PUBLIC_SECTOR"
PUBLIC_CONFIDENCE = {CONFIRMED, HIGH_CONFIDENCE}

PUBLIC_PHRASES = (
    "public-sector client", "public sector client", "government client", "government customer",
    "public administration", "federal administration", "state administration", "public agency",
    "governmental body", "public institution", "öffentlicher auftraggeber", "öffentliche verwaltung",
)
PRIVATE_PHRASES = (
    "private-sector client", "private sector client", "private company", "privately held company",
    "commercial company", "not public sector", "not a public-sector client",
)
PUBLIC_ORGANIZATION_TERMS = (
    "ministry", "municipality", "government", "public administration", "public agency",
    "federal office", "state office", "city administration", "bundesministerium",
    "bundesamt", "landesregierung", "stadtverwaltung", "gemeinde", "magistrat", "kanton",
    "verwaltung", "behörde", "ministerium",
)
OFFICIAL_SUFFIXES = (
    ".gv.at", ".gov", ".gov.uk", ".bund.de", ".admin.ch", ".gouv.fr", ".europa.eu",
)


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip(" \t\r\n,;:.-")


def normalize_country(value: str) -> str:
    normalized = normalize_space(value).casefold()
    if normalized in {"at", "aut"} or any(token in normalized for token in ("austria", "österreich")):
        return "AT"
    if normalized in {"de", "deu"} or any(token in normalized for token in ("germany", "deutschland")):
        return "DE"
    if normalized in {"ch", "che"} or any(token in normalized for token in ("switzerland", "schweiz", "suisse")):
        return "CH"
    return normalize_space(value).upper()


def normalize_locale(value: str, country: str = "") -> str:
    normalized = normalize_space(value).casefold()
    if normalized in {"de-at", "de_at"} or "austrian german" in normalized or "österreich" in normalized:
        return "de-AT"
    if normalized in {"de-de", "de_de"} or "german (germany)" in normalized:
        return "de-DE"
    if normalized in {"de-ch", "de_ch"} or "swiss german" in normalized:
        return "de-CH"
    if any(token in normalized for token in ("german", "deutsch")):
        return {"AT": "de-AT", "DE": "de-DE", "CH": "de-CH"}.get(country, "de-AT")
    if any(token in normalized for token in ("english", "englisch", "en-gb", "british english")):
        return "en"
    return normalize_space(value)


def locale_for_country(country: str) -> str:
    return {"AT": "de-AT", "DE": "de-DE", "CH": "de-CH"}.get(country, "")


def _hostname(url: str) -> str:
    try:
        return (urlparse(url).hostname or "").casefold()
    except ValueError:
        return ""


def _country_from_evidence(text: str, urls: list[str]) -> tuple[str, list[str]]:
    lower = text.casefold()
    if re.search(r"\b(?:austria|austrian|österreich|österreichisch)\b", lower):
        return "AT", ["brief:austria"]
    if re.search(r"\b(?:germany|german federal|deutschland|deutsch(?:e|er|es)? bundes)\b", lower):
        return "DE", ["brief:germany"]
    if re.search(r"\b(?:switzerland|swiss|schweiz|schweizer)\b", lower):
        return "CH", ["brief:switzerland"]
    for value in urls:
        host = _hostname(value)
        if host.endswith(".gv.at") or "oesterreich" in host:
            return "AT", [f"url-country:{host}"]
        if host.endswith(".bund.de") or host.endswith(".de") and any(term in host for term in ("bund", "ministerium", "verwaltung")):
            return "DE", [f"url-country:{host}"]
        if host.endswith(".admin.ch") or host.endswith(".ch") and any(term in host for term in ("admin", "bund", "kanton")):
            return "CH", [f"url-country:{host}"]
    return "", []


def detect_client_context(
    text: str,
    urls: list[str] | None = None,
    *,
    brand_source: str = "",
    organization: str = "",
    explicit_public_sector: bool | None = None,
    country: str = "",
    locale: str = "",
) -> dict[str, object]:
    """Return evidence-separated client classification without network access."""

    urls = list(dict.fromkeys([*(urls or []), *([brand_source] if brand_source.startswith("http") else [])]))
    lower = text.casefold()
    organization = normalize_space(organization)
    organization_lower = organization.casefold()
    evidence: list[str] = []

    explicit_private = any(phrase in lower for phrase in PRIVATE_PHRASES) or bool(re.search(
        r"\bprivate(?:ly owned|[- ]sector|\s+[a-z-]+){0,3}\s+(?:company|enterprise|organization|organisation|client)\b",
        lower,
    ))
    if explicit_public_sector is False or explicit_private:
        confidence = NOT_PUBLIC_SECTOR
        sector = "private"
        evidence.append("explicit:private-sector")
        public_sector = False
    elif explicit_public_sector is True or any(phrase in lower for phrase in PUBLIC_PHRASES):
        confidence = CONFIRMED
        sector = "public"
        evidence.append("explicit:public-sector")
        public_sector = True
    elif organization and any(term in organization_lower for term in PUBLIC_ORGANIZATION_TERMS):
        confidence = CONFIRMED
        sector = "public"
        evidence.append(f"organization:{organization}")
        public_sector = True
    else:
        official_hosts = [host for host in (_hostname(value) for value in urls) if host.endswith(OFFICIAL_SUFFIXES)]
        descriptive_hosts = [
            host for host in (_hostname(value) for value in urls)
            if any(term.replace(" ", "") in host.replace("-", "") for term in PUBLIC_ORGANIZATION_TERMS)
        ]
        brief_terms = [term for term in PUBLIC_ORGANIZATION_TERMS if term in lower]
        if official_hosts and (descriptive_hosts or brief_terms):
            confidence = HIGH_CONFIDENCE
            sector = "public"
            public_sector = True
            evidence.extend(f"official-url:{host}" for host in official_hosts)
            evidence.extend(f"organization-url:{host}" for host in descriptive_hosts)
            evidence.extend(f"brief-organization-term:{term}" for term in brief_terms[:2])
        elif official_hosts or brief_terms:
            confidence = UNCERTAIN
            sector = "unknown"
            public_sector = None
            evidence.extend(f"official-url-only:{host}" for host in official_hosts)
            evidence.extend(f"ambiguous-organization-term:{term}" for term in brief_terms[:2])
        else:
            confidence = NOT_PUBLIC_SECTOR
            sector = "unknown"
            public_sector = False

    normalized_country = normalize_country(country) if country else ""
    country_evidence: list[str] = []
    if not normalized_country:
        normalized_country, country_evidence = _country_from_evidence(
            " ".join(value for value in (text, organization, brand_source) if value), urls,
        )
    evidence.extend(country_evidence)
    normalized_locale = normalize_locale(locale, normalized_country) if locale else locale_for_country(normalized_country)

    return {
        "organization": organization or None,
        "sector": sector,
        "public_sector": public_sector,
        "public_sector_confidence": confidence,
        "country": normalized_country or None,
        "locale": normalized_locale or None,
        "evidence": list(dict.fromkeys(evidence)),
    }


def public_sector_defaults(client: dict[str, object]) -> dict[str, object]:
    confidence = str(client.get("public_sector_confidence") or "")
    locale = str(client.get("locale") or "")
    if confidence not in PUBLIC_CONFIDENCE or not locale:
        return {"applied": False, "reason": "public sector or locale is unresolved"}
    return {
        "applied": True,
        "source": "public-sector-client-default",
        "dashboard": {
            "languages": [locale, "en"] if locale != "en" else ["en"],
            "default_language": locale,
            "language_switch": locale != "en",
        },
        "presentation": {
            "languages": [locale],
            "default_language": locale,
            "bilingual": False,
        },
    }
