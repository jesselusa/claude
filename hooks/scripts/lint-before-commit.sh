#!/usr/bin/env bash
# PreToolUse hook for Bash — runs lint + type-check before `git commit` in pnpm projects.
# Only runs if package.json + pnpm-lock.yaml exist and the scripts are defined.
# Exit 1 blocks the commit; message on stderr goes back to Claude.

input=$(cat)
cmd=$(echo "$input" | jq -r '.tool_input.command // ""')

# Only trigger on git commit
echo "$cmd" | grep -qE '(^|[[:space:];|&])git[[:space:]]+commit\b' || exit 0

# Find nearest package.json walking up from cwd
dir=$(pwd)
while [ "$dir" != "/" ]; do
	[ -f "$dir/package.json" ] && break
	dir=$(dirname "$dir")
done
[ -f "$dir/package.json" ] || exit 0
[ -f "$dir/pnpm-lock.yaml" ] || exit 0

cd "$dir" || exit 0

fail() {
	echo "🛑 Pre-commit check failed: $1" >&2
	echo "Fix the issue or bypass with: git commit --no-verify (not recommended)" >&2
	exit 1
}

has_script() { jq -e --arg s "$1" '.scripts[$s] // empty' package.json >/dev/null 2>&1; }

if has_script lint; then
	pnpm -s lint >/tmp/claude-hook-lint.log 2>&1 || {
		tail -30 /tmp/claude-hook-lint.log >&2
		fail "lint errors"
	}
fi

if has_script type-check; then
	pnpm -s type-check >/tmp/claude-hook-tc.log 2>&1 || {
		tail -30 /tmp/claude-hook-tc.log >&2
		fail "type-check errors"
	}
elif has_script typecheck; then
	pnpm -s typecheck >/tmp/claude-hook-tc.log 2>&1 || {
		tail -30 /tmp/claude-hook-tc.log >&2
		fail "type-check errors"
	}
fi

exit 0
