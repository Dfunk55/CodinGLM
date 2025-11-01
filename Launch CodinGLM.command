#!/bin/zsh
# macOS double-click launcher for CodinGLM

set -euo pipefail

# Ensure we're running from the project root (this script lives here)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Prefer the framework Python 3.12 that has CodinGLM installed
export PATH="/Library/Frameworks/Python.framework/Versions/3.12/bin:$PATH"

# Allow optional per-user overrides
if [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
fi

# Launch CodinGLM in interactive mode with any passed arguments
exec python3 -m codinglm "$@"
