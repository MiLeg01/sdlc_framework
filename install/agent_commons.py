#!/usr/bin/env python3
"""Install, inspect, synchronize, repair, and remove Agent Commons runtime adapters safely."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import sys
import tempfile
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError:
        tomllib = None  # type: ignore[assignment]
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePath
from typing import Any, Mapping


def repository_root_from_installer(installer_path: PurePath) -> PurePath:
    """Derive the repository root without assuming where the checkout lives."""
    return installer_path.parents[1]


LIBRARY_ROOT = Path(repository_root_from_installer(Path(__file__).resolve()))
sys.path.insert(0, str(LIBRARY_ROOT / "tools"))

from runtime_adapters import (  # noqa: E402
    RUNTIMES,
    AdapterError,
    adapter_manifest,
    canonical_global_instructions,
    capability_path,
    load_catalog,
    render_agent,
    render_skill_wrapper,
    runtime_user_path,
    validate_adapters,
    wrapper_skill_name,
)
from skill_catalog import (  # noqa: E402
    SkillCatalogError,
    discover_canonical_skills,
    inspect_canonical_skills,
    parse_frontmatter,
)


MANIFEST_VERSION = 3
SUPPORTED_MANIFEST_VERSIONS = {2, MANIFEST_VERSION}
INSTALL_MODES = ("auto", "symlink", "copy")
BEGIN_MARKER = "<!-- BEGIN AGENT COMMONS MANAGED -->"
END_MARKER = "<!-- END AGENT COMMONS MANAGED -->"
ALL_MANAGED_SCOPES = ("skills", "agents", "global_instructions")


class InstallError(RuntimeError):
    """A safe installation cannot proceed."""


@dataclass(frozen=True)
class PlatformContext:
    key: str
    display_name: str

    @classmethod
    def detect(cls, system_name: str | None = None) -> "PlatformContext":
        detected = (system_name or platform.system()).strip().lower()
        if detected == "windows":
            return cls("windows", "Windows")
        if detected == "darwin":
            return cls("macos", "macOS")
        if detected == "linux":
            return cls("linux", "Linux")
        return cls(detected or os.name, system_name or platform.system() or os.name)


@dataclass(frozen=True)
class CodexSkillState:
    canonical_id: str
    name: str
    source: Path
    target: Path
    status: str
    installed: bool
    discoverable: bool
    detail: str = ""


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def expand_environment_variables(value: str, environment: Mapping[str, str] | None = None) -> str:
    """Expand both PowerShell-style %NAME% and conventional shell variables."""
    variables = os.environ if environment is None else environment

    def replace_percent(match: re.Match[str]) -> str:
        name = match.group(1)
        return variables.get(name, variables.get(name.upper(), match.group(0)))

    expanded = re.sub(r"%([A-Za-z_][A-Za-z0-9_]*)%", replace_percent, value)
    if environment is None:
        return os.path.expandvars(expanded)
    for name, replacement in variables.items():
        expanded = expanded.replace(f"${{{name}}}", replacement).replace(f"${name}", replacement)
    return expanded


def normalize_path(value: str | os.PathLike[str], home: Path | None = None) -> Path:
    raw = expand_environment_variables(os.fspath(value))
    if home is not None and (raw == "~" or raw.startswith("~/") or raw.startswith("~\\")):
        suffix = raw[2:] if len(raw) > 1 else ""
        raw = str(home / suffix) if suffix else str(home)
    return Path(raw).expanduser().resolve()


def sha256_text(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_tree(root: Path) -> str:
    """Hash names, entry kinds, link targets, and file bytes deterministically."""
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        if path.is_symlink():
            digest.update(b"L\0" + relative + b"\0" + os.readlink(path).encode("utf-8") + b"\0")
        elif path.is_dir():
            digest.update(b"D\0" + relative + b"\0")
        elif path.is_file():
            digest.update(b"F\0" + relative + b"\0")
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
            digest.update(b"\0")
    return digest.hexdigest()


def lexical_link_target(path: Path) -> Path:
    raw = Path(os.readlink(path))
    return raw if raw.is_absolute() else path.parent / raw


def same_link(path: Path, source: Path) -> bool:
    if not path.is_symlink():
        return False
    target = lexical_link_target(path)
    try:
        return os.path.samestat(os.stat(target), os.stat(source))
    except OSError:
        # os.stat follows the link, so a governed canonical deletion leaves it dangling. Compare
        # lexically there, or repair reads its own unchanged link as a user modification and
        # refuses to remove the obsolete artifact.
        return target.resolve(strict=False) == source.resolve(strict=False)


def path_exists(path: Path) -> bool:
    return os.path.lexists(path)


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def atomic_copytree(source: Path, target: Path, *, preserve_symlinks: bool = True) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary_root = Path(tempfile.mkdtemp(prefix=f".{target.name}.", dir=target.parent))
    staged = temporary_root / "content"
    try:
        shutil.copytree(source, staged, symlinks=preserve_symlinks)
        os.replace(staged, target)
    finally:
        if temporary_root.exists():
            shutil.rmtree(temporary_root)


class Installer:
    def __init__(
        self,
        library: Path,
        home: Path,
        *,
        platform_context: PlatformContext | None = None,
        symlink_support: bool | None = None,
    ) -> None:
        self.home = normalize_path(home)
        self.library = normalize_path(library, self.home)
        self.platform = platform_context or PlatformContext.detect()
        self.state_home = self.home / ".agent-commons"
        self.manifest_path = self.state_home / "install-manifest.json"
        self.backup_root = self.state_home / "backups"
        self.changes: list[str] = []
        self.notices: list[str] = []
        self.backups: list[dict[str, str]] = []
        self._symlink_support = symlink_support

    @property
    def library_version(self) -> str:
        path = self.library / "VERSION"
        return path.read_text(encoding="utf-8").strip() if path.is_file() else "unknown"

    def validate_sources(self) -> list[str]:
        issues = validate_adapters(self.library, strict_catalog=False)
        try:
            discover_canonical_skills(self.library)
        except SkillCatalogError as exc:
            issues.append(str(exc))
        for relative in ("VERSION", "catalog/capabilities.yaml", "adapters/global-instructions.md"):
            if not (self.library / relative).is_file():
                issues.append(f"canonical library file is missing: {self.library / relative}")
        return issues

    def supports_symlinks(self) -> bool:
        if self._symlink_support is not None:
            return self._symlink_support
        probe_parent = self.home if self.home.is_dir() else None
        try:
            with tempfile.TemporaryDirectory(prefix="agent-commons-link-probe-", dir=probe_parent) as temporary:
                root = Path(temporary)
                source = root / "source"
                link = root / "link"
                source.mkdir()
                link.symlink_to(source, target_is_directory=True)
                self._symlink_support = link.is_symlink() and link.resolve() == source.resolve()
        except (NotImplementedError, OSError):
            self._symlink_support = False
        return self._symlink_support

    def recommended_install_mode(self) -> str:
        return "symlink" if self.supports_symlinks() else "copy"

    def resolve_install_mode(self, requested: str, previous_runtime: dict[str, Any] | None = None) -> str:
        if requested not in INSTALL_MODES:
            raise InstallError(f"unsupported install mode: {requested}")
        if requested == "auto" and previous_runtime:
            recorded = previous_runtime.get("install_mode")
            if recorded == "copy":
                return "copy"
            if recorded == "symlink":
                return "symlink" if self.supports_symlinks() else "copy"
            prior_types = {entry.get("type") for entry in previous_runtime.get("artifacts", [])}
            if "copy" in prior_types:
                return "copy"
            if "symlink" in prior_types:
                return "symlink" if self.supports_symlinks() else "copy"
        if requested == "copy":
            return "copy"
        if requested == "symlink":
            if not self.supports_symlinks():
                raise InstallError(
                    "symbolic links were explicitly requested but cannot be created; "
                    "enable Windows Developer Mode or suitable privileges, or use --install-mode copy"
                )
            return "symlink"
        return self.recommended_install_mode()

    def load_manifest(self, required: bool = False) -> dict[str, Any] | None:
        if not self.manifest_path.exists():
            if required:
                raise InstallError(f"managed manifest is missing: {self.manifest_path}")
            return None
        try:
            data = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise InstallError(f"cannot read managed manifest: {exc}") from exc
        if data.get("manifest_version") not in SUPPORTED_MANIFEST_VERSIONS:
            raise InstallError(f"unsupported managed manifest version: {data.get('manifest_version')!r}")
        return data

    def previous_runtime(self, manifest: dict[str, Any] | None, runtime: str) -> dict[str, Any]:
        return dict(((manifest or {}).get("runtimes", {}).get(runtime, {}) or {}))

    def previous_artifacts(self, manifest: dict[str, Any] | None, runtime: str) -> list[dict[str, Any]]:
        return list(self.previous_runtime(manifest, runtime).get("artifacts", []))

    @staticmethod
    def prior_for_target(previous: list[dict[str, Any]], target: Path) -> dict[str, Any] | None:
        return next((entry for entry in previous if entry.get("target") == str(target)), None)

    @staticmethod
    def prior_for_id(previous: list[dict[str, Any]], identifier: str) -> dict[str, Any] | None:
        return next((entry for entry in previous if entry.get("id") == identifier), None)

    def user_path(self, runtime: str, destination: str) -> Path:
        return Path(runtime_user_path(self.home, runtime, destination))

    def global_path(self, runtime: str) -> Path:
        return self.user_path(runtime, "global_instructions")

    def skill_target(self, runtime: str, identifier: str) -> Path:
        base = self.user_path(runtime, "skills")
        return base / identifier if runtime in {"codex", "claude-code"} else base / identifier / "SKILL.md"

    def agent_target(self, runtime: str, identifier: str, filename: str) -> Path:
        base = self.user_path(runtime, "agents")
        if runtime != "cline":
            return base / filename
        return base / wrapper_skill_name(runtime, identifier, "agent") / filename

    @staticmethod
    def render_codex_collision_alias(identifier: str, alias_name: str, description: str, source: Path) -> str:
        return f'''---
name: {alias_name}
description: Apply the canonical Agent Commons {identifier} workflow. {description}
---

# Managed Agent Commons Codex alias

The canonical `${identifier}` name is occupied by another user skill. Before acting, read `{source}`
completely and follow that workflow. Resolve relative resources from `{source.parent}`.
'''

    def desired_artifacts(
        self,
        runtime: str,
        install_mode: str,
        previous: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        catalog = load_catalog(self.library)
        previous = previous or []
        artifacts: list[dict[str, Any]] = []
        for skill in discover_canonical_skills(self.library):
            identifier = skill.canonical_id
            target = self.skill_target(runtime, identifier)
            prior = self.prior_for_id(previous, identifier)
            if runtime == "codex":
                normal_is_current = (
                    same_link(target, skill.directory)
                    or (
                        target.is_dir()
                        and not target.is_symlink()
                        and sha256_tree(target) == sha256_tree(skill.directory)
                    )
                )
                use_alias = bool(prior and prior.get("kind") == "skill-alias") or (
                    prior is None and path_exists(target) and not normal_is_current
                )
                if use_alias:
                    alias_name = str((prior or {}).get("invocation_name") or f"agent-commons-{skill.name}")
                    alias_target = self.user_path("codex", "skills") / alias_name / "SKILL.md"
                    content = self.render_codex_collision_alias(
                        identifier,
                        alias_name,
                        skill.description,
                        skill.skill_file,
                    )
                    artifacts.append({
                        "type": "file",
                        "kind": "skill-alias",
                        "id": identifier,
                        "source": str(skill.skill_file),
                        "target": str(alias_target),
                        "content": content,
                        "sha256": sha256_text(content),
                        "invocation_name": alias_name,
                        "collision_target": str(target),
                    })
                    continue
            if runtime in {"codex", "claude-code"}:
                source = capability_path("skills", identifier, self.library).parent
                if install_mode == "symlink":
                    artifacts.append({
                        "type": "symlink", "kind": "skill", "id": identifier,
                        "source": str(source), "target": str(target), "install_mode": install_mode,
                    })
                else:
                    artifacts.append({
                        "type": "copy", "kind": "skill", "id": identifier,
                        "source": str(source), "target": str(target), "install_mode": install_mode,
                        "sha256": sha256_tree(source),
                    })
            else:
                content = render_skill_wrapper(runtime, identifier, self.library)
                artifacts.append({
                    "type": "file", "kind": "skill-wrapper", "id": identifier,
                    "target": str(target), "content": content, "sha256": sha256_text(content),
                })
        for identifier in catalog["agents"]:
            filename, content = render_agent(runtime, identifier, self.library)
            artifacts.append({
                "type": "file", "kind": "agent" if runtime != "cline" else "agent-role-wrapper",
                "id": identifier, "target": str(self.agent_target(runtime, identifier, filename)),
                "content": content, "sha256": sha256_text(content),
            })
        section = f"{BEGIN_MARKER}\n{canonical_global_instructions(self.library)}\n{END_MARKER}"
        artifacts.append({
            "type": "managed-section", "kind": "global-instructions",
            "id": "agent-commons-working-agreements", "target": str(self.global_path(runtime)),
            "content": section, "sha256": sha256_text(section),
        })
        return artifacts

    @staticmethod
    def split_managed_section(path: Path, content: str) -> tuple[str, str, str] | None:
        starts = content.count(BEGIN_MARKER)
        ends = content.count(END_MARKER)
        if starts == 0 and ends == 0:
            return None
        if starts != 1 or ends != 1:
            raise InstallError(f"ambiguous Agent Commons markers in {path}")
        begin = content.index(BEGIN_MARKER)
        end = content.index(END_MARKER, begin) + len(END_MARKER)
        return content[:begin], content[begin:end], content[end:]

    def backup(self, path: Path) -> None:
        if not path.exists() or path.is_symlink():
            return
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        directory = self.backup_root / stamp
        counter = 1
        while directory.exists():
            counter += 1
            directory = self.backup_root / f"{stamp}-{counter}"
        try:
            relative = path.relative_to(self.home)
        except ValueError:
            relative = Path(path.name)
        destination = directory / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if path.is_dir():
            shutil.copytree(path, destination, symlinks=True)
            digest = sha256_tree(destination)
        else:
            shutil.copy2(path, destination)
            digest = sha256_file(destination)
        self.backups.append({"source": str(path), "backup": str(destination), "sha256": digest})
        self.changes.append(f"backed up: {path} -> {destination}")

    def target_matches_prior(self, target: Path, prior: dict[str, Any]) -> bool:
        prior_type = prior.get("type")
        if prior_type == "symlink":
            return path_exists(target) and same_link(target, Path(prior["source"]))
        if prior_type == "copy":
            return target.is_dir() and not target.is_symlink() and sha256_tree(target) == prior.get("sha256")
        if prior_type == "file":
            return target.is_file() and not target.is_symlink() and sha256_file(target) == prior.get("sha256")
        if prior_type == "managed-section" and target.is_file() and not target.is_symlink():
            split = self.split_managed_section(target, target.read_text(encoding="utf-8"))
            return split is not None and sha256_text(split[1]) == prior.get("sha256")
        return False

    def target_matches_desired(self, target: Path, artifact: dict[str, Any]) -> bool:
        artifact_type = artifact["type"]
        if artifact_type == "symlink":
            return path_exists(target) and same_link(target, Path(artifact["source"])) and target.exists()
        if artifact_type == "copy":
            return target.is_dir() and not target.is_symlink() and sha256_tree(target) == artifact["sha256"]
        if artifact_type == "file":
            return target.is_file() and not target.is_symlink() and sha256_file(target) == artifact["sha256"]
        if target.is_file() and not target.is_symlink():
            split = self.split_managed_section(target, target.read_text(encoding="utf-8"))
            return split is not None and split[1] == artifact["content"]
        return False

    def preflight(self, desired: list[dict[str, Any]], previous: list[dict[str, Any]], repair: bool) -> None:
        conflicts: list[str] = []
        for artifact in desired:
            target = Path(artifact["target"])
            prior = self.prior_for_target(previous, target)
            if (
                artifact.get("kind") == "skill-alias"
                and not path_exists(target)
                and target.parent.is_dir()
                and any(target.parent.iterdir())
                and prior is None
            ):
                conflicts.append(f"unrelated collision-alias directory: {target.parent}")
                continue
            if not path_exists(target) or self.target_matches_desired(target, artifact):
                continue
            if artifact["type"] == "managed-section" and target.is_file() and not target.is_symlink():
                split = self.split_managed_section(target, target.read_text(encoding="utf-8"))
                if split is None:
                    continue
            if prior and (repair or self.target_matches_prior(target, prior)):
                continue
            label = "directory" if artifact["type"] == "copy" else "path"
            conflicts.append(f"unrelated or locally modified {label}: {target}")
        if conflicts:
            raise InstallError(
                "refusing to overwrite user or drifted content; use repair only for manifest-owned artifacts:\n  - "
                + "\n  - ".join(conflicts)
            )

    def replace_target(self, target: Path) -> None:
        if not path_exists(target):
            return
        if not target.is_symlink():
            self.backup(target)
        remove_path(target)

    def apply_artifact(self, artifact: dict[str, Any]) -> None:
        target = Path(artifact["target"])
        if self.target_matches_desired(target, artifact):
            self.notices.append(f"ok {artifact['kind']}: {target}")
            return
        artifact_type = artifact["type"]
        if artifact_type == "symlink":
            self.replace_target(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(Path(artifact["source"]), target_is_directory=True)
            self.changes.append(f"created {artifact['kind']} symlink: {target} -> {artifact['source']}")
            return
        if artifact_type == "copy":
            self.replace_target(target)
            atomic_copytree(Path(artifact["source"]), target, preserve_symlinks=False)
            self.changes.append(f"synchronized managed {artifact['kind']} copy: {target}")
            return
        if artifact_type == "file":
            self.replace_target(target)
            atomic_write(target, artifact["content"])
            self.changes.append(f"wrote {artifact['kind']}: {target}")
            return
        existed = target.exists()
        content = target.read_text(encoding="utf-8") if existed else ""
        split = self.split_managed_section(target, content)
        if split is None:
            updated = content.rstrip()
            if updated:
                updated += "\n\n"
            updated += artifact["content"] + "\n"
        else:
            updated = split[0] + artifact["content"] + split[2]
        if existed:
            self.backup(target)
        atomic_write(target, updated)
        self.changes.append(f"updated managed global instructions: {target}")

    def artifact_record(self, artifact: dict[str, Any]) -> dict[str, Any]:
        record = {key: value for key, value in artifact.items() if key != "content"}
        record["source_version"] = self.library_version
        record["last_sync"] = now()
        return record

    def manifest_data(
        self,
        previous: dict[str, Any] | None,
        runtime: str,
        install_mode: str,
        artifacts: list[dict[str, Any]],
        managed_scopes: list[str],
    ) -> dict[str, Any]:
        runtimes = dict((previous or {}).get("runtimes", {}))
        prior_runtime = runtimes.get(runtime) or {}
        runtimes[runtime] = {
            "installed_at": prior_runtime.get("installed_at", now()),
            "updated_at": now(),
            "install_mode": install_mode,
            "platform": self.platform.key,
            "managed_scopes": managed_scopes,
            "artifacts": [self.artifact_record(entry) for entry in artifacts],
        }
        return {
            "manifest_version": MANIFEST_VERSION,
            "library": str(self.library),
            "library_version": self.library_version,
            "installed_at": (previous or {}).get("installed_at", now()),
            "updated_at": now(),
            "runtimes": runtimes,
            "backups": list((previous or {}).get("backups", [])) + self.backups,
        }

    @staticmethod
    def comparable_manifest(value: dict[str, Any]) -> dict[str, Any]:
        result = json.loads(json.dumps(value))
        result.pop("updated_at", None)
        for runtime in result.get("runtimes", {}).values():
            runtime.pop("updated_at", None)
            for artifact in runtime.get("artifacts", []):
                artifact.pop("last_sync", None)
        return result

    def write_manifest_if_needed(self, previous: dict[str, Any] | None, candidate: dict[str, Any]) -> None:
        if previous and self.comparable_manifest(candidate) == self.comparable_manifest(previous):
            self.notices.append(f"ok managed manifest: {self.manifest_path}")
            return
        self.state_home.mkdir(parents=True, exist_ok=True)
        atomic_write(self.manifest_path, json.dumps(candidate, indent=2, sort_keys=True) + "\n")
        self.changes.append(f"wrote managed manifest: {self.manifest_path}")
        self.backups.clear()

    def install_runtime(
        self,
        runtime: str,
        requested_mode: str,
        repair: bool = False,
        *,
        skills_only: bool = False,
    ) -> None:
        issues = self.validate_sources()
        if issues:
            raise InstallError("canonical validation failed:\n  - " + "\n  - ".join(issues))
        previous_manifest = self.load_manifest()
        if previous_manifest and normalize_path(previous_manifest.get("library", ""), self.home) != self.library:
            raise InstallError(f"manifest belongs to another canonical library: {previous_manifest.get('library')}")
        prior_runtime = self.previous_runtime(previous_manifest, runtime)
        install_mode = self.resolve_install_mode(requested_mode, prior_runtime)
        previous_all = self.previous_artifacts(previous_manifest, runtime)
        desired_all = self.desired_artifacts(runtime, install_mode, previous_all)
        if skills_only:
            desired = [entry for entry in desired_all if str(entry.get("kind", "")).startswith("skill")]
            previous = [entry for entry in previous_all if str(entry.get("kind", "")).startswith("skill")]
            retained = [entry for entry in previous_all if not str(entry.get("kind", "")).startswith("skill")]
            prior_scopes = set(prior_runtime.get("managed_scopes", []))
            managed_scopes = sorted(prior_scopes | {"skills"})
        else:
            desired = desired_all
            previous = previous_all
            retained = []
            managed_scopes = list(ALL_MANAGED_SCOPES)
        desired_targets = {entry["target"] for entry in desired}
        obsolete = [entry for entry in previous if entry.get("target") not in desired_targets]
        if obsolete and not repair:
            raise InstallError(
                "managed artifacts are no longer present in the canonical adapter set; "
                "run repair to remove unchanged managed ghosts safely:\n  - "
                + "\n  - ".join(str(entry.get("target")) for entry in obsolete)
            )
        unsafe_obsolete = [
            entry
            for entry in obsolete
            if path_exists(Path(entry["target"])) and not self.target_matches_prior(Path(entry["target"]), entry)
        ]
        if unsafe_obsolete:
            raise InstallError(
                "refusing to remove changed obsolete managed artifacts:\n  - "
                + "\n  - ".join(str(entry.get("target")) for entry in unsafe_obsolete)
            )
        self.preflight(desired, previous, repair)
        for artifact in desired:
            self.apply_artifact(artifact)
        for artifact in obsolete:
            target = Path(artifact["target"])
            if not path_exists(target):
                self.notices.append(f"obsolete managed artifact already absent: {target}")
                continue
            if not target.is_symlink():
                self.backup(target)
            remove_path(target)
            if artifact.get("kind") == "skill-alias" and target.parent.is_dir() and not any(target.parent.iterdir()):
                target.parent.rmdir()
            self.changes.append(f"removed obsolete managed {artifact.get('kind', 'artifact')}: {target}")
        candidate = self.manifest_data(
            previous_manifest,
            runtime,
            install_mode,
            retained + desired,
            managed_scopes,
        )
        self.write_manifest_if_needed(previous_manifest, candidate)

    def classify_artifact(self, artifact: dict[str, Any], prior: dict[str, Any]) -> tuple[str, str]:
        target = Path(artifact["target"])
        artifact_type = artifact["type"]
        if not path_exists(target):
            return "MISSING", str(target)
        if artifact_type == "symlink":
            if not target.is_symlink() or not same_link(target, Path(artifact["source"])):
                return "MODIFIED", str(target)
            if not target.exists():
                return "BROKEN", str(target)
            return "CURRENT", str(target)
        if artifact_type == "copy":
            if not target.is_dir() or target.is_symlink():
                return "MODIFIED", str(target)
            current_hash = sha256_tree(target)
            if current_hash == artifact["sha256"]:
                return "CURRENT", str(target)
            if current_hash == prior.get("sha256"):
                return "OUTDATED", str(target)
            return "MODIFIED", str(target)
        if artifact_type == "file":
            if not target.is_file() or target.is_symlink():
                return "MODIFIED", str(target)
            current_hash = sha256_file(target)
            if current_hash == artifact["sha256"]:
                return "CURRENT", str(target)
            if current_hash == prior.get("sha256"):
                return "OUTDATED", str(target)
            return "MODIFIED", str(target)
        if not target.is_file() or target.is_symlink():
            return "MODIFIED", str(target)
        split = self.split_managed_section(target, target.read_text(encoding="utf-8"))
        if split is None:
            return "MISSING", str(target)
        section_hash = sha256_text(split[1])
        if section_hash == artifact["sha256"]:
            return "CURRENT", str(target)
        if section_hash == prior.get("sha256"):
            return "OUTDATED", str(target)
        return "MODIFIED", str(target)

    def verification_issues(self, runtime: str) -> list[str]:
        issues = [f"INVALID canonical source: {issue}" for issue in self.validate_sources()]
        try:
            manifest = self.load_manifest(required=True)
        except InstallError as exc:
            return issues + [f"MISSING {exc}"]
        assert manifest is not None
        if normalize_path(manifest.get("library", ""), self.home) != self.library:
            issues.append(f"MODIFIED manifest canonical library mismatch: {manifest.get('library')}")
        prior_runtime = self.previous_runtime(manifest, runtime)
        recorded = list(prior_runtime.get("artifacts", []))
        if not recorded:
            return issues + [f"MISSING runtime is not installed: {runtime}"]
        install_mode = self.resolve_install_mode("auto", prior_runtime)
        managed_scopes = set(prior_runtime.get("managed_scopes", ALL_MANAGED_SCOPES))
        desired = [
            artifact
            for artifact in self.desired_artifacts(runtime, install_mode, recorded)
            if self.artifact_scope(artifact) in managed_scopes
        ]
        recorded = [artifact for artifact in recorded if self.artifact_scope(artifact) in managed_scopes]
        if {entry["target"] for entry in recorded} != {entry["target"] for entry in desired}:
            issues.append(f"OUTDATED managed manifest entries do not match the {runtime} adapter set")
        for artifact in desired:
            target = Path(artifact["target"])
            prior = self.prior_for_target(recorded, target) or {}
            state, location = self.classify_artifact(artifact, prior)
            if state != "CURRENT":
                issues.append(f"{state} [{artifact['kind']}] {location}")
        return issues

    @staticmethod
    def artifact_scope(artifact: dict[str, Any]) -> str:
        kind = str(artifact.get("kind", ""))
        if kind.startswith("skill"):
            return "skills"
        if kind.startswith("agent"):
            return "agents"
        return "global_instructions"

    def disabled_codex_skill_paths(self) -> tuple[set[Path], list[str]]:
        if tomllib is None:
            return set(), ["WARN: tomllib not available (Python < 3.11); install tomli or upgrade Python to read Codex config"]
        config = self.home / ".codex" / "config.toml"
        if not config.is_file():
            return set(), []
        try:
            data = tomllib.loads(config.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            return set(), [f"INVALID Codex config cannot be parsed: {config}: {exc}"]
        entries = ((data.get("skills") or {}).get("config") or [])
        disabled: set[Path] = set()
        issues: list[str] = []
        if not isinstance(entries, list):
            return disabled, [f"INVALID Codex skills.config must be an array: {config}"]
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
                issues.append(f"INVALID Codex skills.config entry {index}: {config}")
                continue
            if entry.get("enabled", True) is False:
                disabled.add(normalize_path(entry["path"], self.home))
        return disabled, issues

    def codex_skill_states(self) -> tuple[list[CodexSkillState], list[str]]:
        inspections = inspect_canonical_skills(self.library)
        skills = [inspection.skill for inspection in inspections if inspection.skill is not None]
        manifest = self.load_manifest()
        recorded = self.previous_artifacts(manifest, "codex") if manifest else []
        disabled_paths, issues = self.disabled_codex_skill_paths()
        states: list[CodexSkillState] = []
        for inspection in inspections:
            if inspection.skill is not None:
                continue
            states.append(
                CodexSkillState(
                    canonical_id=inspection.canonical_id,
                    name=inspection.canonical_id,
                    source=inspection.directory,
                    target=self.skill_target("codex", inspection.canonical_id),
                    status="INVALID_METADATA",
                    installed=False,
                    discoverable=False,
                    detail="; ".join(inspection.errors),
                )
            )
        for skill in skills:
            source = skill.directory
            target = self.skill_target("codex", skill.canonical_id)
            prior = self.prior_for_id(recorded, skill.canonical_id) or {}
            installed = False
            discoverable = False
            detail = ""
            if prior.get("kind") == "skill-alias":
                alias_file = Path(prior["target"])
                target = alias_file.parent
                if not alias_file.is_file() or alias_file.is_symlink():
                    status = "MISSING"
                    detail = f"managed alias is missing; canonical name is occupied at {prior.get('collision_target')}"
                elif sha256_file(alias_file) != prior.get("sha256"):
                    status = "STALE_COPY"
                    detail = "managed collision alias is modified or outdated"
                else:
                    status = "INSTALLED_ALIAS"
                    installed = True
                    discoverable = True
                    detail = f"invoke as ${prior.get('invocation_name')} because ${skill.name} is occupied"
            elif not path_exists(target):
                status = "MISSING"
            elif target.is_symlink():
                if not target.exists():
                    status = "BROKEN_LINK"
                    detail = f"link target={os.readlink(target)}"
                elif same_link(target, source):
                    status = "INSTALLED_SYMLINK"
                    installed = True
                    discoverable = True
                else:
                    status = "WRONG_TARGET"
                    detail = f"link target={os.readlink(target)}"
            elif target.is_dir():
                current_hash = sha256_tree(target)
                source_hash = sha256_tree(source)
                if current_hash == source_hash:
                    status = "INSTALLED_COPY"
                    installed = True
                    discoverable = True
                else:
                    prior_target = self.prior_for_target(recorded, target) or {}
                    if prior_target.get("type") == "copy" and current_hash == prior_target.get("sha256"):
                        status = "STALE_COPY"
                        detail = "installed managed copy is older than canonical source"
                    else:
                        status = "NAME_COLLISION"
                        detail = "target is occupied by unrelated or locally modified content"
            else:
                status = "WRONG_TARGET"
                detail = "expected a skill directory"

            installed_skill_file = target / "SKILL.md"
            normalized_installed = installed_skill_file.resolve(strict=False)
            normalized_source = skill.skill_file.resolve(strict=False)
            if normalized_installed in disabled_paths or normalized_source in disabled_paths:
                status = "DISABLED_BY_USER_CONFIG"
                discoverable = False
                detail = "disabled by ~/.codex/config.toml"
            states.append(
                CodexSkillState(
                    canonical_id=skill.canonical_id,
                    name=skill.name,
                    source=source,
                    target=target,
                    status=status,
                    installed=installed,
                    discoverable=discoverable,
                    detail=detail,
                )
            )
        canonical_ids = {inspection.canonical_id for inspection in inspections}
        for artifact in recorded:
            if not str(artifact.get("kind", "")).startswith("skill") or artifact.get("id") in canonical_ids:
                continue
            target_path = Path(str(artifact.get("target", "")))
            target = target_path.parent if artifact.get("kind") == "skill-alias" else target_path
            states.append(
                CodexSkillState(
                    canonical_id=str(artifact.get("id")),
                    name=str(artifact.get("invocation_name") or artifact.get("id")),
                    source=Path(str(artifact.get("source", ""))),
                    target=target,
                    status="ORPHANED_MANAGED",
                    installed=path_exists(target_path),
                    discoverable=path_exists(target_path),
                    detail="managed skill is no longer present in the canonical filesystem; run repair",
                )
            )
        return states, issues

    def visible_codex_skill_sources(self) -> list[tuple[str, Path]]:
        roots: list[tuple[str, Path, bool]] = [
            ("USER", self.home / ".agents" / "skills", False),
            ("SYSTEM", self.home / ".codex" / "skills", True),
            ("PLUGIN", self.home / ".codex" / "plugins", True),
        ]
        if self.platform.key != "windows":
            roots.append(("ADMIN", Path("/etc/codex/skills"), True))
        current = self.library
        while True:
            local = current / ".agents" / "skills"
            if local.is_dir():
                roots.append(("REPO", local, False))
            if (current / ".git").exists() or current.parent == current:
                break
            current = current.parent
        sources: list[tuple[str, Path]] = []
        seen: set[Path] = set()
        for label, root, recursive in roots:
            if not root.is_dir():
                continue
            files = root.rglob("SKILL.md") if recursive else root.glob("*/SKILL.md")
            for path in sorted(files):
                absolute = path.absolute()
                if absolute in seen:
                    continue
                seen.add(absolute)
                sources.append((label, path))
        return sources

    def duplicate_codex_skill_names(self) -> dict[str, list[tuple[str, Path]]]:
        names: dict[str, list[tuple[str, Path]]] = {}
        for label, path in self.visible_codex_skill_sources():
            try:
                metadata = parse_frontmatter(path)
            except (OSError, SkillCatalogError):
                continue
            name = metadata.get("name")
            if isinstance(name, str) and name:
                names.setdefault(name, []).append((label, path))
        return {name: entries for name, entries in names.items() if len(entries) > 1}

    @staticmethod
    def codex_skill_counts(states: list[CodexSkillState], duplicate_count: int = 0) -> dict[str, int]:
        canonical = [state for state in states if state.status != "ORPHANED_MANAGED"]
        return {
            "canonical": len(canonical),
            "eligible": len(canonical),
            "valid": sum(state.status != "INVALID_METADATA" for state in canonical),
            "installed": sum(state.installed for state in canonical),
            "missing": sum(state.status == "MISSING" for state in states),
            "broken": sum(state.status == "BROKEN_LINK" for state in states),
            "stale": sum(state.status == "STALE_COPY" for state in states),
            "disabled": sum(state.status == "DISABLED_BY_USER_CONFIG" for state in states),
            "collisions": sum(state.status == "NAME_COLLISION" for state in states) + duplicate_count,
            "aliases": sum(state.status == "INSTALLED_ALIAS" for state in states),
            "wrong_target": sum(state.status == "WRONG_TARGET" for state in states),
            "orphaned": sum(state.status == "ORPHANED_MANAGED" for state in states),
            "invalid": sum(state.status == "INVALID_METADATA" for state in canonical),
            "discoverable": sum(state.discoverable for state in canonical),
        }

    def runtime_skill_summary(self, runtime: str) -> tuple[dict[str, int], bool]:
        """Return skill counts and a healthy flag for any installed runtime."""
        manifest = self.load_manifest()
        if not manifest:
            return {}, True
        prior_runtime = self.previous_runtime(manifest, runtime)
        install_mode = self.resolve_install_mode("auto", prior_runtime)
        recorded = self.previous_artifacts(manifest, runtime)
        desired = [
            a for a in self.desired_artifacts(runtime, install_mode, recorded)
            if self.artifact_scope(a) == "skills"
        ]
        recorded_skills = [a for a in recorded if self.artifact_scope(a) == "skills"]
        counts: dict[str, int] = {
            "total": len(desired),
            "current": 0,
            "outdated": 0,
            "missing": 0,
            "broken": 0,
            "modified": 0,
        }
        for artifact in desired:
            target = Path(artifact["target"])
            prior = self.prior_for_target(recorded_skills, target) or {}
            state, _ = self.classify_artifact(artifact, prior)
            if state == "CURRENT":
                counts["current"] += 1
            elif state == "OUTDATED":
                counts["outdated"] += 1
            elif state == "BROKEN":
                counts["broken"] += 1
            elif state == "MISSING":
                counts["missing"] += 1
            else:
                counts["modified"] += 1
        healthy = counts["current"] == counts["total"]
        return counts, healthy

    def portable_path(self, path: Path) -> str:
        try:
            return "$HOME/" + path.relative_to(self.home).as_posix()
        except ValueError:
            pass
        try:
            return path.relative_to(self.library).as_posix()
        except ValueError:
            return str(path)

    def skill_report_payload(
        self,
        states: list[CodexSkillState],
        issues: list[str],
        duplicates: dict[str, list[tuple[str, Path]]],
        counts: dict[str, int],
    ) -> dict[str, Any]:
        descriptions = {
            inspection.canonical_id: inspection.skill.description
            for inspection in inspect_canonical_skills(self.library)
            if inspection.skill is not None
        }
        records: list[dict[str, Any]] = []
        for state in states:
            if state.status == "ORPHANED_MANAGED":
                continue
            records.append({
                "canonical_skill_id": state.canonical_id,
                "canonical_path": f"skills/{state.canonical_id}",
                "skill_md_path": f"skills/{state.canonical_id}/SKILL.md",
                "skill_name": state.name,
                "description": descriptions.get(state.canonical_id, ""),
                "valid_metadata": state.status != "INVALID_METADATA",
                "enabled": state.status != "DISABLED_BY_USER_CONFIG",
                "codex_compatible": True,
                "expected_codex_path": self.portable_path(state.target),
                "installation_mode": {
                    "INSTALLED_SYMLINK": "symlink",
                    "INSTALLED_COPY": "copy",
                    "INSTALLED_ALIAS": "managed-alias",
                }.get(state.status, "none"),
                "installed": state.installed,
                "discoverable": state.discoverable,
                "status": state.status,
                "detail": state.detail,
            })
        return {
            "schema_version": 1,
            "canonical_root": "skills",
            "codex_user_root": "$HOME/.agents/skills",
            "counts": counts,
            "config_issues": issues,
            "duplicate_names": {
                name: [
                    {"source": label, "path": self.portable_path(path)} for label, path in entries
                ]
                for name, entries in sorted(duplicates.items())
            },
            "skills": records,
        }

    def skills_status(
        self,
        verbose: bool = False,
        *,
        json_output: bool = False,
        output: Path | None = None,
    ) -> int:
        states, issues = self.codex_skill_states()
        duplicates = self.duplicate_codex_skill_names()
        counts = self.codex_skill_counts(states, len(duplicates))
        unhealthy = bool(
            issues
            or counts["missing"]
            or counts["invalid"]
            or counts["broken"]
            or counts["stale"]
            or counts["disabled"]
            or counts["collisions"]
            or counts["wrong_target"]
            or counts["orphaned"]
            or counts["discoverable"] != counts["eligible"]
        )
        if json_output or output is not None:
            content = json.dumps(
                self.skill_report_payload(states, issues, duplicates, counts),
                indent=2,
                sort_keys=True,
            ) + "\n"
            if output is not None:
                output_path = output if output.is_absolute() else Path.cwd() / output
                output_path.parent.mkdir(parents=True, exist_ok=True)
                atomic_write(output_path, content)
            if json_output and output is None:
                print(content, end="")
            return 1 if unhealthy else 0
        print("Agent Commons Skills")
        print()
        labels = (
            ("Canonical:", "canonical"),
            ("Codex eligible:", "eligible"),
            ("Installed:", "installed"),
            ("Valid:", "valid"),
            ("Invalid:", "invalid"),
            ("Discoverable:", "discoverable"),
            ("Missing:", "missing"),
            ("Broken:", "broken"),
            ("Stale:", "stale"),
            ("Disabled:", "disabled"),
            ("Aliases:", "aliases"),
            ("Collisions:", "collisions"),
            ("Wrong target:", "wrong_target"),
            ("Orphaned:", "orphaned"),
        )
        for label, key in labels:
            print(f"{label:<18}{counts[key]}")
        print()
        print(f"Status: {'ISSUES' if unhealthy else 'HEALTHY'}")
        for issue in issues:
            print(f"CONFIG {issue}")
        for name, entries in sorted(duplicates.items()):
            locations = ", ".join(f"{label}:{path}" for label, path in entries)
            print(f"DUPLICATE_NAME {name} - {locations}")
        if verbose or unhealthy:
            print()
            for state in states:
                if verbose or state.status not in {"INSTALLED_SYMLINK", "INSTALLED_COPY", "INSTALLED_ALIAS"}:
                    suffix = f" - {state.detail}" if state.detail else ""
                    print(f"{state.status:<24} {state.canonical_id} -> {state.target}{suffix}")
        return 1 if unhealthy else 0

    def status(self, runtimes: list[str], strict: bool) -> int:
        all_issues = [(runtime, issue) for runtime in runtimes for issue in self.verification_issues(runtime)]
        print(f"platform={self.platform.display_name}")
        print(f"canonical_library={self.library}")
        print(f"manifest={self.manifest_path}")
        print(f"runtimes={','.join(runtimes)}")
        if all_issues:
            print(f"status=issues count={len(all_issues)}")
            for runtime, issue in all_issues:
                print(f"STATE [{runtime}] {issue}")
            return 1 if strict else 0
        print("status=ok")
        return 0

    def runtime_detected(self, runtime: str) -> bool:
        paths = [self.user_path(runtime, name) for name in ("global_instructions", "skills", "agents")]
        return any(path_exists(path) or path.parent.exists() for path in paths)

    def doctor(self) -> int:
        print("Agent Commons environment")
        print()
        print(f"Platform: {self.platform.display_name}")
        print(f"Python: {platform.python_version()}")
        print(f"Repository: {self.library}")
        print(f"Home: {self.home}")
        print()
        print("Install strategy:")
        print(self.recommended_install_mode().upper())
        print()
        print("Runtimes:")
        for runtime in RUNTIMES:
            label = adapter_manifest(runtime)["display_name"]
            print(f"{label:<12} {'detected' if self.runtime_detected(runtime) else 'not detected (offline install supported)'}")
        manifest = self.load_manifest()
        print()
        if not manifest:
            print("Managed installation: not installed")
            issue_count = 0
        else:
            installed = list(manifest.get("runtimes", {}))
            issue_count = sum(len(self.verification_issues(runtime)) for runtime in installed)
            print(f"Managed installation: {'healthy' if issue_count == 0 else f'issues ({issue_count})'}")
        print()
        skill_healthy = True
        if not manifest:
            skill_result = self.skills_status()
            skill_healthy = skill_result == 0
        else:
            installed = list(manifest.get("runtimes", {}))
            print("Skills:")
            for runtime in installed:
                label = adapter_manifest(runtime)["display_name"]
                counts, healthy = self.runtime_skill_summary(runtime)
                if not healthy:
                    skill_healthy = False
                total = counts.get("total", 0)
                current = counts.get("current", 0)
                parts = []
                if counts.get("outdated"):
                    parts.append(f"{counts['outdated']} outdated")
                if counts.get("missing"):
                    parts.append(f"{counts['missing']} missing")
                if counts.get("broken"):
                    parts.append(f"{counts['broken']} broken")
                if counts.get("modified"):
                    parts.append(f"{counts['modified']} modified")
                detail = f" ({', '.join(parts)})" if parts else ""
                print(f"  {label:<12} {current}/{total} installed{detail}")
            if "codex" in installed:
                print()
                self.skills_status()
        return 1 if issue_count or not skill_healthy else 0

    def manual_install(self, runtimes: list[str]) -> int:
        mode = self.recommended_install_mode()
        print("Agent Commons manual installation")
        print(f"Platform: {self.platform.display_name}")
        print(f"Canonical library: {self.library}")
        print(f"Recommended mode: {mode.upper()}")
        print()
        print("Runtime destinations:")
        for runtime in runtimes:
            label = adapter_manifest(runtime)["display_name"]
            print(f"{label}:")
            print(f"  skills: {self.user_path(runtime, 'skills')}")
            print(f"  agents: {self.user_path(runtime, 'agents')}")
            print(f"  instructions: {self.user_path(runtime, 'global_instructions')}")
        print()
        print("Checklist:")
        print("1. Keep this canonical checkout in a permanent location.")
        print("2. Choose the runtime destinations listed above.")
        action = "link each canonical skill directory" if mode == "symlink" else "copy each canonical skill directory"
        print(f"3. For Codex or Claude Code, {action} for every valid canonical skills/*/SKILL.md; use generated wrappers for Cline or OpenCode.")
        print("4. Generate or copy runtime-native agent files from the canonical role definitions.")
        print("5. Merge the marked Agent Commons section into existing global instructions; preserve all other content.")
        print("6. Do not replace unrelated skills, agents, settings, or configuration.")
        print("7. Start the runtime in a temporary project, inspect /skills, and test representative $skill-name invocations.")
        prefix = "py install\\agent_commons.py" if self.platform.key == "windows" else "python3 install/agent_commons.py"
        print(f"8. Reconcile all Codex skills with: {prefix} skills --verbose")
        print(f"9. Verify managed installations with: {prefix} verify")
        print()
        print("This command is informational and made no installation changes.")
        return 0

    def uninstall_runtime(self, runtime: str) -> None:
        manifest = self.load_manifest(required=True)
        assert manifest is not None
        artifacts = self.previous_artifacts(manifest, runtime)
        if not artifacts:
            raise InstallError(f"runtime is not installed: {runtime}")
        for artifact in artifacts:
            target = Path(artifact["target"])
            artifact_type = artifact["type"]
            if not path_exists(target):
                self.notices.append(f"already absent: {target}")
            elif artifact_type == "symlink" and same_link(target, Path(artifact["source"])):
                target.unlink()
                self.changes.append(f"removed managed symlink: {target}")
            elif artifact_type == "copy" and target.is_dir() and not target.is_symlink() and sha256_tree(target) == artifact.get("sha256"):
                shutil.rmtree(target)
                self.changes.append(f"removed managed copy: {target}")
            elif artifact_type == "file" and target.is_file() and not target.is_symlink() and sha256_file(target) == artifact.get("sha256"):
                target.unlink()
                self.changes.append(f"removed managed file: {target}")
                if artifact.get("kind") == "skill-alias" and target.parent.is_dir() and not any(target.parent.iterdir()):
                    target.parent.rmdir()
            elif artifact_type == "managed-section" and target.is_file() and not target.is_symlink():
                split = self.split_managed_section(target, target.read_text(encoding="utf-8"))
                if split is None or sha256_text(split[1]) != artifact.get("sha256"):
                    self.notices.append(f"preserved changed managed section: {target}")
                else:
                    self.backup(target)
                    updated = (split[0].rstrip() + "\n\n" + split[2].lstrip()).strip()
                    atomic_write(target, updated + ("\n" if updated else ""))
                    self.changes.append(f"removed managed global instructions: {target}")
            else:
                self.notices.append(f"preserved changed or unrelated path: {target}")
        runtimes = dict(manifest.get("runtimes", {}))
        runtimes.pop(runtime, None)
        if runtimes:
            manifest["manifest_version"] = MANIFEST_VERSION
            manifest["runtimes"] = runtimes
            manifest["updated_at"] = now()
            manifest["backups"] = list(manifest.get("backups", [])) + self.backups
            atomic_write(self.manifest_path, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
            self.changes.append(f"updated managed manifest: {self.manifest_path}")
            self.backups.clear()
        else:
            self.manifest_path.unlink()
            self.changes.append(f"removed managed manifest: {self.manifest_path}")

    def report(self) -> None:
        for line in self.changes:
            print(f"CHANGED {line}")
        for line in self.notices:
            print(f"UNCHANGED {line}")
        print(f"summary changed={len(self.changes)} unchanged={len(self.notices)}")


def selected_runtimes(
    positional: str | None,
    option: str | None,
    all_runtimes: bool,
    *,
    default_all: bool = False,
) -> list[str]:
    runtime = option or positional
    if option and positional:
        raise InstallError("choose a positional runtime or --runtime, not both")
    if runtime and all_runtimes:
        raise InstallError("choose a runtime or --all, not both")
    if all_runtimes or (default_all and runtime is None):
        return list(RUNTIMES)
    return [runtime or "codex"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("install", "sync", "verify", "status", "skills", "repair", "uninstall-managed", "doctor", "manual-install"),
    )
    parser.add_argument("runtime_positional", nargs="?", choices=RUNTIMES)
    parser.add_argument("--runtime", choices=RUNTIMES, dest="runtime_option")
    parser.add_argument("--all", action="store_true", dest="all_runtimes")
    parser.add_argument("--install-mode", choices=INSTALL_MODES, default="auto")
    parser.add_argument("--verbose", action="store_true", help="show per-skill reconciliation details")
    parser.add_argument("--json", action="store_true", dest="json_output", help="emit machine-readable skill reconciliation")
    parser.add_argument("--output", type=Path, help="write machine-readable skill reconciliation to a file")
    parser.add_argument("--skills-only", action="store_true", help="manage only skill artifacts for the selected runtime")
    parser.add_argument("--library", type=Path, default=LIBRARY_ROOT, help="canonical Agent Commons checkout")
    parser.add_argument("--home", type=Path, default=Path.home(), help="user home; useful for isolated verification")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    installer = Installer(args.library, args.home)
    try:
        if args.command == "doctor":
            return installer.doctor()
        if args.command == "skills":
            return installer.skills_status(args.verbose, json_output=args.json_output, output=args.output)
        runtimes = selected_runtimes(
            args.runtime_positional,
            args.runtime_option,
            args.all_runtimes,
            default_all=args.command == "manual-install",
        )
        if args.command == "manual-install":
            return installer.manual_install(runtimes)
        if args.command == "verify":
            return installer.status(runtimes, strict=True)
        if args.command == "status":
            return installer.status(runtimes, strict=False)
        for runtime in runtimes:
            if args.command == "uninstall-managed":
                installer.uninstall_runtime(runtime)
            else:
                installer.install_runtime(
                    runtime,
                    args.install_mode,
                    repair=args.command == "repair",
                    skills_only=args.skills_only,
                )
    except (InstallError, AdapterError, OSError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1
    installer.report()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
