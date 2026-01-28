#!/bin/bash
# SessionStart hook: Check if README.md is missing in a project directory
# Outputs additionalContext JSON if README is missing

set -e

# Check if this is a project directory
IS_PROJECT=false

if [[ -f "package.json" ]] || [[ -f "pyproject.toml" ]] || [[ -f "requirements.txt" ]] || [[ -d ".git" ]]; then
	IS_PROJECT=true
fi

# Exit silently if not a project
if [[ "$IS_PROJECT" != "true" ]]; then
	exit 0
fi

# Check if README exists
if [[ -f "README.md" ]] || [[ -f "readme.md" ]] || [[ -f "README" ]]; then
	exit 0
fi

# Get project name for context
PROJECT_NAME=$(basename "$(pwd)")

# Output suggestion via additionalContext
cat <<EOF
{
  "additionalContext": "This project ($PROJECT_NAME) has no README.md file. Consider running /create-readme to generate documentation."
}
EOF
