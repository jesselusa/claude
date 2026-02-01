# Pull Skills

Pull the latest skills from the `jesselusa/claude` GitHub repository and create symlinks for any new skills in `~/.claude/skills/`.

## Configuration

- **Skills repo:** `/Users/jesselusa/Documents/GitHub/claude`
- **GitHub remote:** `jesselusa/claude`
- **Symlink target:** `~/.claude/skills/`

## Execution Steps

### 1. Pull Latest from Repository

First, ensure we're on main and can pull cleanly:

```bash
cd /Users/jesselusa/Documents/GitHub/claude && \
  git stash --include-untracked -q 2>/dev/null; \
  git checkout main -q 2>/dev/null; \
  git pull; \
  git stash pop -q 2>/dev/null || true
```

This handles:
- Uncommitted changes (stashed and restored)
- Being on a different branch (switches to main)
- Deleted remote tracking branches

Report the result (already up to date, or list of changes).

### 2. Scan for Skills

List all skill directories (directories containing a SKILL.md file):

```bash
find /Users/jesselusa/Documents/GitHub/claude/skills -maxdepth 2 -name "SKILL.md" -exec dirname {} \;
```

### 3. Check Existing Symlinks

List current symlinks:

```bash
ls -la ~/.claude/skills/
```

### 4. Clean Up Broken Symlinks First

Find and remove any broken symlinks (pointing to deleted skills):

```bash
find ~/.claude/skills -type l ! -exec test -e {} \; -print
```

For each broken symlink found, remove it:
```bash
rm ~/.claude/skills/[broken-link]
```

### 5. Create Missing Symlinks

For each skill directory found in step 2:
1. Get the skill name (directory basename)
2. Check if symlink already exists in `~/.claude/skills/`
3. If not, create symlink:

```bash
ln -s /Users/jesselusa/Documents/GitHub/claude/skills/[skill-name] ~/.claude/skills/[skill-name]
```

### 6. Report Results

Output a summary:

```
## Skills Sync Complete

### Repository Status
[git pull output - commits pulled or "Already up to date"]

### Broken Symlinks Removed
- [skill-name] → removed (target no longer exists)

### New Skills Added
- [skill-name] → symlinked

### Current Skills
[list all skills now available]
```

## Notes

- This skill is idempotent - running it multiple times is safe
- Symlinks point to the repo so skills stay in sync with git
- Run `/pull-skills` after you know new skills have been added to the repo
- Handles dirty working directory by stashing/unstashing
- Always pulls from main branch regardless of current branch
