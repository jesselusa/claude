#!/bin/bash
# Scan for secrets in Claude memory files
# Usage: ./scan-secrets.sh [target_directory]

set -uo pipefail

TARGET="${1:-$HOME/.claude}"

echo "=========================================="
echo "Claude Memory Secret Scanner"
echo "=========================================="
echo "Target: $TARGET"
echo ""
echo "Scanning for secrets..."
echo ""

# Define patterns (simplified for performance)
JWT='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+'
OPENAI='sk-[A-Za-z0-9]{20,}'
ANTHROPIC='sk-ant-[A-Za-z0-9_-]{20,}'
GITHUB='gh[poas]_[A-Za-z0-9]{36}'
AWS='AKIA[0-9A-Z]{16}'
STRIPE='sk_(live|test)_[A-Za-z0-9]{24,}'
SLACK='xox[bp]-[A-Za-z0-9-]+'

echo "Secret Counts by Type"
echo "----------------------------------------"
printf "%-20s %s\n" "Type" "Count"
echo "----------------------------------------"

TOTAL=0

# Count each pattern type
for pattern_info in \
	"JWT tokens|$JWT" \
	"OpenAI keys|$OPENAI" \
	"Anthropic keys|$ANTHROPIC" \
	"GitHub tokens|$GITHUB" \
	"AWS keys|$AWS" \
	"Stripe keys|$STRIPE" \
	"Slack tokens|$SLACK"
do
	name="${pattern_info%%|*}"
	pattern="${pattern_info#*|}"
	count=$(grep -rhoE "$pattern" "$TARGET" 2>/dev/null | wc -l | tr -d ' ')
	TOTAL=$((TOTAL + count))
	if [ "$count" -gt 0 ]; then
		printf "%-20s %s\n" "$name" "$count"
	else
		printf "%-20s %s\n" "$name" "-"
	fi
done

echo "----------------------------------------"
printf "%-20s %s\n" "TOTAL" "$TOTAL"
echo ""

if [ "$TOTAL" -gt 0 ]; then
	echo "Files containing secrets:"
	echo "----------------------------------------"
	# Use combined pattern for file listing
	ALL="$JWT|$OPENAI|$ANTHROPIC|$GITHUB|$AWS|$STRIPE|$SLACK"
	grep -rlE "$ALL" "$TARGET" 2>/dev/null | head -20 | while read -r file; do
		count=$(grep -coE "$ALL" "$file" 2>/dev/null || echo 0)
		printf "  %-60s (%s)\n" "$file" "$count"
	done
	FILE_COUNT=$(grep -rlE "$ALL" "$TARGET" 2>/dev/null | wc -l | tr -d ' ')
	if [ "$FILE_COUNT" -gt 20 ]; then
		echo "  ... and $((FILE_COUNT - 20)) more files"
	fi
	echo ""
	echo "Run: redact-secrets.sh <file> to clean individual files"
	exit 1
else
	echo "No secrets found."
	exit 0
fi
