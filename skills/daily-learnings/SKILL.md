---
name: daily-learnings
description: Scan recent Claude Code session logs, extract universal engineering rules, update the global CLAUDE.md, and open a PR. Also scores past PR outcomes and filters out rejected/in-flight rules before proposing new ones. Invoked daily by the launchagent at ~/Library/LaunchAgents/com.jesselusa.learning-agent.plist.
---

# Daily Learnings

Scan the last 24h of session activity for universal engineering lessons. Update `/Users/jesselusa/Documents/GitHub/claude/CLAUDE.md` and open a PR. Skip anything already rejected in a closed PR or sitting in an open one.

All paths below are absolute — this skill always runs against the `jesselusa/claude` repo on the local machine.

## Step 0: Bail out if today's branch exists

If `feat/daily-learnings-<YYYY-MM-DD>` already exists locally or on origin, today's run already happened. Exit immediately — no scoring, no extraction.

```
git rev-parse --verify feat/daily-learnings-<YYYY-MM-DD> 2>/dev/null
git ls-remote --heads origin feat/daily-learnings-<YYYY-MM-DD>
```

## Step 1: Score past PR outcomes

Read `evals/learning-agent/decisions.jsonl` in the claude repo. For every entry where `outcome` is `null`:

```
gh pr view <pr_url> --json state,mergedAt,closedAt
```

- `MERGED` → `outcome: "merged"`, set `outcome_date` from `mergedAt`
- `CLOSED` → `outcome: "closed"`, set `outcome_date` from `closedAt`
- Still open → leave as `null`

If any entries changed, update the file in place. Track a `log_dirty` flag so you know to commit it later.

## Step 2: Build rule context

From the updated log, build two lists:

- **`closed_rules`** — rules from entries with `outcome: "closed"` (soft warning — don't re-propose unless meaningfully distinct)
- **`open_rules`** — rules from entries still `null` (hard skip — PR awaiting review, don't duplicate)

Both lists are for the global claude repo only. There's no per-repo split like the sync skill has.

## Step 3: Gather session material

Find JSONL files modified in the last 24h under `~/.claude/projects/` (skip anything in a `subagents/` directory).

Extract `user`-type message text — that's where the signal lives. Skip tool outputs, assistant messages, and system reminders. Cap at ~30k chars total; truncate individual messages at 300 chars.

If no recent sessions exist or they contain no user messages, jump to the "Early exit" block at the end.

## Step 4: Extract learnings

Read the current `CLAUDE.md` (first 5k chars is enough for dedup).

Identify rules that are:
- **Universal** — apply to any project regardless of stack, domain, or design. "Run type-check before committing" passes. "Use zinc colors" fails.
- **Absent from CLAUDE.md** — even in different wording
- **Not in `closed_rules`** — unless meaningfully distinct from the rejected version (soft filter)
- **Not in `open_rules`** — hard skip
- **High-confidence** — when in doubt, leave it out

For each rule, pick one of these sections: `Working Style`, `Code Style`, `Testing Approach`, `Before Committing`, `Personal Preferences`. If no section fits, drop the rule.

Also watch for recurring multi-step workflows that deserve a skill stub. Only suggest a skill if the workflow emerged at least twice and is useful across projects.

## Step 5: Apply rules + create skill stubs

For each accepted rule:
- Find the matching `### Section` header in `CLAUDE.md`
- Insert `- <rule text>` before the next `##`/`---` boundary
- Skip if the rule text (lowercased) already appears in that section

For each accepted skill:
- Create `skills/<name>/SKILL.md` with frontmatter (`name`, `description`) and a short stub body with TODO placeholders
- Skip if the file already exists

If nothing was added, jump to the "Early exit" block at the end.

## Step 6: Open the PR

```
git checkout -b feat/daily-learnings-<YYYY-MM-DD>
git add CLAUDE.md skills/<new-skill>/SKILL.md  # only the files you actually touched
git commit -m "feat: daily learnings <YYYY-MM-DD>"
git push -u origin feat/daily-learnings-<YYYY-MM-DD>
gh pr create --title "feat: daily learnings <YYYY-MM-DD>" --assignee @me --body "<see format below>"
```

PR body:
```
## Daily Learnings — YYYY-MM-DD

Automated PR from the /daily-learnings skill.

### Rules added to CLAUDE.md

- [Section] Rule text
- [Section] Another rule

### Skill stubs created

- `/<name>` — one-line description
```

Return to `main` after pushing.

## Step 7: Log the decision

You should already be on `main` (Step 6 returned you there). Append a new entry to `evals/learning-agent/decisions.jsonl`:

```json
{"date":"YYYY-MM-DD","pr_number":42,"pr_url":"https://github.com/jesselusa/claude/pull/42","rules_added":[{"section":"Section","rule":"Rule text"}],"skills_added":["skill-name"],"outcome":null,"outcome_date":null}
```

Then commit + push (this single commit covers both the new entry and any scoring updates from Step 1):

```
git add evals/learning-agent/decisions.jsonl
git commit -m "chore: log learning-agent decisions <YYYY-MM-DD>"
git push origin main
```

## Early exit

If you skipped PR creation (no learnings today, or branch already exists) but `log_dirty` is true from Step 1 scoring, still commit those updates:

```
git add evals/learning-agent/decisions.jsonl
git commit -m "chore: score learning-agent outcomes <YYYY-MM-DD>"
git push origin main
```

If `log_dirty` is false, exit cleanly — there's nothing to commit.

## Rules

- Be conservative — high-confidence rules only. When unsure, drop it. A quiet day is a success, not a failure.
- Universal only — no stack, framework, or design-system specifics
- Soft warnings are a heuristic, not a ban — if the new framing is clearly distinct from the closed version, include it
- Never `--amend` or force-push
- Never modify existing log entries except to fill `outcome`/`outcome_date` during scoring
- If any git/gh command fails, stop and report — don't retry blindly
