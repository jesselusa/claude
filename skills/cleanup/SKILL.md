---
name: cleanup
description: Rename files to follow naming convention Source-Title-date.ext
argument-hint: [directory] [--dry-run] [--force] [--recursive]
---

# Cleanup - File Renaming

Rename files to follow the standard naming convention: `Source-Title-date.ext`

## Naming Convention

Format: `Source-Title-date.ext`

- **Source**: `PascalCase`
  - People: `LastnameFirstname` (e.g., `SmithJohn`)
  - Abbreviations: `UPPERCASE` (e.g., `BCG`, `FBI`, `NASA`)
  - Omit if unknown (do not use "Unknown")
- **Title**: `PascalCase`
  - Omit if unknown (do not use "Untitled")
- **Date formats** (in order of preference):
  - `YYMMDD` - full date known (e.g., `240115`)
  - `YYYY-Qn` - quarterly (e.g., `2024-Q1`)
  - `YYYY-Month` - year and month (e.g., `2024-January`)
  - `YYYY` - year only (e.g., `2024`)
- Use `-` as delimiter between components

## Arguments

- `[directory]` - Target directory (default: `~/Downloads`)
- `--dry-run` - Preview changes without executing
- `--force` - Overwrite existing files if conflicts occur
- `--recursive` - Process subdirectories

## Workflow

This skill uses a two-phase approach for speed and user control.

### Phase 1: Quick Pass (No LLM)

1. Parse arguments and identify target directory

2. Run the rename script to get categorized suggestions:
   ```bash
   python3 ~/.claude/skills/cleanup/rename-files.py --list --new-only [directory]
   ```

3. The script outputs JSON with categorized suggestions:
   ```json
   {
     "auto": [...],
     "needsReview": [...],
     "alreadyProcessed": 5,
     "newFiles": 12,
     "totalFiles": 17
   }
   ```

4. Display summary:
   ```
   Scanning ~/Downloads...
   ├── 17 files found
   ├── 5 previously processed (skipped)
   └── 12 new files
   ```

5. If `auto` suggestions exist, present them for batch selection using AskUserQuestion:
   - List each auto-rename suggestion
   - Ask user to confirm which to apply (default: all)

6. Execute selected auto-renames:
   ```bash
   python3 ~/.claude/skills/cleanup/rename-files.py --rename [--force] [directory]
   ```

7. Record skipped files in history:
   ```bash
   python3 ~/.claude/skills/cleanup/rename-files.py --record-skip <filepath>
   ```

### Phase 2: LLM Review (Optional)

1. If `needsReview` files exist, ask user:
   ```
   3 files need content analysis for better suggestions.
   Analyze with LLM? [y/N]
   ```

2. If user declines, record files as skipped and exit.

3. If user accepts, for each file in `needsReview`:
   - Read file metadata (size, mtime)
   - For text-based files (PDF, DOCX, TXT, MD), read first 1KB of content
   - For images/media, use only filename + metadata
   - Analyze content to determine Source, Title, Date

4. Generate LLM suggestions following these rules:
   - Format: `Source-Title-date.ext`
   - **Omit** any component that cannot be determined
   - Never output "Unknown", "Untitled", or placeholder values

5. Present LLM suggestions for batch selection using AskUserQuestion

6. Execute selected renames and record all files in history

## History

The script maintains history at `~/.claude/cleanup-history.json`:
- Tracks processed files by path and mtime
- Records action taken (renamed, skipped)

To clear history:
```bash
python3 ~/.claude/skills/cleanup/rename-files.py --clear-history
```
