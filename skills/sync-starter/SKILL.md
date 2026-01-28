---
name: sync-starter
description: Sync improvements from current project to starter template
argument-hint: [--dry-run] [--gitignore] [--robots] [--claude] [--no-push]
disable-model-invocation: true
---

# Sync to Starter Template

Extract lessons learned from the current project and sync improvements back to the starter template repository.

**Argument:** $ARGUMENTS

**Default behavior:** Compare current project against remote starter repo and show diffs for approval.

**Modifiers:**
- `--dry-run` or `-n`: Show what would change without modifying
- `--gitignore`: Only sync .gitignore changes
- `--robots`: Only sync robots.txt changes
- `--claude`: Only sync CLAUDE.md Memory section changes
- `--no-push`: Apply changes locally but don't push to remote

## Configuration

- **Starter repo:** `dcnu/starter` (GitHub)
- **Files to sync:** `.gitignore`, `robots.txt`, `CLAUDE.md`
- **Cascade updates:** CLAUDE.md changes trigger README.md updates
- **Local clone path:** `/tmp/starter-sync-$$` (temporary, cleaned up after)

## Sync Flow

The sync follows a cascading update pattern:

```
Current Project → CLAUDE.md → README.md → Remote Repo
```

1. **CLAUDE.md** is the source of truth for tech stack and standards
2. **README.md** derives its tech stack section from CLAUDE.md
3. Changes flow in one direction: CLAUDE.md → README.md → push to remote

## Execution Steps

### 1. Validate Environment

Check current directory is not the starter repo itself:
```bash
git remote get-url origin 2>/dev/null | grep -q "dcnu/starter"
```

If match found, abort: "Cannot sync starter to itself. Run this from a project directory."

### 2. Collect Current Project Files

Read the following files from current project (skip if missing):
- `.gitignore`
- `robots.txt`
- `CLAUDE.md`

### 3. Fetch Starter Template from Remote

Fetch files directly from GitHub using `gh`:
```bash
gh api repos/dcnu/starter/contents/.gitignore --jq '.content' | base64 -d
gh api repos/dcnu/starter/contents/robots.txt --jq '.content' | base64 -d
gh api repos/dcnu/starter/contents/CLAUDE.md --jq '.content' | base64 -d
gh api repos/dcnu/starter/contents/README.md --jq '.content' | base64 -d
```

### 4. Analyze Differences

For each file type, identify additions that could improve the starter:

#### .gitignore Analysis
- Extract all non-comment lines from both files
- Identify patterns in current project not in starter
- Filter out project-specific patterns

#### robots.txt Analysis
- Extract User-agent blocks from both files
- Identify new User-agents blocked in current project

#### CLAUDE.md Analysis
- Focus on the "Memory" section (content after "# Memory" heading)
- Extract bullet points from current project's Memory section
- Identify entries not present in starter's Memory section

### 5. Present Differences for Approval

For each file with changes, display diff and use AskUserQuestion:
- Options: "Yes, add all", "Let me select", "Skip this file"

### 6. Clone and Apply Changes

Clone the starter repo to a temp directory:
```bash
TEMP_DIR=$(mktemp -d)
git clone --depth 1 https://github.com/dcnu/starter.git "$TEMP_DIR"
cd "$TEMP_DIR"
```

Apply approved changes to each file.

### 7. Commit and Push

Stage, commit, and push changes:
```bash
git add .gitignore robots.txt CLAUDE.md README.md
git commit -m "Update: Sync template improvements"
git push origin main
```

### 8. Cleanup

Remove temporary clone:
```bash
rm -rf "$TEMP_DIR"
```

## Output Format

```
## Starter Template Sync - $CWD

Comparing against: github.com/dcnu/starter

### .gitignore
[X new patterns found]
- pattern1 (category)
- pattern2 (category)

### robots.txt
[X new user-agents found]
- UserAgent1 (AI Company)

### CLAUDE.md Memory
[X new entries found]
- Entry 1
- Entry 2

---

Ready to sync? Approve changes to commit and push to remote.
```
