---
name: robots
description: Generate a comprehensive robots.txt for a website or web app
---

Generate a robots.txt file based on user's desired restrictiveness level.

## Workflow

### Step 1: Ask for Restrictiveness Level

Use `AskUserQuestion` to prompt the user:

**Question:** "How restrictive should your robots.txt be?"

**Options:**
1. **Permissive** - Allow all crawlers (good for SEO and AI indexing)
2. **Block AI** - Block AI training/scraping, allow search engines
3. **Block SEO** - Block SEO analysis tools, allow AI and search engines
4. **Maximum** - Block all crawlers (AI, SEO, search engines, archives)

### Step 2: Check for Updated AI Crawlers (Block AI or Maximum only)

If user selected "Block AI" or "Maximum":

1. Fetch the latest AI crawler list:
   ```
   https://raw.githubusercontent.com/ai-robots-txt/ai.robots.txt/refs/heads/main/robots.txt
   ```

2. Parse all `User-agent:` lines from the fetched content

3. Compare against the local template (`block-ai.txt` or `maximum.txt`)

4. If new crawlers are found that aren't in the local template:
   - Display the list of new crawlers to the user
   - Ask if they want to include these new crawlers
   - If yes, add them to the generated output

### Step 3: Determine Output Location

Detect project type and set the output path:

- **Next.js** (has `next.config.*`): `public/robots.txt`
- **Other projects**: `robots.txt` in project root

### Step 4: Generate robots.txt

1. Read the appropriate template from `~/.claude/skills/robots/templates/`:
   - Permissive: `permissive.txt`
   - Block AI: `block-ai.txt`
   - Block SEO: `block-seo.txt`
   - Maximum: `maximum.txt`

2. If new crawlers were found and user accepted them, append to the template content

3. Write to the determined output location (overwrite without backup)

4. Confirm the file was created and summarize what was blocked

## Templates

Located in `~/.claude/skills/robots/templates/`:

| File | Description |
|------|-------------|
| `permissive.txt` | Allow all crawlers |
| `block-ai.txt` | Block AI crawlers, allow search engines |
| `block-seo.txt` | Block SEO tools, allow AI and search engines |
| `maximum.txt` | Block all crawlers |

## Reference

For the latest AI crawler list: https://github.com/ai-robots-txt/ai.robots.txt
