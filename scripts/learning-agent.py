#!/usr/bin/env python3
"""
Daily Learning Agent

Scans recent Claude session logs, extracts learnings, updates CLAUDE.md,
creates skill stubs, and opens PRs across the personal config repo and
four project repos.
"""

import json
import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"
CLAUDE_REPO = Path.home() / "Documents" / "GitHub" / "claude"
CLAUDE_MD_FILE = "CLAUDE.md"
LOG_DIR = Path.home() / ".claude" / "learning-agent" / "logs"
TODAY = datetime.now().strftime("%Y-%m-%d")
BRANCH = f"feat/daily-learnings-{TODAY}"
LOOKBACK_HOURS = 24
SUBAGENTS_DIR = "subagents"

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


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run a subprocess and return the result."""
    log.debug("run: %s (cwd=%s)", " ".join(cmd), cwd)
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True)


def run_claude(prompt: str) -> str | None:
    """Call `claude -p <prompt>` and return stdout, or None on failure."""
    result = run(["claude", "-p", prompt])
    if result.returncode != 0:
        log.warning("claude -p exited %d: %s", result.returncode, result.stderr.strip())
        return None
    return result.stdout.strip()


def branch_exists(repo: Path, branch: str) -> bool:
    """Return True if branch exists locally or on origin."""
    remote = run(["git", "ls-remote", "--heads", "origin", branch], cwd=repo)
    if remote.stdout.strip():
        return True
    local = run(["git", "branch", "--list", branch], cwd=repo)
    return bool(local.stdout.strip())


def has_staged_changes(repo: Path) -> bool:
    """Return True if there are staged changes ready to commit."""
    result = run(["git", "diff", "--cached", "--quiet"], cwd=repo)
    return result.returncode != 0  # exit 1 = has diff


def commit_and_open_pr(
    repo: Path,
    files: list[str],
    commit_msg: str,
    pr_title: str,
    pr_body: str,
) -> str | None:
    """
    Stage files, commit, push to BRANCH, and open a PR.
    Returns the PR URL, or None if nothing to commit or a step fails.
    Always switches back to main when done.
    """
    if branch_exists(repo, BRANCH):
        log.info("Branch '%s' already exists in %s — skipping", BRANCH, repo.name)
        return None

    run(["git", "checkout", "-b", BRANCH], cwd=repo)
    run(["git", "add"] + files, cwd=repo)

    if not has_staged_changes(repo):
        log.info("No changes to commit in %s — skipping PR", repo.name)
        run(["git", "checkout", "main"], cwd=repo)
        run(["git", "branch", "-d", BRANCH], cwd=repo)
        return None

    result = run(["git", "commit", "-m", commit_msg], cwd=repo)
    if result.returncode != 0:
        log.error("Commit failed in %s: %s", repo.name, result.stderr)
        run(["git", "checkout", "main"], cwd=repo)
        return None

    result = run(["git", "push", "-u", "origin", BRANCH], cwd=repo)
    if result.returncode != 0:
        log.error("Push failed in %s: %s", repo.name, result.stderr)
        run(["git", "checkout", "main"], cwd=repo)
        return None

    result = run(
        ["gh", "pr", "create", "--title", pr_title, "--body", pr_body, "--assignee", "@me"],
        cwd=repo,
    )
    if result.returncode != 0:
        log.error("gh pr create failed for %s: %s", repo.name, result.stderr)
        run(["git", "checkout", "main"], cwd=repo)
        return None

    pr_url = result.stdout.strip()
    log.info("Created PR for %s: %s", repo.name, pr_url)
    run(["git", "checkout", "main"], cwd=repo)
    return pr_url


# ---------------------------------------------------------------------------
# Step 1: Find recent session logs
# ---------------------------------------------------------------------------


def find_recent_logs() -> list[Path]:
    """Return JSONL files modified in the last LOOKBACK_HOURS, skipping subagents."""
    cutoff = datetime.now() - timedelta(hours=LOOKBACK_HOURS)
    recent: list[Path] = []

    if not CLAUDE_PROJECTS_DIR.exists():
        log.info("Claude projects dir not found: %s", CLAUDE_PROJECTS_DIR)
        return recent

    for jsonl in CLAUDE_PROJECTS_DIR.rglob("*.jsonl"):
        if SUBAGENTS_DIR in jsonl.parts:
            continue
        if datetime.fromtimestamp(jsonl.stat().st_mtime) >= cutoff:
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

                    content = entry.get("message", {}).get("content", [])
                    if isinstance(content, str):
                        messages.append(content[:MAX_MSG_CHARS])
                        continue

                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            messages.append(block.get("text", "")[:MAX_MSG_CHARS])
        except Exception as exc:
            log.warning("Failed to read %s: %s", path, exc)

    return "\n\n---\n\n".join(messages)[:MAX_SESSION_CHARS]


# ---------------------------------------------------------------------------
# Step 3: Extract learnings via Claude
# ---------------------------------------------------------------------------


def build_extraction_prompt(claude_md_content: str, session_text: str) -> str:
    return f"""You are reviewing Claude Code session logs to extract reusable engineering learnings.

