# Sync Eval Rubric

## Scoring

- **True positive**: PR was merged — rule was correctly identified as universal and relevant
- **False positive**: PR was closed — rule should have been filtered out
- **Precision** = merged / (merged + closed)

## Calibration Metrics

- **Overconfidence rate** = (predicted `will_merge` but closed) / total predictions
- **Underconfidence rate** = (predicted `unsure` but merged) / total predictions
- **Calibration accuracy** = (correct predictions) / total predictions

## Known false-positive patterns

| Pattern | Example | Rule |
|---------|---------|------|
| Incremental sub-bullet | Adding step 5 to an already 4-step Social Sharing list | Skip if it only appends to an already-detailed subsection |
| Design aesthetic on locked system | "Draw from IDE themes" added to PokeCRM (has fixed Pokemon themes) or Arc (monochrome token system) | Skip design aesthetic/inspiration rules when project has a defined visual identity |
| Generic design opinion on flexible project | Single color tip added to LLL's Color & Theme list | Skip if the concept is already covered and this is a minor stylistic elaboration |

## What makes a good sync

- The rule is a direct behavioral instruction for Claude (tool usage, confirmation behavior, session habits)
- The rule introduces a concept entirely absent from the target repo
- The rule applies regardless of the project's stack, scale, or visual aesthetic
