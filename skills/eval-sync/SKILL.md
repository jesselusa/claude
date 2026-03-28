---
name: eval-sync
description: Review outcomes of past CLAUDE.md sync PRs, score decisions, surface patterns, and propose instruction improvements
---

# Eval: CLAUDE.md Sync

Review past sync decisions against actual PR outcomes (merged vs closed) and improve the sync agent's filtering rules.

## Steps

### 1. Load decision log

Read `evals/claude-md-sync/decisions.jsonl`. Parse all entries.

### 2. Fetch outcomes for unresolved entries

For each entry where `outcome` is `null`:
- Check the GitHub PR status via `mcp__github__pull_request_read`
- If merged: set `outcome: "merged"`, record `outcome_date`
- If closed (not merged): set `outcome: "closed"`, record `outcome_date`
- If still open: leave as `null`, skip scoring for this entry

Write updated entries back to `decisions.jsonl`.

### 3. Score resolved entries

- **True positive**: outcome = `merged` (rule was correctly included)
- **False positive**: outcome = `closed` (rule should not have been included)

Calculate:
- Total PRs: X
- Merged (true positive): Y
- Closed (false positive): Z
- Precision: Y / (Y + Z)

### 4. Calibration analysis

Compare LLM self-assessments against actual outcomes:

- **Overconfident**: LLM predicted `will_merge` but user closed the PR
- **Underconfident**: LLM predicted `unsure` but user merged the PR
- **Correct confident**: LLM predicted `will_merge` and user merged
- **Correct cautious**: LLM predicted `unsure` and user closed

Calculate:
- Overconfidence rate: overconfident / total predictions
- Underconfidence rate: underconfident / total predictions
- Overall calibration accuracy: (correct confident + correct cautious) / total

Note: Entries from before the self-assessment system (no `llm_prediction` field) are excluded from calibration metrics but still count toward precision.

### 5. Analyze false positives

For each closed PR, identify why it was wrong. Group patterns:
- Was it an incremental sub-bullet addition?
- Was it a design aesthetic rule for a locked design system?
- Was it a rule already covered differently in the project?
- Was the LLM overconfident (predicted `will_merge`)?
- Other?

### 6. Present findings and propose instruction updates

Show the user:
- Precision score
- Calibration accuracy
- Overconfidence/underconfidence breakdown
- False positive breakdown by pattern
- Proposed additions or changes to the CRITICAL FILTER in `skills/sync-claude-md/SKILL.md`

Use `AskUserQuestion` to confirm each proposed change before applying it.

### 7. Apply approved changes

Edit `skills/sync-claude-md/SKILL.md` with approved filter updates.

Commit and push to a branch, open a PR to `jesselusa/claude`.

### 8. Summary

```
## Eval Results — YYYY-MM-DD

- PRs scored: X
- Precision: Y%
- Calibration accuracy: Z%
- Overconfident predictions: N
- False positives: M
- Filter updates applied: K
```
