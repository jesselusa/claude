#!/usr/bin/env python3
"""
Daily Learning Agent

Scans recent Claude session logs, extracts learnings, updates CLAUDE.md,
creates skill stubs, and opens PRs across the personal config repo and
four project repos.
"""

import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"
CLAUDE_REPO = Path.home() / "Documents" / "GitHub" / "claude"
LOG_DIR = Path.home() / ".claude" / "learning-agent" / "logs"
TODAY = datetime.now().strftime("%Y-%m-%d")
BRANCH = f"feat/daily-learnings-{TODAY}"

PROJECT_REPOS = {
    "pokecrm": Path.home() / "Documents" / "GitHub" / "pokecrm",
    "little-language-labs": Path.home() / "Documents" / "GitHub" / "little-language-labs",
    "palette": Path.home() / "Documents" / "GitHub" / "palette",
    "jesselusa-com": Path.home() / "Documents" / "GitHub" / "jesselusa-com",
}

VALID_SECTIONS = [
    "Working Style",
    "Code Style",
    "Testing Approach",
    "Before Committing",
    "Personal Preferences",
]

MAX_SESSION_CHARS = 30000
MAX_MSG_CHARS = 300
MAX_CLAUDE_MD_CHARS = 5000

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


def setup_logging() -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"{TODAY}.log"
    logger = logging.getLogger("learning-agent")
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s")

    fh = logging.FileHandler(log_file)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    return logger


log = setup_logging()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def run(cmd: list[str], cwd: Path | None = None, capture: bool = True) -> subprocess.CompletedProcess:
    """Run a subprocess, returning the CompletedProcess result."""
    log.debug("run: %s (cwd=%s)", " ".join(cmd), cwd)
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=capture,
        text=True,
    )


def run_claude(prompt: str) -> str:
    """Call `claude -p <prompt>` and return stdout."""
    result = run(["claude", "-p", prompt])
    if result.returncode != 0:
        log.warning("claude -p exited %d: %s", result.returncode, result.stderr.strip())
    return result.stdout.strip()


def branch_exists_remote(repo: Path, branch: str) -> bool:
    result = run(["git", "ls-remote", "--heads", "origin", branch], cwd=repo)
    return bool(result.stdout.strip())


def branch_exists_local(repo: Path, branch: str) -> bool:
    result = run(["git", "branch", "--list", branch], cwd=repo)
    return bool(result.stdout.strip())


def git_diff_empty(repo: Path) -> bool:
    result = run(["git", "diff", "--cached", "--quiet"], cwd=repo)
    # exit 0 = no diff, exit 1 = has diff
    return result.returncode == 0


# ---------------------------------------------------------------------------
# Step 1: Find recent session logs
# ---------------------------------------------------------------------------


def find_recent_logs() -> list[Path]:
    """Return JSONL files modified in the last 24 hours, skipping /subagents/ dirs."""
    cutoff = datetime.now() - timedelta(hours=24)
    recent: list[Path] = []

    if not CLAUDE_PROJECTS_DIR.exists():
        log.info("Claude projects dir not found: %s", CLAUDE_PROJECTS_DIR)
        return recent

    for jsonl in CLAUDE_PROJECTS_DIR.rglob("*.jsonl"):
        # skip anything under a subagents directory
        if "subagents" in jsonl.parts:
            continue
        mtime = datetime.fromtimestamp(jsonl.stat().st_mtime)
        if mtime >= cutoff:
            recent.append(jsonl)

    log.info("Found %d recent session log(s)", len(recent))
    return recent


# ---------------------------------------------------------------------------
# Step 2: Extract human messages
# ---------------------------------------------------------------------------


def extract_human_messages(log_files: list[Path]) -> str:
    """Extract user text messages from JSONL files and return a capped string."""
    messages: list[str] = []

    for path in log_files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    if entry.get("type") != "user":
                        continue

                    content = entry.get("content", [])
                    if isinstance(content, str):
                        # some entries store content as plain string
                        messages.append(content[:MAX_MSG_CHARS])
                        continue

                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            text = block.get("text", "")
                            messages.append(text[:MAX_MSG_CHARS])
        except Exception as exc:
            log.warning("Failed to read %s: %s", path, exc)

    combined = "\n\n---\n\n".join(messages)
    return combined[:MAX_SESSION_CHARS]


# ---------------------------------------------------------------------------
# Step 3: Ask Claude for learnings
# ---------------------------------------------------------------------------


