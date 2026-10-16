#!/usr/bin/env python3
"""Validate canonical-library structure, metadata, references, adapters, evals, and leakage."""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

from resolve_archetypes import load_contract, validate_contract
from runtime_adapters import validate_adapters
import external_capabilities
import build_capability_index
import resolve_capability_gaps
import sync_presentation
import check_presentation_visual_contract

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools" / "evals"))
from eval_common import validate_configuration as validate_eval_configuration

REQUIRED = [
    "README.md", "AGENTS.md", "VERSION", "CHANGELOG.md", "CONTRIBUTING.md",
    "catalog/skills.md", "catalog/agents.md", "catalog/tools.md", "catalog/capability-index.json",
    "catalog/templates.md", "catalog/archetypes.md",
    "evals/skills/scenarios.yaml", "evals/agents/scenarios.yaml", "evals/initialization/scenarios.yaml",
    "evals/initialization/test_initializer.py", "archetypes/composition.yaml",
    "evals/archetypes/scenarios.yaml", "evals/archetypes/test_archetypes.py",
    "archetypes/development/archetype.yaml", "archetypes/legacy-migration/archetype.yaml",
    "archetypes/presentation/archetype.yaml", "archetypes/research/archetype.yaml",
    "archetypes/overlays/architecture-documentation/overlay.yaml",
    "archetypes/overlays/branded-html/overlay.yaml",
    "archetypes/overlays/bilingual-client-delivery/overlay.yaml",
    "archetypes/overlays/durable-state/overlay.yaml",
    "archetypes/overlays/evidence-traceability/overlay.yaml",
    "archetypes/overlays/living-dashboard/overlay.yaml",
    "archetypes/overlays/sales-storytelling/overlay.yaml",
    "evals/installation/test_installer.py", "install/agent_commons.py",
    "catalog/capabilities.yaml", "tools/runtime_adapters.py", "tools/project_runtimes.py",
    "adapters/README.md", "adapters/global-instructions.md",
    "adapters/codex/adapter.yaml", "adapters/claude-code/adapter.yaml",
    "adapters/cline/adapter.yaml", "adapters/opencode/adapter.yaml",
    "adapters/codex/README.md", "adapters/claude-code/README.md",
    "adapters/cline/README.md", "adapters/opencode/README.md",
    "presentation/index.html", "presentation/README.md", "presentation/visual-contract.json",
    "presentation/assets/library-data.js", "presentation/agent-commons.html",
    "catalog/external.md", "external/README.md", "external/sources.yaml",
    "external/schema/sources.schema.json", "external/schema/index.schema.json",
    "external/schema/review.schema.json", "external/index/capabilities.json",
    "external/reviews/README.md", "external/cache/README.md",
    "tools/external_capabilities.py", "tools/resolve_capability_gaps.py", "tools/build_capability_index.py", "evals/external/scenarios.yaml",
    "evals/external/test_external_capabilities.py",
    "skills/deep-research/SKILL.md", "skills/sales-storytelling/SKILL.md",
    "skills/initialize-project/scripts/brief_intake.py",
    "skills/continue-project/SKILL.md",
    "skills/continue-project/scripts/resolve_project_continuation.py",
    "evals/tools/test_project_continuation.py",
    "skills/promote-to-commons/SKILL.md",
    "skills/localize-client-artifact/SKILL.md",
    "skills/localize-client-artifact/scripts/validate_localization.py",
    "evals/tools/test_localization.py",
    "skills/promote-to-commons/references/promotion-contract.md",
    "skills/promote-to-commons/references/report-contract.md",
    "evals/tools/test_promote_to_commons.py", "evals/tools/test_presentation_sync.py",
    "evals/tools/test_diagram_model.py",
    "tools/sync_presentation.py", "tools/refresh_commons_presentation.py",
    "tools/check_presentation_visual_contract.py", "evals/tools/test_presentation_visual_contract.py",
    "skills/update-commons-presentation/SKILL.md",
    "evals/tools/test_presentation_maintenance_contract.py",
    "skills/maintain-project-memory/scripts/manage_project_memory.py",
    "evals/tools/test_project_memory.py",
    "evals/tools/test_project_memory_benchmark.py",
    "evals/tools/benchmark_project_memory.py",
    "evals/README.md",
    "evals/contracts/capabilities.json", "evals/contracts/agents.json", "evals/contracts/thresholds.json",
    "evals/workflows/contracts.json",
    "evals/golden/README.md", "evals/golden/critical-capabilities.json", "evals/golden/agents.json",
    "evals/golden/evaluation-tools.json",
    "evals/golden/workflows.json", "evals/mutations/README.md", "evals/baselines/README.md",
    "evals/fixtures/evaluation/scenarios.json", "evals/fixtures/projects/index.json",
    "evals/fixtures/visual-regression/manifest.json",
    "evals/mutations/hard-fail-cases.json", "evals/mutations/methodology-cases.json",
    "evals/baselines/v1.0.0.json",
    "evals/schemas/eval-contract.schema.json", "evals/schemas/executor-input.schema.json",
    "evals/schemas/executor-output.schema.json", "evals/schemas/codex-executor-output.schema.json",
    "evals/schemas/judge-input.schema.json",
    "evals/schemas/judge-output.schema.json", "evals/schemas/eval-result.schema.json",
    "evals/schemas/workflow-contract.schema.json", "evals/schemas/last-green-baseline.schema.json",
    "evals/evaluation/test_eval_contracts.py", "evals/evaluation/test_impact_selector.py",
    "evals/evaluation/test_eval_runner.py", "evals/evaluation/test_benchmark_portfolio.py",
    "evals/evaluation/test_quality_baselines.py", "evals/evaluation/test_mutation_runner.py",
    "tools/evals/eval_common.py", "tools/evals/select_impacted_evals.py", "tools/evals/run_evals.py",
    "tools/evals/compare_baseline.py", "tools/evals/promote_baseline.py",
    "tools/evals/check_methodology_contracts.py", "tools/evals/run_mutations.py",
    "tools/evals/capture_visual_baselines.mjs",
    "skills/mutation-testing/SKILL.md",
    "skills/mutation-testing/references/tool-adapters.md",
    "skills/mutation-testing/references/survivor-classification.md",
    "skills/mutation-testing/references/quality-gates.md",
    "skills/mutation-testing/references/mutation-report-contract.md",
    "skills/mutation-testing/scripts/assess_mutation_quality.py",
    "skills/mutation-testing/scripts/detect_mutation_tooling.py",
    "evals/tools/test_mutation_quality.py",
    "evals/fixtures/mutation-quality/README.md",
    "evals/fixtures/mutation-quality/benchmark-cases.json",
    "evals/fixtures/mutation-quality/input/tax_calculator.py",
    "evals/fixtures/mutation-quality/input/tax_calculator_weak_suite.py",
    "evals/fixtures/mutation-quality/input/tax_calculator_hardened_suite.py",
    "reports/project-memory-and-deep-analysis.md",
    "reports/v1-dashboard-discovery-and-git-governance-hardening.md",
    "reports/mutation-testing-and-tdd-quality.md",
]
ALLOWED_REPORTS = {
    "project-memory-and-deep-analysis.md",
    "v1-dashboard-discovery-and-git-governance-hardening.md",
    "mutation-testing-and-tdd-quality.md",
}
LEAK_PATTERNS = [
    r"/Users/", r"[A-Z]:\\Users\\",
]
RESOURCE_RE = re.compile(r"(?<![\w.-])((?:scripts|references|assets)/[A-Za-z0-9_.\-/]+)")
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
YAML_BLOCK_KEY_RE = re.compile(r"^(?P<indent> *)(?P<key>[A-Za-z0-9_.-]+):(?:\s|$)")


