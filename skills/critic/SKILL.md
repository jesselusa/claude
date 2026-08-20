---
name: critic
description: Self-critique a draft against a voice-dna.md (and any other context files) via a sub-agent loop until it reads like you wrote it. Works on the last output, pasted text, a file, a page, or a URL.
argument-hint: [optional: file path, URL, or "last" to review the previous output]
---

# Critic: Self-Correct Drafts Against Your Voice

Goal: take a draft (the last assistant output, a file, a URL, or pasted text) and iterate it against a `voice-dna.md` until it reads like the user actually wrote it. Up to 3 rounds.

**Argument:** $ARGUMENTS is what to review. If empty or "last", review the most recent assistant output in this conversation. Otherwise treat as a file path, URL, or inline text.

## Setup: Find the voice file

Look for `voice-dna.md` in this order, use the first one found:

1. `./voice-dna.md` (current working directory, project-specific voice)
2. `./.claude/voice-dna.md`
3. `~/.claude/voice-dna.md` (global user voice)
4. Fall back to the template at `~/.claude/skills/critic/templates/voice-dna.md`

Also pull in any sibling context files next to the voice file (e.g., `tone.md`, `samples/`). These count as additional context for the Critic.

If no `voice-dna.md` exists anywhere and the user wants one, offer to copy the template to `~/.claude/voice-dna.md` and prompt them to paste writing samples at the bottom. Don't block; run with the template if they want to proceed.

## The loop

1. **Load the draft.** Resolve $ARGUMENTS: a file (Read), a URL (WebFetch), "last"/empty (the previous assistant output), or inline text.
2. **Load the voice file** and any sibling context.
3. **Spawn a Critic sub-agent** via the Agent tool (`subagent_type: "general-purpose"`, `model: "opus"`, since this is a judgment call). The sub-agent's only job: review the draft against the voice file and return a verdict + specific feedback.
4. **Revise** in the main session based on the feedback.
5. **Re-run the Critic** on the revision.
6. **Stop** when the Critic returns "Excellent" or after 3 rounds, whichever comes first. Show the final version.

## Critic sub-agent prompt (use this verbatim, filling in `<DRAFT>` and `<VOICE_FILE_CONTENTS>`)

```
You are a Critic. Your only job is to review the draft below against the voice rules and samples, and return specific, actionable feedback.

## Voice and context
<VOICE_FILE_CONTENTS>

## Draft to review
<DRAFT>

## What to check

### Voice match
- Does this read like the writing samples? Same rhythm, sentence length, formality?
- Any banned phrases present? Check every single one in the banned list.
- Does it use words and constructions the samples use?
- Would someone who knows this person recognize their voice?

### Substance
- Does it actually answer what was asked, or an adjacent version?
- Are claims specific and grounded, or vague and generic?
- Is anything padded or restated in different words to seem thorough?

### Final bar
- Would the user send, publish, or present this without editing?

## Output format

Rating: Needs Work | Good | Excellent

If below Excellent, list issues as a bulleted list. Each bullet must:
- Quote or point to the specific sentence/phrase
- Name the rule it violates (reference the voice file)
- Suggest a concrete fix

If Excellent, say so in one line and stop.

## Rules for you, the Critic
- Be specific. "Tone is off" is useless. "Paragraph 3 uses 'Furthermore' which is banned, and structure is more formal than any sample" is useful.
- Reference the actual voice file rules, not general writing standards.
- Don't over-polish. Natural voice includes hedging, casual language, imperfections. That's a feature.
- Max 3 rounds total across the session.
```

## Rules

- Always use `model: "opus"` for the Critic sub-agent (per CLAUDE.md routing).
- Cap at 3 rounds. If still not Excellent after round 3, return the best version with a short note on what's still off.
- Don't modify the voice file. If the user wants to edit it, point them at its path.
- If the draft is a URL or web page, fetch the main content only, skipping nav/footer/boilerplate.
- Show each round's verdict + top 3 issues so the user sees the progression. Keep it tight.