def build_extraction_prompt(claude_md_content: str, session_text: str) -> str:
    claude_md_snippet = claude_md_content[:MAX_CLAUDE_MD_CHARS]

    return f"""You are reviewing Claude Code session logs to extract reusable engineering learnings.

## Current CLAUDE.md (first {MAX_CLAUDE_MD_CHARS} chars)

{claude_md_snippet}

## Session messages from the last 24 hours

{session_text}

## Instructions

Identify patterns from the session messages that represent generic, reusable lessons —
things that should apply across many projects, not just the specific app being built.

Output learnings in EXACTLY this pipe-delimited format (one per line):

  RULE|<section>|<rule text>
  SKILL|<skill-name>|<one-line description>|<2-3 sentence summary>

Where <section> must be one of:
  Working Style, Code Style, Testing Approach, Before Committing, Personal Preferences

Rules:
- Must be generic (not app-specific)
- Must NOT already be present in CLAUDE.md above
- Must be high-confidence lessons (not speculative)
- Rule text should be a single concise imperative sentence

Skills:
- <skill-name> is a lowercase-hyphenated command name (e.g. `db-reset`)
- Only suggest a skill if a recurring multi-step workflow emerged from the session
- Summary must explain what the skill does and when to use it (2-3 sentences)

If nothing qualifies, output exactly: NOTHING_NEW

Do not include any explanation, preamble, or commentary — only the output lines."""


def extract_learnings(claude_md_content: str, session_text: str) -> list[dict]:
    """Returns a list of parsed learning dicts."""
    prompt = build_extraction_prompt(claude_md_content, session_text)
    raw = run_claude(prompt)
    log.debug("Claude raw output:\n%s", raw)

    if "NOTHING_NEW" in raw:
        log.info("No new learnings found.")
        return []

    learnings: list[dict] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("|")
        if parts[0] == "RULE" and len(parts) >= 3:
            section = parts[1].strip()
            rule = parts[2].strip()
            if section in VALID_SECTIONS and rule:
                learnings.append({"type": "RULE", "section": section, "rule": rule})
        elif parts[0] == "SKILL" and len(parts) >= 4:
            name = parts[1].strip()
            description = parts[2].strip()
            summary = parts[3].strip()
            if name and description:
                learnings.append({
                    "type": "SKILL",
                    "name": name,
                    "description": description,
                    "summary": summary,
                })

    log.info("Parsed %d learning(s)", len(learnings))
    return learnings


# ---------------------------------------------------------------------------
# Step 4a: Apply RULE learnings to CLAUDE.md
# ---------------------------------------------------------------------------


def apply_rules_to_claude_md(learnings: list[dict]) -> list[str]:
    """
    Appends new rules to the appropriate sections in CLAUDE.md.
    Returns a list of human-readable descriptions of what was added.
    """
    rules = [l for l in learnings if l["type"] == "RULE"]
    if not rules:
        return []

    claude_md_path = CLAUDE_REPO / "CLAUDE.md"
    content = claude_md_path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)
    added: list[str] = []

    for learning in rules:
        section = learning["section"]
        rule = learning["rule"]
        header = f"### {section}"

        # Find the line index of the section header
        section_idx = None
        for i, line in enumerate(lines):
            if line.strip() == header:
                section_idx = i
                break

        if section_idx is None:
            log.warning("Section '%s' not found in CLAUDE.md — skipping rule: %s", section, rule)
            continue

        # Find the insertion point: just before the next ### or --- after the section
        insert_idx = len(lines)  # default: end of file
        for i in range(section_idx + 1, len(lines)):
            stripped = lines[i].strip()
            if stripped.startswith("###") or stripped == "---":
                insert_idx = i
                break

        # Insert the rule line (with a blank line before if needed)
        rule_line = f"- {rule}\n"
        # Ensure there's a blank line before our insertion if the preceding line isn't blank
        if insert_idx > 0 and lines[insert_idx - 1].strip():
            lines.insert(insert_idx, "\n")
            insert_idx += 1
        lines.insert(insert_idx, rule_line)

        added.append(f"[{section}] {rule}")
        log.info("Added rule to '%s': %s", section, rule)

    if added:
        claude_md_path.write_text("".join(lines), encoding="utf-8")

    return added


# ---------------------------------------------------------------------------
# Step 4b: Create skill stubs
# ---------------------------------------------------------------------------


def create_skill_stubs(learnings: list[dict]) -> list[str]:
    """
    Creates skills/{name}/SKILL.md stubs for SKILL learnings.
    Returns list of skill names created.
    """
    skills = [l for l in learnings if l["type"] == "SKILL"]
    created: list[str] = []

    for skill in skills:
        name = skill["name"]
        description = skill["description"]
        summary = skill["summary"]

        skill_dir = CLAUDE_REPO / "skills" / name
        skill_md = skill_dir / "SKILL.md"

        if skill_md.exists():
            log.info("Skill '%s' already exists — skipping", name)
            continue

        skill_dir.mkdir(parents=True, exist_ok=True)
        content = f"""---
name: /{name}
description: {description}
---

# /{name}

{summary}

## Steps

<!-- TODO: flesh out the steps for this skill -->

1. (Step 1)
2. (Step 2)
3. (Step 3)
"""
        skill_md.write_text(content, encoding="utf-8")
        created.append(name)
        log.info("Created skill stub: %s", skill_md)

    return created