def markdown_anchors(text: str) -> set[str]:
    anchors: set[str] = set()
    for heading in re.findall(r"(?m)^#{1,6}\s+(.+?)\s*$", text):
        value = re.sub(r"<[^>]+>", "", heading).strip().lower()
        value = re.sub(r"[^a-z0-9 _-]", "", value)
        value = re.sub(r"[ _]+", "-", value).strip("-")
        if value:
            anchors.add(value)
    return anchors


def local_markdown_link_errors(root: Path) -> list[str]:
    errors: list[str] = []
    for source in sorted(root.rglob("*.md")):
        if any(part in {".git", ".idea", ".playwright-cli", "output"} for part in source.parts):
            continue
        text = source.read_text(encoding="utf-8", errors="replace")
        for raw_target in MARKDOWN_LINK_RE.findall(text):
            target = raw_target.strip()
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            elif " " in target:
                target = target.split(" ", 1)[0]
            if not target or target.startswith(("#", "http://", "https://", "mailto:", "data:")):
                continue
            path_text, _, fragment = target.partition("#")
            resolved = (source.parent / unquote(path_text)).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                errors.append(f"{source.relative_to(root)}: local link escapes repository {target}")
                continue
            if not resolved.exists():
                errors.append(f"{source.relative_to(root)}: missing local link target {path_text}")
                continue
            if fragment and resolved.is_file() and resolved.suffix.lower() == ".md":
                anchors = markdown_anchors(resolved.read_text(encoding="utf-8", errors="replace"))
                if unquote(fragment).lower() not in anchors:
                    errors.append(f"{source.relative_to(root)}: missing heading fragment {target}")
    return errors


