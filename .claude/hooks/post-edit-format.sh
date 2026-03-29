#!/usr/bin/env bash
set -euo pipefail

# PostToolUse hook: format Python files after Write/Edit
# Receives JSON on stdin from Claude Code

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Skip if no file path or not a Python file
if [[ -z "$FILE_PATH" || "$FILE_PATH" != *.py ]]; then
  exit 0
fi

# Skip if file doesn't exist (e.g. was deleted)
if [[ ! -f "$FILE_PATH" ]]; then
  exit 0
fi

# Format with black and isort (silent unless error)
poetry run black --quiet "$FILE_PATH" 2>/dev/null || true
poetry run isort --quiet "$FILE_PATH" 2>/dev/null || true

exit 0
