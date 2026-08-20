# CLAUDE.md

Rules Claude follows. Every line must pass two tests: **can Claude act on it**, and
**would Claude do something different without it**. Anything a current model already
does by default is noise: it costs context and dilutes the rules that matter.

Structure, install commands, and skill tables belong in README.md.

---

## Session

- `git pull`, then `/git-cleanup` if the session-start hook reports stale branches
- Check `tasks/` for outstanding work
- **Feature branches always.** On main when asked to commit, ask for a branch name first
- Run `/techdebt` before committing. Run `/learn` only if the session produced an actual
  rule: a mistake a rule would have caught, or a correction from Jesse about how to work

---

## Automated by hooks (don't duplicate)

Global hooks in `~/.claude/settings.json` already enforce:
- Block `rm -rf`, destructive DB, `npm`/`yarn install`, `git add .env*`, commits on main,
  force-push to main
- Pre-commit `pnpm lint` + `pnpm type-check` in pnpm projects
- Require explicit `model` param on Agent calls
- SessionStart: branch, task, and merged-branch warnings

Don't run lint/type-check manually before commit. If a hook blocks you, surface the
message and fix the cause; never `--no-verify`.

---

## Subagents

Pass an explicit `model` on every Agent call (a hook requires it). Finding and doing goes to
`sonnet`. Deciding and reviewing goes to `opus`. Never `haiku` for code work.

---

## Writing

Applies to everything Claude writes under Jesse's name: commit messages, PR bodies,
docs, and chat. Full rules in `profile/voice-dna.md` (symlinked to
`~/.claude/voice-dna.md`); this is the enforceable summary.

- **No em dashes. Ever.** Period, comma, colon, semicolon, or parens instead
- **Never negate-then-assert.** "This isn't X, it's Y" / "Not X. Y." State the
  positive claim directly. One instance fails the output
- No validation openers ("Great question", "Good catch"), no meta-narration
  ("Let me...", "I'll now..."), no setup phrases ("Here's the X", "Below is Y"),
  no closing filler ("Let me know if...", "Hope this helps")
- No chained sentence fragments in prose. Fine in bullets and headlines
- Contractions always. Numbers as digits. Short paragraphs, 1-3 sentences
- Cut on sight: load-bearing, thoughtful, comprehensive, robust, seamless,
  leverage (verb), delve, ensure, facilitate, unlock, empower, game-changer,
  "it's important to note". Full table in `voice-dna.md`
- Be specific over thorough. A concrete number beats a hedged summary

Arc's *product* voice is a different file (`arc-master/shared/brand/voice-dna.md`)
and governs user-facing copy. It extends these rules; it doesn't replace them.

---

## Tooling

- **pnpm**, not npm or yarn
- Commits: `type: description` (`feat`, `fix`, `refactor`, `docs`, `test`, `chore`)
- PRs: always `--assignee @me`
- Before opening a PR: `gh pr list --head <branch>`. Don't duplicate or push to a
  merged branch
- **Asking questions: always `AskUserQuestion`**, never options as plain text.
  Non-negotiable. Load via ToolSearch if needed

---

## Code

- Tabs. Concise, no boilerplate. Comments only where the logic isn't self-evident
- Check `components/ui/` before building a new component; reuse one shared component for
  repeated patterns (close buttons, modals, icons) rather than one-off variants
- Promote a new reusable pattern to the shared layer once it has a second caller
- Give immediate visual feedback on user actions: update or clear stale UI at once;
  don't wait on background work
- Tests **after** implementation, not before. No TDD

---

## Database migrations

- **Never `supabase db push` without reading `supabase migration list` first.** Push
  applies every pending local migration, not just the one you wrote
- **Write every migration idempotently**: `create table if not exists`,
  `create or replace view`, `drop policy if exists` before `create policy`,
  `cron.unschedule` before `cron.schedule`. Drift makes a re-run likely, and a re-run
  should be harmless
- **Applying SQL out-of-band puts you in debt.** The dashboard and the Supabase MCP
  stamp their own timestamps. Commit the same SQL as a migration file and repair the
  ledger in the same sitting, or the two histories silently diverge

---

## Recurring audits and routines

- **One writer per file.** Before a routine files a finding, it reads the open PRs and
  the resolved/completed section of the log it writes to. Two routines that both find
  and both fix will collide on whatever lands second
- **Log resolutions, not just findings.** The completed section is the only thing that
  stops the next sweep re-finding a fixed item. When resolving a merge conflict between
  two audit logs, union them and verify the union. A dropped completed entry comes back
  as a duplicate later
- **Name conflict-resolution branches `resolve/`.** Scratch branches like `pr-235-b` are
  indistinguishable from real work a month later
- **Cut a branch only when you have a commit for it.** Empty dated branches block
  date-guarded routines from ever running again

---

## Safety

- Never expose env vars in code or logs. Secrets only in `.env.local`, never committed
- Never `rm -rf`, `DROP`, `TRUNCATE`, or `db reset` without explicit confirmation
- **Never paste a live secret into chat.** Read it from the env file, or have Jesse set
  it directly. A key pasted into a prompt is on disk in the transcript and has to be
  rotated

---

## Security (non-negotiable)

- RLS on day one for every Supabase table
- Rate limiting: 100 req/hr/IP to start, loosen later
- Sanitize inputs on the backend; assume every input is malicious
- Invisible CAPTCHA on registration, login, contact, password reset
- Review AI-generated code before merging

---

## Design

Mobile-first. Design skills (`ui-ux-pro-max`, `frontend-design`, `ui-animation`,
`web-design-guidelines`, `shadcn`) auto-trigger and carry their own rules.

**Never**: Inter/Roboto/Arial, purple-gradient AI clichés, emojis as icons.
**Always**: 4.5:1 contrast (WCAG AA), respect `prefers-reduced-motion`.

Run `/design-inspo` before starting UI to pick 2-3 taste references. Anchors, not
sources to copy tokens from.

---

## Shipping

- Verify with data. A shipped feature isn't an adopted one. Confirm real usage before
  calling it a win
- Complex or ambiguous features: `@workflows/create-prd.md` (plan, tasks, implement,
  verify, commit)

---

## Updating this file

Suggest an update when you made a mistake a rule would have prevented, or found a
pattern worth codifying. Before adding, check that the model doesn't already do it by
default. If it does, the rule is noise. Verbose guidance wastes tokens.
