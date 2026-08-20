# Learnings inbox

Queue for candidate **global** rules. `/learn` appends here instead of writing a
universal rule into a project's CLAUDE.md; `/daily-learnings` drains it on its next run.

Why the queue exists: three routines could write instruction rules, and a universal rule
written by `/learn` would arrive in the same repo a second time when `/sync-claude-md`
pushed the global copy down. One author for global rules, one for project rules.

Format, one bullet each:

```
- [YYYY-MM-DD] [repo] the rule, phrased as an instruction — why it's needed
```

`/daily-learnings` deletes a line in the same commit that promotes or rejects it. A line
left here gets re-proposed tomorrow.

---

## Queued

_(empty)_