## Current CLAUDE.md (first {MAX_CLAUDE_MD_CHARS} chars)

{claude_md_content[:MAX_CLAUDE_MD_CHARS]}

## Session messages from the last {LOOKBACK_HOURS} hours

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
    raw = run_claude(build_extraction_prompt(claude_md_content, session_text))
    log.debug("Claude raw output:\n%s", raw)

    if raw is None or "NOTHING_NEW" in raw:
        log.info("No new learnings found.")
        return []

    learnings: list[dict] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("|")
        if parts[0] == "RULE" and len(parts) >= 3:
            section, rule = parts[1].strip(), parts[2].strip()
            if section in VALID_SECTIONS and rule:
                learnings.append({"type": "RULE", "section": section, "rule": rule})
        elif parts[0] == "SKILL" and len(parts) >= 4:
            name, description, summary = parts[1].strip(), parts[2].strip(), parts[3].strip()
            if name and description:
                learnings.append({"type": "SKILL", "name": name, "description": description, "summary": summary})

    log.info("Parsed %d learning(s)", len(learnings))
    return learnings


# ---------------------------------------------------------------------------
# Step 4a: Apply RULE learnings to CLAUDE.md
# ---------------------------------------------------------------------------


def apply_rules_to_claude_md(learnings: list[dict]) -> tuple[list[str], str]:
    """
    Appends new rules to the appropriate sections in CLAUDE.md.
    Returns (added_descriptions, updated_file_content) — avoids a second disk read.
    """
    claude_md_path = CLAUDE_REPO / CLAUDE_MD_FILE
    content = claude_md_path.read_text(encoding="utf-8")
    rules = [l for l in learnings if l["type"] == "RULE"]
    if not rules:
        return [], content

    lines = content.splitlines(keepends=True)
    added: list[str] = []

    for learning in rules:
        section, rule = learning["section"], learning["rule"]
        header = f"### {section}"

        section_idx = next((i for i, l in enumerate(lines) if l.strip() == header), None)
        if section_idx is None:
            log.warning("Section '%s' not found in CLAUDE.md — skipping rule: %s", section, rule)
            continue

        insert_idx = next(
            (i for i in range(section_idx + 1, len(lines)) if lines[i].strip().startswith("###") or lines[i].strip() == "---"),
            len(lines),
        )

        rule_line = f"- {rule}\n"
        if insert_idx > 0 and lines[insert_idx - 1].strip():
            lines.insert(insert_idx, "\n")
            insert_idx += 1
        lines.insert(insert_idx, rule_line)

        added.append(f"[{section}] {rule}")
        log.info("Added rule to '%s': %s", section, rule)

    updated = "".join(lines)
    if added:
        claude_md_path.write_text(updated, encoding="utf-8")

    return added, updated


# ---------------------------------------------------------------------------
# Step 4b: Create skill stubs
# ---------------------------------------------------------------------------


def create_skill_stubs(learnings: list[dict]) -> list[str]:
    """Creates skills/{name}/SKILL.md stubs. Returns list of names created."""
    created: list[str] = []

    for skill in (l for l in learnings if l["type"] == "SKILL"):
        name, description, summary = skill["name"], skill["description"], skill["summary"]
        skill_md = CLAUDE_REPO / "skills" / name / "SKILL.md"

        if skill_md.exists():
            log.info("Skill '%s' already exists — skipping", name)
            continue

        skill_md.parent.mkdir(parents=True, exist_ok=True)
        skill_md.write_text(
            f"---\nname: /{name}\ndescription: {description}\n---\n\n# /{name}\n\n{summary}\n\n"
            "## Steps\n\n<!-- TODO: flesh out the steps for this skill -->\n\n1. (Step 1)\n2. (Step 2)\n3. (Step 3)\n",
            encoding="utf-8",
        )
        created.append(name)
        log.info("Created skill stub: %s", skill_md)

    return created


