# ssh-audit profile hooks
# Automatically run a quick audit on login if enabled
if [ -f "$HOME/.ssh-check" ] && [ -x "$HOME/.ssh-check" ]; then
    "$HOME/.ssh-check" >/dev/null 2>&1 &
fi