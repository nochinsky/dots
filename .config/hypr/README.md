# Hyprland Config

## Structure

```
hypr/
├── hyprland.conf
├── base/           ← the rice (same on every machine)
│   ├── 00_programs.conf
│   ├── animations.conf
│   ├── autostart.conf
│   ├── env.conf
│   ├── general.conf
│   ├── keybinds.conf
│   └── windowrules.conf
└── host/           ← machine-specific (don't sync blindly)
    ├── monitors.conf        ← your monitor setup
    ├── monitors.conf.example
    ├── nvidia.conf          ← your NVIDIA vars
    └── nvidia.conf.example
```

## Setup on a new machine

1. Copy `base/` and `hyprland.conf` to `~/.config/hypr/`
2. Copy `.example` files from `host/` as needed:
   - `host/monitors.conf.example` → `host/monitors.conf`
   - `host/nvidia.conf.example` → `host/nvidia.conf`
3. Edit the `host/` files for your hardware

## Keeping in sync

When pulling updates to `base/`:
- `base/` is safe to overwrite — it contains the rice
- `host/` is machine-specific — don't overwrite it blindly
- If you edit `base/` directly, consider moving host-specific overrides to `host/`

## Hardware-specific config

| File | Purpose |
|---|---|
| `host/monitors.conf` | Display resolution, refresh rate, position, scale |
| `host/nvidia.conf` | NVIDIA environment variables |

## Keybinds reference

See `base/keybinds.conf` for all keybinds.
