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
	local f="$1"
	local count=0
	count=$((count + $(grep -oE 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+' "$f" 2>/dev/null | wc -l | tr -d ' ')))
	count=$((count + $(grep -oE 'sk-[A-Za-z0-9]{20,}' "$f" 2>/dev/null | wc -l | tr -d ' ')))
	count=$((count + $(grep -oE 'sk-ant-[A-Za-z0-9_-]{20,}' "$f" 2>/dev/null | wc -l | tr -d ' ')))
	count=$((count + $(grep -oE 'gh[poas]_[A-Za-z0-9]{36}' "$f" 2>/dev/null | wc -l | tr -d ' ')))
	count=$((count + $(grep -oE 'AKIA[0-9A-Z]{16}' "$f" 2>/dev/null | wc -l | tr -d ' ')))
	count=$((count + $(grep -oE 'sk_(live|test)_[A-Za-z0-9]{24,}' "$f" 2>/dev/null | wc -l | tr -d ' ')))
	count=$((count + $(grep -oE 'xox[bp]-[A-Za-z0-9-]+' "$f" 2>/dev/null | wc -l | tr -d ' ')))
	echo "$count"
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

# JWT tokens (most common in Claude history)
sed -i '' 's/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*/<REDACTED_JWT>/g' "$FILE"

# OpenAI API keys
sed -i '' 's/sk-[A-Za-z0-9]\{20,\}/<REDACTED_OPENAI_KEY>/g' "$FILE"

# Anthropic API keys
sed -i '' 's/sk-ant-[A-Za-z0-9_-]\{20,\}/<REDACTED_ANTHROPIC_KEY>/g' "$FILE"

# GitHub Personal Access Tokens
sed -i '' 's/ghp_[A-Za-z0-9]\{36\}/<REDACTED_GITHUB_PAT>/g' "$FILE"

# GitHub OAuth tokens
sed -i '' 's/gho_[A-Za-z0-9]\{36\}/<REDACTED_GITHUB_OAUTH>/g' "$FILE"

# GitHub App tokens
sed -i '' 's/ghs_[A-Za-z0-9]\{36\}/<REDACTED_GITHUB_APP>/g' "$FILE"

# GitHub Refresh tokens
sed -i '' 's/ghr_[A-Za-z0-9]\{36\}/<REDACTED_GITHUB_REFRESH>/g' "$FILE"

# AWS Access Key IDs
sed -i '' 's/AKIA[0-9A-Z]\{16\}/<REDACTED_AWS_KEY>/g' "$FILE"

# Stripe Live keys
sed -i '' 's/sk_live_[A-Za-z0-9]\{24,\}/<REDACTED_STRIPE_LIVE>/g' "$FILE"

# Stripe Test keys
sed -i '' 's/sk_test_[A-Za-z0-9]\{24,\}/<REDACTED_STRIPE_TEST>/g' "$FILE"

# Slack Bot tokens
sed -i '' 's/xoxb-[A-Za-z0-9-]*/<REDACTED_SLACK_BOT>/g' "$FILE"

# Slack User tokens
sed -i '' 's/xoxp-[A-Za-z0-9-]*/<REDACTED_SLACK_USER>/g' "$FILE"

# Database URLs (redact password only, preserve structure)
sed -i '' 's/\(postgres:\/\/[^:]*\):[^@]*@/\1:<REDACTED>@/g' "$FILE"
sed -i '' 's/\(mysql:\/\/[^:]*\):[^@]*@/\1:<REDACTED>@/g' "$FILE"
sed -i '' 's/\(mongodb:\/\/[^:]*\):[^@]*@/\1:<REDACTED>@/g' "$FILE"

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
