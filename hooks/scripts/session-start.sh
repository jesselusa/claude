#!/usr/bin/env bash
# SessionStart hook — prints a quick project status line so Claude (and you) know
# the branch state, outstanding tasks, and cleanup opportunities up front.
# Output goes to Claude's context, so keep it tight.

git rev-parse --git-dir >/dev/null 2>&1 || exit 0

branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
echo "📍 Branch: $branch"

# Warn if on main/master with uncommitted changes
if [[ "$branch" == "main" || "$branch" == "master" ]]; then
	if [[ -n $(git status --porcelain 2>/dev/null) ]]; then
		echo "⚠️  Uncommitted changes on $branch — create a feature branch before committing (CLAUDE.md)"
	fi
fi

# README + .gitignore existence (kept from prior session-hooks.json)
[ -f README.md ] || echo "⚠️  No README.md"
[ -f .gitignore ] || echo "⚠️  No .gitignore"

# Task count
if [ -d tasks ]; then
	count=$(find tasks -maxdepth 1 -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
	[ "$count" -gt 0 ] && echo "📋 $count task file(s) in tasks/"
fi

# Merged local branches still hanging around
merged=$(git branch --merged main 2>/dev/null | grep -vE '^\*|[[:space:]](main|master)$' | wc -l | tr -d ' ')
[ "$merged" -gt 0 ] && echo "🧹 $merged merged branch(es) to clean — run /git-cleanup"

exit 0
