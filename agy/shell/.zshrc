export PATH=/usr/local/bin:/usr/bin
if [[ -x "$HOME/.local/bin/mise" ]]; then
  eval "$("$HOME/.local/bin/mise" activate zsh --shims 2>/dev/null)"
elif command -v mise >/dev/null 2>&1; then
  eval "$(mise activate zsh --shims 2>/dev/null)"
fi
