#!/usr/bin/env python3
"""Copy selected dotfile modules, previewing by default and backing up conflicts."""

import argparse
import datetime
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
MODULES = ROOT / "modules"


def check_path(path):
    """Refuse to write through a symlinked directory or into a non-directory."""
    for parent in path.parents:
        if parent.is_symlink():
            raise ValueError(f"Symlinked parent: {parent}; copy this module manually instead.")
        if parent.exists() and not parent.is_dir():
            raise ValueError(f"Parent is not a directory: {parent}")
    if path.exists() and not path.is_file() and not path.is_symlink():
        raise ValueError(f"Destination is not a file: {path}")


def main():
    available = sorted(p.name for p in MODULES.iterdir() if p.is_dir())
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("modules", nargs="*", help="Module names, or all")
    parser.add_argument("--list", action="store_true", help="List available modules")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="Copy files; back up existing files")
    mode.add_argument("--dry-run", action="store_true", help="Preview only (the default)")
    parser.add_argument("--home", type=Path, help="Alternate home for testing; ignores XDG overrides")
    parser.add_argument("--reset-noctalia", action="store_true",
                        help="Back up GUI settings.toml so the declarative config wins")
    args = parser.parse_args()
    if args.list:
        print("\n".join(available))
        return
    selected = list(dict.fromkeys(args.modules))
    if not selected:
        parser.error("Choose modules or all; use --list to see them.")
    if "all" in selected:
        if len(selected) != 1:
            parser.error("Use all on its own.")
        selected = available
    unknown = set(selected) - set(available)
    if unknown:
        parser.error("Unknown modules: " + ", ".join(sorted(unknown)))
    if args.reset_noctalia and "noctalia" not in selected:
        parser.error("--reset-noctalia requires the noctalia module.")
    if args.apply and os.geteuid() == 0:
        parser.error("Run as your normal user, without sudo.")

    home = (args.home or Path.home()).expanduser().absolute()
    config = home / ".config"
    state = home / ".local/state"
    if not args.home:
        config = Path(os.environ.get("XDG_CONFIG_HOME") or config).expanduser()
        state = Path(os.environ.get("XDG_STATE_HOME") or state).expanduser()
    noctalia_config = config
    noctalia_state = state
    if not args.home:
        noctalia_config = Path(os.environ.get("NOCTALIA_CONFIG_HOME") or config).expanduser()
        noctalia_state = Path(os.environ.get("NOCTALIA_STATE_HOME") or state).expanduser()
    if not all(p.is_absolute() for p in (home, config, state, noctalia_config, noctalia_state)):
        parser.error("Home, XDG, and Noctalia paths must be absolute.")
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    backup = state / "dots/backups" / stamp
    wallpaper_dir = home / "Pictures/Wallpapers"
    replacements = {
        '"@WALLPAPER_DIR@"': json.dumps(str(wallpaper_dir), ensure_ascii=False),
        '"@WALLPAPER@"': json.dumps(str(wallpaper_dir / "neon-exzm3l.png"), ensure_ascii=False),
    }
    plan = []
    seen = set()
    for module in selected:
        for source in sorted((MODULES / module).rglob("*")):
            if source.is_symlink():
                raise ValueError(f"Module contains a symlink: {source}")
            if not source.is_file():
                continue
            relative = source.relative_to(MODULES / module)
            if relative.parts[0] == ".config":
                config_root = noctalia_config if module == "noctalia" else config
                target = config_root.joinpath(*relative.parts[1:])
            else:
                target = home / relative
            check_path(target)
            if target in seen:
                raise ValueError(f"Multiple modules write {target}")
            seen.add(target)
            data = source.read_bytes()
            if module == "noctalia" and source.suffix == ".toml":
                content = data.decode("utf-8")
                for token, value in replacements.items():
                    content = content.replace(token, value)
                data = content.encode("utf-8")
            if not target.is_symlink() and target.is_file() and target.read_bytes() == data:
                print(f"unchanged  [{module}] {target}")
                continue
            saved = backup / module / relative
            plan.append((module, source, target, saved, data))

    gui_settings = noctalia_state / "noctalia/settings.toml"
    if "environment" in selected and (config / "systemd/user/niri.service.d/10-path.conf").exists():
        print("Note: an existing niri PATH service drop-in remains in place. "
              "Review docs/modules.md before your next login.")
    reset = args.reset_noctalia and os.path.lexists(gui_settings)
    if reset:
        check_path(gui_settings)
    elif "noctalia" in selected and os.path.lexists(gui_settings):
        print("Note: existing Noctalia GUI settings override config.toml. "
              "Review them or use --reset-noctalia to back up and remove that file.")

    for module, _, target, _, _ in plan:
        action = "back up + copy" if os.path.lexists(target) else "copy"
        print(f"{action:14} [{module}] {target}")
    if reset:
        print(f"back up + remove [noctalia] {gui_settings}")
    if not args.apply:
        print("Preview only. Add --apply to write these changes.")
        return
    if not plan and not reset:
        print("Already up to date.")
        return

    # Check backup paths before any changes; prepare replacement files first.
    check_path(backup / "manifest.json")
    staged = []
    changes = []
    try:
        for module, source, target, saved, data in plan:
            target.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=target.parent, prefix=".dots-", delete=False) as file:
                temp = Path(file.name)
                staged.append((temp, target, saved))
                file.write(data)
            temp.chmod(source.stat().st_mode & 0o777)
        # Backups can include private settings. Protect them even with umask 000.
        backup.mkdir(mode=0o700, parents=True, exist_ok=False)
        manifest = []
        for temp, target, saved in staged:
            previous = os.path.lexists(target)
            changes.append((target, saved, previous))
            if previous:
                saved.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(target), str(saved))
            os.replace(temp, target)
            manifest.append({"target": str(target), "backup": str(saved) if previous else None})
        if reset:
            saved = backup / "noctalia-gui/settings.toml"
            saved.parent.mkdir(parents=True, exist_ok=True)
            changes.append((gui_settings, saved, True))
            shutil.move(str(gui_settings), str(saved))
            manifest.append({"target": str(gui_settings), "backup": str(saved)})
        with open(backup / "manifest.json", "x", encoding="utf-8",
                  opener=lambda path, flags: os.open(path, flags, 0o600)) as file:
            file.write(json.dumps(manifest, indent=2) + "\n")
    except BaseException:
        for target, saved, previous in reversed(changes):
            if saved.exists() or saved.is_symlink():
                if target.exists() or target.is_symlink():
                    target.unlink()
                shutil.move(str(saved), str(target))
            elif not previous and (target.exists() or target.is_symlink()):
                target.unlink()
        raise
    finally:
        for temp, _, _ in staged:
            if temp.exists():
                temp.unlink()
    print(f"Installed. Backup and manifest: {backup}")
    print("Review display settings before starting a new niri session.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        sys.exit(130)
