#!/usr/bin/env bash
set -euo pipefail

# PreToolUse hook: block destructive bash commands
# Receives JSON on stdin from Claude Code

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [[ -z "$COMMAND" ]]; then
  exit 0
fi

# Check for destructive patterns
if echo "$COMMAND" | grep -qE 'rm\s+-rf\s'; then
  echo "BLOCKED: 'rm -rf' is not allowed. Use targeted file removal instead." >&2
  exit 2
fi

if echo "$COMMAND" | grep -qiE 'DROP\s+(TABLE|DATABASE)'; then
  echo "BLOCKED: DROP TABLE/DATABASE is not allowed." >&2
  exit 2
fi

if echo "$COMMAND" | grep -qE 'git\s+push\s+.*(--force|-f)'; then
  echo "BLOCKED: 'git push --force' is not allowed. Use safe push instead." >&2
  exit 2
fi

if echo "$COMMAND" | grep -qE 'git\s+reset\s+--hard'; then
  echo "BLOCKED: 'git reset --hard' is not allowed. Use soft reset or stash." >&2
  exit 2
fi

if echo "$COMMAND" | grep -qE 'git\s+clean\s+-f'; then
  echo "BLOCKED: 'git clean -f' is not allowed. Review untracked files manually." >&2
  exit 2
fi

exit 0
