#!/bin/bash
# PostToolUse hook: Detect git init and suggest README creation
# Reads hook payload from stdin, outputs additionalContext if applicable

set -e

# Read the hook payload from stdin
PAYLOAD=$(cat)

# Check if this is a Bash tool call
TOOL_NAME=$(echo "$PAYLOAD" | jq -r '.tool_name // ""' 2>/dev/null || echo "")
if [[ "$TOOL_NAME" != "Bash" ]]; then
	exit 0
fi

# Get the command that was executed
COMMAND=$(echo "$PAYLOAD" | jq -r '.tool_input.command // ""' 2>/dev/null || echo "")

# Check if command contains "git init"
if [[ ! "$COMMAND" =~ git[[:space:]]+init ]]; then
	exit 0
fi

# Check if README already exists
if [[ -f "README.md" ]] || [[ -f "readme.md" ]] || [[ -f "README" ]]; then
	exit 0
fi

# Get project name for context
PROJECT_NAME=$(basename "$(pwd)")

# Output suggestion via additionalContext
cat <<EOF
{
  "additionalContext": "Git repository initialized. Consider running /create-readme to generate a README.md for $PROJECT_NAME."
}
EOF
