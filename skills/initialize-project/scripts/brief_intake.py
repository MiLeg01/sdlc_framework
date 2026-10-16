#!/usr/bin/env python3
"""Extract a conservative project-intake profile from a natural-language brief."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from client_delivery_policy import (
    CONFIRMED,
    HIGH_CONFIDENCE,
    UNCERTAIN,
    detect_client_context,
    normalize_locale,
    public_sector_defaults,
)


SKIP_DIRECTORIES = {
    ".git", ".idea", ".venv", "node_modules", "vendor", "dist", "build", "target",
    "coverage", "out", "generated", "__pycache__",
}
TECHNOLOGY_EXTENSIONS = {
    ".sas": "SAS",
    ".cbl": "COBOL",
    ".cob": "COBOL",
    ".cpy": "COBOL",
    ".pli": "PL/I",
    ".pl1": "PL/I",
    ".java": "Java",
    ".cs": "C#",
    ".py": "Python",
    ".ts": "TypeScript",
    ".tsx": "React/TypeScript",
    ".js": "JavaScript",
    ".jsx": "React/JavaScript",
    ".c": "C",
    ".cc": "C++",
    ".cpp": "C++",
    ".h": "C/C++",
    ".sql": "SQL",
}
KNOWN_TECHNOLOGIES = [
    "Spring Boot", "AngularJS", "TypeScript", "JavaScript", "PostgreSQL", "Natural",
    "React", "COBOL", "Java", "Python", "Azure", "SAS", "PL/I", "C#", ".NET", "C++", "C",
]
LANGUAGE_OPTIONS = ["English", "German (Austria)", "German + English switch", "Other"]
PRESENTATION_PURPOSES = ("sales", "executive", "technical", "informational", "workshop", "internal")
DIAGRAM_VIEW_OPTIONS = [
    "System / application landscape",
    "Component architecture",
    "Class / domain model",
    "ER / data model",
    "Sequence / interaction flows",
    "Data flows",
    "Migration roadmap",
    "Let the agent determine from the analysis",
]


def extract_methodology_overrides(text: str) -> dict[str, Any]:
    lower = text.casefold()
    no_openspec = bool(re.search(
        r"\b(?:no|without|skip|disable|do not use|don't use)\s+openspec\b|\bopenspec\s+(?:off|disabled)\b",
        lower,
    ))
    no_tdd = bool(re.search(
        r"\b(?:no|without|skip|disable|do not use|don't use)\s+(?:tdd|test[- ]driven development)\b|\b(?:tdd|test[- ]driven development)\s+(?:off|disabled)\b",
        lower,
    ))
    explicit_openspec = not no_openspec and bool(re.search(r"\b(?:use|with|require|adopt)\s+openspec\b", lower))
    explicit_tdd = not no_tdd and bool(re.search(
        r"\b(?:use|with|require|adopt)\s+(?:tdd|test[- ]driven development)\b", lower
    ))
    return {
        "specification": "none" if no_openspec else ("openspec" if explicit_openspec else None),
        "implementation": "normal" if no_tdd else ("test-driven-development" if explicit_tdd else None),
        "explicit_specification": no_openspec or explicit_openspec,
        "explicit_implementation": no_tdd or explicit_tdd,
    }


def unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip(" \t\r\n,;:.-")


def labeled_value(text: str, labels: tuple[str, ...]) -> str:
    for label in labels:
        match = re.search(rf"(?im)^\s*{re.escape(label)}\s*:\s*(.+?)\s*$", text)
        if match:
            return normalize_space(match.group(1))
    return ""


def split_audience(value: str) -> list[str]:
    parts = unique(
        normalize_space(part)
        for part in re.split(r"\s*(?:,|\+|\band\b)\s*", value, flags=re.I)
        if normalize_space(part)
    )
    if len(parts) == 1 and parts[0].casefold() == "both":
        return ["technical", "management"]
    return parts


def extract_topic(text: str) -> str:
    explicit = labeled_value(text, ("topic", "research topic", "presentation topic"))
    if explicit:
        return explicit
    match = re.search(
        r"(?is)\babout\s+(.+?)(?=\n\s*(?:audience|brand|references?|desired outcome|sales objective|source material)\s*:|[.!?]\s*$|\Z)",
        text,
    )
    return normalize_space(match.group(1)) if match else ""


def find_paths(text: str) -> list[str]:
    pattern = r"(?<![A-Za-z0-9])(?:/(?:[A-Za-z0-9._~+@%=-]+/?)+|\.\.?/(?:[A-Za-z0-9._~+@%=-]+/?)+)"
    explicit = [match.group(0).rstrip(".,;:") for match in re.finditer(pattern, text)]
    contextual = [
        match.group(1).rstrip(".,;:")
        for match in re.finditer(
            r"(?i)\b(?:under|from|in|source(?:\s+(?:is|at))?|folder|directory|path)\s+"
            r"(?:the\s+)?(?:read[- ]only\s+)?([A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*)",
            text,
        )
        if match.group(1).casefold() not in {
            "the", "a", "an", "source", "folder", "directory", "path", "read-only", "readonly"
        }
    ]
    return unique([*explicit, *contextual])


def find_urls(text: str) -> list[str]:
    return unique(match.group(0).rstrip(".,;:)") for match in re.finditer(r"https?://[^\s,)]+", text))


def clean_technology(value: str) -> str:
    value = normalize_space(value)
    value = re.sub(
        r"^(?:for\s+)?(?:a\s+)?(?:legacy\s+)?(?:migration|modernization|modernisation|migrate|from)\s+",
        "",
        value,
        flags=re.I,
    )
    value = re.sub(r"^(?:legacy|old)\s+", "", value, flags=re.I)
    value = re.split(r"\b(?:source|application|app|system|code|with|and|for)\b", value, maxsplit=1, flags=re.I)[0]
    words = value.split()
    return " ".join(words[-3:]) if words else ""


def extract_technology_pair(text: str) -> tuple[str, str]:
    arrow = re.search(r"([^\n,;:]{1,80}?)\s*(?:->|→)\s*([^\n,;:.]{1,80})", text, re.I)
    if arrow:
        source = clean_technology(arrow.group(1))
        target = clean_technology(arrow.group(2))
        return source, target
    migration = re.search(
        r"\b(?:migrate|migration\s+from|moderni[sz]e)\s+([A-Za-z0-9+.#/-]+(?:\s+[A-Za-z0-9+.#/-]+){0,2})\s+to\s+([A-Za-z0-9+.#/-]+(?:\s+[A-Za-z0-9+.#/-]+){0,2})",
        text,
        re.I,
    )
    if migration:
        return clean_technology(migration.group(1)), clean_technology(migration.group(2))
    target_only = re.search(
        r"\b(?:eventually\s+)?moderni[sz]e\s+to\s+"
        r"([A-Za-z0-9+.#/-]+(?:\s+[A-Za-z0-9+.#/-]+){0,5})",
        text,
        re.I,
    )
    old_app = re.search(r"\b(?:old|legacy)\s+([A-Za-z0-9+.#/-]+)\s+(?:app|application|system)\b", text, re.I)
    if not old_app:
        old_app = re.search(r"\b(?:analy[sz]e\s+)?legacy\s+([A-Za-z0-9+.#/-]+)\s+(?:in|source\b)", text, re.I)
    replacement = re.search(
        r"\b(?:a\s+)?([A-Za-z0-9+.#/-]+(?:\s+[A-Za-z0-9+.#/-]+){0,2})\s+replacement\b",
        text,
        re.I,
    )
    replacement_value = clean_technology(replacement.group(1)) if replacement else ""
    if replacement_value.lower() in {"build", "create", "full", "the"}:
        replacement_value = ""
    target_only_value = normalize_space(target_only.group(1)) if target_only else ""
    return (
        clean_technology(old_app.group(1)) if old_app else "",
        replacement_value or target_only_value,
    )


def extract_technologies(text: str, source: str, target: str) -> list[str]:
    technologies = [source, target]
    for technology in KNOWN_TECHNOLOGIES:
        if re.search(rf"(?<![A-Za-z0-9]){re.escape(technology)}(?![A-Za-z0-9])", text, re.I):
            technologies.append(technology)
    return unique(technologies)


def extract_scopes(text: str, migration_intent: str) -> list[str]:
    lower = text.lower()
    scopes: list[str] = []
    legacy_signal = any(token in lower for token in (
        "legacy", "migrate", "migration", "modernize", "modernise", "old app", "old application",
    )) or bool(re.search(r"\bold\s+[A-Za-z0-9+.#/-]+\s+(?:app|application|system)\b", text, re.I))
    if legacy_signal:
        scopes.append("legacy-migration")
    development_signal = any(token in lower for token in (
        "new development", "development project", "software development", "new application",
        "new service", "build a new", "build a service", "prototype", "proof of concept",
        "implement the migration", "implement migration", "full replacement", "build replacement",
    )) or ("development" in lower and not legacy_signal)
    if development_signal or migration_intent == "implementation":
        scopes.append("development")
    if any(token in lower for token in (
        "research", "market study", "competitor analysis", "industry analysis",
        "architecture analysis", "architecture assessment", "application architecture review",
        "integration assessment", "solution architecture discovery",
    )):
        scopes.append("research")
    if any(token in lower for token in ("presentation", "sales deck", "sales presentation", "slide deck")):
        scopes.append("presentation")
    return unique(scopes)


def extract_migration_intent(text: str) -> str:
    lower = text.lower()
    if any(token in lower for token in ("analysis only", "analyse only", "analyze only", "no implementation")):
        return "analysis-only"
    if any(token in lower for token in (
        "prepare implementation", "prepare for implementation", "implementation preparation",
        "implementation-ready backlog", "implementation ready backlog",
        "prepare the migration", "prepare migration", "migration preparation", "migration plan",
        "plan the migration", "migration readiness", "eventually modernize", "eventually modernise",
    )):
        return "preparation"
    if any(token in lower for token in (
        "implement the migration", "implement migration", "full migration", "full replacement",
        "implement the full", "update the source in-place", "modify the source in-place",
    )):
        return "implementation"
    if "implementation" in lower and "implementation backlog" not in lower and any(
        token in lower for token in ("legacy", "migration", "migrate", "modernize", "modernise")
    ):
        return "implementation"
    if re.search(r"\bprepare\s+(?:a\s+)?[A-Za-z0-9+.#/-]+(?:\s+[A-Za-z0-9+.#/-]+){0,2}\s+replacement\b", text, re.I):
        return "preparation"
    return ""


def extract_diagram_views(text: str) -> list[str]:
    lower = text.lower()
    mappings = [
        (("system landscape", "application landscape", "integration map", "applications and integrations", "all applications and integrations"), "system-landscape"),
        (("component architecture", "component diagram", "application architecture", "solution architecture", "service architecture", "modules and services"), "component-architecture"),
        (("class diagram", "domain model", "object model", "core java domain"), "class"),
        (("er diagram", "entity relationship", "entity-relationship", "database relationships", "database schema", "data model", "erd"), "er"),
        (("sequence diagram", "interaction diagram", "request flow", "login flow", "authentication flow", "calls between services", "service call flow"), "sequence"),
        (("data-flow", "data flow", "data lineage", "where data moves", "movement of data", "etl flow", "batch flow", "sas flow"), "data-flow"),
        (("migration roadmap", "migration waves", "transition architecture", "strangler steps", "legacy retirement", "coexistence roadmap"), "migration-roadmap"),
    ]
    return unique(identifier for terms, identifier in mappings if any(term in lower for term in terms))


def extract_deliverables(text: str, migration_intent: str) -> list[str]:
    lower = text.lower()
    mappings = [
        (("analysis", "analyse", "analyze"), "source-analysis"),
        (("requirements", "business rules"), "requirements-extraction"),
        (("specifications", "specification", "openspec"), "openspec-specifications"),
        (("traceability", "traceable"), "requirements-traceability"),
        (("dependency graph", "dependencies"), "dependency-analysis"),
        (("data-flow", "data flow"), "data-flow-analysis"),
        (("target architecture",), "target-architecture"),
        (("architecture", "topology"), "architecture"),
        (("proof of concept", "prototype", "poc"), "prototype"),
        (("implementation", "implement"), "implementation"),
        (("tests", "testing"), "tests"),
        (("dashboard",), "html-dashboard"),
        (("management report", "report"), "management-report"),
        (("presentation", "sales deck", "slide deck"), "presentation"),
    ]
    deliverables: list[str] = []
    for terms, identifier in mappings:
        if any(term in lower for term in terms):
            deliverables.append(identifier)
    if migration_intent == "preparation":
        deliverables = [value for value in deliverables if value != "implementation"]
        deliverables.append("migration-preparation")
    elif migration_intent == "implementation":
        deliverables.append("migration-implementation")
    if migration_intent in {"preparation", "implementation"} or (
        "development" in lower and "analysis only" not in lower
    ):
        deliverables.append("openspec-specifications")
    return unique(deliverables)


def extract_html_artifact(text: str, scopes: list[str]) -> str:
    lower = text.lower()
    if "dashboard" in lower:
        if any(token in lower for token in ("management dashboard", "executive dashboard", "cio dashboard")):
            return "management-dashboard"
        if "technical" in lower or "legacy-migration" in scopes:
            return "technical-dashboard"
        return "project-dashboard"
    if any(token in lower for token in ("sales presentation", "sales deck")):
        return "sales-presentation"
    if "presentation" in lower or "slide deck" in lower:
        return "executive-presentation"
    return ""


def extract_brand(text: str, urls: list[str]) -> str:
    lower = text.lower()
    explicit = labeled_value(text, ("brand", "branding", "visual identity"))
    if explicit:
        normalized = explicit.lower().strip()
        if normalized in {"client", "client brand"}:
            return "client-brand"
        if normalized in {"organization", "organisation", "organization brand", "organisation brand"}:
            return "organization"
        if normalized in {"neutral", "neutral premium"}:
            return "neutral-premium"
        return explicit
    if "organization brand" in lower or "organisation brand" in lower:
        return "organization"
    if "client brand" in lower or "client branding" in lower:
        for url in urls:
            position = lower.find(url.lower())
            window = lower[max(0, position - 120): position + len(url) + 40]
            if "client brand" in window or "client branding" in window:
                return url
        return "client-brand"
    if "neutral premium" in lower or "neutral branding" in lower or "neutral design" in lower:
        return "neutral-premium"
    local_reference = re.search(
        r"\b(?:use\s+)?(?:the\s+)?(?:brand|branding|visual identity)\s+from\s+([^\s,;]+)",
        text,
        re.I,
    )
    if local_reference:
        return local_reference.group(1).strip(".\"'")
    for url in urls:
        window = lower[max(0, lower.find(url.lower()) - 80): lower.find(url.lower()) + len(url) + 80]
        if "brand" in window or "website" in window or "visual" in window:
            return url
    return ""


def _artifact_policy(
    languages: list[str],
    default_language: str,
    multiple: bool,
    source: str,
    switch_field: str,
) -> dict[str, Any]:
    return {
        "resolved": bool(languages and default_language),
        "languages": unique(languages),
        "default_language": default_language or None,
        switch_field: bool(multiple),
        "source": source,
    }


def extract_localization(text: str, html_artifact: str, client: dict[str, Any]) -> dict[str, Any]:
    lower = text.casefold()
    working_value = labeled_value(text, ("working language", "internal working language"))
    client_value = labeled_value(text, ("client delivery", "client language", "client-facing language", "delivery language"))
    country = str(client.get("country") or "")
    working_language = normalize_locale(working_value, country) if working_value else ""
    client_language = normalize_locale(client_value, country) if client_value else ""
    german_signal = bool(client_language.startswith("de-")) or bool(re.search(
        r"\b(?:language|delivery|deliver|artifact|dashboard|presentation|deck)\b[^.\n]{0,80}"
        r"\b(?:german|deutsch|de-at|austrian german)\b|"
        r"\b(?:in|auf)\s+(?:german|deutsch)\b",
        lower,
    ))
    english_signal = client_language == "en" or bool(re.search(
        r"\b(?:language|delivery|deliver|artifact|dashboard|presentation|deck)\b[^.\n]{0,80}"
        r"\b(?:english|englisch|en-gb)\b|"
        r"\b(?:in|auf)\s+(?:english|englisch)\b",
        lower,
    ))
    austrian_client = "austrian client" in lower or "österreichischen kunden" in lower
    bilingual = any(token in lower for token in (
        "bilingual", "language switch", "language toggle", "keep english available",
        "english switch", "german/english", "german + english", "deutsch/english",
        "deutsch/englisch", "deutsch + english", "deutsch + englisch",
    ))
    if html_artifact and german_signal and not working_value and not client_language:
        client_language = "de-AT"
    if html_artifact and english_signal and not german_signal and not working_value and not client_language:
        client_language = "en"
    if bilingual:
        working_language = working_language or "en"
        if not client_language and (german_signal or austrian_client):
            client_language = "de-AT"
    if client_language == "de-AT" and english_signal:
        bilingual = True
        working_language = working_language or "en"

    defaults = public_sector_defaults(client)
    dashboard = _artifact_policy([], "", False, "unresolved", "language_switch")
    presentation = _artifact_policy([], "", False, "unresolved", "bilingual")
    if defaults.get("applied"):
        dashboard = _artifact_policy(
            list(defaults["dashboard"]["languages"]),
            str(defaults["dashboard"]["default_language"]),
            bool(defaults["dashboard"]["language_switch"]),
            "public-sector-client-default",
            "language_switch",
        )
        presentation = _artifact_policy(
            list(defaults["presentation"]["languages"]),
            str(defaults["presentation"]["default_language"]),
            bool(defaults["presentation"]["bilingual"]),
            "public-sector-client-default",
            "bilingual",
        )

    generic_languages = unique([client_language, working_language])
    if bilingual:
        generic_languages = unique([client_language or str(client.get("locale") or "de-AT"), working_language or "en"])
    if client_language or bilingual:
        generic_default = client_language or generic_languages[0]
        if "dashboard" in html_artifact or html_artifact == "combination":
            dashboard = _artifact_policy(
                generic_languages or [generic_default], generic_default, bilingual,
                "explicit-client-language", "language_switch",
            )
        if "presentation" in html_artifact or html_artifact == "combination":
            presentation = _artifact_policy(
                generic_languages or [generic_default], generic_default, bilingual,
                "explicit-client-language", "bilingual",
            )

    public_locale = str(client.get("locale") or "de-AT")
    if re.search(r"\bdashboard\b[^.\n]{0,100}\b(?:german|deutsch|de-at)\s+only\b", lower):
        dashboard = _artifact_policy([public_locale], public_locale, False, "explicit-project-instruction", "language_switch")
    if re.search(r"\bdashboard\b[^.\n]{0,120}\benglish\s+(?:first|default)\b", lower):
        dashboard = _artifact_policy(["en", public_locale], "en", True, "explicit-project-instruction", "language_switch")
    if re.search(r"\b(?:sales\s+)?presentation\b[^.\n]{0,100}\b(?:must\s+be\s+|in\s+)?english\b", lower):
        presentation = _artifact_policy(["en"], "en", False, "explicit-project-instruction", "bilingual")
    if re.search(r"\b(?:sales\s+deck|sales\s+presentation|presentation)\b[^.\n]{0,120}\b(?:bilingual|german\s*\+\s*english|deutsch\s*\+\s*englisch)\b", lower):
        presentation = _artifact_policy([public_locale, "en"], public_locale, True, "explicit-project-instruction", "bilingual")

    relevant_resolved = (
        dashboard["resolved"] if "dashboard" in html_artifact else
        presentation["resolved"] if "presentation" in html_artifact else
        dashboard["resolved"] or presentation["resolved"]
    )
    return {
        "resolved": bool(working_language or relevant_resolved),
        "working_language": working_language or None,
        "dashboard": dashboard,
        "presentation": presentation,
    }


def extract_audience(text: str) -> list[str]:
    explicit = labeled_value(text, ("audience", "target audience", "customer"))
    if explicit:
        return split_audience(explicit)
    lower = text.lower()
    technical = any(token in lower for token in ("technical team", "technical users", "engineers", "developers", "architects")) or bool(re.search(r"\btechnical\b", lower))
    management = any(token in lower for token in ("management", "executives", "executive", "cio", "leadership"))
    if technical and management:
        return ["technical", "management"]
    if technical:
        return ["technical"]
    if management:
        return ["management"]
    return []


def source_access(text: str, path: str, all_paths: list[str]) -> str:
    lower = text.lower()
    index = lower.find(path.lower())
    window = lower[max(0, index - 100): index + len(path) + 120] if index >= 0 else lower
    if any(token in window for token in ("read-only", "read only", "do not modify", "must not modify")):
        return "read-only"
    if any(token in window for token in ("read-write", "writable", "may modify", "can modify")):
        return "read-write"
    global_read_only = any(token in lower for token in (
        "source is read-only", "source is read only", "sources are read-only", "sources are read only",
        "create files only in the new project", "files only in the new project",
    ))
    if global_read_only and len(all_paths) >= 1:
        return "read-only"
    return "unspecified"


def inspect_source(path_value: str, cwd: Path) -> dict[str, Any]:
    source_path = Path(path_value).expanduser()
    if not source_path.is_absolute():
        source_path = (cwd / source_path).resolve()
    result: dict[str, Any] = {
        "path": str(source_path),
        "exists": source_path.exists(),
        "kind": "missing",
        "technologies": [],
        "build_files": [],
        "has_tests": False,
        "has_documentation": False,
        "has_schemas": False,
        "files_sampled": 0,
        "artifacts": [],
        "inventory_failures": [],
        "inventory_complete": True,
        "inventory_fingerprint": None,
    }
    if not source_path.exists():
        return result
    result["kind"] = "directory" if source_path.is_dir() else "file"
    candidates = [source_path] if source_path.is_file() else source_path.rglob("*")
    technologies: set[str] = set()
    build_files: set[str] = set()
    for candidate in candidates:
        if any(part in SKIP_DIRECTORIES for part in candidate.parts):
            continue
        if not candidate.is_file():
            continue
        result["files_sampled"] += 1
        technology = TECHNOLOGY_EXTENSIONS.get(candidate.suffix.lower())
        if technology:
            technologies.add(technology)
        name = candidate.name.lower()
        if name in {"pom.xml", "build.gradle", "build.gradle.kts", "package.json", "requirements.txt", "pyproject.toml", "makefile", "dockerfile"}:
            build_files.add(candidate.name)
        relative_text = str(candidate.relative_to(source_path) if source_path.is_dir() else candidate.name).lower()
        result["has_tests"] = result["has_tests"] or any(part in relative_text for part in ("test", "spec"))
        result["has_documentation"] = result["has_documentation"] or candidate.suffix.lower() in {".md", ".adoc", ".rst"}
        result["has_schemas"] = result["has_schemas"] or candidate.suffix.lower() in {".xsd", ".wsdl", ".avsc", ".proto"}
        relative = candidate.relative_to(source_path).as_posix() if source_path.is_dir() else candidate.name
        try:
            digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
            size = candidate.stat().st_size
        except OSError as exc:
            result["inventory_failures"].append({"path": relative, "error": type(exc).__name__})
        else:
            result["artifacts"].append({
                "id": "ART-" + hashlib.sha256(relative.encode()).hexdigest()[:12].upper(),
                "path": relative,
                "size": size,
                "sha256": digest,
                "language": technology or "unknown",
            })
        if result["files_sampled"] >= 800:
            result["inventory_complete"] = False
            break
    result["technologies"] = sorted(technologies)
    result["build_files"] = sorted(build_files)
    fingerprint_input = "\n".join(
        f"{item['path']}\t{item['sha256']}" for item in result["artifacts"]
    )
    result["inventory_fingerprint"] = hashlib.sha256(fingerprint_input.encode()).hexdigest()
    return result


def question(identifier: str, prompt: str, options: list[str] | None = None) -> dict[str, Any]:
    return {"id": identifier, "question": prompt, "options": options or []}


def parse_brief(text: str, cwd: Path) -> dict[str, Any]:
    raw = text
    brief = normalize_space(text)
    lower = brief.lower()
    urls = find_urls(brief)
    paths = [path for path in find_paths(brief) if not any(path in url for url in urls)]
    source_technology, target_technology = extract_technology_pair(brief)
    migration_intent = extract_migration_intent(brief)
    methodology = extract_methodology_overrides(brief)
    diagram_views = extract_diagram_views(brief)
    architecture_documentation = bool(diagram_views) or any(
        token in lower for token in ("architecture documentation", "technical diagrams", "architecture views")
    )
    scopes = extract_scopes(brief, migration_intent)
    technologies = extract_technologies(brief, source_technology, target_technology)
    deliverables = extract_deliverables(brief, migration_intent)
    if methodology["specification"] == "none":
        deliverables = [value for value in deliverables if value != "openspec-specifications"]
    deliverables = unique([*deliverables, *(f"diagram:{view}" for view in diagram_views)])
    html_artifact = extract_html_artifact(brief, scopes)
    brand_source = extract_brand(raw, urls)
    if not html_artifact and brand_source and "legacy-migration" in scopes and any(
        value in deliverables for value in ("requirements-extraction", "openspec-specifications")
    ):
        html_artifact = "technical-dashboard"
    client_organization = labeled_value(raw, ("client organization", "client organisation", "client", "organization", "organisation"))
    client_country = labeled_value(raw, ("client country", "country"))
    client_locale = labeled_value(raw, ("client locale", "locale"))
    client = detect_client_context(
        raw,
        urls,
        brand_source=brand_source,
        organization=client_organization,
        country=client_country,
        locale=client_locale,
    )
    localization = extract_localization(raw, html_artifact, client)
    audience = extract_audience(raw)
    topic = extract_topic(raw)
    explicit_purpose = labeled_value(raw, ("presentation purpose", "purpose"))
    purpose_text = explicit_purpose.lower() if explicit_purpose else lower
    presentation_purposes = [
        purpose for purpose in PRESENTATION_PURPOSES
        if re.search(rf"\b{purpose}\s+(?:presentation|deck|workshop)\b", purpose_text)
        or (explicit_purpose and re.search(rf"\b{purpose}\b", purpose_text))
    ]
    desired_outcome = labeled_value(raw, ("desired outcome", "outcome", "next action"))
    sales_objective = labeled_value(raw, ("sales objective", "sales goal", "call to action"))
    research_goal = labeled_value(raw, ("research goal", "research question"))
    source_material = labeled_value(raw, ("source material", "sources"))
    dashboard_purposes = [value for value in (
        "analysis" if "source-analysis" in deliverables else "",
        "requirements" if "requirements-extraction" in deliverables else "",
        "specifications" if "openspec-specifications" in deliverables else "",
        "traceability" if "openspec-specifications" in deliverables or "requirements-traceability" in deliverables else "",
        "delivery" if migration_intent == "implementation" or "development" in scopes else "",
        "status" if "status" in lower else "",
    ) if value]
    sources: list[dict[str, Any]] = []
    discovered_sources: list[dict[str, Any]] = []
    for path in paths:
        access = source_access(brief, path, paths)
        inspection = inspect_source(path, cwd)
        sources.append({
            "path": inspection["path"],
            "role": "legacy-source" if "legacy-migration" in scopes else "reference-source",
            "access": access,
        })
        discovered_sources.append(inspection)

    conflicts: list[dict[str, str]] = []
    asks_source_mutation = any(token in lower for token in (
        "update the source in-place", "modify the source in-place", "change the source in-place",
        "edit the legacy source", "write to the source",
    ))
    if asks_source_mutation and any(source["access"] == "read-only" for source in sources):
        conflicts.append({
            "id": "source-permission-conflict",
            "detail": "The brief marks source as read-only and also requests in-place source modification.",
        })
    if migration_intent == "analysis-only" and any(token in lower for token in ("implement", "full replacement", "build replacement")):
        conflicts.append({
            "id": "scope-conflict",
            "detail": "The brief says analysis only and also requests implementation.",
        })

    known = {
        "scopes": scopes,
        "source_technology": source_technology or None,
        "target_technology": target_technology or None,
        "sources": sources,
        "deliverables": deliverables,
        "html_artifact": html_artifact or None,
        "brand_source": brand_source or None,
        "client": client,
        "audience": audience,
        "dashboard_purposes": dashboard_purposes,
        "migration_intent": migration_intent or None,
        "technologies": technologies,
        "references": unique([
            *urls,
            brand_source if brand_source and brand_source not in {"client-brand", "organization", "neutral-premium"} else "",
        ]),
        "research_topic": topic if "research" in scopes else None,
        "research_goal": research_goal or None,
        "presentation_topic": topic if "presentation" in scopes else None,
        "presentation_purposes": presentation_purposes,
        "desired_outcome": desired_outcome or None,
        "sales_objective": sales_objective or None,
        "source_material": [item.strip() for item in source_material.split(",") if item.strip()],
        "diagram_views": diagram_views,
        "localization": localization,
        "methodology": methodology,
    }
    inferred: dict[str, Any] = {}
    if "requirements-extraction" in deliverables and "legacy-migration" in scopes:
        inferred["evidence_traceability"] = True
    if html_artifact and "dashboard" in html_artifact:
        inferred["living_dashboard"] = True
    if migration_intent == "preparation":
        inferred["full_target_implementation"] = False
        inferred["specifications"] = methodology["specification"] or "openspec"
        inferred["tdd"] = "normal" if methodology["implementation"] == "normal" else "planned"
    elif migration_intent == "implementation" or "development" in scopes:
        inferred["specifications"] = methodology["specification"] or "openspec"
        inferred["tdd"] = "normal" if methodology["implementation"] == "normal" else "active"
    elif migration_intent == "analysis-only":
        inferred["specifications"] = "none"
        inferred["tdd"] = "none"
    if architecture_documentation:
        inferred["architecture_documentation"] = True
    if localization["dashboard"].get("language_switch") or localization["presentation"].get("bilingual"):
        inferred["bilingual_client_delivery"] = True
    if client.get("public_sector_confidence") in {CONFIRMED, HIGH_CONFIDENCE}:
        inferred["public_sector_client_delivery"] = True

    discovered_technologies = unique([
        technology
        for source in discovered_sources
        for technology in source.get("technologies", [])
    ])

    missing: list[dict[str, Any]] = []
    if not scopes:
        missing.append(question("project.scope", "What kind of project is this?", ["Legacy migration/analysis", "Development", "Research", "Presentation", "Hybrid / combination"]))
    if "legacy-migration" in scopes and not sources:
        missing.append(question("sources.location", "Where is the legacy/source material located?"))
    if "legacy-migration" in scopes and not source_technology and not discovered_technologies:
        missing.append(question("migration.source_technology", "What is the source technology?"))
    if "legacy-migration" in scopes and not target_technology and migration_intent in {"preparation", "implementation"}:
        missing.append(question("migration.target_technology", "What target technology should migration preparation use?"))
    if "legacy-migration" in scopes and target_technology and not migration_intent:
        missing.append(question("migration.intent", "Is the target in scope for analysis, migration preparation, or full implementation?", ["Analyze only", "Prepare migration", "Implement migration"]))
    if not deliverables:
        missing.append(question("project.deliverables", "Which concrete outputs should initialization prepare for?"))
    if architecture_documentation and not diagram_views:
        missing.append(question("architecture.views", "Which architecture views do you expect?", DIAGRAM_VIEW_OPTIONS))
    if html_artifact and "presentation" in scopes and not audience:
        missing.append(question("dashboard.audience", "Who is the main dashboard or presentation audience?", ["Technical team", "Management", "Both", "Another audience"]))
    if html_artifact and client.get("public_sector_confidence") == UNCERTAIN and not localization["resolved"]:
        missing.append(question("client.sector", "Is this organization a public-sector client?", ["Yes", "No"]))
    elif html_artifact and client.get("public_sector") and not client.get("locale") and not localization["resolved"]:
        missing.append(question("client.locale", "Which client locale should govern delivery?", ["German (Austria)", "German (Germany)", "German (Switzerland)", "Other"]))
    elif html_artifact and not localization["resolved"]:
        missing.append(question("artifact.language", "Client-facing language?", LANGUAGE_OPTIONS))
    if "research" in scopes and not topic:
        missing.append(question("research.topic", "What topic or research question should be investigated?"))
    if "research" in scopes and not (research_goal or desired_outcome):
        missing.append(question("research.goal", "What decision or downstream artifact should the research support?"))
    if "presentation" in scopes and not topic:
        missing.append(question("presentation.topic", "What is the presentation about?"))
    if "presentation" in scopes and not audience:
        missing.append(question("presentation.audience", "Who will see the presentation?"))
    if "presentation" in scopes and not presentation_purposes:
        missing.append(question("presentation.purpose", "What presentation purpose applies?", list(PRESENTATION_PURPOSES)))
    if "presentation" in scopes and not (desired_outcome or sales_objective):
        missing.append(question("presentation.outcome", "What should the audience think or do after viewing it?"))

    if source_technology and discovered_technologies and all(
        source_technology.casefold() != value.casefold() for value in discovered_technologies
    ):
        conflicts.append({
            "id": "source-technology-conflict",
            "detail": (
                f"The brief identifies {source_technology} as the source technology, but bounded inspection "
                f"discovered {', '.join(discovered_technologies)}. Confirm the intended source boundary."
            ),
        })
    discovered = {
        "sources": discovered_sources,
        "source_technology": (
            discovered_technologies[0]
            if len(discovered_technologies) == 1
            else f"multi-language: {', '.join(discovered_technologies)}"
            if discovered_technologies
            else None
        ),
        "technologies": discovered_technologies,
    }
    return {
        "schema_version": 1,
        "mode": "brief-driven",
        "summary": brief,
        "known": known,
        "discovered": discovered,
        "inferred": inferred,
        "missing": missing,
        "conflicts": conflicts,
    }


def interactive_questions() -> list[dict[str, Any]]:
    return [
        question("project.scope", "What kind of project is this?", ["Legacy migration/analysis", "Development", "Research", "Presentation", "Hybrid / combination"]),
        question("project.goal", "What outcome, concrete deliverables, and observable definition of done matter?"),
        question("project.runtime", "Which supported agent runtime or runtimes should this project use?"),
    ]
