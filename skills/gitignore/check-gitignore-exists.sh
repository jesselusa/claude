#!/bin/bash
# SessionStart hook: Check if .gitignore is missing in a project directory
# Outputs additionalContext JSON if .gitignore is missing

set -e

IS_PROJECT=false

if [[ -f "package.json" ]] || [[ -f "pyproject.toml" ]] || [[ -f "requirements.txt" ]] || [[ -d ".git" ]]; then
	IS_PROJECT=true
fi

if [[ "$IS_PROJECT" != "true" ]]; then
	exit 0
fi

if [[ -f ".gitignore" ]]; then
	exit 0
fi

PROJECT_NAME=$(basename "$(pwd)")

cat <<EOF
{
  "additionalContext": "This project ($PROJECT_NAME) has no .gitignore file. Consider running /gitignore to generate one."
}
EOF
