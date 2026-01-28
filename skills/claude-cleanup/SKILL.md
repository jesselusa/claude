---
name: claude-cleanup
description: Scan and redact secrets from Claude memory files
disable-model-invocation: true
---

# Claude Cleanup

Scan and redact secrets from Claude's memory files.

**Argument:** $ARGUMENTS

---

## Step 1: Run Scan

```bash
~/.claude/skills/claude-cleanup/scan-secrets.sh ~/.claude
```

If `$CWD` differs from `~/.claude`, also scan:
```bash
~/.claude/skills/claude-cleanup/scan-secrets.sh "$CWD/.claude"
```

## Step 2: Review Results

If secrets found (exit code 1), display the output and ask:

```
Header: "Action"
Question: "How to handle found secrets?"
Options:
  - "Redact all" - Replace with <REDACTED_*> placeholders
  - "Redact specific files" - Choose which files to clean
  - "Skip" - No changes
```

## Step 3: Redact (if requested)

For each file to redact:
```bash
~/.claude/skills/claude-cleanup/redact-secrets.sh <file>
```

## Step 4: Verify

Re-run scan to confirm cleanup:
```bash
~/.claude/skills/claude-cleanup/scan-secrets.sh ~/.claude
```

Report results. If secrets remain, offer to continue.
