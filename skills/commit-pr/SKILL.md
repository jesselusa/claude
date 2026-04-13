---
name: commit-pr
description: Commit all changes and open a PR on a feature branch (global hooks handle branch, .env, lint, and type-check enforcement)
disable-model-invocation: true
---

# Commit & PR

End-of-task workflow: commit, push, and open a PR. Global hooks enforce the safety rails, so this skill focuses on intent (message, PR body).

**Hooks in play (automatic, don't duplicate):**
- `git commit` on main → blocked
- `git add .env*` (non-example) → blocked
- Pre-commit: `pnpm lint` + `pnpm type-check` run automatically (if scripts exist)

---

## Steps

### 1. If on main, create a feature branch

If the blocker hook fires on commit, you'll know you're on main. Front-run it: check branch first, and if on `main`/`master`, use `AskUserQuestion` to ask for a branch name, then:

```bash
git checkout -b <branch-name>
```

### 2. Check for changes

```bash
git status --short
```

Nothing staged or modified → "Nothing to commit." and exit.

### 3. Run tests (if present)

Lint + type-check run automatically at commit time via hooks. Tests don't — run them here if the project has them:

```bash
grep -q '"test"' package.json 2>/dev/null && pnpm test
```

If tests fail, stop. Don't proceed to commit.

### 4. Commit message

Use `AskUserQuestion`:
> "Describe what this commit does (I'll format it as a conventional commit):"

Format as `type: description` — types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`.

```bash
git add -A
git commit -m "<type>: <description>"
```

If the commit is blocked by hooks (lint/type-check failure, .env staged), surface the hook message to the user and stop. Don't bypass with `--no-verify`.

### 5. Rebase/merge main if needed

```bash
git fetch origin main
git merge-tree $(git merge-base HEAD origin/main) HEAD origin/main 2>/dev/null | grep -c '<<<<<<<' || true
```

If conflicts, `git merge origin/main`, resolve, `git add`, `git commit -m "merge: resolve conflicts with main"`.

### 6. Push

```bash
git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null \
  && git push \
  || git push -u origin "$(git branch --show-current)"
```

### 7. Create PR (if not already one)

```bash
gh pr view --json url -q .url 2>/dev/null
```

Exists → print URL, exit. Otherwise:

```bash
gh pr create \
  --title "<commit message>" \
  --assignee @me \
  --body "$(cat <<'EOF'
## Summary
<brief description of changes>

## Test plan
- [ ] Tested locally

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Output the PR URL.