# ---------------------------------------------------------------------------
# Step 5: Create PR for /claude repo
# ---------------------------------------------------------------------------


def create_claude_repo_pr(added_rules: list[str], created_skills: list[str]) -> str | None:
    """Commit CLAUDE.md + skill stubs to a feature branch and open a PR."""
    files = [CLAUDE_MD_FILE] + [f"skills/{s}/SKILL.md" for s in created_skills]
    rules_md = "\n".join(f"- {r}" for r in added_rules) if added_rules else "_None_"
    skills_md = "\n".join(f"- `/{s}`" for s in created_skills) if created_skills else "_None_"

    return commit_and_open_pr(
        CLAUDE_REPO,
        files,
        f"feat: daily learnings {TODAY}",
        f"feat: daily learnings {TODAY}",
        f"## Daily Learnings — {TODAY}\n\nAutomated PR from the daily learning agent.\n\n"
        f"### Rules added to CLAUDE.md\n\n{rules_md}\n\n"
        f"### Skill stubs created\n\n{skills_md}\n\n---\nGenerated by `scripts/learning-agent.py`",
    )


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


def sync_project_repo(
    repo_name: str, repo_path: Path, global_claude_md: str, claude_repo_pr_url: str | None
) -> None:
    """Sync global CLAUDE.md learnings to a project repo and open a PR."""
    log.info("Syncing %s...", repo_name)

    if not repo_path.exists():
        log.warning("Repo path does not exist: %s — skipping", repo_path)
        return

    project_claude_md_path = repo_path / CLAUDE_MD_FILE
    if not project_claude_md_path.exists():
        log.warning("No CLAUDE.md found in %s — skipping", repo_path)
        return

    original_content = project_claude_md_path.read_text(encoding="utf-8")
    updated_content = run_claude(build_sync_prompt(global_claude_md, original_content))

    if updated_content is None or "NO_CHANGES" in updated_content:
        log.info("No changes for %s — skipping PR", repo_name)
        return

    project_claude_md_path.write_text(updated_content, encoding="utf-8")

    ref_line = f"\nSee source PR: {claude_repo_pr_url}" if claude_repo_pr_url else ""
    pr_url = commit_and_open_pr(
        repo_path,
        [CLAUDE_MD_FILE],
        f"feat: sync CLAUDE.md learnings {TODAY}",
        f"feat: sync CLAUDE.md learnings {TODAY}",
        f"## Sync CLAUDE.md — {TODAY}\n\nAutomated PR to sync generic engineering rules "
        f"from the global `jesselusa/claude` config.{ref_line}\n\n---\nGenerated by `scripts/learning-agent.py`",
    )

    if pr_url is None:
        # Restore if nothing was committed (e.g. branch already existed)
        project_claude_md_path.write_text(original_content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    log.info("=== Daily Learning Agent — %s ===", TODAY)

    recent_logs = find_recent_logs()
    if not recent_logs:
        log.info("No session logs modified in the last %d hours. Exiting.", LOOKBACK_HOURS)
        sys.exit(0)

    session_text = extract_human_messages(recent_logs)
    if not session_text.strip():
        log.info("No user messages found in recent logs. Exiting.")
        sys.exit(0)

    log.info("Extracted %d chars of session text", len(session_text))

    claude_md_content = (CLAUDE_REPO / CLAUDE_MD_FILE).read_text(encoding="utf-8")

    learnings = extract_learnings(claude_md_content, session_text)
    if not learnings:
        log.info("No actionable learnings. Exiting.")
        sys.exit(0)

    added_rules, updated_claude_md = apply_rules_to_claude_md(learnings)
    created_skills = create_skill_stubs(learnings)

    if not added_rules and not created_skills:
        log.info("Learnings parsed but nothing new to apply. Exiting.")
        sys.exit(0)

    claude_repo_pr_url = None
    try:
        claude_repo_pr_url = create_claude_repo_pr(added_rules, created_skills)
    except Exception as exc:
        log.error("Failed to create PR for claude repo: %s", exc)

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(sync_project_repo, name, path, updated_claude_md, claude_repo_pr_url): name
            for name, path in PROJECT_REPOS.items()
        }
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                log.error("Failed to sync %s: %s", futures[future], exc)

    log.info("=== Done ===")


if __name__ == "__main__":
    main()
