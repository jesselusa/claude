#!/usr/bin/env bash
# PreToolUse hook for Bash — non-blocking reminder on `git commit` if the
# staged diff touches high-signal paths without staging the corresponding docs.
# Exits 0 either way. Claude sees the stderr and asks the user before proceeding.

input=$(cat)
cmd=$(echo "$input" | jq -r '.tool_input.command // ""')

# Only fire on `git commit`
echo "$cmd" | grep -qE '(^|[[:space:];|&])git[[:space:]]+commit\b' || exit 0

# Only run inside this repo's working tree — don't spam every project
repo_root=$(git rev-parse --show-toplevel 2>/dev/null)
[ -z "$repo_root" ] && exit 0
case "$repo_root" in
	*"/Documents/GitHub/claude") : ;;
	*) exit 0 ;;
esac

staged=$(git diff --cached --name-status 2>/dev/null)
[ -z "$staged" ] && exit 0

notes=()

# Rule 1: new skill added → README.md + CLAUDE.md should both be staged
if echo "$staged" | grep -qE '^A[[:space:]]+skills/[^/]+/SKILL\.md'; then
	echo "$staged" | grep -qE '^[AM][[:space:]]+README\.md$' \
		|| notes+=("New skill added — update the skills table in README.md")
	echo "$staged" | grep -qE '^[AM][[:space:]]+CLAUDE\.md$' \
		|| notes+=("New skill added — update the skills table in CLAUDE.md")
fi

# Rule 2: new or deleted hook script → hooks/README.md should be staged
if echo "$staged" | grep -qE '^[AD][[:space:]]+hooks/scripts/'; then
	echo "$staged" | grep -qE '^[AM][[:space:]]+hooks/README\.md$' \
		|| notes+=("Hook script added/removed — update hooks/README.md")
fi

# Rule 3: template changes → README.md templates section should be staged
if echo "$staged" | grep -qE '^[AD][[:space:]]+templates/[^/]+\.md$'; then
	echo "$staged" | grep -qE '^[AM][[:space:]]+README\.md$' \
		|| notes+=("Template added/removed — update the Templates section of README.md")
fi

[ ${#notes[@]} -eq 0 ] && exit 0

{
	echo "📝 Doc-drift check (non-blocking):"
	for n in "${notes[@]}"; do echo "  • $n"; done
	echo ""
	echo "ACTION for Claude: before running this commit, use AskUserQuestion to ask the user whether to update these docs first or commit as-is. Do not bypass with --no-verify."
} >&2

exit 0
