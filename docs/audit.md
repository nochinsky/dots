# Dotfiles audit · October 3, 2026

The desktop is coherent and usable, and its main configs validate. The repo
now has the pieces needed to share and reinstall that desktop on an existing
Arch system. It is not a fully provisioned or boot-tested operating system.

This review compared the published modules with the live configuration,
installed upstream template scripts, runtime services, and current upstream
documentation. Live configs were inspected but not changed. Several findings
were in the export/installer added for this repository.

## Verified issues addressed

| Finding | Impact | Resolution |
| :--- | :--- | :--- |
| PATH setup ran only in interactive Bash | niri-session uses a login shell that can be noninteractive; user tools were missing from the exported environment | User paths and optional Cargo initialization now run before the interactive guard. A test checks inherited entries and repeated sourcing. |
| niri service had a fixed replacement PATH | Extra inherited paths, such as custom tools and Cargo, could be dropped | Removed the shipped service override. Bash preserves the login PATH; environment.d supplies user-service paths. Existing copies need manual migration. |
| Installer ignored Noctalia-specific directory variables | With a separate shell profile, it could write config or reset GUI settings in the wrong profile | Added NOCTALIA_CONFIG_HOME / NOCTALIA_STATE_HOME precedence and an isolation test. |
| Backup permissions followed the user's umask | Original settings and paths could be exposed if the backup root was traversable | New backup directories are 0700 and manifests are 0600, including with umask 000. |
| Ctrl+C bypassed rollback | An interrupted replacement sequence could leave a partial installation | Rollback now handles interruption; a test interrupts after one successful replacement. |
| “Separate modules” did not explain runtime theme writes | Installing Noctalia alone still enables templates that can edit other application configs later | Documented dependencies, theme ownership, opt-out, and cleanup behavior in module notes. Noctalia's defaults were retained. |
| CI only checked generic syntax/data formats | It could miss valid TOML/KDL containing unsupported desktop settings | Added a separate Arch container job running actual niri and Noctalia validators. |

The first two findings are related: getting the login-shell environment right
removes the need for a fixed service-level workaround. Upstream niri-session
imports the login environment into the user manager before starting niri.
For existing installations, see [PATH migration](modules.md#shell-and-graphical-path).

Noctalia's config/state layering and runtime template writes are intentional
upstream behavior. The issue was insufficient documentation of their scope,
not the use of templates itself. See [configuration layering](https://docs.noctalia.dev/noctalia/configuration/)
and [app theming](https://docs.noctalia.dev/noctalia/theming/app-theming/).

## Live setup: remaining observations

These are observations about the current machine. They are not changes applied
by the repo audit.

- **Duplicate Cargo initialization:** the live `.bash_profile` sources
  `.cargo/env` twice. This is redundant; the exported Bash module initializes
  it once per sourcing and tolerates Cargo being absent.
- **Version-specific tool paths:** the live niri service override names mise's
  `installs/node/latest` and `installs/npm/latest` directories. These rely on
  that machine's installations and override inherited PATH. The repo now uses
  mise's default shims instead; installing the repo does not automatically
  remove the old live drop-in.
- **Two UI fonts:** generic `sans-serif` resolves to Inter, but the live GTK
  preference explicitly uses `Adwaita Sans 11`. Both work. If one font across
  all UI surfaces is the goal, choose it in both places. Fontconfig fallback
  rules do not override every explicit application font preference.
- **Static optional palettes:** Fastfetch and `kdeglobals` are snapshots;
  enabled Noctalia templates do not keep those two synchronized with changing
  wallpapers. `kdeglobals` also does not select a Qt platform-theme plugin.
- **Historical log messages:** earlier Noctalia sessions logged missing sound
  events and PipeWire/Wayland disconnection during shutdown. The current
  session's checked services are running, so these messages alone do not
  establish an ongoing config defect. Investigate if the symptoms recur.

The font difference and static snapshots are optional consistency choices.
They do not justify replacing fonts or adding another theme tool by default.

## Choices that are sound

- niri's rounded/clipped windows, floating settings rule, activation flag,
  Noctalia autostart, and overview backdrop match the
  [Noctalia niri integration guide](https://docs.noctalia.dev/noctalia/compositor-settings/niri/).
- Host display settings are isolated in an example; shared defaults do not
  force every user to use the laptop's connector or scale.
- Noctalia's declarative appearance config is shared without exporting private
  clipboard, notification, account, or session-history data.
- Copying module files lets the shell regenerate its themes without changing
  the Git checkout. A symlink-based manager is also reasonable, but is not
  required for a well-maintained dotfile repo.
- Bash's interactive-only tools are guarded, and unrelated destination files
  are kept. Existing file symlinks are backed up without overwriting their
  targets; symlinked parent directories are refused.
- Actual font matches were correct for English, Japanese, Korean, and
  Simplified/Traditional/Hong Kong Chinese across generic font families.
- Idle locking/blanking is declared together at five minutes. The running
  shell holds a “Lock before sleep” inhibitor. Interactive lock/unlock and
  lid-close suspend were not triggered during this review.

Gaps, rounded corners, focus-follows-mouse, animation timing, the monochrome
palette, and an optional greeter are preferences rather than violations of
dotfile best practices.

## Verification and practical limits

Fourteen installer tests passed, covering previews, selective installs,
backups, symlinks, custom directories, interruption, permissions, and login
PATH behavior. TOML/JSON/XML, local doc links, and shell syntax passed.

A full install into a temporary home passed niri, Noctalia, Fastfetch, and
Starship checks, including the merged Noctalia export and wallpaper path.
Both desktop configs also validated in a clean Arch container with freshly
installed packages. The live user manager had no failed units; checked portal
and WirePlumber services were active.

Remaining release-quality work is a fresh graphical login or VM install using
only the documented dependencies, with manual checks of the launcher,
clipboard, screenshots, lock/unlock, screen sharing, and audio/brightness keys.
A container config validator cannot verify those interactions. The installer
is not crash/power-loss atomic, and it does not automatically delete retired
files or restore later edits made by applications.

The earlier screenshot predates the final bar/GTK adjustments, as its README
caption states. Replacing it with a new clean screenshot would improve visual
accuracy. Wallpaper redistribution rights remain unverified; see
[credits](credits.md).
