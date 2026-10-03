"""Exercise installs in disposable homes, never the real desktop."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("dots_install", ROOT / "install.py")
INSTALL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSTALL)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dots-tests-")
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / "home"
        self.home.mkdir()

    def run_install(self, *args, home=True, env=None):
        command = [sys.executable, str(ROOT / "install.py")]
        if home:
            command += ["--home", str(self.home)]
        return subprocess.run(command + list(args), capture_output=True, text=True, env=env)

    def manifests(self):
        return sorted((self.home / ".local/state/dots/backups").glob("*/manifest.json"))

    def test_preview_does_not_create_any_files(self):
        result = self.run_install("all")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Preview only", result.stdout)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_selective_install_preserves_unrelated_files(self):
        other = self.home / ".config/kitty/other.conf"
        other.parent.mkdir(parents=True)
        other.write_text("keep me")
        result = self.run_install("kitty", "--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((other.parent / "kitty.conf").is_file())
        self.assertEqual(other.read_text(), "keep me")
        self.assertFalse((self.home / ".config/niri").exists())
        self.assertFalse((self.home / "apply.sh").exists())

    def test_conflicts_are_backed_up_and_repeat_is_idempotent(self):
        target = self.home / ".config/starship.toml"
        target.parent.mkdir()
        target.write_text("original")
        result = self.run_install("starship", "--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads(self.manifests()[0].read_text())
        self.assertEqual(Path(manifest[0]["backup"]).read_text(), "original")
        self.assertEqual(manifest[0]["target"], str(target))
        first = target.read_bytes()
        again = self.run_install("starship", "--apply")
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertEqual(target.read_bytes(), first)
        self.assertEqual(len(self.manifests()), 1)

    def test_file_symlink_is_saved_without_modifying_its_target(self):
        original = Path(self.temp.name) / "managed.toml"
        original.write_text("managed file")
        target = self.home / ".config/starship.toml"
        target.parent.mkdir()
        target.symlink_to(original)
        result = self.run_install("starship", "--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(target.is_symlink())
        self.assertEqual(original.read_text(), "managed file")
        saved = Path(json.loads(self.manifests()[0].read_text())[0]["backup"])
        self.assertTrue(saved.is_symlink())
        self.assertEqual(saved.resolve(), original)

    def test_symlinked_parent_is_refused_before_any_module_is_written(self):
        external = Path(self.temp.name) / "external"
        external.mkdir()
        (self.home / ".config").symlink_to(external)
        result = self.run_install("bash", "kitty", "--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Symlinked parent", result.stderr)
        self.assertFalse((self.home / ".bashrc").exists())
        self.assertEqual(list(external.iterdir()), [])

    def test_full_install_renders_paths_and_has_only_payload_files(self):
        # Quotes and spaces in a home path must remain valid TOML.
        self.home = Path(self.temp.name) / 'quoted "home space'
        self.home.mkdir()
        result = self.run_install("all", "--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        config = tomllib.loads((self.home / ".config/noctalia/config.toml").read_text())
        self.assertEqual(config["wallpaper"]["directory"], str(self.home / "Pictures/Wallpapers"))
        wallpaper = Path(config["wallpaper"]["default"]["path"])
        self.assertTrue(wallpaper.is_file())
        self.assertEqual(wallpaper.read_bytes(),
                         (ROOT / "modules/wallpaper/Pictures/Wallpapers/neon-exzm3l.png").read_bytes())
        self.assertFalse((self.home / "README.md").exists())
        self.assertFalse((self.home / "apply.sh").exists())

    def test_reset_noctalia_only_removes_gui_settings_and_saves_them(self):
        gui = self.home / ".local/state/noctalia/settings.toml"
        gui.parent.mkdir(parents=True)
        gui.write_text('[theme]\nmode = "light"\n')
        history = gui.parent / "notification_history.json"
        history.write_text('["private"]')
        preview = self.run_install("noctalia", "--reset-noctalia")
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertTrue(gui.exists())
        result = self.run_install("noctalia", "--reset-noctalia", "--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(gui.exists())
        self.assertEqual(history.read_text(), '["private"]')
        entries = json.loads(self.manifests()[0].read_text())
        saved = next(entry for entry in entries if entry["target"] == str(gui))
        self.assertEqual(Path(saved["backup"]).read_text(), '[theme]\nmode = "light"\n')

    def test_custom_xdg_destinations(self):
        config = self.home / "custom-config"
        state = self.home / "custom-state"
        env = dict(os.environ, HOME=str(self.home), XDG_CONFIG_HOME=str(config), XDG_STATE_HOME=str(state))
        result = self.run_install("kitty", "--apply", home=False, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((config / "kitty/kitty.conf").is_file())
        self.assertTrue(list((state / "dots/backups").glob("*/manifest.json")))
        self.assertFalse((self.home / ".config").exists())

    def test_noctalia_overrides_use_their_own_config_and_state_roots(self):
        config = self.home / "xdg-config"
        state = self.home / "xdg-state"
        noctalia_config = self.home / "shell-config"
        noctalia_state = self.home / "shell-state"
        gui = noctalia_state / "noctalia/settings.toml"
        gui.parent.mkdir(parents=True)
        gui.write_text('[theme]\nmode = "light"\n')
        other_gui = state / "noctalia/settings.toml"
        other_gui.parent.mkdir(parents=True)
        other_gui.write_text("leave this profile alone")
        env = dict(os.environ, HOME=str(self.home), XDG_CONFIG_HOME=str(config),
                   XDG_STATE_HOME=str(state), NOCTALIA_CONFIG_HOME=str(noctalia_config),
                   NOCTALIA_STATE_HOME=str(noctalia_state))
        result = self.run_install("kitty", "noctalia", "--reset-noctalia", "--apply", home=False, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((config / "kitty/kitty.conf").is_file())
        self.assertTrue((noctalia_config / "noctalia/config.toml").is_file())
        self.assertFalse((config / "noctalia/config.toml").exists())
        self.assertFalse(gui.exists())
        self.assertEqual(other_gui.read_text(), "leave this profile alone")
        entries = json.loads(next((state / "dots/backups").glob("*/manifest.json")).read_text())
        saved = next(entry for entry in entries if entry["target"] == str(gui))
        self.assertEqual(Path(saved["backup"]).read_text(), '[theme]\nmode = "light"\n')

    def test_backup_permissions_are_private_even_with_permissive_umask(self):
        previous_umask = os.umask(0)
        try:
            result = self.run_install("starship", "--apply")
        finally:
            os.umask(previous_umask)
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = self.manifests()[0]
        self.assertEqual(manifest.parent.stat().st_mode & 0o777, 0o700)
        self.assertEqual(manifest.stat().st_mode & 0o777, 0o600)

    def test_noninteractive_shell_preserves_path_and_does_not_duplicate_entries(self):
        result = self.run_install("bash", "--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        env = dict(os.environ, HOME=str(self.home), PATH="/opt/custom/bin:/usr/bin:/bin")
        result = subprocess.run(["/usr/bin/bash", "--noprofile", "--norc", "-c",
                                 'source "$HOME/.bash_profile"; source "$HOME/.bashrc"; printf "%s" "$PATH"'],
                                env=env, capture_output=True, text=True, check=True)
        entries = result.stdout.split(":")
        self.assertEqual(entries.count(str(self.home / ".local/bin")), 1)
        self.assertEqual(entries.count(str(self.home / ".local/share/mise/shims")), 1)
        self.assertIn("/opt/custom/bin", entries)

    def test_invalid_module_leaves_home_unchanged(self):
        result = self.run_install("kitty", "unknown", "--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_failed_write_restores_original_files(self):
        target = self.home / ".config/starship.toml"
        target.parent.mkdir()
        target.write_text("original")
        argv = ["install.py", "starship", "--apply", "--home", str(self.home)]
        with mock.patch.object(sys, "argv", argv), \
             mock.patch.object(INSTALL.os, "replace", side_effect=OSError("injected failure")):
            with self.assertRaises(OSError):
                INSTALL.main()
        self.assertEqual(target.read_text(), "original")
        self.assertEqual(list(target.parent.glob(".dots-*")), [])

    def test_interrupt_after_a_replacement_rolls_back_the_transaction(self):
        target = self.home / ".config/kitty/kitty.conf"
        target.parent.mkdir(parents=True)
        target.write_text("original")
        real_replace = os.replace
        calls = 0

        def interrupt_second_replace(source, dest):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise KeyboardInterrupt()
            return real_replace(source, dest)

        argv = ["install.py", "kitty", "--apply", "--home", str(self.home)]
        with mock.patch.object(sys, "argv", argv), \
             mock.patch.object(INSTALL.os, "replace", side_effect=interrupt_second_replace):
            with self.assertRaises(KeyboardInterrupt):
                INSTALL.main()
        self.assertEqual(target.read_text(), "original")
        self.assertFalse((target.parent / "themes/noctalia.conf").exists())
        self.assertEqual(list(self.home.rglob(".dots-*")), [])


if __name__ == "__main__":
    unittest.main()
