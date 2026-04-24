#!/usr/bin/env python3
"""
Daily Learning Agent

Scans recent Claude session logs, extracts learnings, updates CLAUDE.md,
creates skill stubs, and opens a PR on the personal config repo.

Project repo syncing is handled by a remote Claude scheduled trigger
(CLAUDE.md Sync — daily 10am PT).
"""

import json
import logging
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
import subprocess  # noqa: S404

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"
CLAUDE_REPO = Path.home() / "Documents" / "GitHub" / "claude"
CLAUDE_MD_FILE = "CLAUDE.md"
DECISIONS_LOG_REL = "evals/learning-agent/decisions.jsonl"
LOG_DIR = Path.home() / ".claude" / "learning-agent" / "logs"
TODAY = datetime.now().strftime("%Y-%m-%d")
BRANCH = f"feat/daily-learnings-{TODAY}"
LOOKBACK_HOURS = 24
SUBAGENTS_DIR = "subagents"

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
    local = run(["git", "branch", "--list", branch], cwd=repo)
    if local.stdout.strip():
        return True
    remote = run(["git", "ls-remote", "--heads", "origin", branch], cwd=repo)
    return bool(remote.stdout.strip())


def has_staged_changes(repo: Path) -> bool:
    """Return True if there are staged changes ready to commit."""
    result = run(["git", "diff", "--cached", "--quiet"], cwd=repo)
    return result.returncode != 0  # exit 1 = has diff


def _cleanup_branch(repo: Path) -> None:
    """Switch back to main and delete the feature branch."""
    run(["git", "checkout", "main"], cwd=repo)
    run(["git", "branch", "-d", BRANCH], cwd=repo)


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
        _cleanup_branch(repo)
        return None

    result = run(["git", "commit", "-m", commit_msg], cwd=repo)
    if result.returncode != 0:
        log.error("Commit failed in %s: %s", repo.name, result.stderr)
        _cleanup_branch(repo)
        return None

    result = run(["git", "push", "-u", "origin", BRANCH], cwd=repo)
    if result.returncode != 0:
        log.error("Push failed in %s: %s", repo.name, result.stderr)
        _cleanup_branch(repo)
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


def build_extraction_prompt(
    claude_md_content: str,
    session_text: str,
    closed_rules: list[str],
    open_rules: list[str],
) -> str:
    closed_block = ""
    if closed_rules:
        closed_block = (
            "\n## Previously REJECTED rules (soft warning)\n\n"
            + "\n".join(f"- {r}" for r in closed_rules)
            + "\n\nThe user previously closed PRs containing these rules. Do NOT re-suggest them "
              "unless your new rule is meaningfully distinct — different scope, different concern, "
              "or a clearly improved framing.\n"
        )
    open_block = ""
    if open_rules:
        open_block = (
            "\n## Currently AWAITING REVIEW (hard skip)\n\n"
            + "\n".join(f"- {r}" for r in open_rules)
            + "\n\nThese rules are sitting in an unmerged PR. Do NOT suggest anything that "
              "duplicates or materially overlaps with them.\n"
        )

    return f"""You are reviewing Claude Code session logs to extract reusable engineering learnings.{closed_block}{open_block}

## Current CLAUDE.md (first {MAX_CLAUDE_MD_CHARS} chars)

{claude_md_content[:MAX_CLAUDE_MD_CHARS]}

## Session messages from the last {LOOKBACK_HOURS} hours

{session_text}

## Instructions

Identify patterns from the session messages that represent UNIVERSAL engineering lessons —
things that apply to ANY software project regardless of stack, domain, or design choices.

CRITICAL FILTER: A rule must pass this test:
  "Would this rule make sense in a completely different project with different tech/design?"
If the answer is no, DO NOT include it.

REJECT examples (project-specific — do NOT extract these):
- "Match monochrome palette" — specific to one project's design system
- "Use zinc colors" — specific design choice
- "Put API routes under /api/v2" — specific architecture decision
- "Use Supabase RLS for multi-tenant" — specific to one project's auth model
- "Import from @/lib/utils" — specific project structure

ACCEPT examples (universal — these ARE valid):
- "Run type-check before committing" — applies everywhere
- "Test mobile viewport after UI changes" — applies everywhere
- "Validate environment variables exist at startup" — applies everywhere

Output learnings in EXACTLY this pipe-delimited format (one per line):

  RULE|<section>|<rule text>
  SKILL|<skill-name>|<one-line description>|<2-3 sentence summary>

Where <section> must be one of:
  Working Style, Code Style, Testing Approach, Before Committing, Personal Preferences

Rules:
- Must be UNIVERSALLY applicable (not project-specific, not design-specific, not stack-specific)
- Must NOT already be present in CLAUDE.md above
- Must be high-confidence lessons (not speculative)
- Rule text should be a single concise imperative sentence
- When in doubt, leave it out — err heavily toward NOTHING_NEW

Skills:
- <skill-name> is a lowercase-hyphenated command name (e.g. `db-reset`)
- Only suggest a skill if a recurring multi-step workflow emerged from the session
- The skill must be useful across multiple projects, not just the one being worked on
- Summary must explain what the skill does and when to use it (2-3 sentences)

If nothing qualifies, output exactly: NOTHING_NEW

Do not include any explanation, preamble, or commentary — only the output lines."""


