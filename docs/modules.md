# Module notes

Modules can be installed separately, but the complete desktop intentionally
connects several of them. Selecting a module chooses files to copy; it does
not install its applications or automatically select other modules.

| Module | Required for the intended behavior |
| :--- | :--- |
| `niri` | niri; Noctalia for its launcher/panel/lock/media bindings; Kitty and Nautilus for app shortcuts |
| `noctalia` | Noctalia v5; the `wallpaper` module or your own image paths; review theme targets below |
| `kitty` | Kitty and FiraCode Nerd Font; the shipped palette works without Noctalia |
| `gtk` | GTK apps; adw-gtk3 for GTK 3; run `scripts/apply-gtk.sh` explicitly for dconf preferences |
| `qt` | An application that reads KDE color settings; this does not configure a Qt platform-theme plugin |
| `fonts` | Inter, FiraCode Nerd Font, Noto CJK, and Noto emoji from the package list |
| `bash` | Bash; fzf, Starship, mise, and Cargo are optional and detected before use |
| `starship` | Starship plus initialization in your shell; the `bash` module provides it for Bash |
| `fastfetch`, `btop` | The matching CLI app |
| `environment` | systemd user services; shells use their own initialization |
| `wallpaper` | An image viewer or wallpaper renderer; it does not start one |

## Noctalia owns its enabled theme targets

The config enables `gtk3`, `gtk4`, `kitty`, `niri`, and `starship` templates.
When Noctalia starts or its palette changes, these templates generate colors
and may edit includes, palette selections, and GTK appearance preferences in
those apps' existing configs. This happens independently of which modules you
selected in `install.py`.

Before using only Noctalia's bar/panels with your own app themes, edit the
installed `[theme.templates]` table to select your intended targets. An empty
`builtin_ids = []` opts out of all built-in app theming. Disabling previously
enabled templates also invokes Noctalia's cleanup hooks, which can remove their
generated files/includes. Back up your own configs before changing that scope.
See [upstream app theming](https://docs.noctalia.dev/noctalia/theming/app-theming/).

The installer backs up files it copies; it cannot back up every later write by
a running application. Copy snippets manually if you want to preserve your
existing main config file rather than replace it.

Fastfetch and the optional `qt` palette are static snapshots. They do not follow
wallpaper changes through the enabled templates. The repo does not promise
automatic recoloring of every application.

## Shell and graphical PATH

The `bash` module sets user binary/shim paths for both interactive terminals
and noninteractive login shells. It preserves your inherited PATH and avoids
duplicate entries. This lets `niri-session` import a usable login environment.

`environment.d` supplies those paths to systemd user services. Both files use
mise's default data directory; if you customize `MISE_DATA_DIR` or its shim
directory, adapt those entries. You still need to install and configure any
developer runtimes yourself. After an external package manager adds executables
inside a mise runtime, `mise reshim` may be needed. See
[mise shims](https://mise.jdx.dev/dev-tools/shims.html).

The former fixed `niri.service.d/10-path.conf` is no longer shipped. If you
installed an earlier version, inspect that drop-in and remove it if it is the
repo's old fixed PATH override. Then run `systemctl --user daemon-reload` before
your next login. The copy installer keeps existing untracked files, so it does
not remove retired files for you.
