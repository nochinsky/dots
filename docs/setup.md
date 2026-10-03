# Setup

These files reproduce the desktop on an existing Arch Linux installation.
The installer uses Python 3; the repository checks require Python 3.11 or newer.
They do not provision disks, bootloaders, GPU drivers, networking, or a login
manager. Install the correct drivers for your own hardware first.

## 1. Packages

Review [desktop.txt](../packages/desktop.txt) before running this in Bash:

```bash
mapfile -t packages < <(sed '/^[[:space:]]*#/d; /^[[:space:]]*$/d' packages/desktop.txt)
sudo pacman -Syu --needed "${packages[@]}"
```

Noctalia is the native v5 `noctalia` package in Arch's extra repository.
The v4 `noctalia-shell` package is not compatible with this TOML config.
See [Noctalia's installation guide](https://docs.noctalia.dev/noctalia/getting-started/installation/).

Optional CLI tools are listed in [extras.txt](../packages/extras.txt):

```bash
mapfile -t packages < <(sed '/^[[:space:]]*#/d; /^[[:space:]]*$/d' packages/extras.txt)
sudo pacman -S --needed "${packages[@]}"
```

The `bash` module gracefully skips missing fzf, Starship, mise, and Cargo.
The editor variables use `nvim`; install Neovim or change them.

## 2. Install the files

```bash
python install.py all                       # read the preview
python install.py all --apply
```

Run as your normal user. Nothing invokes sudo, executes module scripts, reloads
your running desktop, or enables services.
Review [module notes](modules.md) for dependencies and Noctalia's later theme
writes when you install only part of the desktop.

The installer fills the two wallpaper placeholders in the Noctalia TOML with
your home directory. To copy that config manually, replace `@WALLPAPER_DIR@`
and `@WALLPAPER@` with your wallpaper folder and image path.

For an existing Noctalia setup, GUI settings load after `config.toml` and can
override its appearance. Review your `~/.local/state/noctalia/settings.toml`.
To start with this repo's settings, explicitly back up and remove that override:

```bash
python install.py noctalia --reset-noctalia          # preview
python install.py noctalia --reset-noctalia --apply
```

This only removes `settings.toml`; clipboard data, notification history, and
other state remain in place. Other TOML files already in the Noctalia config
directory may also override values: review them before starting the session.
See [Noctalia's config layering](https://docs.noctalia.dev/noctalia/configuration/).

The installer also honors `NOCTALIA_CONFIG_HOME` and `NOCTALIA_STATE_HOME`
when set. They take precedence over XDG directories for Noctalia's own files.
`--home` ignores both sets of overrides for an isolated test installation.

## 3. Match your displays and keyboard

The tracked [outputs.kdl](../modules/niri/.config/niri/noctalia/outputs.kdl)
uses niri's automatic display selection. Adjust the installed copy for your
connectors, scale, and arrangement:

```bash
niri msg outputs
```

My laptop uses `eDP-1`, 2880×1800 at 120Hz, and 1.5 scale. Its exact config is
[laptop-outputs.kdl](../examples/laptop-outputs.kdl); copy it over
`~/.config/niri/noctalia/outputs.kdl` if that suits your display. Display names
and scale are machine-specific. With a custom `XDG_CONFIG_HOME`, use that
directory in place of `~/.config` throughout these instructions.

The keyboard follows the system layout. Configure it with `localectl` or set
an `xkb` block under `input.keyboard` in niri. `Mod` is Super on the default
niri keyboard setup. See the [niri configuration reference](https://niri-wm.github.io/niri/Configuration:-Introduction).

## 4. GTK, audio, and the session

Apply the three GTK preferences explicitly from your graphical session:

```bash
sh scripts/apply-gtk.sh
```

This selects `adw-gtk3-dark`, Adwaita icons, and the dark color preference. The
fontconfig module sets generic UI and monospace font fallbacks. Explicit app
font choices can still take precedence.

Ensure PipeWire and WirePlumber are running. Arch normally supplies activation
units; if they are disabled in your existing setup, enable them:

```bash
systemctl --user enable --now pipewire.socket pipewire-pulse.socket wireplumber.service
```

UPower and power-profiles-daemon provide the battery and power profile widgets.
Your network stack and Bluetooth service should already be configured if you
want those controls to work. This repo does not replace their system setup.

Validate before logging out:

```bash
niri validate
noctalia config validate
```

Then log into the **niri** session in your display manager, or run
`niri-session` from a TTY. The config starts Noctalia automatically. Log in again
for updated login-shell and user-service environments. Avoid starting a second
Noctalia instance. See [migration notes](modules.md#shell-and-graphical-path) if
you installed the previous fixed PATH service override.

Noctalia's first-run assistant may appear on a fresh profile. Keep the imported
theme/bar choices; changes made there or in Settings create GUI overrides.

## Optional login screen

My machine uses greetd with Noctalia Greeter. This is separate from the desktop
and is not required. Install `greetd` and `noctalia-greeter` through a package
source you trust; the latter was locally installed here and is not present in
my enabled official Arch repositories.

After checking the installed session command, adapt
[greetd.toml](../examples/greetd.toml) for `/etc/greetd/config.toml`. Choose a
single display manager and enable it yourself. When the shell is running,
`noctalia msg greeter-sync` syncs its appearance to the greeter.

Automatic GNOME Keyring unlock also needs login-session/PAM integration; merely
installing the package is not enough. This machine's `/etc/pam.d/greetd` has
custom `pam_gnome_keyring.so` authentication and `auto_start` session entries
that the stock greetd package lacks. This repo does not install those system
authentication changes. Configure your chosen login manager's keyring
integration, and check that your default keyring unlocks at login. Otherwise
Noctalia's encrypted clipboard history may be unavailable until it is unlocked.
See [Noctalia's keyring guide](https://docs.noctalia.dev/noctalia/configuration/secret-service/).

## Changes, backups, and removal

Configs are copies: edit the installed files freely, then copy intentional
changes back into the corresponding repo module. Noctalia-generated theme
files are snapshots; the shared template settings regenerate them.

Each install creates a manifest in
`~/.local/state/dots/backups/<timestamp>/manifest.json` (or your
`XDG_STATE_HOME`). It records destination paths and original-file backups.
The per-install directory is private (0700), and its manifest is 0600. This
also protects original settings when the user's umask permits public reads.
Restore those originals to the recorded destinations to undo replacements.
For entries whose `backup` is `null`, remove the installed file if you no
longer want it. Keep changes you made after installation before restoring.

The installer refuses symlinked parent directories rather than writing through
them. Existing destination-file symlinks are backed up as symlinks; their
targets are left untouched. If you already manage a whole config directory
with symlinks, copy the desired snippets through your own dotfile workflow.

Idle locks and blanks after 300 seconds. It does not suspend. Lid-close
behavior comes from your system's logind configuration.

## Verify a change

```bash
python -m unittest discover -s tests -v
python scripts/check.py
bash -n modules/bash/.bashrc modules/bash/.bash_profile
sh -n scripts/apply-gtk.sh
niri validate -c modules/niri/.config/niri/config.kdl
noctalia config validate modules/noctalia/.config/noctalia/config.toml
```

GitHub Actions runs the installer tests, data-format checks, documentation
links, and shell syntax checks. A separate Arch container job installs current
niri and Noctalia packages and runs their semantic config validators. This
catches incompatibilities with rolling releases; it does not boot a graphical
session or test a complete OS install.
