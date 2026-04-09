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
| `/sync-starter` | Sync content between projects and starter template |
| `/commit-pr` | Lint → typecheck → commit → push → create PR on feature branch |
| `/tasks` | View and update outstanding tasks in the tasks/ directory |
| `/session-end` | End-of-session wrapper: runs /techdebt → /learn → /git-cleanup in sequence |
| `/setup-integration` | Scaffold third-party service setup (Stripe, Notion, Twilio, Cloudinary, Supabase) |
| `/security-patch` | Check dependabot alerts across all repos, auto-patch, create PRs |
| `/sync-claude-md` | Sync universal rules from global CLAUDE.md to all project repos, create PRs |
| `/eval-sync` | Score past sync decisions against PR outcomes, surface patterns, improve filters |
| `/remind-me` | Show what's been built, what's left, and what to work on next |

---

## Before You Work

At the start of every session:
1. Run `git pull` to ensure you have the latest code
2. Run `/git-cleanup` to prune branches from merged PRs
3. Check `tasks/` directory for outstanding work

---

## Working Style

### Build for Model Trajectory
Don't over-scaffold AI integrations. Models improve monthly — keep wrappers thin and replaceable. Build for where models are going, not where they are.

### Speed > Perfection
Prototype in real code, iterate there. Don't spend time on elaborate mocks/wireframes when you can build and polish live.

### Demand Clarity Before Building
Ruthless specificity in prompts/specs > technical knowledge. Garbage in = garbage faster with AI. Push back on vague requirements before writing code.

### Act Confidently
Make changes without excessive confirmation. Git provides safety - work can always be reverted with `git checkout .`

### Parallel Work
When tasks are independent (don't touch same files), use parallel agents:
- Frontend + backend simultaneously
- Tests + implementation in separate contexts

### Stay Focused
Focus on one concern per task. If asked about unrelated work, suggest starting a fresh context.

### Always Use Feature Branches
Never commit directly to main. If already on main when asked to commit, create a feature branch first and ask for a name.

### End-of-Session Checklist
Before signing off, always run `/techdebt` → `/learn` → `/git-cleanup` in that order. Proactively offer this at the end of every session.

### Multi-Repo Awareness
When cleaning up branches, default to checking all 5 repos: pokecrm, little-language-labs, palette, jesselusa.com, arc — unless a specific repo is specified.

### Proactively Share Session Learnings
At the end of every session, volunteer what you learned and ask if it should go into CLAUDE.md before the user has to ask.

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
6. **Check PR/branch status** - before creating or updating a PR, run `gh pr list --head <branch>` to check if a PR already exists and whether it's been merged. Don't create duplicate PRs or push to merged branches.
7. **Commit to feature branch** - always commit to a feature branch, then create a PR to merge

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

**After creating a skill:** Update both the skills table in CLAUDE.md and README.md. Then re-run the symlink command so the new skill is immediately available:
```bash
for skill in ~/Documents/GitHub/claude/skills/*/; do ln -sf "$skill" ~/.claude/skills/; done
```

**When adding Python scripts:** Immediately add `__pycache__/` (or the script directory's cache path) to `.gitignore` before running the script for the first time, to avoid accidentally committing bytecode.

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

- Reuse a single shared component for repeated UI patterns (close buttons, modals, icons) across all screens — never create one-off variants.

- Before creating new UI components or patterns, search for and reuse existing shared components in the project first

- When introducing a new reusable pattern not already in the project's shared components, add it back to the shared layer after implementation

- Provide immediate visual feedback after user actions — update or remove stale UI elements instantly without waiting for background processes

- Maintain consistent UI patterns across similar component types (drawers, modals, detail panels) within the same application
### Tooling
- **Package manager**: `pnpm` (not npm/yarn)
- **Pre-build**: Always run `lint` + `type-check` before builds
- **Commit format**: `type: description` (e.g., `feat: add login`, `fix: timezone bug`)
  - Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`
- **PR creation**: Always use `--assignee @me` when creating PRs with `gh pr create`
- **Asking questions**: ALWAYS use the `AskUserQuestion` tool when asking the user anything with options — never list options as plain text. This applies to confirmations, multi-choice decisions, preference questions, and any prompt where the user picks from choices. This is non-negotiable — do not ask questions by writing numbered or bulleted lists in text. Load the tool via ToolSearch if needed and use it every time.

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

Avoid generic "AI slop" aesthetics. Make distinctive frontends that surprise and delight. Root design in actual user needs, not surface-level aesthetics.

### Design System First
Before building UI, generate a tailored design system for the project:
- Define pattern (hero-centric, dashboard, editorial, etc.) based on product type
- Pick a cohesive style (soft UI, brutalist, minimalist, etc.) matched to the brand
- Set colors with clear roles: primary, secondary, CTA, background, text
- Choose font pairing with mood alignment (elegant, technical, playful, etc.)
- Define key effects (shadows, transitions, hover states)
- List anti-patterns to avoid for this specific project

### Typography
- Choose beautiful, unique fonts - avoid Inter, Roboto, Arial, system fonts
- Distinctive choices elevate the whole design
- Pair fonts intentionally (display + body) with mood alignment

### Color & Theme
- Commit to a cohesive aesthetic, use CSS variables
- Dominant colors with sharp accents > timid, evenly-distributed palettes
- Draw from IDE themes and cultural aesthetics for inspiration
- Vary between light/dark themes - don't default to the same thing every time
- Ensure light mode text contrast 4.5:1 minimum (WCAG AA)

### Motion
- Use animations for effects and micro-interactions
- Prioritize CSS-only solutions for HTML, Motion library for React
- One well-orchestrated page load with staggered reveals > scattered micro-interactions
- Smooth transitions (150-300ms) on all interactive elements
- Respect `prefers-reduced-motion` always

### Backgrounds
- Create atmosphere and depth, not solid colors
- Layer CSS gradients, geometric patterns, contextual effects

### Pre-Delivery Checklist
Before shipping any UI:
- [ ] No emojis as icons (use SVG: Heroicons/Lucide)
- [ ] `cursor-pointer` on all clickable elements
- [ ] Hover states with smooth transitions (150-300ms)
- [ ] Focus states visible for keyboard navigation
- [ ] `prefers-reduced-motion` respected
- [ ] Responsive: 375px, 768px, 1024px, 1440px tested

### Avoid
- Overused fonts (Inter, Roboto, Space Grotesk, Arial)
- Clichéd color schemes (purple gradients on white, "AI purple/pink gradients")
- Predictable layouts and cookie-cutter patterns
- Safe, generic choices - think outside the box
- Emojis as functional icons
- Harsh/jarring animations

### Installed Design Skills
These auto-trigger on frontend tasks — no manual invocation needed:
- **ui-ux-pro-max** — UX strategy + design system generator (161 product types, 84 styles)
- **taste-skill** (7 sub-skills) — premium design quality, brutalist/minimalist styles, full output enforcement
- **ui-animation** — motion/animation guidelines (CSS, framer-motion, springs)
- **web-design-guidelines** — 100+ web design principles from Vercel team
- **frontend-design** / **shadcn** — already installed via plugins

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
