# PRD: Daily Learning Agent

## 1. Introduction / Overview

Every Claude Code session produces learnings — patterns, mistakes, preferences, and reusable rules — that currently get lost unless manually captured via `/learn`. This agent runs daily at a fixed time, scrapes recent session logs across all projects, extracts generic reusable learnings, updates the global `/claude` config (CLAUDE.md + new skills), and propagates those updates to all 4 project repos via pull requests.

**Goal:** Zero-effort continuous improvement of Claude's instructions across all repos, with human review gated behind PRs.

---

## 2. Goals

1. Automatically capture generic learnings from session history without manual `/learn` runs
2. Keep `/claude`'s CLAUDE.md and skills up to date daily
3. Propagate approved learnings to all project repos (pokecrm, LLL, palette, jesselusa.com) via sync PRs
4. Require zero user effort to trigger — runs on a fixed daily schedule

---

## 3. User Stories

- **As Jesse**, I want my Claude instructions to improve automatically over time so I don't have to remember to run `/learn` after every session.
- **As Jesse**, I want to review changes before they merge so I stay in control of what gets codified.
- **As Jesse**, I want all my project repos to stay in sync with the latest global lessons so I get consistent Claude behavior everywhere.

---

## 4. Functional Requirements

### 4.1 Scheduling
1. The agent runs daily at a fixed local time (e.g. 9am) via macOS launchd.
2. It must run without an active Claude Code session or terminal.
3. It must not require any user interaction to trigger.

### 4.2 Session Log Ingestion
4. The agent reads recent session logs from `~/.claude/projects/` — all `.jsonl` files modified in the last 24 hours.
5. It extracts only human (`"type": "user"`) and assistant messages relevant to lessons learned (mistakes corrected, patterns discussed, rules added).
6. It skips subagent logs (`/subagents/` directories).

### 4.3 Learning Extraction
7. The agent uses Claude (via the Anthropic API) to analyze the ingested messages and extract candidate learnings.
8. A learning is considered **generic** if it is not tied to a specific app's domain (e.g. Pokemon CRM logic, LLL magazine pricing) and could apply to any project the user works on.
9. Claude autonomously decides what is generic — no user approval step before committing.
10. Duplicate learnings (already present in `/claude`'s CLAUDE.md) are skipped.
11. Learnings are categorized as either:
    - **CLAUDE.md rule** — a working style preference, code style rule, or workflow instruction
    - **New skill candidate** — a repeated multi-step workflow worth packaging as a `/skill`

### 4.4 Updates to /claude
12. CLAUDE.md rule updates are appended or inserted into the appropriate section of `/claude/CLAUDE.md`.
13. New skill candidates generate a stub `SKILL.md` in `skills/<name>/` following the existing skill format.
14. All changes are committed to a dated feature branch: `feat/daily-learnings-YYYY-MM-DD`.
15. A single bundled PR is opened against `main` in `jesselusa/claude` with `--assignee @me`.
16. If no new learnings are found, no commit or PR is created (silent skip).

### 4.5 Sync to Project Repos
17. After the `/claude` PR is opened, the agent runs the equivalent of `/sync-starter --pull` in each of the 4 project repos: pokecrm, little-language-labs, palette, jesselusa.com.
18. Each repo gets its own feature branch (`feat/sync-learnings-YYYY-MM-DD`) and a separate PR opened with `--assignee @me`.
19. If a repo has no changes after sync, no PR is opened for it (silent skip).
20. The agent assumes project repos are cloned locally at `~/Documents/GitHub/<repo-name>`.

### 4.6 Reporting
21. The agent writes a brief run log to `~/.claude/learning-agent/logs/YYYY-MM-DD.log` including: learnings found, files changed, PRs opened.
22. If any step fails (API error, git conflict, missing repo), the error is logged and the agent continues with the remaining repos rather than stopping entirely.

---

## 5. Non-Goals (Out of Scope)

- **Auto-merging PRs** — all changes require human review before merging
- **User approval of individual learnings** before commit — Claude decides autonomously
- **Learning from subagent conversations** — only top-level session logs are analyzed
- **Email or push notifications** — run log file is the only output
- **Running during active Claude Code sessions** — launchd fires at a fixed time regardless

---

## 6. Technical Considerations

- **Runtime:** macOS launchd plist, running a shell script or Node.js/Python script
- **AI calls:** Claude Code CLI (`claude --print "..."`) for learning extraction — uses existing Claude Code account, no API key required
- **Git operations:** `gh` CLI for PR creation; `git` for branching and committing
- **Session log format:** JSONL — parse with `jq` or Python's `json` module
- **Auth:** Script needs access to GitHub via `gh` CLI (already authenticated on machine)
- **Idempotency:** If the agent runs twice in a day, the second run should detect the existing branch/PR and skip

---

## 7. Success Metrics

- PRs are opened to `/claude` at least 3x per week when sessions are active
- Zero manual `/learn` runs needed after the first month of operation
- Project repos stay within 1 day of `/claude`'s latest learnings

---

## 8. Open Questions

- Should the agent use `claude-sonnet-4-6` (smarter, slower, more expensive) or `claude-haiku-4-5` (faster, cheaper) for learning extraction?
- ~~What's the right cutoff for "too trivial to codify"?~~ **Resolved:** Claude uses its own judgment. Tune after seeing first few runs.
- ~~Should the launchd job run even on days with no session activity?~~ **Resolved:** Check for new logs first; skip the `claude --print` call entirely if no session activity in the last 24hrs.
