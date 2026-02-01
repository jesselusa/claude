---
name: techdebt
description: Find and eliminate technical debt - duplicated code, dead code, inconsistent patterns
argument-hint: [directory or file]
---

# Tech Debt Hunter

Run at the end of every session to find and kill technical debt.

**Argument:** $ARGUMENTS (defaults to files changed in current session/branch)

---

## Quick Mode (Default)

Scan recently changed files for quick wins:

1. Get changed files: `git diff --name-only HEAD~5` or `git diff --name-only main`
2. Run checks on those files only
3. Fix issues automatically where safe
4. Report what was cleaned up

---

## Checks

### 1. Dead Code

**Unused imports:**
```bash
# TypeScript/JavaScript
npx knip --include files,exports,dependencies

# Python
ruff check --select F401,F841 .
```

**Unused functions/variables:**
- Grep for function definitions, check if they're called anywhere
- Flag exports not imported elsewhere in the codebase

**Action:** Remove dead code automatically. Commit: `chore: remove dead code`

---

### 2. Duplicated Code

**Find similar blocks:**
- Look for 3+ lines that appear multiple times
- Check for copy-pasted logic with minor variations
- Identify repeated patterns that could be abstracted

**Detection approach:**
```bash
# Use jscpd for JS/TS
npx jscpd --min-lines 3 --min-tokens 50 src/

# For Python, check with pylint
pylint --disable=all --enable=duplicate-code .
```

**Action:**
- If duplication is in recently changed files → extract to shared function
- If duplication spans modules → flag for review, don't auto-fix

---

### 3. Console.logs & Debug Statements

```bash
# Find leftover debugging
grep -rn "console\.log\|console\.debug\|debugger\|print(" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.py" src/
```

**Exclude:**
- Files in `scripts/` or `debug/` directories
- Intentional logging (error handling, analytics)

**Action:** Remove debug statements. Commit: `chore: remove debug statements`

---

### 4. TODO/FIXME Comments

```bash
grep -rn "TODO\|FIXME\|HACK\|XXX" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.py" src/
```

**Action:**
- List all found TODOs with file:line
- For TODOs in recently changed files, ask: "Resolve now or keep?"
- Don't auto-delete - these are intentional markers

---

### 5. Inconsistent Patterns

**Naming conventions:**
- camelCase vs snake_case mixing
- Inconsistent file naming (kebab-case vs PascalCase)

**Import style:**
- Mixed relative/absolute imports
- Inconsistent import ordering

**Component patterns:**
- Arrow functions vs function declarations
- Default exports vs named exports mixing

**Action:** Flag inconsistencies in recently changed files, offer to standardize

---

### 6. Type Issues (TypeScript)

```bash
# Find any types
grep -rn ": any\|as any" --include="*.ts" --include="*.tsx" src/

# Find type assertions that could be narrowed
grep -rn "as [A-Z]" --include="*.ts" --include="*.tsx" src/
```

**Action:** Flag `any` types in recently changed files, offer to add proper types

---

### 7. Large Files

```bash
# Files over 300 lines
find src -name "*.ts" -o -name "*.tsx" -o -name "*.py" | xargs wc -l | sort -n | tail -20
```

**Action:** Flag files > 300 lines that were recently modified, suggest splits

---

## Output Format

```
## Tech Debt Report

### Cleaned Up ✓
- Removed 3 unused imports (auth.ts, api.ts)
- Removed 2 console.logs (dashboard.tsx)
- Removed dead function `oldHelper` (utils.ts)

### Needs Review
- Duplicated code: src/api/users.ts:45 ↔ src/api/posts.ts:32
- Large file: src/components/Dashboard.tsx (412 lines)
- 5 TODO comments found (list below)

### TODOs in Changed Files
1. src/auth.ts:23 - TODO: add rate limiting
2. src/api.ts:89 - FIXME: handle edge case

### Stats
- Files scanned: 12
- Issues fixed: 5
- Issues flagged: 3
```

---

## Commit Strategy

Group fixes into logical commits:
- `chore: remove dead code` - unused imports, functions, variables
- `chore: remove debug statements` - console.logs, debuggers
- `refactor: extract shared function` - if deduplicating code

Don't create commits for flagged-only items.

---

## Full Scan Mode

Run with `--full` or on entire directory to scan everything:

```
/techdebt --full
/techdebt src/
```

This runs all checks on the entire codebase, not just recent changes.
