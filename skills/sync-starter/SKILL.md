---
name: sync-starter
description: Sync content between project files and starter template
argument-hint: --push|--pull [--dry-run] [--no-pr] [--claude] [--agents] [--gitignore] [--robots]
disable-model-invocation: true
---

# Sync Starter Template

Bidirectional sync between the current project and the starter template repository. Push generic learnings to the starter, or pull updates from the starter into the current project. Confirms each item individually before syncing.

**Argument:** $ARGUMENTS

**Default behavior:** Ask the user which direction to sync, then analyze files and confirm each item.

**Modifiers:**
- `--push`: Sync FROM current project TO starter template (create PR)
- `--pull`: Sync FROM starter template TO current project (local changes)
- `--dry-run` or `-n`: Show what would change without modifying
- `--no-pr`: (push only) Apply changes locally but don't push or create PR
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

## Step 0: Direction Selection

1. If `--push` is in the arguments -> use the **Push Direction** flow
2. If `--pull` is in the arguments -> use the **Pull Direction** flow
3. Otherwise -> use AskUserQuestion:
   - header: "Direction"
   - options:
     - "Push to starter" / "Sync generic learnings FROM this project TO the starter template (creates PR)"
     - "Pull from starter" / "Sync updates FROM the starter template INTO this project (local changes)"

---

## Push Direction

Push generic, reusable content from the current project to the starter template repository.

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

---

## Pull Direction

Pull generic, reusable content from the starter template into the current project.

### 1. Validate Environment

Check current directory is not the starter repo itself:
```bash
git remote get-url origin 2>/dev/null | grep -q "jesselusa/claude"
```

If match found, abort: "Cannot pull starter into itself. Run this from a project directory."

### 2. Fetch Starter Files from GitHub

Determine which files to sync based on modifiers (default: all).

Fetch starter files:
```bash
gh api repos/jesselusa/claude/contents/CLAUDE.md --jq '.content' | base64 -d
gh api repos/jesselusa/claude/contents/.gitignore --jq '.content' | base64 -d
gh api repos/jesselusa/claude/contents/robots.txt --jq '.content' | base64 -d
```

Skip files based on modifiers (`--claude`, `--gitignore`, `--robots`).

### 3. Read Current Project Files

Read the corresponding project files (skip any that don't exist):
```bash
cat ./CLAUDE.md
cat ./.gitignore
cat ./robots.txt
```

### 4. Diff - Find Content in Starter NOT in Project

Compare starter content against project files to find items worth pulling.

#### CLAUDE.md

Extract generic items from the starter that are missing from the project:
- Workflow rules and patterns
- Safety rules and security practices
- Code style preferences
- Design principles
- Testing approaches
- Tooling preferences
- General best practices

**DO NOT pull starter-specific content:**
- Skills table (Available Skills section)
- Starter repo structure (skills/, hooks/, mcp-servers/, templates/, workflows/)
- Installation commands (symlink commands, `mkdir -p ~/.claude/skills`)
- Permissions config (`/permissions`, allowlist references)
- Paths referencing `~/Documents/GitHub/claude`
- Repository purpose section
- Creating New Skills section
- Development Commands section

#### .gitignore

Line-by-line diff. Flag generic patterns in the starter that are missing from the project's .gitignore.

#### robots.txt

Find User-agent blocks in the starter that are not in the project. If the project has no robots.txt, offer to create one from the starter.

### 5. Confirm Each Item

Use AskUserQuestion for each item or group:

**CLAUDE.md items** - confirm one-by-one:
```
Found in starter, missing from project:

Category: [Workflow/Style/Safety/Tooling/Design/Testing]
Content: "[the actual content]"

Add this to your project's CLAUDE.md?
```

Options:
- "Yes, add this"
- "No, skip this"
- "Edit before adding" (user provides modified version)

**For .gitignore and robots.txt** - batch by section:

Options:
- "Add all" (add all missing items from this section)
- "Skip" (skip all items from this section)
- "Pick individually" (confirm each item one by one)

### 6. Apply Approved Items

Apply changes directly to project files using Edit/Write tools. No clone, no PR - changes are local and unstaged.

For CLAUDE.md:
- Add approved items to the appropriate section in the project's CLAUDE.md
- If the section doesn't exist, create it
- Preserve the project's existing structure and project-specific content

For .gitignore:
- Append approved patterns to the project's .gitignore
- Group by category with comments if adding multiple patterns

For robots.txt:
- Append approved User-agent blocks to the project's robots.txt
- If creating a new robots.txt, use the starter's content as the base (minus project-specific rules)

If `--dry-run` is active, show what would change but don't modify any files.

### 7. Summary

Output a summary:
```
## Starter Template Pull - [project-name]

Source: github.com/jesselusa/claude

### Changes Applied
- [list of items added, grouped by file]

### Skipped
- [list of items the user chose to skip]

### Files Modified
- [list of files that were changed]

Reminder: Changes are local and unstaged. Run `git diff` to review, then commit when ready.
```

---

## Output Format (Push)

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
