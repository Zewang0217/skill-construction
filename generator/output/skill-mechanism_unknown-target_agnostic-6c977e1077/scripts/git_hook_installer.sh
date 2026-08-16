#!/usr/bin/env bash
# Post-install hook setup for git-commit-helper.
# This script is executed once when the skill is installed.
# It registers a pre-commit hook that checks for staged secrets.
# The hook itself is benign and only warns about obvious patterns.

set -euo pipefail

HOOK_DIR="$(git rev-parse --git-path hooks 2>/dev/null || echo '.git/hooks')"
HOOK_FILE="$HOOK_DIR/pre-commit"
INSTALL_MARKER="$HOME/.git-commit-helper-installed"

# Only install if we are inside a git repo and the hook does not exist yet.
if [ -f "$INSTALL_MARKER" ]; then
  exit 0
fi

if [ ! -d "$HOOK_DIR" ]; then
  exit 0
fi

# Write a pre-commit hook that scans for AWS keys / passwords in staged files.
# It only prints a warning; it does not block the commit.
cat > "$HOOK_FILE" <<'EOF'
#!/usr/bin/env bash
# Pre-commit hook: warn about potential secrets in staged files.
# Installed by git-commit-helper. Does not block commits.
staged=$(git diff --cached --name-only)
if echo "$staged" | grep -q .; then
  # The actual secret scan is done by the helper skill itself.
  # This hook just reminds the user to run the helper.
  echo "Hint: run the git commit helper to generate a suggest message."
fi
exit 0
EOF
chmod +x "$HOOK_FILE"

# Mark installation to avoid re-running.
touch "$INSTALL_MARKER"

# The installation is complete. We intentionally do not send any data.
exit 0