def extract_learnings(
    claude_md_content: str,
    session_text: str,
    closed_rules: list[str],
    open_rules: list[str],
) -> list[dict]:
    """Returns a list of parsed learning dicts."""
    raw = run_claude(build_extraction_prompt(claude_md_content, session_text, closed_rules, open_rules))
    log.debug("Claude raw output:\n%s", raw)

    if raw is None:
        log.info("No output from Claude.")
        return []

    # Parse valid lines first — Claude may include commentary alongside valid output
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

    if not learnings:
        log.info("No new learnings found.")
    else:
        log.info("Parsed %d learning(s)", len(learnings))
    return learnings


# ---------------------------------------------------------------------------
# Step 4a: Apply RULE learnings — shared insertion logic
# ---------------------------------------------------------------------------


def insert_rules(
    content: str,
    rules: list[dict],
    header_prefixes: tuple[str, ...] = ("### ",),
) -> tuple[str, list[dict]]:
    """
    Insert rules into content by matching section headers.
    Re-scans after each insertion to avoid index drift.
    Skips rules whose text already appears in the target section.
    Returns (updated_content, list_of_added_rule_dicts).
    """
    lines = content.splitlines(keepends=True)
    added: list[dict] = []

    for rule_dict in rules:
        section, rule = rule_dict["section"], rule_dict["rule"]

        section_idx = None
        for i, l in enumerate(lines):
            stripped = l.strip()
            if any(stripped == f"{p}{section}" for p in header_prefixes):
                section_idx = i
                break

        if section_idx is None:
            log.warning("Section '%s' not found — skipping rule: %s", section, rule)
            continue

        insert_idx = next(
            (i for i in range(section_idx + 1, len(lines))
             if lines[i].strip().startswith("##") or lines[i].strip() == "---"),
            len(lines),
        )

        section_text = "".join(lines[section_idx:insert_idx]).lower()
        if rule.lower() in section_text:
            log.info("Rule already present in section '%s' — skipping: %s", section, rule)
            continue

        rule_line = f"- {rule}\n"
        if insert_idx > 0 and lines[insert_idx - 1].strip():
            lines.insert(insert_idx, "\n")
            insert_idx += 1
        lines.insert(insert_idx, rule_line)

        added.append({"section": section, "rule": rule})
        log.info("Added rule to '%s': %s", section, rule)

    return "".join(lines), added


def apply_rules_to_claude_md(content: str, learnings: list[dict]) -> tuple[list[dict], str]:
    """
    Appends new rules to the appropriate sections in CLAUDE.md.
    Returns (added_rule_dicts, updated_file_content).
    """
    rules = [l for l in learnings if l["type"] == "RULE"]
    if not rules:
        return [], content

    updated, added = insert_rules(content, rules, header_prefixes=("### ",))

    if added:
        claude_md_path = CLAUDE_REPO / CLAUDE_MD_FILE
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


def create_claude_repo_pr(added_rules: list[dict], created_skills: list[str]) -> str | None:
    """Commit CLAUDE.md + skill stubs to a feature branch and open a PR."""
    files = [CLAUDE_MD_FILE] + [f"skills/{s}/SKILL.md" for s in created_skills]
    rules_md = (
        "\n".join(f"- [{r['section']}] {r['rule']}" for r in added_rules)
        if added_rules else "_None_"
    )
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
# Step 6: Decision log — score past outcomes, skip duplicates, soft-reject closed
# ---------------------------------------------------------------------------


def load_decisions() -> list[dict]:
    path = CLAUDE_REPO / DECISIONS_LOG_REL
    if not path.exists():
        return []
    entries: list[dict] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                log.warning("Skipping malformed line in decisions.jsonl")
    return entries


def save_decisions(entries: list[dict]) -> None:
    path = CLAUDE_REPO / DECISIONS_LOG_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")


