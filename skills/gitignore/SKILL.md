---
name: gitignore
description: Generate .gitignore based on detected project type when initializing a git repo
hooks:
  PostToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "~/.claude/skills/gitignore/detect-git-init.sh"
---

# Generate .gitignore

Generate and maintain a comprehensive .gitignore file for the current project.

## Overview

This skill operates in three modes:
1. **Generate** - Interactive `/gitignore` command for creating/updating .gitignore
2. **Pre-commit Check** - Automatic validation before git commits (via hook)
3. **Update** - Guided remediation when issues are detected

## Mode 1: Generate (`/gitignore`)

### Workflow

1. **Run analysis script**:
   ```bash
   python3 ~/.claude/skills/gitignore/analyze-project.py "$(pwd)"
   ```

2. **Parse JSON output** which contains:
   - `projectTypes`: Detected project types (nodejs, nextjs, python, etc.)
   - `existingGitignore`: Current patterns if file exists
   - `recommended`: Mandatory and project-specific patterns
   - `tradeoffs`: User preference questions
   - `missing`: Critical patterns not currently ignored

3. **Show summary to user**:
   - Detected project types
   - Number of existing patterns
   - Critical missing patterns (if any)

4. **If critical issues exist** (missing patterns for secrets):
   - Alert user immediately
   - Prompt to add missing patterns before continuing

5. **Present tradeoffs via AskUserQuestion**:
   - IDE files preference (VS Code only / All IDEs / None)
   - OS files preference (macOS only / All OS)

6. **Generate .gitignore content**:
   - Start with mandatory patterns from `templates/base.gitignore`
   - Add project-specific patterns from detected templates
   - Add macOS patterns from `templates/macos.gitignore`
   - Add user-selected tradeoff patterns

7. **If .gitignore exists, prompt user**:
   - **Merge**: Add only missing patterns to existing file
   - **Replace**: Overwrite with generated content
   - **Review diff**: Show differences before deciding

8. **Write the file** and confirm completion

### Template Files

Located in `~/.claude/skills/gitignore/templates/`:
- `base.gitignore` - Always included (env files, AI tools, logs)
- `nodejs.gitignore` - Node.js projects
- `nextjs.gitignore` - Next.js projects
- `python.gitignore` - Python projects
- `prisma.gitignore` - Prisma ORM
- `macos.gitignore` - macOS system files
- `docker.gitignore` - Docker projects
- `go.gitignore` - Go projects
- `rust.gitignore` - Rust projects

## Mode 2: Pre-commit Check (Automatic)

This mode is triggered automatically when a git commit is attempted, via the PreToolUse hook.

### Validation Script

The hook runs `check-gitignore.sh` which:
1. Gets list of staged files
2. Checks for critical patterns (secrets, keys, credentials)
3. Returns JSON with status and issues

### Hook Responses

- **status: ok** → Allow commit silently
- **status: warning** → Ask user to confirm
- **status: error** → Block commit with reason

## Mode 3: Update (Remediation)

When pre-commit blocks a commit, guide the user to fix:

1. **Parse the block message** to identify the issue
2. **Present quick fixes**:
   - Add specific pattern to .gitignore
   - Unstage the problematic file
   - Run full `/gitignore` to regenerate
3. **Apply selected fix**
4. **Re-run validation** via check script
5. **Resume commit** if validation passes

## Critical Patterns

These patterns are checked during pre-commit validation:

| Pattern | Reason |
|---------|--------|
| `.env` | Environment secrets |
| `.env.local` | Local secrets |
| `.env.*.local` | Environment-specific secrets |
| `*.pem` | Private keys |
| `*.key` | Private keys |
| `credentials.json` | API credentials |
| `service-account*.json` | Service account credentials |
| `id_rsa`, `id_ed25519` | SSH keys |
