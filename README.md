# dots

A minimal Arch Linux desktop built around **niri** and **Noctalia**:
rounded windows, a quiet translucent bar, and a monochrome palette generated
from the wallpaper.

![niri and Noctalia with a scenery wallpaper and monochrome terminal](assets/desktop.webp)

The repo root mirrors `$HOME`. There is no installer: copy the files and adjust
the display settings for your machine.

## Contents

| Path | What it is |
| :--- | :--- |
| [.config/niri/](.config/niri/) | Compositor, window rules, keybinds, displays |
| [.config/noctalia/](.config/noctalia/) | Bar, launcher, idle, wallpaper, color templates |
| [.config/kitty/](.config/kitty/) · [gtk-3.0/](.config/gtk-3.0/) · [gtk-4.0/](.config/gtk-4.0/) | Terminal and GTK colors |
| [.config/fontconfig/](.config/fontconfig/) · [starship.toml](.config/starship.toml) · [fastfetch/](.config/fastfetch/) · [kdeglobals](.config/kdeglobals) | Fonts, prompt, fetch, Qt colors |
| [.bashrc](.bashrc) · [.config/environment.d/](.config/environment.d/) | Shell and user-session environment |
| [Pictures/Wallpapers/](Pictures/Wallpapers/) | The wallpaper |
| [packages/](packages/) · [examples/](examples/) | Package lists and display example |

## Install

```bash
git clone https://github.com/nochinsky/dots.git
cd dots

# Arch packages: desktop, then optional CLI tools
sudo pacman -Syu --needed $(cat packages/base.txt)
sudo pacman -Syu --needed $(cat packages/optional.txt) # optional

# Back up existing files, then copy into $HOME
tar -czf ~/dots-backup-$(date +%F).tar.gz ~/.config ~/.bashrc ~/.bash_profile ~/Pictures 2>/dev/null
mkdir -p ~/.config ~/Pictures
cp -r .config/. ~/.config/
cp .bashrc .bash_profile ~/
cp -r Pictures/. ~/Pictures/
```

Noctalia must be the v5 `noctalia` package, not the incompatible v4
`noctalia-shell`. Tested with niri 26.04, Noctalia 5.2.1, and kitty 0.49.2.

Set the GTK preferences, check the configs, then log into the niri session:

```bash
gsettings set org.gnome.desktop.interface gtk-theme 'adw-gtk3-dark'
gsettings set org.gnome.desktop.interface icon-theme 'Adwaita'
gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'

niri validate
noctalia config validate
```

## Displays and keyboard

niri picks the mode and scale for each output automatically; the shipped
[outputs.kdl](.config/niri/noctalia/outputs.kdl) is comments only. Add an
`output` block after running `niri msg outputs`, or start from the
[laptop example](examples/laptop-outputs.kdl). The keyboard layout comes from
the system (`localectl` or an `xkb` block); `Mod` is Super.

## Keybindings

| Keys | Action |
| :--- | :--- |
| `Super + Return` / `Super + Space` | Terminal / launcher |
| `Super + E` / `Super + D` / `Super + I` | Files / control center / settings |
| `Super + L` / `Super + V` / `Super + P` | Lock / clipboard / power menu |
| `Super + W`, `Super + Shift + W` | Next / random wallpaper |
| `Super + Tab` / `Alt + Tab` | Overview / recent windows |
| `Super + arrows` / `Super + Shift + arrows` | Focus / move window |
| `Super + 1…9` / `Super + Shift + 1…9` | Focus / move to workspace |
| `Super + F` / `Super + M` / `Super + T` | Fullscreen / maximize / floating |
| `Super + Q` | Close window |
| `Print` / `Ctrl + Print` | Screenshot region / fullscreen |
| `Super + Shift + /` | Hotkey overlay |

The full list is in [binds.kdl](.config/niri/noctalia/binds.kdl).

## Notes

- Noctalia generates `niri/noctalia.kdl`, the kitty theme, the GTK
  `noctalia.css` files, and the Starship palette. They ship for first-start
  colors but are overwritten on theme changes; `[theme.templates]` in
  [config.toml](.config/noctalia/config.toml) controls which apps it touches.
- `~/.local/state/noctalia/settings.toml`, written by the Settings window and
  first-run setup, loads after `config.toml` and wins. Remove it to fall back
  to this config.
- The default wallpaper is `~/Pictures/Wallpapers/scenery-96l5xd.webp`; the
  picker browses `~/Pictures`. Change both paths for your own image.
- `.bashrc` and `environment.d` add `~/.local/bin` and mise shims to `PATH` and
  set `EDITOR=nvim`.

## Credits

[niri](https://github.com/niri-wm/niri) · [Noctalia](https://github.com/noctalia-dev/noctalia) ·
[kitty](https://sw.kovidgoyal.net/kitty/) · [adw-gtk3](https://github.com/lassekongo83/adw-gtk3) ·
[Inter](https://rsms.me/inter/), [Fira Code](https://github.com/tonsky/FiraCode),
[Nerd Fonts](https://www.nerdfonts.com/), [Noto](https://notofonts.github.io/) — fonts.
Wallpaper: [Wallhaven #96l5xd](https://wallhaven.cc/w/96l5xd) by **RevanLord**.

## License

[MIT](LICENSE). The wallpaper and screenshot are excluded from that license;
their creators retain the rights.
