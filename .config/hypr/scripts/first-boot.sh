#!/bin/bash
# first-boot — runs once, applies GTK/cursor theme, then self-destructs
set -euo pipefail
MARKER="$HOME/.config/hypr/.first-boot-done"

[[ -f "$MARKER" ]] && exit 0

# GTK theme
gsettings set org.gnome.desktop.interface gtk-theme 'adw-gtk3-dark'
gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'

# Cursor
gsettings set org.gnome.desktop.interface cursor-theme 'Adwaita'
gsettings set org.gnome.desktop.interface cursor-size 24

touch "$MARKER"
