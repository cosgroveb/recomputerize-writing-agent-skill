import json
import os
from pathlib import Path
import runpy
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
NAME = "recomputerize-writing-agent-skill"


class InstallTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="recomputerize test ")
        self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name)
        self.package = self.work / "plugin $ ' copy"
        shutil.copytree(
            ROOT,
            self.package,
            ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__"),
        )
        self.user_root = self.work / "user"
        self.destination = self.user_root / ".local/share/agents/skills" / NAME
        self.agent_link = self.user_root / ".agents/skills" / NAME
        self.claude_link = self.user_root / ".claude/skills" / NAME
        self.environment = os.environ.copy()
        self.environment.pop("XDG_DATA_HOME", None)
        self.environment.pop("CLAUDE_CONFIG_DIR", None)

    def command(self, action="install", *extra):
        return [
            sys.executable,
            str(self.package / "scripts/install.py"),
            action,
            "--home", str(self.user_root),
            *extra,
        ]

    def run_installer(self, action="install", *extra, success=True):
        result = subprocess.run(
            self.command(action, *extra),
            cwd=self.work,
            env=self.environment,
            capture_output=True,
            text=True,
            timeout=15,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def change_package(self, version, body):
        manifest_path = self.package / "plugin.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["version"] = version
        manifest_path.write_text(json.dumps(manifest))
        (self.package / "skills" / NAME / "SKILL.md").write_text(body)

    def assert_installed(self):
        self.assertEqual(self.agent_link.readlink(), self.destination)
        self.assertEqual(self.claude_link.readlink(), self.destination)
        self.assertEqual(
            (self.agent_link / "SKILL.md").read_bytes(),
            (self.package / "skills" / NAME / "SKILL.md").read_bytes(),
        )
        self.assertEqual(
            (self.destination / "LICENSE").read_bytes(),
            (self.package / "LICENSE").read_bytes(),
        )

    def test_install_is_idempotent_and_independent_of_plugin_cache(self):
        self.run_installer()
        self.assert_installed()
        installed = self.destination / "SKILL.md"
        original_stat = installed.stat()
        self.run_installer()
        self.assertEqual(installed.stat().st_ino, original_stat.st_ino)
        self.assertEqual(installed.stat().st_mtime_ns, original_stat.st_mtime_ns)
        shutil.rmtree(self.package)
        self.assertIn("You are what you are.", installed.read_text())
        self.assertTrue((self.claude_link / "SKILL.md").is_file())

    def test_xdg_data_home_and_claude_config_dir(self):
        data_root = self.work / "custom data"
        claude_root = self.work / "custom claude"
        self.environment["XDG_DATA_HOME"] = str(data_root)
        self.environment["CLAUDE_CONFIG_DIR"] = str(claude_root)
        self.destination = data_root / "agents/skills" / NAME
        self.claude_link = claude_root / "skills" / NAME
        self.run_installer()
        self.assert_installed()
        self.assertFalse((self.user_root / ".local").exists())
        self.run_installer("uninstall")
        self.assertFalse(self.agent_link.is_symlink())
        self.assertFalse(self.destination.exists())

    def test_relative_or_empty_xdg_data_home_uses_default(self):
        for value in ("relative/path", ""):
            with self.subTest(value=value):
                self.environment["XDG_DATA_HOME"] = value
                self.run_installer()
                self.assert_installed()
                self.run_installer("uninstall")
        self.assertFalse((self.work / "relative").exists())

    def test_upgrade_removes_obsolete_files_and_preserves_executable_mode(self):
        resource = self.package / "skills" / NAME / "old.txt"
        resource.write_text("obsolete")
        self.run_installer()
        resource.unlink()
        executable = self.package / "skills" / NAME / "example.sh"
        executable.write_text("#!/bin/sh\nexit 0\n")
        executable.chmod(0o755)
        self.change_package("0.2.0", "Updated skill.\n")
        self.run_installer("install", "--auto")
        self.assert_installed()
        self.assertFalse((self.destination / "old.txt").exists())
        self.assertEqual((self.destination / "example.sh").stat().st_mode & 0o777, 0o755)

    def test_older_marketplace_cannot_downgrade_shared_skill(self):
        self.change_package("0.2.0", "Newer content.\n")
        self.run_installer()
        self.change_package("0.1.0", "Older content.\n")
        self.claude_link.unlink()
        self.run_installer("install", "--auto")
        self.assertEqual((self.destination / "SKILL.md").read_text(), "Newer content.\n")
        self.assertEqual(self.claude_link.readlink(), self.destination)
        self.run_installer()
        self.assertEqual((self.destination / "SKILL.md").read_text(), "Older content.\n")

    def test_unmanaged_data_directory_is_preserved(self):
        self.destination.mkdir(parents=True)
        sentinel = self.destination / "mine.txt"
        sentinel.write_text("keep")
        result = self.run_installer(success=False)
        self.assertIn("Refusing", result.stderr)
        self.assertEqual(sentinel.read_text(), "keep")
        self.assertFalse(self.agent_link.is_symlink())
        self.run_installer("uninstall", success=False)
        self.assertEqual(sentinel.read_text(), "keep")

    def test_unmanaged_discovery_entries_are_preserved(self):
        for kind in ("directory", "file", "symlink", "broken-symlink"):
            with self.subTest(kind=kind):
                self.claude_link.parent.mkdir(parents=True, exist_ok=True)
                foreign = self.work / "foreign"
                foreign.mkdir(exist_ok=True)
                (foreign / "keep.txt").write_text("keep")
                if kind == "directory":
                    self.claude_link.mkdir()
                elif kind == "file":
                    self.claude_link.write_text("keep")
                else:
                    target = foreign if kind == "symlink" else self.work / "missing"
                    self.claude_link.symlink_to(target)
                result = self.run_installer(success=False)
                self.assertIn("Refusing", result.stderr)
                self.assertFalse(self.destination.exists())
                self.assertFalse(self.agent_link.is_symlink())
                self.assertEqual((foreign / "keep.txt").read_text(), "keep")
                if kind == "directory":
                    self.claude_link.rmdir()
                else:
                    self.claude_link.unlink()

    def test_canonical_symlink_is_preserved(self):
        self.destination.parent.mkdir(parents=True)
        foreign = self.work / "foreign"
        foreign.mkdir()
        self.destination.symlink_to(foreign, target_is_directory=True)
        self.run_installer(success=False)
        self.assertEqual(self.destination.readlink(), foreign)
        self.assertEqual(list(foreign.iterdir()), [])

    def test_conflicting_link_prevents_upgrade_and_uninstall(self):
        self.run_installer()
        previous = (self.destination / "SKILL.md").read_bytes()
        self.claude_link.unlink()
        self.claude_link.write_text("keep")
        self.change_package("0.2.0", "replacement")
        self.run_installer(success=False)
        self.run_installer("uninstall", success=False)
        self.assertEqual((self.destination / "SKILL.md").read_bytes(), previous)
        self.assertEqual(self.claude_link.read_text(), "keep")
        self.assertTrue(self.agent_link.is_symlink())

    def test_copy_failure_preserves_previous_installation(self):
        self.run_installer()
        previous = (self.destination / "SKILL.md").read_bytes()
        (self.package / "skills" / NAME / "broken").symlink_to(self.work / "missing")
        self.run_installer(success=False)
        self.assertEqual((self.destination / "SKILL.md").read_bytes(), previous)
        self.assertTrue((self.agent_link / "SKILL.md").is_file())

    def test_interrupted_replacement_restores_previous_installation(self):
        self.run_installer()
        previous = (self.destination / "SKILL.md").read_bytes()
        self.change_package("0.2.0", "replacement")
        installer = runpy.run_path(str(self.package / "scripts/install.py"))
        original_rename = Path.rename

        def interrupt_replacement(path, target):
            if path.name == "skill" and target == self.destination:
                raise KeyboardInterrupt
            return original_rename(path, target)

        with patch.object(Path, "rename", interrupt_replacement):
            with self.assertRaises(KeyboardInterrupt):
                installer["install"](
                    self.destination, (self.agent_link, self.claude_link), "0.1.0", False
                )
        self.assertEqual((self.destination / "SKILL.md").read_bytes(), previous)

    def test_uninstall_preserves_neighbors_and_can_repeat(self):
        self.run_installer()
        neighbor = self.destination.parent / "another-skill"
        neighbor.mkdir()
        (neighbor / "SKILL.md").write_text("keep")
        self.run_installer("uninstall")
        self.run_installer("uninstall")
        self.assertFalse(self.destination.exists())
        self.assertFalse(self.agent_link.is_symlink())
        self.assertFalse(self.claude_link.is_symlink())
        self.assertEqual((neighbor / "SKILL.md").read_text(), "keep")

    def test_parallel_installs_complete_consistently(self):
        processes = [
            subprocess.Popen(
                self.command("install", "--auto"),
                cwd=self.work,
                env=self.environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            for _ in range(4)
        ]
        for process in processes:
            stdout, stderr = process.communicate(timeout=15)
            self.assertEqual(process.returncode, 0, stderr)
            self.assertEqual(stdout, "")
        self.assert_installed()

    def test_marketplace_hook_runs_without_context_output(self):
        hook_file = json.loads((self.package / "hooks/hooks.json").read_text())
        hook = hook_file["hooks"]["SessionStart"][0]["hooks"][0]
        environment = self.environment | {"CLAUDE_PLUGIN_ROOT": str(self.package)}
        command = hook["command"] + " --home " + shlex.quote(str(self.user_root))
        result = subprocess.run(
            ["sh", "-c", command],
            cwd=self.work,
            env=environment,
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assert_installed()


if __name__ == "__main__":
    unittest.main()
