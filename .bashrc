# ~/.bashrc

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

# --- PATH (not set automatically on Arch) ---
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:$PATH"

# --- Editor ---
export EDITOR=nvim
export VISUAL=nvim

# --- XDG base directories (keeps ~/ clean) ---
export XDG_CACHE_HOME="$HOME/.cache"
export XDG_CONFIG_HOME="$HOME/.config"
export XDG_DATA_HOME="$HOME/.local/share"
export XDG_STATE_HOME="$HOME/.local/state"

# --- Prompt ---
PS1='[\u@\h \W]\$ '

# --- Aliases ---
alias ls='ls --color=auto'
alias ll='ls -lh'
alias la='ls -lAh'
alias grep='grep --color=auto'
