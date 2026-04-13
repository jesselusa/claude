---
name: design-inspo
description: Pick 2-3 design systems from awesome-design-systems as taste references before building UI — inspiration only, not copying
argument-hint: [what you're building]
---

# Design Inspo — Anchor New UI To Real Taste References

Goal: before designing a new UI, pick 1-3 real-world design systems to use as **taste references**. We are NOT copying tokens, components, or design language. We're anchoring aesthetic decisions (mood, density, motion, type feel) to something that exists in the world, so the result doesn't drift into generic AI-flavored UI.

**Argument:** $ARGUMENTS — what the user is building (e.g., "a minimal finance dashboard", "a playful pet app landing page")

## Steps

1. **Clarify the brief** — if $ARGUMENTS is vague or empty, use the `AskUserQuestion` tool to ask:
   - What are you building? (product type / page)
   - What mood? (e.g., serious/editorial, playful, utilitarian, luxury, technical)
   - Any brands whose feel you already like?

2. **Suggest 2-3 reference systems** from the awesome-design-systems list (https://github.com/alexpate/awesome-design-systems). Pick based on mood fit, not popularity. Examples of good anchoring:
   - Luxury / editorial → Apple HIG, Arc (Browser), Airbnb DLS
   - Utilitarian / data-dense → IBM Carbon, Atlassian, GitLab Pajamas
   - Playful / consumer → Shopify Polaris, Duolingo, Mailchimp
   - Technical / developer → Stripe, Linear, Vercel Geist
   - Warm / content → Medium, Spotify Encore, WordPress

   Use `AskUserQuestion` to let the user pick 1-3 (or override with their own).

3. **Pull live context** on the chosen systems. For each, use `WebFetch` against the system's public site (not the awesome-design-systems repo itself) to capture:
   - Color palette philosophy (what do they do with color?)
   - Type system feel (what's the personality?)
   - Motion / interaction character
   - What makes it distinctive — one sentence

4. **Output a short "Taste Brief"** — this is the actual artifact. Keep it tight, ~150 words total:

   ```
   ## Taste Brief: <what they're building>

   Anchoring to: <System A> + <System B> (+ optional C)

   **Why these:** one sentence on the mood these combine into.

   **Borrow (as inspo, not copy):**
   - From <A>: <one specific quality — e.g., "restrained color, type does the work">
   - From <B>: <one specific quality — e.g., "tactile hover states, subtle depth">

   **Avoid:** 2-3 anti-patterns for this specific project (e.g., "no purple gradients, no glassmorphism, no Inter").

   **Starting moves:**
   - Type: <suggested pairing direction, not exact fonts yet>
   - Color: <dominant + accent direction>
   - Motion: <character — e.g., "crisp, 150ms, no bounces">
   ```

5. **Do NOT** generate tokens, Tailwind config, or components. This skill ends at the taste brief. The user takes it from there (or hands it to another skill / frontend-design plugin).

## Rules

- Inspiration only. Never copy exact colors, fonts, or component code from the reference systems.
- Keep the brief short — it's an anchor, not a spec.
- If the user already named brands they like in the prompt, skip straight to step 3.
- Prefer 2 references over 3. Two clear poles beat three muddy ones.
