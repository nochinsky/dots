# dots

A minimal Arch Linux desktop built around **niri** and **Noctalia**: rounded
windows, a quiet translucent bar, and a monochrome palette generated from the
wallpaper.

![niri and Noctalia with a scenery wallpaper and monochrome terminal](assets/desktop.webp)

The repo mirrors `$HOME`. There is no installer: copy only the files you want.

## Copy what you need

| Want | Copy | Packages |
| :--- | :--- | :--- |
| Terminal | `.config/kitty/` | `kitty` |
| Prompt | `.config/starship.toml` | `starship` |
| Fonts | `.config/fontconfig/` | `inter-font`, `ttf-firacode-nerd`, `ttf-nerd-fonts-symbols`, `noto-fonts-cjk`, `noto-fonts-emoji` |
| GTK and Qt colors | `.config/gtk-3.0/`, `.config/gtk-4.0/`, `.config/kdeglobals` | `adw-gtk-theme`, `adwaita-icon-theme` |
| System info | `.config/fastfetch/` | `fastfetch` |
| Shell | `.bashrc`, `.bash_profile` | `mise`, `fzf` (optional) |
| Full desktop | everything above, plus `.config/niri/`, `.config/noctalia/`, `.config/environment.d/`, `Pictures/` | [`packages/base.txt`](packages/base.txt) |

## Full install

```bash
git clone https://github.com/nochinsky/dots.git
cd dots

sudo pacman -S --needed $(cat packages/base.txt)
sudo pacman -S --needed $(cat packages/optional.txt)   # optional CLI tools

# Back up what you have, then copy. Same-named files are overwritten.
tar -czf ~/dots-backup-$(date +%F).tar.gz ~/.config ~/.bashrc ~/.bash_profile 2>/dev/null
cp -r .config/. ~/.config/
cp .bashrc .bash_profile ~/
cp -r Pictures/. ~/Pictures/
```

Noctalia must be the v5 `noctalia` package, not the incompatible v4
`noctalia-shell`. Tested with niri 26.04, Noctalia 5.2.1, and kitty 0.49.2.

Set the GTK preferences, validate the configs, then log into the niri session:

```bash
gsettings set org.gnome.desktop.interface gtk-theme 'adw-gtk3-dark'
gsettings set org.gnome.desktop.interface icon-theme 'Adwaita'
gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'

niri validate
noctalia config validate
```

## Displays

niri picks the mode and scale for each output automatically. The shipped
[outputs.kdl](.config/niri/noctalia/outputs.kdl) is comments only. Add an
`output` block after running `niri msg outputs`, or start from the
[laptop example](examples/laptop-outputs.kdl).

## Keybindings

`Mod` is Super. The full list is in [docs/keybindings.md](docs/keybindings.md).

## Notes

- Noctalia generates `niri/noctalia.kdl`, the kitty theme, the GTK
  `noctalia.css` files, and the Starship palette. They ship for first-start
  colors and are overwritten on theme changes. `[theme.templates]` in
  [config.toml](.config/noctalia/config.toml) controls which apps it touches.
- `~/.local/state/noctalia/settings.toml`, written by the Settings window, loads
  after `config.toml` and wins. Remove it to fall back to this config.
- The default wallpaper is `~/Pictures/Wallpapers/scenery-96l5xd.webp`. Change
  it in [config.toml](.config/noctalia/config.toml) for your own image.

## Credits

[niri](https://github.com/niri-wm/niri) · [Noctalia](https://github.com/noctalia-dev/noctalia) ·
[kitty](https://sw.kovidgoyal.net/kitty/) · [adw-gtk3](https://github.com/lassekongo83/adw-gtk3) ·
Wallpaper: [Wallhaven #96l5xd](https://wallhaven.cc/w/96l5xd) by **RevanLord**.

## License

[MIT](LICENSE). The wallpaper and screenshot are excluded from that license;
their creators retain the rights.
