---
name: learn
description: Review the session and suggest CLAUDE.md updates based on what was learned
argument-hint: [--dry-run]
---

# Learn from Session

Review the current session context and suggest updates to the project's CLAUDE.md based on patterns, mistakes, preferences, and decisions discovered during work.

**Argument:** $ARGUMENTS

**Modifiers:**
- `--dry-run` or `-n`: Show suggestions without modifying anything

## What to Extract

Scan the session for:

1. **Mistakes that could be prevented** — errors that a CLAUDE.md rule would catch next time
2. **Workflow patterns** — repeated approaches that should be codified
3. **Tool/library preferences** — choices made about tools, libraries, or configurations
4. **Code style decisions** — formatting, naming, or structural patterns chosen
5. **Project-specific conventions** — architecture decisions, file organization, naming schemes
6. **Safety lessons** — things that broke or almost broke that need guardrails

## What NOT to Extract

- One-off debugging steps
- Session-specific context (current task details, temporary state)
- Information already in CLAUDE.md
- Speculative conclusions from a single incident (unless clearly universal)

## Execution Steps

### 1. Read the Project's CLAUDE.md

```bash
cat ./CLAUDE.md
```

If no CLAUDE.md exists, note that one should be created and proceed with suggestions.

### 2. Review Session Context

Analyze the full conversation history for learnings. For each potential learning, categorize it:

- **Workflow** — how to work with the codebase
- **Style** — code formatting and conventions
- **Stack** — tools, libraries, dependencies
- **Safety** — security and safety rules
- **Testing** — testing approaches
- **Design** — UI/UX decisions
- **Project** — project-specific conventions

### 3. Present Each Learning Individually

For EACH potential learning found, use `AskUserQuestion` to confirm. Present 1-2 learnings per question to keep decisions focused.

Format each learning as the exact text that would be added to CLAUDE.md.

Options for each:
- "Add to CLAUDE.md" — apply the change
- "Skip" — don't add this one
- "Edit first" — user provides modified version

### 4. Apply Approved Changes

For each approved learning:
1. Determine which section of CLAUDE.md it belongs in (or create a new section if needed)
2. Add the content using the Edit tool
3. Keep the same tone and formatting as existing CLAUDE.md content

If `--dry-run` was specified, show the final diff but don't write changes.

### 5. Summary

After all learnings are reviewed:

```
## Session Learnings

### Added to CLAUDE.md
- [list each added item with its category]

### Skipped
- [list skipped items]

### Stats
- Learnings found: X
- Added: Y
- Skipped: Z
```

## Guidelines

- Keep suggestions concise — match the tone of the existing CLAUDE.md
- Don't suggest things that are obvious or already standard practice
- Prefer actionable instructions ("Always do X") over observations ("X is important")
- Group related learnings when presenting to the user
- If the same lesson applies to multiple projects, mention that it might also belong in the global CLAUDE.md
