# nochinsky-dots

## Install order

1. **System base** — archinstall or manual Arch setup
2. **GPU drivers** — if NVIDIA, follow `nvidia-install.txt`
3. **Core packages** — `sudo pacman -S --needed $(grep -v '^#' core-pkgs.txt)`
4. **Optional packages** — pick from `optional-pkgs.txt` per host
5. **Post-install** — run through `post-install.txt`
6. **Copy configs** — mirror everything into `~/.config/`:
   - `hypr/`, `waybar/`, `wofi/`, `kitty/`, `mako/`, `gtk-4.0/`, `images/wallpapers/`
7. **Host config** — create `~/.config/hypr/host/monitors.conf` and `nvidia.conf` from the `.example` files
8. **Reboot** — `first-boot.sh` runs once, applies GTK theme + cursor via gsettings, then self-skips

## Structure

| Path | Purpose |
|---|---|
| `core-pkgs.txt` | Packages required for the rice to function |
| `optional-pkgs.txt` | Per-host hardware packages |
| `nvidia-install.txt` | NVIDIA driver setup (modeset, mkinitcpio, UKI) |
| `post-install.txt` | System tweaks (pacman, mirrors, fstrim, power profiles, cleanup) |
| `hypr/` | Hyprland config (base rice + host overrides) |
| `hypr/scripts/first-boot.sh` | One-time gsettings theming, runs on first boot only |
| `waybar/` | Waybar bar + style |
| `wofi/` | App launcher |
| `kitty/` | Terminal |
| `mako/` | Notification daemon |
| `gtk-4.0/` | GTK4/libadwaita dark theme config |
| `images/wallpapers/` | Wallpaper images |
