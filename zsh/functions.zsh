
#WRK_DIR="$HOME/code/dotfiles/zsh/misc"

#cdtmux(){
# if [[ $# == 0 ]]; then
#     cd $HOME && tmux send-keys -t 0 "cd $HOME && clear && ls" C-m
# else
#    cd $1 && tmux send-keys -t 0 "cd $PWD && clear && ls" C-m
# fi
#}

#FN_DIR="$WRK_DIR/functions"
#source $FN_DIR/back.zsh
up(){
    local d=""
    limit=$1
    for ((i=1 ; i <= limit ; i++))
        do
            d=$d/..
        done
    d=$(echo $d | sed 's/^\///')
    if [ -z "$d" ]; then
        d=..
    fi
    cd $d
  }

extract () {
 if [ -f $1 ] ; then
     case $1 in
         *.tar.bz2)   tar xvjf $1    ;;
         *.tar.gz)    tar xvzf $1    ;;
         *.bz2)       bunzip2 $1     ;;
         *.rar)       unrar x $1       ;;
         *.gz)        gunzip $1      ;;
         *.tar)       tar xvf $1     ;;
         *.tbz2)      tar xvjf $1    ;;
         *.tgz)       tar xvzf $1    ;;
         *.zip)       unzip $1       ;;
         *.Z)         uncompress $1  ;;
         *.7z)        7z x $1        ;;
         *)           echo "don't know how to extract '$1'..." ;;
     esac
 else
     echo "'$1' is not a valid file!"
 fi
 }

s() {
    if [[ $# == 0 ]]; then
        sudo $(fc -ln -1 -1)  # Latest command in history
    else
        sudo "$@"
    fi
}

backup() {
  if [[ -f $1 ]]; then
    local bucp="$1~"
    if [[ ! -e $CWD/$bucp || $2 == "-o" ]]; then
      cp $1 $bucp
    else
      echo "Older backup exists, append -o to override."
    fi
  else
    echo "$1 is not a file."
  fi
}

#activate() {
#  if [[ $# == 0 ]]; then
#    if [[ -f $VENV_DEFAULT ]]; then
#      source $VENV_DEFAULT
#    else
#      echo "No default venv and no arguments given, set DEFAULT_ENV to the path of your activate script."
#    fi
#  else
#    local tmp="$VENV_PATH/$1"
#    if [[ -d $tmp ]]; then
#      source "$tmp/bin/activate"
#    else
#      echo "Argument not in VENV_PATH, or VENV_PATH not set."
#    fi
#  fi
#}

##
##   recursive cd  (source in .bash_aliases)
##
##   c            go to last dir
##   c path       go to path, if not in cwd search forward and backward for
##                *PaTh* in tree
#
## (optional) use env var HUMANISM_CD_DEPTH for maxdepth
#if [ -z $HUMANISM_CD_DEPTH ]; then
#    HUMANISM_CD_DEPTH=8
#fi
#dir_in_tree () {
#    local BASEDIR="$1"
#    local SEARCH="${@:2}"
#    local DEPTH=1
#    local DIR
#    for DEPTH in $(seq 1 $HUMANISM_CD_DEPTH); do
#        # timeout forces stop after one second
#        if [ "Linux" = "$OS" ]; then
#            DIR=$(timeout -s SIGKILL 1s \
#                  /usr/bin/env find $BASEDIR -mindepth $DEPTH -maxdepth $DEPTH -iname "*$SEARCH*" -type d \
#                           -printf "%C@ %p\n" 2>/dev/null | sort -n | tail -1 | awk '{$1=""; print}' )
#                        #-exec stat --format "%Y##%n" humanism.sh/dbg (NOTE ISSUE WITH SPACE)
#        else
#            DIRS=$(/usr/bin/env find $BASEDIR -depth $DEPTH -iname "*$SEARCH*" -type d \
#                       -exec stat -f "%m %N" {} 2>/dev/null \; & sleep 0.5; kill $! 2>/dev/null)
#            if [[ $DIRS ]]; then
#                DIR=$(echo "$DIRS"  | sort -n | tail -1 | awk '{$1=""; print}')
#            fi
#        fi
#
#        if [[ $DIR ]]; then
#            # remove trailing space
#            echo "${DIR## }"
#            break
#        fi
#        DEPTH=$(($DEPTH+1))
#    done
#}
#c () {
#    # no args: go to last dir
#    if [ $# -eq 0 ]; then
#        if [ -f ~/.cwd ]; then
#                builtin cd "`cat ~/.cwd`"
#        else
#                builtin cd
#        fi
#        pwd > ~/.cwd
#        return 0
#    # arg1: if has a slash then assume its just a direct path we do not need to find
#    # oh and, suck up all args as the path. hence no more: cd ./a\ dir\ with\ spaces/
#    elif [[ "$1" == */* ]]; then
#            builtin cd "$*"
#            pwd > ~/.cwd
#            return 0
#    # arg1: has no slashes so find it in the cwd
#    else
#        D=$(dir_in_tree . "$*")
#        if [[ "$D" ]]; then
#            builtin cd "$D"
#            pwd > ~/.cwd
#            return 0
#        fi
#        # now search backward and upward
#        echo "<>"
#        local FINDBASEDIR=""
#        for i in $(seq 1 $HUMANISM_CD_DEPTH); do
#                FINDBASEDIR="../$FINDBASEDIR"
#                D=$(dir_in_tree "$FINDBASEDIR" "$*")
#                if [[ "$D" ]]; then
#                       builtin cd "$D"
#                       pwd > ~/.cwd
#                       break
#                fi
#        done
#    fi
#    }
#    cd () {
#        builtin cd "$@"
#        pwd >! ~/.cwd
#    }
