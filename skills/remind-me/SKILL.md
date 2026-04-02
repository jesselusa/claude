---
name: remind-me
description: Show what's been built, what's left, and what to work on next — works across any project
argument-hint: [focus-area]
---

# Remind Me — Where Did I Leave Off?

Audit the project state and produce a concise status report. This is for when you're picking the project back up after a break.

**Argument:** $ARGUMENTS (optional focus area like "payments", "coaching", "UI")

## Steps

1. **Read CLAUDE.md** to understand the project structure and conventions
2. **Check tasks/** directory for outstanding work, PRDs, or plans
3. **Check git history** — `git log --oneline -20` to see recent work
4. **Scan the codebase** — identify what's built by looking at the project structure
5. **Cross-reference** tasks/plans against what exists in the codebase

## Output Format

Produce a report with these sections:

### What's Done
Bullet list of completed features with confidence level. Only mark something as done if the code exists AND is wired to real data.

### What's In Progress
Anything partially built — UI exists but not wired, tables exist but no queries, etc.

### What's Left (by priority)
Group remaining work into:
- **Core (ship-blocking)** — features needed before the app is usable
- **Paid tier** — features behind the subscription
- **Growth** — nice-to-haves, marketing, content

### Suggested Next Step
Based on what's closest to done or most impactful, suggest 1-2 things to work on next.

## Rules
- Be honest about what's actually working vs what's just scaffolded
- If `$ARGUMENTS` specifies a focus area, zoom into that area specifically
- Keep the output scannable — no walls of text
- Adapt to whatever project type you're in (Next.js, SwiftUI, etc.)
