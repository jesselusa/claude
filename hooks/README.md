# Claude Code Hooks

Hooks run automatically in response to Claude's actions. Place `hooks.json` in your project's `.claude/` directory.

## Available Hooks

| Hook | Trigger | Purpose |
|------|---------|---------|
| `SessionStart` | When Claude Code starts | Check project setup |
| `PreToolUse` | Before tool runs | Validate or block actions |
| `PostToolUse` | After tool runs | Run follow-up commands |
| `Notification` | On events | Alert on certain conditions |

## Setup

Copy the desired hooks file to your project:

```bash
mkdir -p /path/to/project/.claude
cp hooks/nextjs-hooks.json /path/to/project/.claude/hooks.json
```

## Hook Files

- `session-hooks.json` - SessionStart checks (README.md, .gitignore exist)
- `nextjs-hooks.json` - Lint + type check after edits, build check before commit
- `python-hooks.json` - Ruff lint/format after edits, pytest before commit
