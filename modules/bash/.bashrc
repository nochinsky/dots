export EDITOR=nvim
export VISUAL=nvim

[[ $- != *i* ]] && return

alias ls='ls --color=auto'
alias grep='grep --color=auto'
PS1='[\u@\h \W]\$ '

export PATH="$HOME/.local/bin:$PATH"

[[ ! -f /usr/share/fzf/key-bindings.bash ]] || source /usr/share/fzf/key-bindings.bash
[[ ! -f /usr/share/fzf/completion.bash ]] || source /usr/share/fzf/completion.bash

if command -v starship >/dev/null 2>&1; then
    eval "$(starship init bash)"
fi
if command -v mise >/dev/null 2>&1; then
    eval "$(mise activate bash)"
fi
[[ ! -f "$HOME/.cargo/env" ]] || source "$HOME/.cargo/env"
