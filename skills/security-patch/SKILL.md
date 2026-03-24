---
name: security-patch
description: Check and auto-patch open Dependabot security vulnerabilities across all personal repos
disable-model-invocation: true
---

# Security Patch

Check open Dependabot alerts across all personal repos and auto-patch what's fixable. Manual alternative to a scheduled GitHub Action.

**Repos checked:**
- jesselusa/pokecrm
- jesselusa/little-language-labs
- jesselusa/palette
- jesselusa/jesselusa.com

---

## Steps

### 1. Check Alerts

Fetch open Dependabot alerts for each repo:

```bash
for repo in pokecrm little-language-labs palette jesselusa.com; do
  echo "=== jesselusa/$repo ==="
  gh api repos/jesselusa/$repo/dependabot/alerts \
    --jq '[.[] | select(.state=="open")] | map({package: .security_vulnerability.package.name, severity: .security_advisory.severity, summary: .security_advisory.summary, fixedIn: .security_vulnerability.first_patched_version.identifier}) | .[]'
done
```

Display results as a table: Repo | Package | Severity | Fixed In | Summary

If no open alerts found, output "No open security vulnerabilities found." and stop.

---

### 2. For Each Affected Repo

#### a. Check local availability

```bash
ls ~/Documents/GitHub/{repo-name}
```

If not found locally, skip to **Fallback** for that repo.

#### b. Create a feature branch

```bash
cd ~/Documents/GitHub/{repo-name}
git checkout main && git pull
git checkout -b fix/security-patch-$(date +%Y-%m-%d)
```

#### c. Apply fixes

```bash
pnpm audit --fix
```

For specific packages named in alerts:

```bash
pnpm update {package-name}
```

If no auto-fix exists (major version bump required), flag as **needs manual intervention** and skip.

#### d. Verify nothing broke

```bash
pnpm lint && pnpm type-check
```

If checks fail and fix is non-trivial, revert that package's changes and flag it.

#### e. Skip if no changes

```bash
git diff --stat
```

If nothing changed, delete the branch and move to the next repo.

#### f. Commit and push

```bash
git add package.json pnpm-lock.yaml
git commit -m "fix: patch security vulnerabilities"
git push -u origin fix/security-patch-$(date +%Y-%m-%d)
```

#### g. Open a PR

```bash
gh pr create \
  --title "fix: patch security vulnerabilities" \
  --body "Auto-patched open Dependabot alerts via /security-patch.

## Packages Updated
{list packages}

## Verification
- [x] pnpm audit --fix applied
- [x] lint passed
- [x] type-check passed" \
  --assignee @me
```

---

### 3. Fallback (Repo Not Cloned Locally)

Provide manual commands to run from that repo's directory:

```bash
git checkout main && git pull
git checkout -b fix/security-patch-$(date +%Y-%m-%d)
pnpm audit --fix
pnpm lint && pnpm type-check
git add package.json pnpm-lock.yaml
git commit -m "fix: patch security vulnerabilities"
git push -u origin fix/security-patch-$(date +%Y-%m-%d)
gh pr create --title "fix: patch security vulnerabilities" --assignee @me
```

---

## Output Format

```
Security Patch Report

Alerts Found:
  pokecrm       lodash   HIGH      → Patched
  palette       axios    MODERATE  → Patched
  jesselusa.com next     HIGH      → Needs manual intervention (major bump)

PRs Created:
  https://github.com/jesselusa/pokecrm/pull/...
  https://github.com/jesselusa/palette/pull/...

Needs Manual Intervention:
  jesselusa/jesselusa.com — next requires major version bump. Review changelog before upgrading.
```
