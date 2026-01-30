---
name: sync-starter
description: Sync generic learnings from project CLAUDE.md back to starter template
argument-hint: [--dry-run] [--no-pr]
disable-model-invocation: true
---

# Sync to Starter Template

Extract generic, reusable guidance from the current project's CLAUDE.md and sync it back to the starter template repository. Confirms each item individually before syncing.

**Argument:** $ARGUMENTS

**Default behavior:** Analyze project's CLAUDE.md for generic content, confirm each item with user, then create a PR with approved changes.

**Modifiers:**
- `--dry-run` or `-n`: Show what would change without modifying
- `--no-pr`: Apply changes locally but don't push or create PR

## Configuration

- **Starter repo:** `jesselusa/claude` (GitHub)
- **Source file:** Project's `CLAUDE.md`
- **Target file:** Starter's `CLAUDE.md`

## What Gets Synced

Only sync content that is **generic and reusable across any project**:

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

## Execution Steps

### 1. Validate Environment

Check current directory is not the starter repo itself:
```bash
git remote get-url origin 2>/dev/null | grep -q "jesselusa/claude"
```

If match found, abort: "Cannot sync starter to itself. Run this from a project directory."

### 2. Read Both CLAUDE.md Files

Read project's CLAUDE.md:
```bash
cat ./CLAUDE.md
```

Fetch starter's CLAUDE.md from GitHub:
```bash
gh api repos/jesselusa/claude/contents/CLAUDE.md --jq '.content' | base64 -d
```

### 3. Extract Generic Content

Parse the project's CLAUDE.md and identify sections/bullet points that are:
- Generic enough to apply to any project
- Not already present in the starter's CLAUDE.md
- Valuable as reusable guidance

For each potential item, categorize it:
- **Workflow**: How to work with the codebase
- **Style**: Code formatting and conventions
- **Safety**: Security and safety rules
- **Tooling**: Tool preferences and commands
- **Design**: UI/UX principles
- **Testing**: Testing approaches

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

Add approved items to the appropriate section in CLAUDE.md.

### 6. Create Branch, Commit, Push, and Open PR

Create branch with auto-generated name:
```bash
BRANCH_NAME="sync/$(basename "$OLDPWD")-$(date +%Y%m%d-%H%M%S)"
git checkout -b "$BRANCH_NAME"
```

Commit changes:
```bash
git add CLAUDE.md
git commit -m "$(cat <<'EOF'
sync: learnings from [project-name]

Synced generic guidance from [project-name] to starter template.

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
