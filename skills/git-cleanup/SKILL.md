---
name: git-cleanup
description: Delete local and remote branches whose PRs are merged, and prune abandoned worktrees
disable-model-invocation: true
---

# Git Cleanup

Delete branches whose work has landed, and the worktrees left behind with them.

**Argument:** `$ARGUMENTS` — a repo path, or nothing for the current repo.

---

## The thing that makes this non-obvious

**`git branch --merged` and `: gone]` both miss squash-merged branches.** A squash
merge writes one *new* commit to main, so the branch's own commits never appear in
main's history and `--merged` reports it as unmerged forever. If the remote branch
also still exists, `: gone]` misses it too.

Squash is the default merge on these repos, so relying on either signal leaves
essentially everything behind. In August 2026 that was 54 stale branches across three
repos, every one of them fully merged.

**The reliable signal is the PR state**, from `gh pr list --head <branch> --state all`.
Use it as the primary classifier. Treat `--merged` and `: gone]` as extra evidence,
never as the test.

---

## Steps

### 1. Fetch and fast-forward

```bash
git fetch --all --prune
git checkout "$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo main)"
git pull --ff-only
```

If `pull --ff-only` fails, main has diverged locally. Stop and tell the user; don't
merge or reset it yourself.

### 2. Classify every branch by its PR

Local and remote, one pass each:

```bash
for b in $(git branch --format='%(refname:short)' | grep -v "^$MAIN$"); do
  printf '%s\t%s\t%s\n' "$b" \
    "$(gh pr list --head "$b" --state all --json number,state -q '.[0]|"\(.number):\(.state)"')" \
    "$(git log -1 --format=%cs "$b")"
done
```

Bucket the results:

| PR state | Verdict |
|---|---|
| `MERGED` | **Delete.** Content is in main regardless of what `--merged` says. |
| `OPEN` | **Keep.** Work in flight. |
| `CLOSED` | **Ask.** Rejected work. Usually delete, but it's the user's call. |
| no PR | **Investigate** — see step 3. |

### 3. Branches with no PR need a content check

These are the dangerous ones: scratch branches, abandoned experiments, and
occasionally real unlanded work. Never bulk-delete this bucket.

For each, find whether its content reached main *some other way*:

```bash
git log main..<branch> --oneline          # what it claims to add
```

Then grep main for the distinctive artifact each commit introduces — a new file, a
new symbol, a new migration. A file that exists in main means it landed under a
different branch name. A file that doesn't means the work is genuinely unlanded.

Report unlanded branches to the user with what they contain. Don't delete them.

### 4. Prune worktrees

Worktrees outlive the branches they were cut for and are easy to miss.

```bash
git worktree list
git worktree remove --force <path>   # for each whose branch is in the delete bucket
git worktree prune
```

A worktree must be removed *before* its branch can be deleted.

### 5. Confirm, then delete

Show the user the buckets with `AskUserQuestion` (`multiSelect: true`), labelled by
verdict. Then:

```bash
git branch -D <branch>...                  # -D: -d refuses squash-merged branches
git push origin --delete <branch>...       # remote, if it still exists
```

`-D` is correct here, not reckless: `-d` rejects every squash-merged branch, which is
all of them. The safety net is step 2, not the flag. Deleted local branches stay in
the reflog for ~90 days.

### 6. Report

Count deleted, kept, and flagged-as-unlanded, per repo. Name every unlanded branch and
say what's in it — that's the part the user has to act on.

---

## Multi-repo

With no argument, run against the current repo only. Sweep other repos only when the
user names them.