# ---------------------------------------------------------------------------
# Step 5: Create PR for /claude repo
# ---------------------------------------------------------------------------


def create_claude_repo_pr(added_rules: list[str], created_skills: list[str]) -> str | None:
    """
    Commits changes to CLAUDE.md and new skill stubs in the claude repo,
    pushes to a feature branch, and opens a PR. Returns the PR URL or None.
    """
    repo = CLAUDE_REPO

    # Check if branch already exists (idempotent)
    if branch_exists_remote(repo, BRANCH) or branch_exists_local(repo, BRANCH):
        log.info("Branch '%s' already exists in claude repo — skipping PR", BRANCH)
        return None

    # Create and switch to branch
    result = run(["git", "checkout", "-b", BRANCH], cwd=repo)
    if result.returncode != 0:
        log.error("Failed to create branch in claude repo: %s", result.stderr)
        return None

    # Stage changed files
    files_to_stage: list[str] = ["CLAUDE.md"]
    for skill_name in created_skills:
        files_to_stage.append(f"skills/{skill_name}/SKILL.md")

    run(["git", "add"] + files_to_stage, cwd=repo)

    # Check if there's actually anything to commit
    status = run(["git", "status", "--porcelain"], cwd=repo)
    if not status.stdout.strip():
        log.info("No changes to commit in claude repo — skipping PR")
        run(["git", "checkout", "main"], cwd=repo)
        run(["git", "branch", "-d", BRANCH], cwd=repo)
        return None

    # Commit
    commit_msg = f"feat: daily learnings {TODAY}"
    result = run(["git", "commit", "-m", commit_msg], cwd=repo)
    if result.returncode != 0:
        log.error("Commit failed in claude repo: %s", result.stderr)
        return None

    # Push
    result = run(["git", "push", "-u", "origin", BRANCH], cwd=repo)
    if result.returncode != 0:
        log.error("Push failed in claude repo: %s", result.stderr)
        return None

    # Build PR body
    rules_section = "\n".join(f"- {r}" for r in added_rules) if added_rules else "_None_"
    skills_section = "\n".join(f"- `/{s}`" for s in created_skills) if created_skills else "_None_"

    pr_body = f"""## Daily Learnings — {TODAY}

Automated PR from the daily learning agent.

### Rules added to CLAUDE.md

{rules_section}

### Skill stubs created

{skills_section}

---
Generated by `scripts/learning-agent.py`"""

    result = run(
        [
            "gh", "pr", "create",
            "--title", f"feat: daily learnings {TODAY}",
            "--body", pr_body,
            "--assignee", "@me",
        ],
        cwd=repo,
    )

    if result.returncode != 0:
        log.error("gh pr create failed for claude repo: %s", result.stderr)
        return None

    pr_url = result.stdout.strip()
    log.info("Created PR for claude repo: %s", pr_url)

    # Switch back to main
    run(["git", "checkout", "main"], cwd=repo)

    return pr_url


# ---------------------------------------------------------------------------
# Step 6: Sync to project repos
# ---------------------------------------------------------------------------


def build_sync_prompt(global_claude_md: str, project_claude_md: str) -> str:
    return f"""You are merging generic engineering rules from a global CLAUDE.md into a project-specific CLAUDE.md.

## Global CLAUDE.md (source of new rules)

{global_claude_md}

## Project CLAUDE.md (current content)

{project_claude_md}

## Instructions

Identify any generic rules in the global CLAUDE.md that are NOT yet present in the
project CLAUDE.md and that would be applicable to a typical software project.

Do NOT include rules that are clearly specific to the global config repo itself
(e.g. "creating skills", "syncing repositories", etc.).

If there are rules to add, output the COMPLETE updated project CLAUDE.md with the
new rules merged in naturally. Do not add commentary — only output the file contents.

If there are no new rules to add, output exactly: NO_CHANGES"""


