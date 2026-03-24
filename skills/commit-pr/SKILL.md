---
name: commit-pr
description: Lint, type-check, commit all changes, push, and open a PR on a feature branch
disable-model-invocation: true
---

# Commit & PR

The standard end-of-task workflow: verify, commit, push, and open a pull request.

---

## Steps

### 1. Check branch

```bash
git branch --show-current
```

If on `main` or `master`:
- Use `AskUserQuestion` to ask for a feature branch name
- Create and switch to it: `git checkout -b <branch-name>`

If already on a feature branch, continue.

### 2. Check for changes

```bash
git status --short
```

If nothing to commit, output "Nothing to commit." and exit.

### 3. Warn about sensitive files

```bash
git status --short | grep -E '\.env'
```

If any `.env` files are staged or modified, warn the user and ask before proceeding. Never commit `.env` files.

### 4. Lint

```bash
pnpm lint
```

If this fails, report the errors and **stop**. Do not commit broken code.

If `pnpm lint` is not available, try `pnpm run lint`. If no lint script exists, skip and note it.

### 5. Type-check

```bash
pnpm type-check
```

If this fails, report the errors and **stop**.

If `pnpm type-check` is not available, try `tsc --noEmit`. If neither works, skip and note it.

### 6. Stage changes

```bash
git add -A
```

Exclude any `.env*` files from staging.

### 7. Commit message

Use `AskUserQuestion` to ask:
> "Describe what this commit does (I'll format it as a conventional commit):"

Format the response as `type: description` where type is one of: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`.

```bash
git commit -m "<type>: <description>"
```

### 8. Check for merge conflicts with main

Before pushing, check if the branch is behind main and has conflicts:

```bash
git fetch origin main
git merge-tree $(git merge-base HEAD origin/main) HEAD origin/main 2>/dev/null | grep -c '<<<<<<<' || true
```

If there are potential conflicts, merge main into the branch:

```bash
git merge origin/main
```

If merge conflicts occur:
1. List the conflicted files: `git diff --name-only --diff-filter=U`
2. Read each conflicted file and resolve the conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
3. Keep both sides' changes where they don't contradict, or pick the correct version
4. Stage resolved files: `git add <file>`
5. Run lint and type-check again to verify the resolution
6. Commit the merge: `git commit -m "merge: resolve conflicts with main"`

If no conflicts, the merge completes automatically.

### 9. Push

Check if upstream is set:

```bash
git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null
```

If no upstream (first push on this branch):

```bash
git push -u origin <branch-name>
```

Otherwise:

```bash
git push
```

### 10. Create PR

Check if a PR already exists for this branch:

```bash
gh pr view --json url -q .url 2>/dev/null
```

If a PR already exists, output its URL and exit.

Otherwise:

```bash
gh pr create \
  --title "<commit message>" \
  --body "$(cat <<'EOF'
## Summary
<brief description of changes>

## Test plan
- [ ] Lint passes
- [ ] Type-check passes
- [ ] Tested locally

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)" \
  --assignee @me
```

Output the PR URL when done.
