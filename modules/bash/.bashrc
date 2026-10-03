export EDITOR=nvim
export VISUAL=nvim

# Login shells used by niri-session are noninteractive too. Preserve the
# inherited PATH and avoid adding duplicate entries when this file is sourced.
for dots_path in "$HOME/.local/share/mise/shims" "$HOME/.local/bin"; do
    case ":${PATH:-}:" in
        *":$dots_path:"*) ;;
        *) PATH="$dots_path${PATH:+:$PATH}" ;;
    esac
done
unset dots_path
export PATH
[[ ! -f "$HOME/.cargo/env" ]] || source "$HOME/.cargo/env"

[[ $- != *i* ]] && return

alias ls='ls --color=auto'
alias grep='grep --color=auto'
PS1='[\u@\h \W]\$ '

[[ ! -f /usr/share/fzf/key-bindings.bash ]] || source /usr/share/fzf/key-bindings.bash
[[ ! -f /usr/share/fzf/completion.bash ]] || source /usr/share/fzf/completion.bash

if command -v starship >/dev/null 2>&1; then
    eval "$(starship init bash)"
fi
if command -v mise >/dev/null 2>&1; then
    eval "$(mise activate bash)"
fi
