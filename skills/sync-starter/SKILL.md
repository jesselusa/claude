---
name: sync-starter
description: Sync generic learnings from project files back to starter template
argument-hint: [--dry-run] [--no-pr] [--claude] [--agents] [--gitignore] [--robots]
disable-model-invocation: true
---

# Sync to Starter Template

Extract generic, reusable content from the current project and sync it back to the starter template repository. Confirms each item individually before syncing.

**Argument:** $ARGUMENTS

**Default behavior:** Analyze all syncable files for generic content, confirm each item with user, then create a PR with approved changes.

**Modifiers:**
- `--dry-run` or `-n`: Show what would change without modifying
- `--no-pr`: Apply changes locally but don't push or create PR
- `--claude`: Only sync CLAUDE.md
- `--agents`: Only sync agents.md
- `--gitignore`: Only sync .gitignore
- `--robots`: Only sync robots.txt

## Configuration

- **Starter repo:** `jesselusa/claude` (GitHub)
- **Files to sync:** `CLAUDE.md`, `agents.md`, `.gitignore`, `robots.txt`

## What Gets Synced

Only sync content that is **generic and reusable across any project**.

### CLAUDE.md & agents.md

**SYNC (Generic):**
- Workflow patterns (e.g., "Always run lint before commit")
- Code style preferences (e.g., "Use tabs for indentation")
- Tool preferences (e.g., "Use pnpm, not npm")
- Safety rules (e.g., "Never expose env variables")
- Design principles (e.g., "Mobile-first responsive design")
- Commit conventions (e.g., "feat/fix/refactor format")
- Testing approaches
- General best practices

**DON'T SYNC (Project-Specific):**
- Project name or description
- Specific file paths or directory structures
- Data models or database schemas
- API endpoints or routes
- Component names
- Feature-specific instructions
- Tech stack details unique to this project

### .gitignore

**SYNC:**
- Common patterns for the detected tech stack (Node, Python, etc.)
- IDE/editor files (.vscode, .idea)
- OS files (.DS_Store, Thumbs.db)
- Generic build artifacts

**DON'T SYNC:**
- Project-specific paths
- Custom local-only patterns

### robots.txt

**SYNC:**
- AI bot blocking rules (GPTBot, CCBot, etc.)
- Common crawler rules

**DON'T SYNC:**
- Site-specific paths
- Custom allow/disallow rules

## Execution Steps

### 1. Validate Environment

Check current directory is not the starter repo itself:
```bash
git remote get-url origin 2>/dev/null | grep -q "jesselusa/claude"
```

If match found, abort: "Cannot sync starter to itself. Run this from a project directory."

### 2. Read Source and Target Files

Determine which files to sync based on modifiers (default: all).

Read project files (skip if missing):
```bash
cat ./CLAUDE.md
cat ./agents.md
cat ./.gitignore
cat ./robots.txt
```

Fetch starter files from GitHub:
```bash
gh api repos/jesselusa/claude/contents/CLAUDE.md --jq '.content' | base64 -d
gh api repos/jesselusa/claude/contents/agents.md --jq '.content' | base64 -d
gh api repos/jesselusa/claude/contents/.gitignore --jq '.content' | base64 -d
gh api repos/jesselusa/claude/contents/robots.txt --jq '.content' | base64 -d
```

### 3. Extract Generic Content

For each file type, identify content that is:
- Generic enough to apply to any project
- Not already present in the starter
- Valuable as reusable guidance

**For CLAUDE.md/agents.md**, categorize items:
- **Workflow**: How to work with the codebase
- **Style**: Code formatting and conventions
- **Safety**: Security and safety rules
- **Tooling**: Tool preferences and commands
- **Design**: UI/UX principles
- **Testing**: Testing approaches

**For .gitignore**, identify:
- New patterns not in starter
- Patterns that are generic (not project-specific paths)

**For robots.txt**, identify:
- New User-agent blocks
- New Disallow rules that are generic

### 4. Confirm Each Item Individually

For EACH generic item found, use AskUserQuestion to confirm:

```
Found potential sync item:

Category: [Workflow/Style/Safety/etc.]
Content: "[the actual content]"

Should this be synced to the starter template?
```

Options:
- "Yes, sync this"
- "No, skip this"
- "Edit before syncing" (user provides modified version)

Continue until all items are reviewed.

### 5. Clone and Apply Changes

If any items were approved:

```bash
TEMP_DIR=$(mktemp -d)
git clone --depth 1 https://github.com/jesselusa/claude.git "$TEMP_DIR"
cd "$TEMP_DIR"
```

Add approved items to the appropriate files (CLAUDE.md, agents.md, .gitignore, and/or robots.txt).

### 6. Create Branch, Commit, Push, and Open PR

Create branch with auto-generated name:
```bash
BRANCH_NAME="sync/$(basename "$OLDPWD")-$(date +%Y%m%d-%H%M%S)"
git checkout -b "$BRANCH_NAME"
```

Commit changes (only add files that were modified):
```bash
git add CLAUDE.md agents.md .gitignore robots.txt 2>/dev/null
git commit -m "$(cat <<'EOF'
sync: learnings from [project-name]

Synced generic content from [project-name] to starter template.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

Push and create PR:
```bash
git push -u origin "$BRANCH_NAME"
gh pr create --title "sync: learnings from [project-name]" --body "$(cat <<'EOF'
## Summary
Synced generic, reusable guidance from [project-name].

### Items synced
- [list approved items]

🤖 Generated with [Claude Code](https://claude.ai/code)
EOF
)"
```

The `gh pr create` command will output the PR URL.

### 7. Cleanup

```bash
rm -rf "$TEMP_DIR"
```

## Output Format

```
## Starter Template Sync - [project-name]

Comparing against: github.com/jesselusa/claude

### Potential Items Found

1. [Category] "[content snippet]"
   → User approved / skipped / edited

2. [Category] "[content snippet]"
   → User approved / skipped / edited

...

### Summary
- X items approved
- Y items skipped
- Z items edited

[If approved items exist]
Branch: sync/[project-name]-[timestamp]
PR: [URL from gh pr create]
```