def yaml_duplicate_mapping_key_errors(text: str, label: str) -> list[str]:
    """Report duplicate block-mapping keys without accepting silent overwrites."""
    errors: list[str] = []
    ancestry: list[tuple[int, str]] = []
    seen: dict[tuple[str, ...], dict[str, int]] = {}
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = YAML_BLOCK_KEY_RE.match(line)
        if not match:
            continue
        indent = len(match.group("indent"))
        key = match.group("key")
        while ancestry and ancestry[-1][0] >= indent:
            ancestry.pop()
        parent = tuple(item[1] for item in ancestry)
        first_lines = seen.setdefault(parent, {})
        if key in first_lines:
            path = ".".join((*parent, key))
            errors.append(
                f"{label}:{line_number}: duplicate mapping key {path} "
                f"(first at line {first_lines[key]})"
            )
        else:
            first_lines[key] = line_number
        ancestry.append((indent, key))
    return errors


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("unterminated YAML frontmatter")
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")
    for obsolete in ("provenance",):
        if (ROOT / obsolete).exists():
            errors.append(f"obsolete product-archaeology path remains: {obsolete}/")
    reports = ROOT / "reports"
    if reports.is_dir():
        unexpected_reports = sorted(
            path.name for path in reports.iterdir()
            if path.is_file() and path.name not in ALLOWED_REPORTS
        )
        if unexpected_reports:
            errors.append(f"unexpected product report files: {unexpected_reports}")
    errors.extend(f"markdown link: {error}" for error in local_markdown_link_errors(ROOT))
    errors.extend(f"evaluation architecture: {error}" for error in validate_eval_configuration())

    errors.extend(f"archetype contract: {error}" for error in validate_contract())
    errors.extend(f"capability expectations: {error}" for error in resolve_capability_gaps.validate_expectations())
    errors.extend(f"runtime adapter: {error}" for error in validate_adapters())
    try:
        external_registry = external_capabilities.load_json(ROOT / "external" / "sources.yaml")
        external_index = external_capabilities.load_json(ROOT / "external" / "index" / "capabilities.json")
        errors.extend(f"external registry: {error}" for error in external_capabilities.validate_registry(external_registry))
        external_errors, external_warnings = external_capabilities.validate_index(external_index, external_registry)
        errors.extend(f"external index: {error}" for error in external_errors)
        warnings.extend(f"external index: {warning}" for warning in external_warnings)
        for review in sorted((ROOT / "external" / "reviews").glob("*.md")):
            if review.name != "README.md":
                errors.extend(f"external review: {error}" for error in external_capabilities.validate_review(review))
    except external_capabilities.ExternalCapabilityError as exc:
        errors.append(f"external intelligence: {exc}")
    try:
        composition = load_contract()
    except ValueError:
        composition = {}
    archetype_catalog = (ROOT / "catalog" / "archetypes.md").read_text(encoding="utf-8") if (ROOT / "catalog" / "archetypes.md").exists() else ""
    for registry_name in ("archetypes", "overlays"):
        for identifier in composition.get(registry_name, {}):
            if f"`{identifier}`" not in archetype_catalog:
                errors.append(f"catalog/archetypes.md does not expose {registry_name[:-1]} {identifier}")

    errors.extend(f"presentation: {error}" for error in sync_presentation.validate())
    errors.extend(
        f"presentation visual contract: {error}"
        for error in check_presentation_visual_contract.validate_current()
    )
    expected_index = build_capability_index.generate()
    try:
        actual_index = json.loads((ROOT / "catalog" / "capability-index.json").read_text(encoding="utf-8"))
        if actual_index != expected_index:
            errors.append("catalog/capability-index.json is stale; run tools/build_capability_index.py")
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"capability index: {exc}")

    skill_names = []
    for skill_dir in sorted((ROOT / "skills").iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file():
            errors.append(f"missing SKILL.md: {skill_dir.name}")
            continue
        text = skill_file.read_text(encoding="utf-8")
        try:
            metadata = frontmatter(text)
        except ValueError as exc:
            errors.append(f"{skill_dir.name}: {exc}")
            continue
        if set(metadata) != {"name", "description"}:
            errors.append(f"{skill_dir.name}: frontmatter keys must be name and description")
        if metadata.get("name") != skill_dir.name:
            errors.append(f"{skill_dir.name}: name does not match directory")
        if not metadata.get("description") or len(metadata["description"]) < 40:
            errors.append(f"{skill_dir.name}: description is missing or too short")
        if "Do not use" not in metadata.get("description", ""):
            errors.append(f"{skill_dir.name}: description must state when not to use it")
        if "TODO" in text or "[TODO" in text:
            errors.append(f"{skill_dir.name}: unresolved TODO in SKILL.md")
        skill_names.append(skill_dir.name)
        if re.search(r"\$[a-z][a-z0-9-]+", text):
            errors.append(f"{skill_dir.name}: canonical workflow contains runtime-specific $ invocation syntax")
        if re.search(r"\.codex/", text, re.I):
            errors.append(f"{skill_dir.name}: canonical workflow contains a Codex installation path")
        for relative in RESOURCE_RE.findall(text):
            cleaned = relative.rstrip(".,;:)")
            if not (skill_dir / cleaned).exists():
                errors.append(f"{skill_dir.name}: missing referenced resource {cleaned}")
        if len(text.splitlines()) > 500:
            warnings.append(f"{skill_dir.name}: SKILL.md exceeds 500 lines")

    try:
        capability_catalog = json.loads((ROOT / "catalog" / "capabilities.yaml").read_text(encoding="utf-8"))
        catalog_skill_ids = set(capability_catalog.get("skills", {}))
        filesystem_skill_ids = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
        if filesystem_skill_ids != catalog_skill_ids:
            errors.append(
                "skill catalog/filesystem mismatch: "
                f"missing={sorted(filesystem_skill_ids - catalog_skill_ids)} "
                f"stale={sorted(catalog_skill_ids - filesystem_skill_ids)}"
            )
        filesystem_agent_ids = {path.stem for path in (ROOT / "agents").glob("*.yaml")}
        catalog_agent_ids = set(capability_catalog.get("agents", {}))
        if filesystem_agent_ids != catalog_agent_ids:
            errors.append(
                "agent catalog/filesystem mismatch: "
                f"missing={sorted(filesystem_agent_ids - catalog_agent_ids)} "
                f"stale={sorted(catalog_agent_ids - filesystem_agent_ids)}"
            )
        for kind in capability_catalog.get("capability_kinds", []):
            seen_paths: set[str] = set()
            for identifier, entry in capability_catalog.get(kind, {}).items():
                relative = entry.get("path") if isinstance(entry, dict) else None
                if not isinstance(relative, str) or not relative:
                    errors.append(f"catalog {kind}:{identifier} has no path")
                    continue
                if relative in seen_paths:
                    errors.append(f"catalog {kind} reuses path: {relative}")
                seen_paths.add(relative)
                if not (ROOT / relative).is_file() and not (ROOT / relative).is_dir():
                    errors.append(f"catalog {kind}:{identifier} points to missing path {relative}")
        for identifier, entry in capability_catalog.get("skills", {}).items():
            related = entry.get("related", [])
            if not isinstance(related, list):
                errors.append(f"catalog skill {identifier}: related must be a list")
                continue
            unknown = sorted(set(related) - catalog_skill_ids)
            if unknown:
                errors.append(f"catalog skill {identifier}: unknown related skills {unknown}")
            if identifier in related:
                errors.append(f"catalog skill {identifier}: cannot relate to itself")
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"capability catalog relationships: {exc}")

    skill_eval = (ROOT / "evals/skills/scenarios.yaml").read_text(encoding="utf-8") if (ROOT / "evals/skills/scenarios.yaml").exists() else ""
    errors.extend(yaml_duplicate_mapping_key_errors(skill_eval, "evals/skills/scenarios.yaml"))
    for name in skill_names:
        if f"  {name}:" not in skill_eval:
            errors.append(f"missing skill evaluation: {name}")

    agent_names = [path.stem for path in sorted((ROOT / "agents").glob("*.yaml"))]
    for path in sorted((ROOT / "agents").glob("*.yaml")):
        try:
            agent = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON-compatible agent YAML {path.name}: {exc}")
            continue
        required_agent_fields = {"id", "kind", "version", "description", "instructions"}
        missing = required_agent_fields - agent.keys()
        if missing:
            errors.append(f"{path.name}: missing required fields {sorted(missing)}")
        if agent.get("id") != path.stem or agent.get("kind") != "agent":
            errors.append(f"{path.name}: id or kind does not match canonical agent")
    agent_eval = (ROOT / "evals/agents/scenarios.yaml").read_text(encoding="utf-8") if (ROOT / "evals/agents/scenarios.yaml").exists() else ""
    for name in agent_names:
        if f"  {name}:" not in agent_eval:
            errors.append(f"missing agent evaluation: {name}")

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip() if (ROOT / "VERSION").exists() else ""
    initializer = ROOT / "skills" / "initialize-project" / "scripts" / "initialize_project.py"
    if version and initializer.exists() and f'LIBRARY_VERSION = "{version}"' not in initializer.read_text(encoding="utf-8"):
        errors.append("VERSION does not match initializer LIBRARY_VERSION")

    for path in sorted(ROOT.rglob("*.py")):
        if ".git" in path.parts:
            continue
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            errors.append(f"syntax error: {path.relative_to(ROOT)}:{exc.lineno}: {exc.msg}")

    promoted_roots = [ROOT / "skills", ROOT / "agents", ROOT / "templates", ROOT / "archetypes"]
    for base in promoted_roots:
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {".md", ".yaml", ".yml", ".json", ".py", ".html", ".toml"}:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for pattern in LEAK_PATTERNS:
                if re.search(pattern, text, re.I):
                    errors.append(f"possible project-specific leakage in {path.relative_to(ROOT)}: {pattern}")

    print(f"skills={len(skill_names)} agents={len(agent_names)} errors={len(errors)} warnings={len(warnings)}")
    for warning in warnings:
        print(f"WARNING {warning}")
    for error in errors:
        print(f"ERROR {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
