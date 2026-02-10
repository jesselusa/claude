# CLAUDE.md

This file contains instructions Claude follows. Every section should pass the test: "Can Claude act on this?"

User-facing tips (how to prompt, workflow advice, productivity tips) belong in README.md, not here.

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
| `/learn` | Review session and suggest CLAUDE.md updates |
| `/create-new-project` | Scaffold new project with templates, optional PRD & GitHub |
| `/create-readme` | Generate README.md and LICENSE |
| `/gitignore` | Generate .gitignore by project type |
| `/git-cleanup` | Prune stale refs and delete merged local branches |
| `/kill-ports` | Find and kill processes on TCP ports |
| `/robots` | Generate robots.txt with AI/SEO blocking |
| `/sync-starter` | Sync improvements back to this starter template |

---

## Before You Work

At the start of every session:
1. Run `git pull` to ensure you have the latest code
2. Run `/git-cleanup` to prune branches from merged PRs
3. Check `tasks/` directory for outstanding work

---

## Working Style

### Act Confidently
Make changes without excessive confirmation. Git provides safety - work can always be reverted with `git checkout .`

### Parallel Work
When tasks are independent (don't touch same files), use parallel agents:
- Frontend + backend simultaneously
- Tests + implementation in separate contexts

### Stay Focused
Focus on one concern per task. If asked about unrelated work, suggest starting a fresh context.

---

## Testing Approach

### Write Tests After Implementation
Don't use TDD. Implement first, then write tests immediately after in the same context while you have full understanding of what was built.

### Self-Verification (Critical)
After every change:
- Run tests, lint, type-check
- For UI: verify in browser, check mobile, confirm no console errors
- Don't declare done until verification passes
- If verification fails: fix → re-verify → repeat until green

---

## Before Committing

1. **Clean** - run `/techdebt` to remove dead code, debug statements, duplicates
2. **Verify** - tests, lint, type-check pass
3. **Update tasks** - mark completed `[x]` in `tasks/`, add new tasks discovered
4. **Update docs** if you changed:
   - Data model → update schema docs or comments
   - API/structure → update README
   - Patterns/preferences → update CLAUDE.md
5. **Teach Claude** - review the session for lessons learned (mistakes, improvements, patterns). Ask the user if they want them added to CLAUDE.md
6. **Commit to feature branch** - always commit to a feature branch, then create a PR to merge

---

## Creating New Skills

When creating skills, use this structure:

```
skill-name/
├── SKILL.md          # Required: skill definition
├── *.sh              # Optional: supporting scripts
└── templates/        # Optional: template files
```

**Location:** `skills/<name>/SKILL.md` - Claude Code finds them automatically after symlinking to `~/.claude/skills/`

**After creating a skill:** Update both the skills table in CLAUDE.md and README.md.

---

## Updating This File

You have permission to suggest updates to CLAUDE.md when:
- You make a mistake that could be prevented by a rule
- You discover a pattern that should be codified
- Existing guidance is outdated or redundant

Keep instructions concise - verbose guidance wastes tokens.

---

## Personal Preferences

### Languages & Stack
- **Primary**: TypeScript/JavaScript, Python
- **Frontend**: Next.js (App Router) with React
- **Styling**: Tailwind CSS + ShadCN UI
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
- **PR creation**: Always use `--assignee @me` when creating PRs with `gh pr create`
- **Asking questions**: ALWAYS use the `AskUserQuestion` tool when asking the user anything with options — never list options as plain text. This applies to confirmations, multi-choice decisions, preference questions, and any prompt where the user picks from choices

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

### Social Sharing & Metadata (Next.js)

When building Next.js apps, always implement proper social sharing:

1. **Create `opengraph-image.tsx`** - Dynamic 1200x630 PNG for share previews (WhatsApp, Twitter, iMessage). SVG won't work - must be raster.
2. **Create `icon.tsx` and `apple-icon.tsx`** - Dynamic favicons with rounded corners (20% radius). Avoids separate image files.
3. **Add metadata to `layout.tsx`** - Include `openGraph` and `twitter` objects for full social metadata.
4. **Test** by visiting `/opengraph-image`, `/icon`, `/apple-icon` directly in dev.
5. **Debug caching** - WhatsApp aggressively caches. Use Facebook's debug tool: https://developers.facebook.com/tools/debug/

---

## Development Workflow

### For Simple Tasks
Skip planning. Just implement obvious features directly.

### For Complex or Ambiguous Features

Follow the PRD workflow in `@workflows/create-prd.md`:

1. **Plan** - Create PRD with clarifying questions, generate tasks
2. **Implement** - Work through tasks incrementally
3. **Test** - Write tests, run full test suite
4. **Verify** - Staff engineer review: Is this over-engineered? Under-engineered?
5. **Commit** - Only after verification passes

### Plan Mode Rules

When in plan mode:
- **Extreme concision** - bullet points, no fluff
- **End with unresolved questions** - list anything blocking or unclear
- **Scannable format** - bullet points over paragraphs

When things go sideways, stop pushing - switch back to plan mode and re-plan.

### Branch Cleanup After PRs

After merging PRs:
1. GitHub auto-deletes remote branches on merge (if enabled in repo settings)
2. Run `git fetch --prune` to remove stale remote refs locally
3. Switch to main: `git checkout main && git pull`
4. Delete local feature branch: `git branch -d <branch-name>`

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
- Don't wait for remote CI - run tests locally
- Don't add features beyond what was asked
- Don't create abstractions for one-time operations
