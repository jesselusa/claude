# claude

Personal Claude Code configuration repository with preferences, skills, hooks, templates, and workflows.

## Quick Start

```bash
# Clone the repo
git clone https://github.com/jesselusa/claude.git ~/Documents/GitHub/claude

# Install skills globally
mkdir -p ~/.claude/skills
for skill in ~/Documents/GitHub/claude/skills/*/; do
    ln -sf "$skill" ~/.claude/skills/
done
```

## Structure

```
claude/
├── CLAUDE.md          # Global preferences and coding style
├── skills/            # Custom slash commands
├── hooks/             # Automation hooks (lint, build checks)
├── templates/         # CLAUDE.md templates for new projects
├── workflows/         # PRD → Tasks workflow templates
└── mcp-servers/       # MCP server configurations
```

## Skills

Custom slash commands available after installation:

| Command | Description |
|---------|-------------|
| `/security-audit` | 7-phase security audit (deps, secrets, logs) |
| `/techdebt` | End-of-session cleanup (dead code, duplicates, TODOs) |
| `/claude-cleanup` | Scan and redact secrets from Claude memory |
| `/cleanup` | Rename files to `Source-Title-date.ext` convention |
| `/create-new-project` | Scaffold new project with templates, optional PRD, optional GitHub repo |
| `/create-readme` | Generate README.md and LICENSE |
| `/gitignore` | Generate .gitignore by project type |
| `/git-cleanup` | Prune stale refs and delete merged local branches |
| `/kill-ports` | Find and kill processes on TCP ports |
| `/robots` | Generate robots.txt with AI/SEO blocking |
| `/sync-starter` | Sync improvements to starter template |

Based on [dcnu/claude](https://github.com/dcnu/claude).

## Workflows

Structured AI-assisted development process:

```
1. Create PRD  →  2. Generate Tasks  →  3. Execute Tasks
```

```bash
# 1. Create a PRD
Use @workflows/create-prd.md to build: [feature description]

# 2. Generate tasks from PRD
Create tasks from @tasks/prd-[feature].md using @workflows/generate-tasks.md

# 3. Execute tasks incrementally
Start on task 1.1 from tasks/tasks-[feature].md
```

Based on [snarktank/ai-dev-tasks](https://github.com/snarktank/ai-dev-tasks).

## Templates

CLAUDE.md templates for different project types:

- `nextjs.md` - Next.js projects with Supabase
- `python.md` - Python projects
- `agents.md` - Generic AI assistant guidance
- `starter.md` - Minimal starter template

Copy to a new project:
```bash
cp ~/Documents/GitHub/claude/templates/nextjs.md /path/to/project/CLAUDE.md
```

## Hooks

Automation hooks for Claude Code:

- **Session hooks** - Check for README.md and .gitignore on session start
- **Next.js hooks** - Run lint after edits, build check before commits
- **Python hooks** - Run ruff/mypy after edits

## Preferences

### Stack
- **Languages**: TypeScript/JavaScript, Python
- **Frontend**: Next.js (App Router), Tailwind CSS
- **Backend**: Supabase
- **Deployment**: Vercel

### Code Style
- Tabs for indentation
- Concise, minimal code
- Mobile-first responsive design
- `pnpm` as package manager

### Commit Format
```
type: description
```
Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`

---

## Working with Claude Code

Tips for getting the most out of Claude Code.

### Just Talk To It

- Keep prompts short: 1-2 sentences is often enough
- Don't over-specify - let the agent figure out implementation details
- Under-prompt intentionally to discover unexpected solutions
- Trust the agent to read the codebase and follow existing patterns
- **Use voice dictation** (fn x2 on macOS) - you speak 3x faster than you type

### Screenshots > Descriptions

- For UI work, paste a screenshot of what you want (or a bug you see)
- Visual references are faster and more precise than written descriptions
- Use screenshots for ~50% of UI-related prompts

### Trust Git, Not Approval Prompts

- Rely on git history and `git checkout .` rather than approving every action
- Nothing catastrophic happens if you have version control
- Speed > excessive caution for local development

### Queue, Don't Wait

- While an agent is working, type your next instruction
- Queue messages instead of crafting "perfect" continuation prompts
- Momentum matters more than polish

### Power Prompts

Effective prompts to try:

- "Grill me on these changes and don't make a PR until I pass your test"
- "Prove to me this works" - have Claude diff behavior between main and feature branch
- "Knowing everything you know now, scrap this and implement the elegant solution"
- "Use subagents" - appending this throws more compute at the problem

---

## Multi-Agent Workflow

### Running Multiple Agents

- **Use git worktrees** - spin up 3-5 worktrees, each with its own Claude session (biggest productivity unlock)
- Set up shell aliases (za, zb, zc) to hop between worktrees in one keystroke
- Also run sessions on claude.ai web - use `&` to hand off, `--teleport` to switch back
- Keep a dedicated "analysis" worktree for reading logs and running queries

### When to Parallelize

- Independent features that don't touch the same files
- Frontend + backend work simultaneously
- Tests + implementation in parallel contexts

---

## Bug Fixing Tips

- Paste a Slack bug thread and just say "fix"
- "Go fix the failing CI tests" - don't micromanage how
- Point Claude at logs (docker, Vercel, Supabase) to troubleshoot

---

## Refactoring Time

Dedicate ~20% of time to AI-driven refactoring. Good for low-focus days:

- "Update dependencies and fix any breaking changes"
- "Improve test coverage for [module]"
- "Find inconsistent patterns and standardize"

---

## Maintaining CLAUDE.md

- Claude is eerily good at writing rules for itself - let it
- Periodically audit for redundancy and outdated guidance
- Keep instructions concise - verbose guidance wastes tokens
- Remove guidance that newer models handle automatically

---

## License

MIT
