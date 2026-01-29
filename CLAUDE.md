# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a personal Claude Code configuration repository containing:
- Global preferences and coding style
- MCP server configurations
- Custom hooks
- Project templates for CLAUDE.md files
- Custom skills (slash commands)

## Structure

```
jl-claude-assistant/
├── CLAUDE.md          # This file - global preferences
├── mcp-servers/       # MCP server configurations
├── hooks/             # Custom automation hooks
├── templates/         # CLAUDE.md templates for different project types
├── workflows/         # AI dev workflow templates (PRD → Tasks → Execute)
└── skills/            # Custom slash commands (/security-audit, etc.)
```

---

## Workflow Philosophy

### Just Talk To It
- Keep prompts short: 1-2 sentences is often enough
- Don't over-specify - let the agent figure out implementation details
- Under-prompt intentionally to discover unexpected solutions
- Trust the agent to read the codebase and follow existing patterns

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

---

## Multi-Agent Workflow

### Running Multiple Agents
- Open 2-4 Claude Code terminals working in parallel
- Give each agent a distinct feature or area to avoid conflicts
- All agents can work in the same folder - use atomic commits to stay clean

### When to Parallelize
- Independent features that don't touch the same files
- Frontend + backend work simultaneously
- Tests + implementation in parallel contexts

### Keeping Context Clean
- Each agent should focus on one concern
- Don't overload a single context with unrelated tasks
- Start fresh contexts for experimental/exploratory work

---

## Testing Approach

### Test After, Not Before
- Skip TDD - write tests *after* implementation
- Request tests immediately after each feature, in the same context
- This catches bugs while the agent has full context of what was built

### Self-Verification
- Agents should run their own tests, lint, and type-check
- Close the loop: agents verify their work before declaring done
- Don't wait for CI - run tests locally through agents

---

## Refactoring Time

Dedicate ~20% of time to AI-driven refactoring. Good for low-focus days:

- "Find and remove dead code"
- "Look for duplicated logic and consolidate"
- "Update dependencies and fix any breaking changes"
- "Improve test coverage for [module]"
- "Find inconsistent patterns and standardize"

---

## This File is Living

- Let agents update this CLAUDE.md with new patterns discovered during work
- Periodically audit for redundancy and outdated guidance
- Keep instructions concise - verbose guidance wastes tokens
- Remove guidance that newer models handle automatically

---

## Personal Preferences

### Languages & Stack
- **Primary**: TypeScript/JavaScript, Python
- **Frontend**: Next.js (App Router) with React
- **Styling**: Tailwind CSS
- **Backend**: Supabase (Postgres, Auth, Realtime)
- **Deployment**: Vercel

### Code Style
- Concise and minimal - avoid unnecessary boilerplate
- Comments only when logic isn't self-evident
- Prefer simple solutions over clever ones
- Keep files focused and small
- Use tabs for indentation (not spaces)

### Tooling
- **Package manager**: `pnpm` (not npm/yarn)
- **Pre-build**: Always run `lint` + `type-check` before builds
- **Commit format**: `type: description` (e.g., `feat: add login`, `fix: timezone bug`)
  - Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`

### Safety Rules
- Never expose environment variables in code or logs
- Never run `rm -rf` without explicit user confirmation
- Never run destructive database commands (`DROP`, `TRUNCATE`, `db reset`)
- Secrets only in `.env.local` (never committed)

### Design
- Mobile-first responsive design - always optimize for phone use

---

## Development Workflow

### For Clear, Straightforward Tasks
Just do it. Skip planning for obvious features - say "add a settings page" and let the agent figure it out.

### For Ambiguous or Complex Features
Follow this structured process:

1. **Create PRD** - `Use @workflows/create-prd.md to build: [feature description]`
2. **Generate Tasks** - `Create tasks from @tasks/prd-[feature].md using @workflows/generate-tasks.md`
3. **Execute** - Work through tasks incrementally, checking off as completed

Reserve detailed planning for genuinely ambiguous architectural decisions.

---

## What NOT to Do

- Don't over-engineer tooling (no custom agent frameworks)
- Don't use excessive MCPs - they clutter context
- Don't write perfect prompts - iterate instead
- Don't review every line of generated code - focus on outcomes
- Don't wait for remote CI - run tests locally
