---
name: git-cleanup
description: Prune stale remote refs and delete local branches whose PRs were merged
disable-model-invocation: true
---

# Git Cleanup

Clean up local branches after PRs are merged on GitHub.

---

## Steps

1. **Fetch and prune** remote refs:

```bash
git fetch --prune
```

2. **Determine main branch** (`main` or `master`):

```bash
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@'
```

Fall back to `main` if unset.

3. **Switch to main** and pull latest:

```bash
git checkout <main-branch> && git pull
```

4. **Find stale local branches** — branches where the remote tracking branch is gone:

```bash
git branch -vv | grep ': gone]'
```

Also find merged branches (excluding main):

```bash
git branch --merged <main-branch> | grep -v '^\*' | grep -v <main-branch>
```

Combine and deduplicate both lists.

5. **If no stale branches found:** Output "No stale branches to clean up." and exit.

6. **Prompt user** with `AskUserQuestion`:
   - `multiSelect: true`
   - Header: "Branches"
   - Question: "Which branches do you want to delete?"
   - Options: Each branch name as label, with status in description ("remote gone" or "merged into main")

7. **Delete selected** with `git branch -d <branch>`. If `-d` fails (unmerged), warn user and ask if they want to force-delete with `-D`.

8. **Report** which branches were deleted.
