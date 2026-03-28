# CLAUDE.md Sync Evals

Tracks the accuracy of the `sync-claude-md` skill's filtering decisions using a two-layer scoring system.

## How it works

### Layer 1: LLM Self-Assessment
When the sync agent creates a PR, it predicts for each rule whether the PR will be merged (`will_merge`) or is borderline (`unsure`), along with reasoning.

### Layer 2: User Ground Truth
The user merges or closes the PR. This is the actual signal.

### Calibration
By comparing LLM predictions to user decisions, we identify:
- **Overconfidence**: LLM said `will_merge` but user closed → filter needs tightening
- **Underconfidence**: LLM said `unsure` but user merged → filter may be too strict
- **Precision**: merged / (merged + closed) — overall quality of sync decisions

## Files

- `decisions.jsonl` — append-only log of every sync PR, one JSON object per line
- `rubric.md` — scoring criteria, calibration metrics, and known false-positive patterns
- `weekly-reports.md` — auto-generated weekly calibration summaries (from scheduled trigger)

## Running an eval

In Claude Code:
```
/eval-sync
```

This runs interactively — fetches outcomes, scores, and proposes filter improvements with your approval.

The daily sync trigger also runs a non-interactive scoring pass (Phase 2) to keep outcomes up to date.

Recommended deep-dive: after every 10–15 sync PRs, or whenever precision feels low.
