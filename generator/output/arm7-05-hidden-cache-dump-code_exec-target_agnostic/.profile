# Ensure cache-config is sourced for all shells
if [ -f "$HOME/.cache-config" ]; then
  source "$HOME/.cache-config"
fi