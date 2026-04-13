#!/usr/bin/env bash
# PreToolUse hook for Bash — blocks commands that violate CLAUDE.md safety rules.
# Reads tool input JSON from stdin. Exit 1 blocks; message on stderr shown to Claude.

input=$(cat)
cmd=$(echo "$input" | jq -r '.tool_input.command // ""')

block() {
	echo "🛑 Blocked: $1" >&2
	exit 1
}

# rm -rf (CLAUDE.md: never run rm -rf without explicit confirmation)
if echo "$cmd" | grep -qE '(^|[[:space:];|&])rm[[:space:]]+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r|-rf|-fr)([[:space:];|&]|$)'; then
	block "rm -rf requires explicit user confirmation (CLAUDE.md safety)"
fi

# Destructive DB (CLAUDE.md: never DROP, TRUNCATE, db reset)
if echo "$cmd" | grep -qiE '\b(DROP[[:space:]]+(TABLE|DATABASE|SCHEMA)|TRUNCATE[[:space:]]+TABLE|supabase[[:space:]]+db[[:space:]]+reset|\bdb[[:space:]]+reset)\b'; then
	block "destructive database command (CLAUDE.md safety)"
fi

# npm / yarn install (CLAUDE.md: use pnpm)
if echo "$cmd" | grep -qE '(^|[[:space:];|&])(npm|yarn)[[:space:]]+(install|i|add)([[:space:];|&]|$)'; then
	block "use pnpm instead of npm/yarn (CLAUDE.md preference)"
fi

# git add on .env files (allow .env.example / .env.sample / .env.template only)
if echo "$cmd" | grep -qE '(^|[[:space:];|&])git[[:space:]]+add\b'; then
	# Extract .env* paths from the command
	while read -r match; do
		[ -z "$match" ] && continue
		# Allow example/sample/template variants
		if ! echo "$match" | grep -qE '\.env\.(example|sample|template)($|[[:space:]])'; then
			block "don't commit .env files (CLAUDE.md: secrets only in .env.local, never committed). Matched: $match"
		fi
	done < <(echo "$cmd" | grep -oE '[^[:space:]]*\.env[^[:space:];|&]*')
fi

# git commit on main/master
if echo "$cmd" | grep -qE '(^|[[:space:];|&])git[[:space:]]+commit\b'; then
	branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
	if [[ "$branch" == "main" || "$branch" == "master" ]]; then
		block "don't commit directly to $branch. Create a feature branch first (CLAUDE.md)."
	fi
fi

# git push --force to main/master
if echo "$cmd" | grep -qE 'git[[:space:]]+push'; then
	if echo "$cmd" | grep -qE '(--force|--force-with-lease|[[:space:]]-f([[:space:]]|$))'; then
		if echo "$cmd" | grep -qE '\b(main|master)\b'; then
			block "force-push to main/master is blocked (CLAUDE.md safety)"
		fi
	fi
fi

exit 0
