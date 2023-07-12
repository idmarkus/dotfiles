# If not running interactively, don't do anything
[[ $- != *i* ]] && return

export PS1="\[\033[38;5;3m\]\w\[$(tput sgr0)\]\[\033[38;5;15m\] \[$(tput sgr0)\]\[\033[38;5;2m\]|\[$(tput sgr0)\]\[\033[38;5;15m\] \[$(tput sgr0)\]\[\033[38;5;1m\]>\[$(tput sgr0)\]\[\033[38;5;15m\] \[$(tput sgr0)\]"

export VISUAL=emacs

# Sources
source ~/humanism.sh 'cd'
source ~/.bash_aliases
source ~/.bash_functions

if [[ -d "$HOME/.local/bin" ]]; then
    export PATH="$PATH:$HOME/.local/bin"
fi

# if on windows
if [[ "$MSYSTEM" ]]; then
    export NODE_PATH="/msys64/mingw64/lib/node_modules"
    export PATH="$PATH:/mingw64/bin"
fi
# Automatically cd if input is a directory
shopt -s autocd

# Dircolors
# eval `dircolors ~/.dircolors`