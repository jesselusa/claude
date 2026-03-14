#!/bin/bash
# Fast pre-commit gitignore validation
# Outputs JSON with status and issues

set -e

CRITICAL_PATTERNS=(
	".env"
	".env.local"
	".env.development.local"
	".env.production.local"
	".env.test.local"
	"*.pem"
	"*.key"
	"credentials.json"
	"service-account*.json"
	"id_rsa"
	"id_ed25519"
)

STAGED_FILES=$(git diff --cached --name-only 2>/dev/null || echo "")

if [[ -z "$STAGED_FILES" ]]; then
	echo '{"status": "ok", "issues": []}'
	exit 0
fi

if [[ ! -f ".gitignore" ]]; then
	echo '{"status": "warning", "issues": [{"severity": "warning", "message": "No .gitignore file found", "pattern": null}]}'
	exit 0
fi

ISSUES="[]"
STATUS="ok"

for pattern in "${CRITICAL_PATTERNS[@]}"; do
	if [[ "$pattern" == *"*"* ]]; then
		GREP_PATTERN=$(echo "$pattern" | sed 's/\./\\./g' | sed 's/\*/.*/')
		MATCHED_FILES=$(echo "$STAGED_FILES" | grep -E "^${GREP_PATTERN}$" || true)
	else
		MATCHED_FILES=$(echo "$STAGED_FILES" | grep -E "^${pattern}$" || true)
	fi

	if [[ -n "$MATCHED_FILES" ]]; then
		while IFS= read -r file; do
			if [[ -n "$file" ]]; then
				ISSUES=$(echo "$ISSUES" | jq --arg f "$file" --arg p "$pattern" \
					'. + [{"severity": "critical", "message": "\($f) would be committed (secrets at risk)", "pattern": $p}]')
				STATUS="error"
			fi
		done <<< "$MATCHED_FILES"
	fi
done

while IFS= read -r file; do
	[[ -z "$file" ]] && continue
	if [[ -f "$file" ]]; then
		SIZE=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
		if [[ "$SIZE" -gt 10485760 ]]; then
			ISSUES=$(echo "$ISSUES" | jq --arg f "$file" \
				'. + [{"severity": "warning", "message": "\($f) is larger than 10MB", "pattern": null}]')
			if [[ "$STATUS" == "ok" ]]; then
				STATUS="warning"
			fi
		fi
	fi
done <<< "$STAGED_FILES"

jq -n --arg status "$STATUS" --argjson issues "$ISSUES" '{status: $status, issues: $issues}'
