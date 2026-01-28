#!/bin/bash
# PreToolUse hook wrapper for gitignore validation
# Only activates for git commit commands
# Returns JSON response for Claude Code hook system

INPUT=$(cat)

TOOL_NAME=$(echo "$INPUT" | grep -o '"tool_name"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"tool_name"[[:space:]]*:[[:space:]]*"//' | sed 's/".*//')

if [[ "$TOOL_NAME" != "Bash" ]]; then
	echo '{"decision": "allow"}'
	exit 0
fi

COMMAND=$(echo "$INPUT" | grep -o '"command"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"command"[[:space:]]*:[[:space:]]*"//' | sed 's/".*//')

if [[ ! "$COMMAND" =~ ^git[[:space:]]+commit ]]; then
	echo '{"decision": "allow"}'
	exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECK_RESULT=$("$SCRIPT_DIR/check-gitignore.sh" 2>/dev/null)

if [[ $? -ne 0 ]]; then
	echo '{"decision": "allow"}'
	exit 0
fi

STATUS=$(echo "$CHECK_RESULT" | grep -o '"status"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"status"[[:space:]]*:[[:space:]]*"//' | sed 's/".*//')

case "$STATUS" in
	"ok")
		echo '{"decision": "allow"}'
		;;
	"warning")
		MESSAGE=$(echo "$CHECK_RESULT" | grep -o '"message"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"message"[[:space:]]*:[[:space:]]*"//' | sed 's/".*//')
		echo "{\"decision\": \"ask\", \"message\": \"Warning: $MESSAGE. Continue with commit?\"}"
		;;
	"error")
		MESSAGE=$(echo "$CHECK_RESULT" | grep -o '"message"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"message"[[:space:]]*:[[:space:]]*"//' | sed 's/".*//')
		echo "{\"decision\": \"block\", \"message\": \"Blocked: $MESSAGE. Run /gitignore to fix.\"}"
		;;
	*)
		echo '{"decision": "allow"}'
		;;
esac