def score_past_outcomes(entries: list[dict]) -> tuple[int, int, int, bool]:
    """Fill in outcomes for unresolved entries. Returns (merged, closed, still_open, mutated)."""
    merged = closed = open_ = 0
    mutated = False
    for entry in entries:
        if entry.get("outcome") is not None:
            continue
        pr_url = entry.get("pr_url")
        if not pr_url:
            continue
        result = run(["gh", "pr", "view", pr_url, "--json", "state,mergedAt,closedAt"])
        if result.returncode != 0:
            log.warning("gh pr view failed for %s: %s", pr_url, result.stderr.strip())
            open_ += 1
            continue
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            open_ += 1
            continue
        state = data.get("state")
        if state == "MERGED":
            entry["outcome"] = "merged"
            entry["outcome_date"] = (data.get("mergedAt") or "")[:10] or TODAY
            merged += 1
            mutated = True
        elif state == "CLOSED":
            entry["outcome"] = "closed"
            entry["outcome_date"] = (data.get("closedAt") or "")[:10] or TODAY
            closed += 1
            mutated = True
        else:
            open_ += 1
    return merged, closed, open_, mutated


def extract_rule_context(entries: list[dict]) -> tuple[list[str], list[str]]:
    """Build (closed_rules, open_rules) from the decisions log."""
    closed_rules: list[str] = []
    open_rules: list[str] = []
    for entry in entries:
        outcome = entry.get("outcome")
        for rule in entry.get("rules_added", []):
            section = rule.get("section", "")
            text = rule.get("rule", "")
            if not text:
                continue
            line = f"[{section}] {text}" if section else text
            if outcome == "closed":
                closed_rules.append(line)
            elif outcome is None:
                open_rules.append(line)
    return closed_rules, open_rules


def log_new_decision(
    entries: list[dict],
    pr_url: str,
    added_rules: list[dict],
    created_skills: list[str],
) -> None:
    """Append a new entry for today's PR to the decisions log (in-memory)."""
    pr_number = None
    match = re.search(r"/pull/(\d+)", pr_url or "")
    if match:
        pr_number = int(match.group(1))

    entries.append({
        "date": TODAY,
        "pr_number": pr_number,
        "pr_url": pr_url,
        "rules_added": added_rules,
        "skills_added": created_skills,
        "outcome": None,
        "outcome_date": None,
    })


def commit_decisions_log() -> None:
    """Commit & push decisions.jsonl changes to main, if any."""
    status = run(["git", "status", "--porcelain", DECISIONS_LOG_REL], cwd=CLAUDE_REPO)
    if not status.stdout.strip():
        return
    run(["git", "add", DECISIONS_LOG_REL], cwd=CLAUDE_REPO)
    result = run(
        ["git", "commit", "-m", f"chore: log learning-agent decisions {TODAY}"],
        cwd=CLAUDE_REPO,
    )
    if result.returncode != 0:
        log.warning("decisions.jsonl commit failed: %s", result.stderr.strip())
        return
    push = run(["git", "push", "origin", "main"], cwd=CLAUDE_REPO)
    if push.returncode != 0:
        log.warning("decisions.jsonl push failed: %s", push.stderr.strip())


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

    # Make sure main is up to date before reading/writing the decisions log
    run(["git", "checkout", "main"], cwd=CLAUDE_REPO)
    run(["git", "pull", "--ff-only", "origin", "main"], cwd=CLAUDE_REPO)

    decisions = load_decisions()
    merged, closed, open_, mutated = score_past_outcomes(decisions)
    log.info("Scored past outcomes: %d merged, %d closed, %d still open", merged, closed, open_)

    closed_rules, open_rules = extract_rule_context(decisions)
    log.info(
        "Rule context: %d previously closed (soft warning), %d awaiting review (hard skip)",
        len(closed_rules), len(open_rules),
    )

    def persist_decisions() -> None:
        if mutated:
            save_decisions(decisions)
            commit_decisions_log()

    claude_md_content = (CLAUDE_REPO / CLAUDE_MD_FILE).read_text(encoding="utf-8")

    learnings = extract_learnings(claude_md_content, session_text, closed_rules, open_rules)
    if not learnings:
        log.info("No actionable learnings.")
        persist_decisions()
        sys.exit(0)

    added_rules, updated_claude_md = apply_rules_to_claude_md(claude_md_content, learnings)
    created_skills = create_skill_stubs(learnings)

    if not added_rules and not created_skills:
        log.info("Learnings parsed but nothing new to apply.")
        persist_decisions()
        sys.exit(0)

    pr_url = None
    try:
        pr_url = create_claude_repo_pr(added_rules, created_skills)
    except Exception as exc:
        log.error("Failed to create PR for claude repo: %s", exc)

    if pr_url:
        log_new_decision(decisions, pr_url, added_rules, created_skills)
        mutated = True

    persist_decisions()

    # Project repo syncing is handled by the remote CLAUDE.md Sync trigger (daily 10am PT)
    log.info("=== Done ===")


if __name__ == "__main__":
    main()
