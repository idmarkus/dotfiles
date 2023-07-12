# Oh-my-zsh
export ZSH=$HOME/.oh-my-zsh
plugins=(archlinux history-substring-search)
source $ZSH/oh-my-zsh.sh
#source ~/code/scripts/humanism.sh 'cd'
# Test
#source $HOME/code/scripts/humanism.sh

# Python's path.
#py_libraries="$HOME/code/libraries/python"
#export PYTHONPATH="$PYTHONPATH:$py_libraries"

# Options
#setopt extended_glob
setopt autocd
setopt correct
# globdots:
# Lets hidden files ('.filename')
# be matched by globs.
setopt globdots
setopt histignoredups
# noclobber:
# Disallows piping into an existing file,
# eg; ls > file.txt, will fail if file.txt exists.
# To override use '>!', this will also be what is
# stored in the history, so using '!!' will run;
# ls >! file.txt
setopt noclobber    # Bang overrides.

#    # Tests;
#setopt auto_pushd
#setopt pushd_ignore_dups
#setopt pushdminus

# Variables
export EDITOR='emacs'
export VISUAL='emacs'

# Modules
extpath="$HOME/code/dotfiles/zsh"
source $extpath/aliases.zsh
source $extpath/functions.zsh
source $extpath/archlinux.zsh
source $extpath/syntax/zsh-syntax-highlighting.zsh
source $extpath/history-search/zsh-history-substring-search.zsh

source /usr/share/zsh/plugins/zsh-dircolors-solarized/zsh-dircolors-solarized.zsh

# Prompt
PROMPT="%F{yellow}%{${fg[yellow]}%}%3~%(0?. . ${fg[red]}%? )%{${reset_color}%}%F{green}| %(?.%F{magenta}.%F{red})>%f "

# Dircolors
#eval `dircolors ~/.dircolors`
