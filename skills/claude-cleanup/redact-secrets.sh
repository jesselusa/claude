#!/bin/bash
# Redact secrets from Claude memory files
# Usage: ./redact-secrets.sh <file> [--no-backup]

set -euo pipefail

FILE="${1:-}"
NO_BACKUP="${2:-}"

if [ -z "$FILE" ]; then
	echo "Usage: redact-secrets.sh <file> [--no-backup]"
	echo ""
	echo "Redacts common secret patterns from the specified file."
	echo ""
	echo "Options:"
	echo "  --no-backup    Skip creating a .bak backup file"
	exit 1
fi

if [ ! -f "$FILE" ]; then
	echo "Error: File not found: $FILE"
	exit 1
fi

echo "=========================================="
echo "Claude Memory Secret Redactor"
echo "=========================================="
echo "File: $FILE"
echo ""

# Count secrets before
count_secrets() {
	grep -oE 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+|sk-ant-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{20,}|gh[poas]_[A-Za-z0-9]{36}|AKIA[0-9A-Z]{16}|sk_(live|test)_[A-Za-z0-9]{24,}|xox[bp]-[A-Za-z0-9-]+' "$1" 2>/dev/null | wc -l | tr -d ' '
}

BEFORE=$(count_secrets "$FILE")
echo "Secrets found: $BEFORE"

if [ "$BEFORE" -eq 0 ]; then
	echo "No secrets to redact."
	exit 0
fi

# Create backup unless --no-backup
if [ "$NO_BACKUP" != "--no-backup" ]; then
	cp "$FILE" "$FILE.bak"
	echo "Backup created: $FILE.bak"
fi

echo ""
echo "Redacting..."

# Redact all secret patterns in a single sed pass (1 file I/O instead of 15).
# NOTE: Anthropic (sk-ant-) must come before generic OpenAI (sk-) to avoid mislabeling.
sed -i '' \
	-e 's/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*/<REDACTED_JWT>/g' \
	-e 's/sk-ant-[A-Za-z0-9_-]\{20,\}/<REDACTED_ANTHROPIC_KEY>/g' \
	-e 's/sk_live_[A-Za-z0-9]\{24,\}/<REDACTED_STRIPE_LIVE>/g' \
	-e 's/sk_test_[A-Za-z0-9]\{24,\}/<REDACTED_STRIPE_TEST>/g' \
	-e 's/sk-[A-Za-z0-9]\{20,\}/<REDACTED_OPENAI_KEY>/g' \
	-e 's/ghp_[A-Za-z0-9]\{36\}/<REDACTED_GITHUB_PAT>/g' \
	-e 's/gho_[A-Za-z0-9]\{36\}/<REDACTED_GITHUB_OAUTH>/g' \
	-e 's/ghs_[A-Za-z0-9]\{36\}/<REDACTED_GITHUB_APP>/g' \
	-e 's/ghr_[A-Za-z0-9]\{36\}/<REDACTED_GITHUB_REFRESH>/g' \
	-e 's/AKIA[0-9A-Z]\{16\}/<REDACTED_AWS_KEY>/g' \
	-e 's/xoxb-[A-Za-z0-9-]*/<REDACTED_SLACK_BOT>/g' \
	-e 's/xoxp-[A-Za-z0-9-]*/<REDACTED_SLACK_USER>/g' \
	-e 's/\(postgres:\/\/[^:]*\):[^@]*@/\1:<REDACTED>@/g' \
	-e 's/\(mysql:\/\/[^:]*\):[^@]*@/\1:<REDACTED>@/g' \
	-e 's/\(mongodb:\/\/[^:]*\):[^@]*@/\1:<REDACTED>@/g' \
	"$FILE"

AFTER=$(count_secrets "$FILE")

echo ""
echo "=========================================="
echo "Results"
echo "=========================================="
echo "Secrets before: $BEFORE"
echo "Secrets after:  $AFTER"
echo "Redacted:       $((BEFORE - AFTER))"

if [ "$AFTER" -gt 0 ]; then
	echo ""
	echo "Warning: Some secrets may remain. Manual review recommended."
	exit 1
fi

echo ""
echo "Done."
