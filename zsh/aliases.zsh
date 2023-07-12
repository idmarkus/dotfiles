alias aliae="$VISUAL /home/markus/code/dotfiles/zsh/aliases.zsh"
alias functae="$VISUAL /home/markus/code/dotfiles/zsh/functions.zsh"
alias zshrc="$VISUAL ~/code/dotfiles/zshrc.zsh"
alias reload='source ~/code/dotfiles/zshrc.zsh'
alias back='cd $OLDPWD'
#alias -g code="$HOME/code"
#alias -g books="$MEDIA/books"
#alias -g documents="$MEDIA/documents"

# Internal
# alias tst='source ~/envs/tst/bin/activate'
# alias ls='ls --color=auto'
alias lsf='ls -a | grep'
alias f.='find . | grep'
alias ls='ls -FAXh --group-directories-first --color=auto'
alias tree='tree -F --dirsfirst'
alias cp='cp -i'
alias di='di -f TM1ub -n' # disk-info, -format[fsType, Mountpoint, %(1), Used, Blocks(total)], -noheaders
# Todo.txt
#alias tdo='todo.sh'
alias xfsettings='xfce4-settings-manager'
alias ycmconfig='/home/markus/.vim/bundle/YCM-Generator/config_gen.py'
# IHaskell and IPython
nb='source /home/markus/code/envs/ihaskell/pyth/bin/activate && ipython notebook --profile=ihaskell'
alias nb=$nb
alias notebook=$nb

