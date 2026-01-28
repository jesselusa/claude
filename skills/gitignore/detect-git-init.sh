#!/bin/bash
# PostToolUse hook: Detect git init and suggest .gitignore creation
# Reads hook payload from stdin, outputs additionalContext if applicable

set -e

PAYLOAD=$(cat)

TOOL_NAME=$(echo "$PAYLOAD" | jq -r '.tool_name // ""' 2>/dev/null || echo "")
if [[ "$TOOL_NAME" != "Bash" ]]; then
	exit 0
fi

COMMAND=$(echo "$PAYLOAD" | jq -r '.tool_input.command // ""' 2>/dev/null || echo "")

if [[ ! "$COMMAND" =~ git[[:space:]]+init ]]; then
	exit 0
fi

if [[ -f ".gitignore" ]]; then
	exit 0
fi

PROJECT_NAME=$(basename "$(pwd)")

cat <<EOF
{
  "additionalContext": "Git repository initialized. Consider running /gitignore to generate a .gitignore for $PROJECT_NAME."
}
EOF
