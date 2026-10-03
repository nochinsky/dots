#!/bin/sh
# Run explicitly inside your graphical session after installing the gtk module.
set -eu
gsettings set org.gnome.desktop.interface gtk-theme 'adw-gtk3-dark'
gsettings set org.gnome.desktop.interface icon-theme 'Adwaita'
gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'
