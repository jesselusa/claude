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
claude/
├── CLAUDE.md          # This file - global preferences
├── skills/            # Custom slash commands (see below)
├── hooks/             # Automation hooks (lint, build checks)
├── templates/         # CLAUDE.md templates for new projects
├── workflows/         # PRD → Tasks workflow templates
└── mcp-servers/       # MCP server configurations
```

## Development Commands

```bash
# Install skills globally (symlink for easy updates)
mkdir -p ~/.claude/skills
for skill in ~/Documents/GitHub/claude/skills/*/; do
    ln -sf "$skill" ~/.claude/skills/
done

# Test a skill locally
cd ~/.claude/skills && ls -la  # verify symlinks

# Copy a hook to a project
cp hooks/nextjs-hooks.json /path/to/project/.claude/hooks.json

# Copy a template to a new project
cp templates/nextjs.md /path/to/project/CLAUDE.md
```

## Available Skills

| Command | Description |
|---------|-------------|
| `/security-audit` | 7-phase security audit (deps, secrets, logs) |
| `/techdebt` | End-of-session cleanup (dead code, duplicates, TODOs) |
| `/claude-cleanup` | Scan and redact secrets from Claude memory |
| `/cleanup` | Rename files to `Source-Title-date.ext` convention |
| `/create-new-project` | Scaffold new project with templates, optional PRD & GitHub |
| `/create-readme` | Generate README.md and LICENSE |
| `/gitignore` | Generate .gitignore by project type |
| `/kill-ports` | Find and kill processes on TCP ports |
| `/robots` | Generate robots.txt with AI/SEO blocking |
| `/sync-starter` | Sync improvements back to this starter template |

---

## Workflow Philosophy

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

### Self-Verification (Critical)
**Give Claude a way to verify its work - this 2-3x's quality.**

- Run tests, lint, type-check after every change
- For UI: test in browser, check mobile, verify no console errors
- Close the loop before declaring done
- If verification fails: fix → re-verify → repeat until green

### Bug Fixing
- Paste a Slack bug thread and just say "fix"
- "Go fix the failing CI tests" - don't micromanage how
- Point Claude at logs (docker, Vercel, Supabase) to troubleshoot

---

## End of Session Checklist

Before wrapping up:

1. **Verify** - run tests, lint, type-check pass
2. **Clean** - run `/techdebt` to remove dead code, duplicates, debug statements
3. **Update tasks** - mark completed `[x]`, add new tasks discovered
4. **Update docs** - if you changed: data model, structure, stack, patterns, or features
5. **Teach Claude** - if Claude made a mistake, say "Update CLAUDE.md so you don't make that mistake again"

---

## Creating New Skills

If you do something more than once a day, turn it into a skill.

**Location:** `skills/<name>/SKILL.md` - Claude Code finds them automatically after symlinking to `~/.claude/skills/`

**Structure:**
```
skill-name/
├── SKILL.md          # Required: skill definition
├── *.sh              # Optional: supporting scripts
└── templates/        # Optional: template files
```

---

## Refactoring Time

Dedicate ~20% of time to AI-driven refactoring. Good for low-focus days:

- "Update dependencies and fix any breaking changes"
- "Improve test coverage for [module]"
- "Find inconsistent patterns and standardize"

---

## This File is Living

- Claude is eerily good at writing rules for itself - let it
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
- Always use existing components first - check `components/ui/` before creating new UI elements

### Tooling
- **Package manager**: `pnpm` (not npm/yarn)
- **Pre-build**: Always run `lint` + `type-check` before builds
- **Commit format**: `type: description` (e.g., `feat: add login`, `fix: timezone bug`)
  - Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`
- **Interactive prompts**: Use `AskUserQuestion` tool for lists, yes/no confirmations, and multi-choice decisions - provides a clean numbered UI that's faster than typing

### Safety Rules
- Never expose environment variables in code or logs
- Never run `rm -rf` without explicit user confirmation
- Never run destructive database commands (`DROP`, `TRUNCATE`, `db reset`)
- Secrets only in `.env.local` (never committed)

### Security (Non-Negotiable)
- **RLS on day one** - enable Row Level Security on all Supabase tables, test manually
- **Rate limiting** - start strict (100 req/hr/IP), loosen later
- **Sanitize inputs** - validate on backend, assume every input is malicious
- **CAPTCHA** - on registration, login, contact forms, password reset (invisible mode)
- **Review AI code** - don't blindly trust; let another AI or human review before merging

### Design
- Mobile-first responsive design - always optimize for phone use

---

## Frontend Design

Avoid generic "AI slop" aesthetics. Make distinctive frontends that surprise and delight.

### Typography
- Choose beautiful, unique fonts - avoid Inter, Roboto, Arial, system fonts
- Distinctive choices elevate the whole design

### Color & Theme
- Commit to a cohesive aesthetic, use CSS variables
- Dominant colors with sharp accents > timid, evenly-distributed palettes
- Draw from IDE themes and cultural aesthetics for inspiration
- Vary between light/dark themes - don't default to the same thing every time

### Motion
- Use animations for effects and micro-interactions
- Prioritize CSS-only solutions for HTML, Motion library for React
- One well-orchestrated page load with staggered reveals > scattered micro-interactions

### Backgrounds
- Create atmosphere and depth, not solid colors
- Layer CSS gradients, geometric patterns, contextual effects

### Avoid
- Overused fonts (Inter, Roboto, Space Grotesk, Arial)
- Clichéd color schemes (purple gradients on white)
- Predictable layouts and cookie-cutter patterns
- Safe, generic choices - think outside the box

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

### Plan Mode Rules
**Start most sessions in Plan mode (shift+tab twice).** Iterate on the plan until it's solid, then switch to auto-accept and Claude can usually 1-shot it.

- **Extreme concision** - sacrifice grammar for brevity. No fluff, no filler.
- **End with unresolved questions** - list anything blocking or unclear
- **Scannable format** - bullet points over paragraphs
- **When things go sideways** - stop pushing, switch back to plan mode, re-plan
- **Staff engineer review** - have a second Claude review the plan before implementing

The loop: **Plan → Implement → Test → Verify → Commit → Repeat**

### Task Tracking
- Check `tasks/` directory for task files to see outstanding work before starting

---

## Permissions

Use `/permissions` to pre-allow common safe commands and avoid approval prompts:
- git commands (status, diff, log, add, commit, push)
- pnpm/npm commands (install, run, test, build)
- gh CLI (pr, issue)
- Basic tools (ls, pwd, curl, jq)

Check `.claude/settings.json` for current allowlist.

---

## What NOT to Do

- Don't over-engineer tooling (no custom agent frameworks)
- Don't use excessive MCPs - they clutter context
- Don't write perfect prompts - iterate instead
- Don't review every line of generated code - focus on outcomes
- Don't wait for remote CI - run tests locally
