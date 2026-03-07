---
name: session-end
description: End-of-session wrap-up — runs techdebt, learn, git-cleanup, tasks check, and prints a summary
disable-model-invocation: true
---

# Session End

Run the full end-of-session cleanup sequence in order: `/techdebt` → `/learn` → `/git-cleanup` → tasks check → summary.

---

## Steps

### 1. Tech Debt

Run `/techdebt` on files changed in the current branch:

```bash
git diff --name-only main 2>/dev/null || git diff --name-only HEAD
```

Scan those files for: dead code, debug/console statements, duplicate code, leftover TODO comments. Apply safe fixes. Commit any changes made:

```bash
git commit -m "chore: tech debt cleanup"
```

Report what was cleaned up before moving on.

---

### 2. Session Learnings

Run `/learn` — review the full session for patterns, mistakes, and decisions worth codifying.

For each potential CLAUDE.md update, use `AskUserQuestion`:
- Options: `Add to CLAUDE.md`, `Skip`, `Edit first`

Apply approved changes immediately. Keep suggestions concise and actionable.

---

### 3. Git Cleanup

Run `/git-cleanup`:

1. Fetch and prune remote refs:

```bash
git fetch --prune
```

2. Determine main branch and switch to it:

```bash
git checkout main && git pull
```

3. Find stale local branches (remote gone or merged into main):

```bash
git branch -vv | grep ': gone]'
git branch --merged main | grep -v '^\*' | grep -v main
```

4. If stale branches exist, use `AskUserQuestion` (`multiSelect: true`) to ask which to delete.

5. Delete selected branches with `git branch -d`. Warn and offer `-D` if `-d` fails.

---

### 4. Tasks Check

Look for a `tasks/` directory in the project root. If it exists, read all task files and extract open `- [ ]` items.

If open tasks are found, display them grouped by file. Use `AskUserQuestion` (`multiSelect: true`):

> "Which tasks are now complete and should be marked done?"

Update selected tasks from `- [ ]` to `- [x]`.

If no tasks directory or no open tasks exist, note it and continue.

---

### 5. Summary

Print a clean session summary:

```
---
Session complete.

Tech Debt:    <fixes applied, or "Nothing to clean up">
Learnings:   <items added to CLAUDE.md, or "Nothing added">
Git Cleanup: <branches deleted, or "No stale branches">
Tasks:       <tasks marked complete, or "No changes">
---
```
