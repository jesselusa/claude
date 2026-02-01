# jl-claude-assistant

Personal Claude Code configuration repository with preferences, skills, hooks, templates, and workflows.

## Quick Start

```bash
# Clone the repo
git clone https://github.com/jesselusa/jl-claude-assistant.git ~/Documents/GitHub/jl-claude-assistant

# Install skills globally
mkdir -p ~/.claude/skills
for skill in ~/Documents/GitHub/jl-claude-assistant/skills/*/; do
    ln -sf "$skill" ~/.claude/skills/
done
```

## Structure

```
jl-claude-assistant/
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
| `/create-readme` | Generate README.md and LICENSE |
| `/gitignore` | Generate .gitignore by project type |
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
cp ~/Documents/GitHub/jl-claude-assistant/templates/nextjs.md /path/to/project/CLAUDE.md
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

## License

MIT