def sync_project_repo(repo_name: str, repo_path: Path, global_claude_md: str, claude_repo_pr_url: str | None):
    """Sync global CLAUDE.md learnings to a project repo and open a PR."""
    log.info("Syncing %s...", repo_name)

    if not repo_path.exists():
        log.warning("Repo path does not exist: %s — skipping", repo_path)
        return

    project_claude_md_path = repo_path / "CLAUDE.md"
    if not project_claude_md_path.exists():
        log.warning("No CLAUDE.md found in %s — skipping", repo_path)
        return

    # Idempotent: skip if branch already exists
    if branch_exists_remote(repo_path, BRANCH) or branch_exists_local(repo_path, BRANCH):
        log.info("Branch '%s' already exists in %s — skipping", BRANCH, repo_name)
        return

    project_claude_md = project_claude_md_path.read_text(encoding="utf-8")

    prompt = build_sync_prompt(global_claude_md, project_claude_md)
    updated_content = run_claude(prompt)

    if "NO_CHANGES" in updated_content:
        log.info("No changes for %s — skipping PR", repo_name)
        return

    # Write the updated CLAUDE.md
    project_claude_md_path.write_text(updated_content, encoding="utf-8")

    # Create branch
    result = run(["git", "checkout", "-b", BRANCH], cwd=repo_path)
    if result.returncode != 0:
        log.error("Failed to create branch in %s: %s", repo_name, result.stderr)
        project_claude_md_path.write_text(project_claude_md, encoding="utf-8")  # restore
        return

    # Stage
    run(["git", "add", "CLAUDE.md"], cwd=repo_path)

    # Verify there's actually a diff
    status = run(["git", "status", "--porcelain"], cwd=repo_path)
    if not status.stdout.strip():
        log.info("git diff empty for %s after sync — skipping PR", repo_name)
        run(["git", "checkout", "main"], cwd=repo_path)
        run(["git", "branch", "-d", BRANCH], cwd=repo_path)
        return

    # Commit
    commit_msg = f"feat: sync CLAUDE.md learnings {TODAY}"
    result = run(["git", "commit", "-m", commit_msg], cwd=repo_path)
    if result.returncode != 0:
        log.error("Commit failed in %s: %s", repo_name, result.stderr)
        run(["git", "checkout", "main"], cwd=repo_path)
        return

    # Push
    result = run(["git", "push", "-u", "origin", BRANCH], cwd=repo_path)
    if result.returncode != 0:
        log.error("Push failed in %s: %s", repo_name, result.stderr)
        run(["git", "checkout", "main"], cwd=repo_path)
        return

    # PR body
    ref_line = f"\nSee source PR: {claude_repo_pr_url}" if claude_repo_pr_url else ""
    pr_body = f"""## Sync CLAUDE.md — {TODAY}

Automated PR to sync generic engineering rules from the global `jesselusa/claude` config.{ref_line}

---
Generated by `scripts/learning-agent.py`"""

    result = run(
        [
            "gh", "pr", "create",
            "--title", f"feat: sync CLAUDE.md learnings {TODAY}",
            "--body", pr_body,
            "--assignee", "@me",
        ],
        cwd=repo_path,
    )

    if result.returncode != 0:
        log.error("gh pr create failed for %s: %s", repo_name, result.stderr)
    else:
        log.info("Created PR for %s: %s", repo_name, result.stdout.strip())

    # Switch back to main
    run(["git", "checkout", "main"], cwd=repo_path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    log.info("=== Daily Learning Agent — %s ===", TODAY)

    # Step 1: Find recent logs
    recent_logs = find_recent_logs()
    if not recent_logs:
        log.info("No session logs modified in the last 24 hours. Exiting.")
        sys.exit(0)

    # Step 2: Extract human messages
    session_text = extract_human_messages(recent_logs)
    if not session_text.strip():
        log.info("No user messages found in recent logs. Exiting.")
        sys.exit(0)

    log.info("Extracted %d chars of session text", len(session_text))

    # Read current CLAUDE.md
    claude_md_path = CLAUDE_REPO / "CLAUDE.md"
    claude_md_content = claude_md_path.read_text(encoding="utf-8")

    # Step 3: Extract learnings via Claude
    learnings = extract_learnings(claude_md_content, session_text)
    if not learnings:
        log.info("No actionable learnings. Exiting.")
        sys.exit(0)

    # Step 4a: Apply rules to CLAUDE.md
    added_rules = apply_rules_to_claude_md(learnings)

    # Step 4b: Create skill stubs
    created_skills = create_skill_stubs(learnings)

    if not added_rules and not created_skills:
        log.info("Learnings parsed but nothing new to apply. Exiting.")
        sys.exit(0)

    # Step 5: Create PR for /claude repo
    claude_repo_pr_url = None
    try:
        claude_repo_pr_url = create_claude_repo_pr(added_rules, created_skills)
    except Exception as exc:
        log.error("Failed to create PR for claude repo: %s", exc)

    # Reload CLAUDE.md after any modifications for use in project syncing
    claude_md_content = claude_md_path.read_text(encoding="utf-8")

    # Step 6: Sync to project repos
    for repo_name, repo_path in PROJECT_REPOS.items():
        try:
            sync_project_repo(repo_name, repo_path, claude_md_content, claude_repo_pr_url)
        except Exception as exc:
            log.error("Failed to sync %s: %s", repo_name, exc)

    log.info("=== Done ===")


if __name__ == "__main__":
    main()
