# Oh My Zsh sources every *.zsh file of this folder, so this survives Oh My Zsh updates and does not replace ~/.zshrc.
# Replace ls with eza (maintained fork of exa), long listing with hidden files by default (like "ls -la").
#
# Most ls options work as-is with eza (-l, -a, -A, -h, -R, -r, -1, -d, -F, -i, --color...), but two common
# ones mean something else in eza: "-t" expects a value and "-S" is the block size. The function below
# translates them to the ls behavior: -t sorts by modification time (newest first), -S sorts by size (largest first).
if (( $+commands[eza] )); then
  # A leftover "alias ls=..." would make the definition below a parse error (and take precedence over it)
  unalias ls 2>/dev/null
  function ls {
    local -a args=()
    local sort_key="" reverse=0 arg letters letter

    for arg in "$@"; do
      if [[ $arg == -[^-]* ]]; then
        # Bundled short options such as -ltr: handle t, S and r here, keep the others
        letters=${arg#-}
        local kept=""
        for letter in ${(s::)letters}; do
          case $letter in
            t) sort_key=modified ;;
            S) sort_key=size ;;
            r) reverse=$(( 1 - reverse )) ;;
            *) kept+=$letter ;;
          esac
        done
        [[ -n $kept ]] && args+=("-$kept")
      else
        args+=("$arg")
      fi
    done

    if [[ -n $sort_key ]]; then
      args+=("--sort=$sort_key")
      # eza sorts oldest/smallest first, ls sorts newest/largest first
      reverse=$(( 1 - reverse ))
    fi
    (( reverse )) && args+=(--reverse)

    command eza -la "${args[@]}"
  }
fi
