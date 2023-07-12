# Quick calculator
? () { 
    echo "$*" | bc -l; }

# Smart decompress
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
 # export -f extract

# Arbitrary cd parent
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
# export -f up

# Sudo, or sudo last cmd if no arg
s() {
    if [[ $# == 0 ]]; then
        sudo $(history -p '!!')
    else
        sudo "$@"
    fi
}

# cp | mv, then go to dir
cpg (){
  if [ -d "$2" ];then
    cp $1 $2 && cd $2
  else
    cp $1 $2
  fi
}

mvg (){
  if [ -d "$2" ];then
    mv $1 $2 && cd $2
  else
    mv $1 $2
  fi
}

# cd and ls
cl() {
  local dir="$1"
  local dir="${dir:=$HOME}"
  if [[ -d "$dir" ]]; then
    cd "$dir" >/dev/null; ls
  else
    echo "bash: cl: $dir: Directory not found"
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

dirsum()
{
    if [[ ! -d $1 ]]; then
        echo "dirsum: $1 not a directory"
    else
        du -skc "$1"/* | sort -n
    fi
}

## todo
#todo() {
#    if [[ ! -f $HOME/.todo ]]; then
#        touch "$HOME/.todo"
#    fi
#
#    if ! (($#)); then
#        cat "$HOME/.todo"
#    elif [[ "$1" == "-l" ]]; then
#        nl -b a "$HOME/.todo"
#    elif [[ "$1" == "-c" ]]; then
#        > $HOME/.todo
#    elif [[ "$1" == "-r" ]]; then
#        nl -b a "$HOME/.todo"
#        eval printf %.0s- '{1..'"${COLUMNS:-$(tput cols)}"\}; echo
#        read -p "Type a number to remove: " number
#        sed -i ${number}d $HOME/.todo "$HOME/.todo"
#    else
#        printf "%s\n" "$*" >> "$HOME/.todo"#    fi
#}

##activate
#activate() {
#  if [[ $# == 0 ]]; then
#    if [[ -f $VENV_DEFAULT ]]; then
#      source $VENV_DEFAULT && VENV="tst"
#    else
#      echo "No default venv and no arguments given, set DEFAULT_ENV to the path of your activate script."
#    fi
#  else
#    local tmp="$VENV_PATH/$1"
#    if [[ -d $tmp ]]; then
#      source "$tmp/bin/activate" && VENV="$1"
#    else
#      echo "Argument not in VENV_PATH, or VENV_PATH not set."
#    fi
#  fi
#}
#
#nb() {
#  if [[ $VENV == "none" ]]; then
#    activate
#  fi
#  if [[ $# == 0 ]]; then
#    ipython notebook --profile=entry
#  else
#    ipython notebook --profile=$1
#  fi
#}

# notetaking
# note () {
#     # if file doesn't exist, create it
#     if [[ ! -f $HOME/.notes ]]; then
#         touch "$HOME/.notes"
#     fi

#     if ! (($#)); then
#         # no arguments, print file
#         cat "$HOME/.notes"
#     elif [[ "$1" == "-c" ]]; then
#         # clear file
#         printf "%s" > "$HOME/.notes"
#     else
#         # add all arguments to file
#         printf "%s\n" "$*" >> "$HOME/.notes"
#     fi
# }


pal()
{
    local palfile="$HOME/.persist_aliases"
    # Always create the file at invocation, so that we can 'cat' blindly in case of no argument.
    if [[ "! -f $palfile" ]]; then
        touch "$palfile"
    fi
    # Handle arguments slightly
    if [[ "$#" == 0 ]]; then
        cat "$palfile"
    # -r to remove an alias in palfile
    elif [[ "$1" == "-r" || "$1" == "-R" ]]; then
        #cp "$palfile" "$palfile~"  #backup
        sed "/alias $2/d" "$palfile" | sort > "$palfile~"
        mv "$palfile" "$palfile~~"
        mv "$palfile~" "$palfile"
        mv "$palfile~~" "$palfile~"
        cat "$palfile"
        printf "\n"
        printf "Removed $2. Rerun with '-b' to restore file.\n"
    # -b to restore backup of palfile if exists
    elif [[ "$1" == "-b" || "$1" == "-B" ]]; then
        if [[ -f "$palfile~" ]]; then
            mv "$palfile" "$palfile~~"
            mv "$palfile~" "$palfile"
            mv "$palfile~~" "$palfile~"
        else
            echo "error: pal: no backup file found: $palfile~"
        fi
    else
        local alias_symbol=$1  # Save first argument
        shift                  # Shift argument list
        local alias_cmd=$@     # '$@' is now arg2, arg3, ... , argN
    
        echo "alias $alias_symbol='$alias_cmd'" >> $HOME/.persist_aliases
        cat "$palfile"
        printf "\n"
        echo "Added $alias_symbol."
    fi
}


#hello

# Scripting tests, remove if forget
# source ~/develop/tmp/bashtst.sh

# tstt() {
#     if [[ $# == 0 ]]; then
#         echo "No args"
#     else
#         echo "$@"
#     fi
# }


