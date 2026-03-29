#!/usr/bin/env bash
set -euo pipefail

# PreToolUse hook: block editing sensitive files
# Receives JSON on stdin from Claude Code

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

BASENAME=$(basename "$FILE_PATH")

# Block .env files
if [[ "$BASENAME" == .env* ]]; then
  echo "BLOCKED: Editing .env files is not allowed. These may contain secrets." >&2
  exit 2
fi

# Block private keys
if [[ "$BASENAME" == *.pem || "$BASENAME" == *.key ]]; then
  echo "BLOCKED: Editing private key files (*.pem, *.key) is not allowed." >&2
  exit 2
fi

# Block git internals
if [[ "$FILE_PATH" == */.git/* || "$FILE_PATH" == *.git\\* ]]; then
  echo "BLOCKED: Editing .git/ internals is not allowed." >&2
  exit 2
fi

# Block lock files
if [[ "$BASENAME" == "poetry.lock" || "$BASENAME" == "package-lock.json" || "$BASENAME" == "pnpm-lock.yaml" ]]; then
  echo "BLOCKED: Editing lock files is not allowed. Use package manager commands instead." >&2
  exit 2
fi

exit 0
