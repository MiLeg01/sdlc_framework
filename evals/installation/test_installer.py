#!/usr/bin/env python3
"""Runtime-portable installer evaluations using isolated temporary homes."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path, PureWindowsPath


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "install" / "agent_commons.py"
RUNTIMES = ("codex", "claude-code", "cline", "opencode")
sys.path.insert(0, str(ROOT / "install"))
sys.path.insert(0, str(ROOT / "tools"))

from agent_commons import (  # noqa: E402
    InstallError,
    Installer,
    PlatformContext,
    expand_environment_variables,
    repository_root_from_installer,
    sha256_tree,
)
from runtime_adapters import runtime_user_path  # noqa: E402


class InstallerScenarios(unittest.TestCase):
    def run_checked(self, command: list[str]) -> subprocess.CompletedProcess[str]:
        """Fail with the installer's own output; a bare CalledProcessError hides why CI broke."""
        completed = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(
            completed.returncode, 0,
            f"{' '.join(command)}\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
        )
        return completed

    def run_installer(
        self,
        home: Path,
        command: str,
        runtime: str | None = None,
        all_runtimes: bool = False,
        install_mode: str | None = None,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        args = [sys.executable, str(SCRIPT), command]
        if runtime:
            args.append(runtime)
        if all_runtimes:
            args.append("--all")
        if install_mode:
            args += ["--install-mode", install_mode]
        args += ["--library", str(ROOT), "--home", str(home)]
        return subprocess.run(args, check=check, capture_output=True, text=True)

    def manifest(self, home: Path) -> dict[str, object]:
        path = home / ".agent-commons" / "install-manifest.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_codex_install_is_idempotent_and_preserves_unrelated_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            unrelated = home / ".agents" / "skills" / "unrelated" / "SKILL.md"
            unrelated.parent.mkdir(parents=True)
            unrelated.write_text("user-owned\n", encoding="utf-8")
            instructions = home / ".codex" / "AGENTS.md"
            instructions.parent.mkdir(parents=True)
            instructions.write_text("# Personal\n\nKeep this.\n", encoding="utf-8")

            first = self.run_installer(home, "install", "codex")
            manifest_path = home / ".agent-commons" / "install-manifest.json"
            first_manifest = manifest_path.read_bytes()
            second = self.run_installer(home, "install", "codex")

            self.assertIn("changed=0", second.stdout)
            self.assertEqual(first_manifest, manifest_path.read_bytes())
            self.assertEqual(unrelated.read_text(encoding="utf-8"), "user-owned\n")
            self.assertIn("Keep this.", instructions.read_text(encoding="utf-8"))
            manifest = json.loads(first_manifest)
            self.assertEqual(manifest["manifest_version"], 3)
            self.assertEqual(manifest["runtimes"]["codex"]["install_mode"], "symlink")
            self.assertIn("codex", manifest["runtimes"])
            self.assertIn("backed up", first.stdout)
            self.run_installer(home, "verify", "codex")

    def test_skills_only_install_ignores_unrelated_agent_and_global_instruction_conflicts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            agent = home / ".codex" / "agents" / "legacy-discovery-specialist.toml"
            agent.parent.mkdir(parents=True)
            agent.write_text("user-owned agent\n", encoding="utf-8")
            instructions = home / ".codex" / "AGENTS.md"
            instructions.write_text("user-owned instructions\n", encoding="utf-8")

            result = self.run_checked(
                [
                    sys.executable,
                    str(SCRIPT),
                    "install",
                    "codex",
                    "--skills-only",
                    "--library",
                    str(ROOT),
                    "--home",
                    str(home),
                ],
            )

            self.assertIn("summary changed=", result.stdout)
            self.assertEqual(agent.read_text(encoding="utf-8"), "user-owned agent\n")
            self.assertEqual(instructions.read_text(encoding="utf-8"), "user-owned instructions\n")
            self.assertTrue((home / ".agents" / "skills" / "initialize-project").is_symlink())
            manifest = self.manifest(home)
            self.assertTrue(all(item["kind"].startswith("skill") for item in manifest["runtimes"]["codex"]["artifacts"]))
            self.assertEqual(manifest["runtimes"]["codex"]["managed_scopes"], ["skills"])
            self.run_installer(home, "verify", "codex")

    def test_codex_install_discovers_new_filesystem_skill_without_allowlist_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            library = root / "agent-commons-library"
            home = root / "home"
            shutil.copytree(ROOT, library, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            skill = library / "skills" / "example-new-skill"
            skill.mkdir()
            (skill / "SKILL.md").write_text(
                "---\n"
                "name: example-new-skill\n"
                "description: Exercise dynamic canonical skill discovery for installer regression coverage. "
                "Use when testing new-skill installation. Do not use for production workflows.\n"
                "---\n\n"
                "# Example new skill\n",
                encoding="utf-8",
            )

            result = self.run_checked(
                [
                    sys.executable,
                    str(library / "install" / "agent_commons.py"),
                    "install",
                    "codex",
                    "--library",
                    str(library),
                    "--home",
                    str(home),
                ],
            )

            installed = home / ".agents" / "skills" / "example-new-skill"
            self.assertTrue(installed.is_symlink(), result.stdout)
            self.assertEqual(installed.resolve(), skill.resolve())

    def test_repair_removes_unchanged_managed_skill_after_governed_canonical_deletion(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            library = root / "agent-commons-library"
            home = root / "home"
            shutil.copytree(ROOT, library, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            script = library / "install" / "agent_commons.py"

            self.run_checked(
                [sys.executable, str(script), "install", "codex", "--library", str(library), "--home", str(home)],
            )
            removed_id = "sales-storytelling"
            installed = home / ".agents" / "skills" / removed_id
            self.assertTrue(installed.is_symlink())

            shutil.rmtree(library / "skills" / removed_id)
            catalog_path = library / "catalog" / "capabilities.yaml"
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            catalog["skills"].pop(removed_id)
            catalog_path.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
            interfaces_path = library / "adapters" / "codex" / "skill-interfaces.yaml"
            interfaces = json.loads(interfaces_path.read_text(encoding="utf-8"))
            interfaces["interfaces"].pop(removed_id)
            interfaces_path.write_text(json.dumps(interfaces, indent=2) + "\n", encoding="utf-8")

            self.run_checked(
                [sys.executable, str(script), "repair", "codex", "--library", str(library), "--home", str(home)],
            )

            self.assertFalse(os.path.lexists(installed))
            manifest = json.loads((home / ".agent-commons" / "install-manifest.json").read_text(encoding="utf-8"))
            ids = {item["id"] for item in manifest["runtimes"]["codex"]["artifacts"] if item["kind"].startswith("skill")}
            self.assertNotIn(removed_id, ids)

    def test_repair_reconciles_managed_canonical_skill_rename_without_ghost(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            library = root / "agent-commons-library"
            home = root / "home"
            shutil.copytree(ROOT, library, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            script = library / "install" / "agent_commons.py"
            base = ["--library", str(library), "--home", str(home)]
            self.run_checked(
                [sys.executable, str(script), "install", "codex", *base],
            )

            old_id = "sales-storytelling"
            new_id = "sales-narrative"
            shutil.move(library / "skills" / old_id, library / "skills" / new_id)
            renamed_skill = library / "skills" / new_id / "SKILL.md"
            renamed_skill.write_text(
                renamed_skill.read_text(encoding="utf-8").replace(f"name: {old_id}", f"name: {new_id}", 1),
                encoding="utf-8",
            )
            catalog_path = library / "catalog" / "capabilities.yaml"
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            entry = catalog["skills"].pop(old_id)
            entry["path"] = f"skills/{new_id}/SKILL.md"
            catalog["skills"][new_id] = entry
            catalog_path.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
            interfaces_path = library / "adapters" / "codex" / "skill-interfaces.yaml"
            interfaces = json.loads(interfaces_path.read_text(encoding="utf-8"))
            interfaces["interfaces"][new_id] = interfaces["interfaces"].pop(old_id)
            interfaces_path.write_text(json.dumps(interfaces, indent=2) + "\n", encoding="utf-8")

            self.run_checked(
                [sys.executable, str(script), "repair", "codex", *base],
            )

            old_target = home / ".agents" / "skills" / old_id
            new_target = home / ".agents" / "skills" / new_id
            self.assertFalse(os.path.lexists(old_target))
            self.assertTrue(new_target.is_symlink())
            self.assertEqual(new_target.resolve(), (library / "skills" / new_id).resolve())

    def test_all_runtimes_generate_valid_isolated_native_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            self.run_installer(home, "install", all_runtimes=True)
            self.run_installer(home, "verify", all_runtimes=True)
            manifest = self.manifest(home)
            self.assertEqual(set(manifest["runtimes"]), set(RUNTIMES))
            self.assertTrue((home / ".agents" / "skills" / "initialize-project").is_symlink())
            self.assertTrue((home / ".claude" / "skills" / "initialize-project").is_symlink())
            self.assertIn(
                "read `" + str(ROOT / "skills" / "initialize-project" / "SKILL.md") + "` completely",
                (home / ".cline" / "skills" / "initialize-project" / "SKILL.md").read_text(encoding="utf-8"),
            )
            self.assertTrue((home / ".config" / "opencode" / "agents" / "legacy-discovery-specialist.md").is_file())

    def test_conflict_is_never_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            conflict = home / ".agents" / "skills" / "initialize-project"
            conflict.mkdir(parents=True)
            marker = conflict / "user.txt"
            marker.write_text("owned\n", encoding="utf-8")
            alias_conflict = home / ".agents" / "skills" / "agent-commons-initialize-project"
            alias_conflict.mkdir(parents=True)
            alias_marker = alias_conflict / "user.txt"
            alias_marker.write_text("also owned\n", encoding="utf-8")
            result = self.run_installer(home, "install", "codex", check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(marker.read_text(encoding="utf-8"), "owned\n")
            self.assertEqual(alias_marker.read_text(encoding="utf-8"), "also owned\n")
            self.assertFalse((home / ".agent-commons" / "install-manifest.json").exists())

    def test_codex_name_collision_uses_managed_alias_without_overwriting_third_party_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            conflict = home / ".agents" / "skills" / "frontend-design"
            conflict.mkdir(parents=True)
            third_party = "---\nname: frontend-design\ndescription: Third-party workflow.\n---\n"
            (conflict / "SKILL.md").write_text(third_party, encoding="utf-8")

            self.run_installer(home, "install", "codex")

            self.assertEqual((conflict / "SKILL.md").read_text(encoding="utf-8"), third_party)
            alias = home / ".agents" / "skills" / "agent-commons-frontend-design" / "SKILL.md"
            self.assertTrue(alias.is_file())
            self.assertIn("name: agent-commons-frontend-design", alias.read_text(encoding="utf-8"))
            status = self.run_installer(home, "skills")
            self.assertIn("Aliases:          1", status.stdout)
            self.assertIn("Collisions:       0", status.stdout)
            self.assertIn("Status: HEALTHY", status.stdout)

    def test_repair_recreates_missing_links_and_repairs_owned_wrapper_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            self.run_installer(home, "install", "codex")
            link = home / ".agents" / "skills" / "inventory-codebase"
            link.unlink()
            self.run_installer(home, "repair", "codex")
            self.assertTrue(link.is_symlink())

            self.run_installer(home, "install", "cline")
            wrapper = home / ".cline" / "skills" / "inventory-codebase" / "SKILL.md"
            wrapper.write_text("managed file edited locally\n", encoding="utf-8")
            failed = self.run_installer(home, "sync", "cline", check=False)
            self.assertNotEqual(failed.returncode, 0)
            repaired = self.run_installer(home, "repair", "cline")
            self.assertIn("backed up", repaired.stdout)
            self.run_installer(home, "verify", "cline")

    def test_skills_status_detects_broken_link_and_repair_restores_it(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            self.run_installer(home, "install", "codex")
            link = home / ".agents" / "skills" / "inventory-codebase"
            link.unlink()
            link.symlink_to(home / "missing-canonical-skill", target_is_directory=True)

            broken = self.run_installer(home, "skills", check=False)
            self.assertNotEqual(broken.returncode, 0)
            self.assertIn("Broken:           1", broken.stdout)
            self.assertIn("BROKEN_LINK", broken.stdout)

            self.run_installer(home, "repair", "codex")
            self.assertEqual(link.resolve(), (ROOT / "skills" / "inventory-codebase").resolve())
            self.run_installer(home, "skills")

    def test_skills_status_reports_user_disabled_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            self.run_installer(home, "install", "codex")
            skill_file = home / ".agents" / "skills" / "initialize-project" / "SKILL.md"
            config = home / ".codex" / "config.toml"
            config.parent.mkdir(parents=True, exist_ok=True)
            config.write_text(
                "[[skills.config]]\n"
                f'path = "{skill_file}"\n'
                "enabled = false\n",
                encoding="utf-8",
            )

            status = self.run_installer(home, "skills", check=False)

            self.assertNotEqual(status.returncode, 0)
            self.assertIn("Disabled:         1", status.stdout)
            self.assertIn("DISABLED_BY_USER_CONFIG", status.stdout)
            self.assertIn("initialize-project", status.stdout)

    def test_skills_status_reports_duplicate_names_across_visible_user_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            self.run_installer(home, "install", "codex")
            duplicate = home / ".agents" / "skills" / "duplicate-initialize-project"
            duplicate.mkdir()
            (duplicate / "SKILL.md").write_text(
                "---\n"
                "name: initialize-project\n"
                "description: Conflicting user skill for collision detection.\n"
                "---\n",
                encoding="utf-8",
            )

            status = self.run_installer(home, "skills", check=False)

            self.assertNotEqual(status.returncode, 0)
            self.assertIn("Collisions:       1", status.stdout)
            self.assertIn("DUPLICATE_NAME", status.stdout)
            self.assertIn("initialize-project", status.stdout)

    def test_skills_status_detects_stale_managed_copy_and_repair_synchronizes_it(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            library = root / "agent-commons-library"
            home = root / "home"
            shutil.copytree(ROOT, library, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            script = library / "install" / "agent_commons.py"
            base = ["--library", str(library), "--home", str(home)]
            self.run_checked(
                [sys.executable, str(script), "install", "codex", "--install-mode", "copy", *base],
            )
            canonical = library / "skills" / "inventory-codebase" / "SKILL.md"
            canonical.write_text(canonical.read_text(encoding="utf-8") + "\n<!-- canonical update -->\n", encoding="utf-8")

            stale = subprocess.run(
                [sys.executable, str(script), "skills", *base],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(stale.returncode, 0)
            self.assertIn("Stale:            1", stale.stdout)
            self.assertIn("STALE_COPY", stale.stdout)

            self.run_checked(
                [sys.executable, str(script), "repair", "codex", "--install-mode", "copy", *base],
            )
            installed = home / ".agents" / "skills" / "inventory-codebase" / "SKILL.md"
            self.assertEqual(installed.read_text(encoding="utf-8"), canonical.read_text(encoding="utf-8"))

    def test_cline_agent_limitation_is_explicit_and_not_fake_native_parity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            self.run_installer(home, "install", "cline")
            role = home / ".cline" / "skills" / "agent-legacy-discovery-specialist" / "SKILL.md"
            text = role.read_text(encoding="utf-8")
            self.assertIn("does not document reusable custom subagent definitions", text)
            self.assertIn("without claiming native custom-agent parity", text)

    def test_uninstall_one_runtime_preserves_other_runtime_and_user_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            unrelated = home / ".config" / "opencode" / "user-owned.txt"
            unrelated.parent.mkdir(parents=True)
            unrelated.write_text("keep\n", encoding="utf-8")
            self.run_installer(home, "install", all_runtimes=True)
            self.run_installer(home, "uninstall-managed", "cline")
            self.assertEqual(unrelated.read_text(encoding="utf-8"), "keep\n")
            self.assertFalse((home / ".cline" / "skills" / "initialize-project" / "SKILL.md").exists())
            self.assertTrue((home / ".agents" / "skills" / "initialize-project").is_symlink())
            self.assertTrue((home / ".claude" / "skills" / "initialize-project").is_symlink())
            self.run_installer(home, "verify", "codex")
            self.run_installer(home, "verify", "claude-code")
            self.run_installer(home, "verify", "opencode")
            self.assertNotIn("cline", self.manifest(home)["runtimes"])

    def test_uninstall_last_runtime_removes_manifest_only_after_managed_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            instructions = home / ".codex" / "AGENTS.md"
            instructions.parent.mkdir(parents=True)
            instructions.write_text("# Personal\n", encoding="utf-8")
            self.run_installer(home, "install", "codex")
            self.run_installer(home, "uninstall-managed", "codex")
            self.assertEqual(instructions.read_text(encoding="utf-8"), "# Personal\n")
            self.assertFalse((home / ".agent-commons" / "install-manifest.json").exists())
            skills = home / ".agents" / "skills"
            if skills.exists():
                self.assertEqual(os.listdir(skills), [])

    def test_windows_auto_uses_managed_copy_without_symlink_privileges(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary) / "Test User ü"
            home.mkdir()
            installer = Installer(
                ROOT,
                home,
                platform_context=PlatformContext("windows", "Windows"),
                symlink_support=False,
            )
            installer.install_runtime("codex", "auto")
            skill = home / ".agents" / "skills" / "initialize-project"
            self.assertTrue(skill.is_dir())
            self.assertFalse(skill.is_symlink())
            manifest = self.manifest(home)
            self.assertEqual(manifest["runtimes"]["codex"]["install_mode"], "copy")
            copy_record = next(
                artifact
                for artifact in manifest["runtimes"]["codex"]["artifacts"]
                if artifact["id"] == "initialize-project"
            )
            self.assertEqual(copy_record["type"], "copy")
            self.assertIn("sha256", copy_record)
            self.assertIn("last_sync", copy_record)
            self.assertEqual(installer.verification_issues("codex"), [])
            installer.install_runtime("claude-code", "auto")
            self.assertEqual(installer.verification_issues("claude-code"), [])
            self.assertEqual(set(self.manifest(home)["runtimes"]), {"codex", "claude-code"})

    def test_managed_copy_refuses_sync_of_local_changes_then_repairs_and_uninstalls(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            installer = Installer(ROOT, home, symlink_support=False)
            installer.install_runtime("codex", "auto")
            skill_file = home / ".agents" / "skills" / "initialize-project" / "SKILL.md"
            skill_file.write_text(skill_file.read_text(encoding="utf-8") + "\nlocal edit\n", encoding="utf-8")
            with self.assertRaises(InstallError):
                installer.install_runtime("codex", "auto")
            self.assertTrue(any(issue.startswith("MODIFIED") for issue in installer.verification_issues("codex")))
            installer.install_runtime("codex", "auto", repair=True)
            self.assertEqual(installer.verification_issues("codex"), [])
            installer.uninstall_runtime("codex")
            self.assertFalse((home / ".agents" / "skills" / "initialize-project").exists())
            self.assertFalse((home / ".agent-commons" / "install-manifest.json").exists())

    def test_explicit_symlink_mode_fails_with_actionable_message_when_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            installer = Installer(
                ROOT,
                Path(temporary),
                platform_context=PlatformContext("windows", "Windows"),
                symlink_support=False,
            )
            with self.assertRaisesRegex(InstallError, "Developer Mode|--install-mode copy"):
                installer.resolve_install_mode("symlink")

    def test_copy_state_distinguishes_outdated_from_modified(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "skill"
            target.mkdir()
            (target / "SKILL.md").write_text("installed\n", encoding="utf-8")
            installed_hash = sha256_tree(target)
            installer = Installer(ROOT, Path(temporary), symlink_support=False)
            artifact = {"type": "copy", "target": str(target), "sha256": "new-source-hash"}
            state, _ = installer.classify_artifact(artifact, {"sha256": installed_hash})
            self.assertEqual(state, "OUTDATED")
            (target / "SKILL.md").write_text("local edit\n", encoding="utf-8")
            state, _ = installer.classify_artifact(artifact, {"sha256": installed_hash})
            self.assertEqual(state, "MODIFIED")

    def test_windows_path_model_and_environment_expansion_are_drive_independent(self) -> None:
        home = PureWindowsPath("C:/Users/Test User")
        self.assertEqual(
            runtime_user_path(home, "codex", "skills"),
            PureWindowsPath("C:/Users/Test User/.agents/skills"),
        )
        self.assertEqual(
            runtime_user_path(home, "opencode", "agents"),
            PureWindowsPath("C:/Users/Test User/.config/opencode/agents"),
        )
        script = PureWindowsPath("D:/Tools/Agent Commons Library/install/agent_commons.py")
        self.assertEqual(
            repository_root_from_installer(script),
            PureWindowsPath("D:/Tools/Agent Commons Library"),
        )
        self.assertEqual(
            expand_environment_variables(r"%USERPROFILE%\Agent Commons", {"USERPROFILE": r"C:\Users\Test User"}),
            r"C:\Users\Test User\Agent Commons",
        )

    def test_doctor_and_manual_install_are_informational(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            doctor = self.run_installer(home, "doctor", check=False)
            manual = self.run_installer(home, "manual-install")
            self.assertNotEqual(doctor.returncode, 0)
            self.assertIn("Agent Commons environment", doctor.stdout)
            self.assertIn("Install strategy:", doctor.stdout)
            self.assertIn("Agent Commons Skills", doctor.stdout)
            self.assertIn("Missing:", doctor.stdout)
            self.assertIn("Runtime destinations:", manual.stdout)
            self.assertIn("made no installation changes", manual.stdout)
            self.assertFalse((home / ".agent-commons").exists())

    def test_skills_command_reports_complete_codex_reconciliation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            self.run_installer(home, "install", "codex")

            result = self.run_installer(home, "skills")

            self.assertIn("Agent Commons Skills", result.stdout)
            self.assertIn("Canonical:", result.stdout)
            self.assertIn("Codex eligible:", result.stdout)
            self.assertIn("Missing:          0", result.stdout)
            self.assertIn("Broken:           0", result.stdout)
            self.assertIn("Stale:            0", result.stdout)
            self.assertIn("Disabled:         0", result.stdout)
            self.assertIn("Collisions:       0", result.stdout)
            self.assertIn("Status: HEALTHY", result.stdout)

    def test_skills_command_retains_invalid_canonical_skill_in_validation_matrix(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            library = root / "agent-commons-library"
            home = root / "home"
            shutil.copytree(ROOT, library, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            valid_skill_count = sum(
                1 for path in (library / "skills").iterdir()
                if path.is_dir() and (path / "SKILL.md").is_file()
            )
            invalid = library / "skills" / "invalid-example"
            invalid.mkdir()
            (invalid / "SKILL.md").write_text("# Missing front matter\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(library / "install" / "agent_commons.py"),
                    "skills",
                    "--verbose",
                    "--library",
                    str(library),
                    "--home",
                    str(home),
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(f"Canonical:        {valid_skill_count + 1}", result.stdout)
            self.assertIn(f"Valid:            {valid_skill_count}", result.stdout)
            self.assertIn("Invalid:          1", result.stdout)
            self.assertIn("INVALID_METADATA", result.stdout)
            self.assertIn("invalid-example", result.stdout)

    def test_skills_command_writes_portable_json_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            home = root / "home"
            output = root / "skills.json"
            self.run_installer(home, "install", "codex")

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "skills",
                    "--json",
                    "--output",
                    str(output),
                    "--library",
                    str(ROOT),
                    "--home",
                    str(home),
                ],
            )

            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(data["counts"]["canonical"], len(data["skills"]))
            self.assertEqual(data["counts"]["missing"], 0)
            self.assertTrue(all(item["canonical_path"].startswith("skills/") for item in data["skills"]))
            self.assertTrue(all(item["expected_codex_path"].startswith("$HOME/.agents/skills/") for item in data["skills"]))


if __name__ == "__main__":
    unittest.main()
