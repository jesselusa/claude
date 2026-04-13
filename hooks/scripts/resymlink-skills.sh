#!/usr/bin/env bash
# PostToolUse hook for Edit/Write — re-symlinks skills when anything in
# ~/Documents/GitHub/claude/skills/ is touched, so new skills are picked up
# without a manual symlink step.

input=$(cat)
file=$(echo "$input" | jq -r '.tool_input.file_path // ""')

case "$file" in
	*"/claude/skills/"*)
		for skill in ~/Documents/GitHub/claude/skills/*/; do
			ln -sf "$skill" ~/.claude/skills/ 2>/dev/null
		done
		echo "🔄 Re-symlinked skills"
		;;
esac

exit 0
