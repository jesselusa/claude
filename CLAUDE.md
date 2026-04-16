# CLAUDE.md

Instructions Claude follows. Every section must pass the test: **"Can Claude act on this?"**
Structure, install commands, skill tables, and workflow tips belong in README.md, not here.

---

## Before You Work

At the start of every session:
1. `git pull`
2. `/git-cleanup` to prune branches from merged PRs
3. Check `tasks/` for outstanding work

---

## Working Style

- **Build for model trajectory** — keep AI wrappers thin; models improve monthly
- **Speed > perfection** — prototype in real code; no elaborate mocks
- **Demand clarity before building** — push back on vague requirements; specificity > knowledge
- **Act confidently** — git provides safety; changes can be reverted
- **Parallel work** — independent tasks = parallel agents. Create shared infra first, parallelize second, consolidate after
- **Stay focused** — one concern per task; fresh context for unrelated work
- **Always use feature branches** — if on main when asked to commit, ask for a branch name first
- **End-of-session** — always run `/techdebt` → `/learn` → `/git-cleanup` in that order
- **Multi-repo awareness** — when cleaning branches, default to checking all 6: `arc`, `arc-ios`, `pokecrm`, `little-language-labs`, `palette`, `jesselusa.com`
- **Proactively share learnings** — at session end, volunteer what you learned and ask if it should go in CLAUDE.md

---

## Model Routing (subagents)

Main session stays on Opus. When spawning subagents via the Agent tool, **always pass an explicit `model` param**:

- **`sonnet`** — execution, search, mechanical work. `Explore`, `pr-comment-resolver`, `bug-reproduction-validator`, `framework-docs-researcher`, `git-history-analyzer`, most research agents, bulk refactors.
- **`opus`** — reasoning, planning, review. `Plan`, `architecture-strategist`, `kieran-*-reviewer`, `dhh-rails-reviewer`, `spec-flow-analyzer`, `performance-oracle`, `security-sentinel`.
- **Never `haiku`** for code work.

Finding/doing → sonnet. Deciding/reviewing → opus. When unsure, default to sonnet.

---

## Automated by Hooks (don't duplicate)

Global hooks in `~/.claude/settings.json` already enforce:
- Block `rm -rf`, destructive DB, `npm`/`yarn install`, `git add .env*`, commits on main, force-push to main
- Pre-commit `pnpm lint` + `pnpm type-check` in pnpm projects
- Require explicit `model` param on Agent calls
- Auto-resymlink skills after editing `skills/*`
- SessionStart: branch, task, merged-branch warnings
- Doc-drift: warn on `git commit` in this repo if new skill/hook/template is staged without the corresponding doc update

Don't manually run lint/type-check before commit — the hook does it. If a hook blocks you, surface the message and fix the underlying issue; never bypass with `--no-verify`.

---

## Testing Approach

- Write tests **after** implementation, not before (no TDD)
- After every change: tests + lint + type-check
- For UI: verify in browser + mobile, confirm no console errors
- Don't declare done until verification passes

---

## Before Committing

1. `/techdebt` — remove dead code, debug statements, duplicates
2. Run tests (lint + type-check handled by hook)
3. Update `tasks/` — mark `[x]`, add new discovered
4. Update docs if you changed: data model, API/structure, or patterns/preferences
5. `gh pr list --head <branch>` before creating a PR — don't duplicate or push to merged branches
6. Commit to feature branch → create PR with `--assignee @me`

---

## Personal Preferences

### Stack
TypeScript/JavaScript + Python · Next.js (App Router) · Tailwind + ShadCN · Supabase · Vercel

### Code Style
- Concise, minimal, no unnecessary boilerplate
- Comments only when logic isn't self-evident
- Tabs for indentation
- Check `components/ui/` before creating new components
- Reuse a single shared component for repeated UI patterns (close buttons, modals, icons) — never one-off variants
- When introducing a new reusable pattern, promote it to the shared layer after implementation
- Provide immediate visual feedback after user actions — update or remove stale UI elements instantly, don't wait for background work
- Maintain consistent UI patterns across similar component types (drawers, modals, detail panels) within the same app

- Persist user-entered form data locally so it survives failed API calls and retries — never require the user to retype input after a failure.
### Tooling
- Package manager: **pnpm** (not npm/yarn)
- Commit format: `type: description` — `feat`, `fix`, `refactor`, `docs`, `test`, `chore`
- PR creation: always `--assignee @me`
- **Asking questions**: always use `AskUserQuestion` — never list options as plain text. Non-negotiable. Load via ToolSearch if needed.

### Safety
- Never expose env vars in code or logs
- Secrets only in `.env.local` (never committed)
- Never run `rm -rf`, `DROP`, `TRUNCATE`, or `db reset` without explicit confirmation

### Security (non-negotiable)
- RLS on day one for all Supabase tables
- Rate limiting: 100 req/hr/IP strict, loosen later
- Sanitize inputs on backend; assume every input is malicious
- CAPTCHA on registration/login/contact/password-reset (invisible mode)
- Review AI-generated code before merging

### Design
- Mobile-first

---

## Frontend Design

Installed design skills (`ui-ux-pro-max`, `frontend-design`, `taste-skill`, `ui-animation`, `web-design-guidelines`, `shadcn`) auto-trigger on frontend tasks and enforce quality — don't duplicate their rules here.

Before starting UI, run `/design-inspo` to pick 2–3 taste references (never copy tokens from reference systems; use them as anchors).

**Avoid**: Inter/Roboto/Arial, purple-gradient AI clichés, emojis as icons, cookie-cutter layouts. **Always**: 4.5:1 contrast (WCAG AA), respect `prefers-reduced-motion`.

---

## Development Workflow

- **Simple tasks** — skip planning, just implement
- **Complex/ambiguous features** — follow `@workflows/create-prd.md` (plan → tasks → implement → verify → commit)
- **Plan mode** — extreme concision, bullets over paragraphs, end with unresolved questions. Switch back to plan mode when things go sideways.

---

## What NOT to Do

- Don't over-engineer tooling (no custom agent frameworks)
- Don't use excessive MCPs — they clutter context
- Don't wait for remote CI — run tests locally
- Don't add features beyond what was asked
- Don't create abstractions for one-time operations

---

## Updating This File

You have permission to suggest updates when you made a mistake a rule would have prevented, or found a pattern worth codifying. Keep it concise — verbose guidance wastes tokens.
