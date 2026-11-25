#
# ~/.bashrc
#

# Login shells (including niri-session's) are noninteractive too, so PATH is
# set before the interactive check. Entries are skipped if already present, so
# sourcing this file twice does not duplicate them.
for dots_path in "$HOME/.local/share/mise/shims" "$HOME/.local/bin"; do
    case ":${PATH:-}:" in
        *":$dots_path:"*) ;;
        *) PATH="$dots_path${PATH:+:$PATH}" ;;
    esac
done
unset dots_path
export PATH
[[ ! -f "$HOME/.cargo/env" ]] || source "$HOME/.cargo/env"

# Exported so child processes see them (git, crontab, sudoedit, ...). GUI apps
# get them via ~/.config/environment.d/10-user.conf.
export EDITOR=nvim
export VISUAL=nvim

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

alias ls='ls --color=auto'
alias grep='grep --color=auto'
PS1='[\u@\h \W]\$ '

# fzf: fuzzy history (Ctrl+R) and file completion (Ctrl+T)
[[ ! -f /usr/share/fzf/key-bindings.bash ]] || source /usr/share/fzf/key-bindings.bash
[[ ! -f /usr/share/fzf/completion.bash ]] || source /usr/share/fzf/completion.bash

# starship prompt and mise, each only if installed
if command -v starship >/dev/null 2>&1; then
    eval "$(starship init bash)"
fi
if command -v mise >/dev/null 2>&1; then
    eval "$(mise activate bash)"
fi
