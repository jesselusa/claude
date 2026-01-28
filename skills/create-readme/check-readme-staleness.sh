#!/bin/bash
# PostToolUse hook: Check if README needs updating after commits
# Triggers suggestion when 10+ significant files changed since last README update

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

# Check if command contains "git commit"
if [[ ! "$COMMAND" =~ git[[:space:]]+commit ]]; then
	exit 0
fi

# Check if tool succeeded
TOOL_RESULT=$(echo "$PAYLOAD" | jq -r '.tool_result // ""' 2>/dev/null || echo "")
if [[ "$TOOL_RESULT" == *"error"* ]] || [[ "$TOOL_RESULT" == *"nothing to commit"* ]]; then
	exit 0
fi

# Check if README exists
if [[ ! -f "README.md" ]] && [[ ! -f "readme.md" ]]; then
	exit 0
fi

# Find the README file
README_FILE="README.md"
if [[ -f "readme.md" ]]; then
	README_FILE="readme.md"
fi

# Get the last commit that touched README
LAST_README_COMMIT=$(git log -1 --format="%H" -- "$README_FILE" 2>/dev/null || echo "")

if [[ -z "$LAST_README_COMMIT" ]]; then
	LAST_README_COMMIT=$(git rev-list --max-parents=0 HEAD 2>/dev/null || echo "")
fi

if [[ -z "$LAST_README_COMMIT" ]]; then
	exit 0
fi

# Count significant changes since last README update
SIGNIFICANT_CHANGES=$(git diff --name-only "$LAST_README_COMMIT"..HEAD 2>/dev/null | grep -E \
	'^src/|\.tsx?$|\.py$|^package\.json$|^pyproject\.toml$|^tests?/|^next\.config\.|^prisma/schema\.prisma$|\.env\.example$' | wc -l | tr -d ' ')

THRESHOLD=10

if [[ "$SIGNIFICANT_CHANGES" -lt "$THRESHOLD" ]]; then
	exit 0
fi

SRC_CHANGES=$(git diff --name-only "$LAST_README_COMMIT"..HEAD 2>/dev/null | grep -E '^src/|\.tsx?$|\.py$' | wc -l | tr -d ' ')
DEP_CHANGES=$(git diff --name-only "$LAST_README_COMMIT"..HEAD 2>/dev/null | grep -E '^package\.json$|^pyproject\.toml$' | wc -l | tr -d ' ')
TEST_CHANGES=$(git diff --name-only "$LAST_README_COMMIT"..HEAD 2>/dev/null | grep -E '^tests?/|\.test\.' | wc -l | tr -d ' ')
CONFIG_CHANGES=$(git diff --name-only "$LAST_README_COMMIT"..HEAD 2>/dev/null | grep -E '^next\.config\.|^prisma/|\.env\.example$' | wc -l | tr -d ' ')

SUMMARY="$SIGNIFICANT_CHANGES files changed: ${SRC_CHANGES} source, ${DEP_CHANGES} deps, ${TEST_CHANGES} tests, ${CONFIG_CHANGES} config"

cat <<EOF
{
  "additionalContext": "README.md may be stale. Since last update: $SUMMARY. Consider running /create-readme to refresh documentation."
}
EOF
