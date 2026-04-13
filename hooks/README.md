# Claude Code Hooks

Hooks run automatically in response to Claude's actions. They enforce rules, block dangerous commands, and save tokens by moving repeated work out of the conversation.

## Global hooks (installed)

Wired into `~/.claude/settings.json`. Source scripts live in `hooks/scripts/`.

| Script | Event | What it does |
|--------|-------|--------------|
| `block-dangerous-bash.sh` | PreToolUse / Bash | Blocks `rm -rf`, DROP/TRUNCATE/db reset, `git commit` on main, `git push --force` to main, `git add .env*` (allows `.env.example/.sample/.template`), `npm`/`yarn install` |
| `lint-before-commit.sh` | PreToolUse / Bash | On `git commit`, runs `pnpm lint` + `pnpm type-check` (if scripts exist) in the nearest `package.json` dir. Only fires in pnpm projects. |
| `resymlink-skills.sh` | PostToolUse / Edit\|Write\|MultiEdit | After editing anything in `~/Documents/GitHub/claude/skills/`, re-runs the skills symlink loop so new skills appear immediately. |
| `session-start.sh` | SessionStart | Prints branch, warns on uncommitted-changes-on-main, counts task files in `tasks/`, counts merged local branches, checks README + .gitignore exist. |
| `require-agent-model.sh` | PreToolUse / Agent | Blocks subagent calls that don't pass an explicit `model` param, so model routing (CLAUDE.md) is enforced. Also blocks `haiku` for code work. |

### What's intentionally NOT hooked

- **Auto-lint after every edit** — token bloat (lint output lands in Claude's context per edit). Pre-commit hook catches the same issues once.
- **Auto `git pull` on session start** — surprise factor with dirty worktrees.
- **UserPromptSubmit context injection** — adds tokens every turn.
- **Post-commit `/techdebt` reminders** — spam; `/session-end` handles this.
- **`gh pr create` flag warnings** — hooks can't rewrite commands; stays in CLAUDE.md as guidance.

## Per-project hook templates

Copy into a project's `.claude/` dir for project-specific automation.

| File | For | Purpose |
|------|-----|---------|
| `nextjs-hooks.json` | Next.js projects | Lint + type-check on TS/TSX edits, build check before commit |
| `python-hooks.json` | Python projects | Ruff lint/format after edits, pytest before commit |
| `session-hooks.json` | Any project | SessionStart README + .gitignore check (superseded globally by `session-start.sh`) |

Install per-project:

```bash
mkdir -p /path/to/project/.claude
cp hooks/nextjs-hooks.json /path/to/project/.claude/hooks.json
```

## Adding a new global hook

1. Write the script in `hooks/scripts/`, `chmod +x` it.
2. For Bash hooks, parse stdin JSON: `cmd=$(jq -r '.tool_input.command // ""')`. Exit 1 + stderr message to block.
3. Register it in `~/.claude/settings.json` under `hooks.<Event>` with matcher + command path.
4. Test with: `echo '{"tool_input":{"command":"..."}}' | ./hooks/scripts/<script>.sh`

## Hook events reference

| Event | Fires | Matcher | Notes |
|-------|-------|---------|-------|
| `SessionStart` | Claude Code opens | none | stdout → Claude's context |
| `PreToolUse` | Before a tool runs | tool name (`Bash`, `Edit`, etc.) | Exit 1 blocks; stderr shown to Claude |
| `PostToolUse` | After tool succeeds | tool name (pipe-separated ok) | stdout → Claude's context |
| `UserPromptSubmit` | You send a message | none | stdout injected (costs tokens) |
