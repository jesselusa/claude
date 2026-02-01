# Claude Code Skills

Custom skills (slash commands) for Claude Code. Based on [dcnu/claude](https://github.com/dcnu/claude).

## Available Skills

| Skill | Command | Description |
|-------|---------|-------------|
| Security Audit | `/security-audit` | Comprehensive 7-phase security audit (deps, secrets, logs) |
| Claude Cleanup | `/claude-cleanup` | Scan and redact secrets from Claude memory files |
| Cleanup | `/cleanup` | Rename files to `Source-Title-date.ext` convention |
| Create New Project | `/create-new-project` | Scaffold new project with templates, optional PRD & GitHub |
| Create README | `/create-readme` | Generate README.md and LICENSE for projects |
| Gitignore | `/gitignore` | Generate .gitignore based on detected project type |
| Kill Ports | `/kill-ports` | Find and kill processes listening on TCP ports |
| Robots | `/robots` | Generate robots.txt with AI/SEO blocking options |
| Sync Starter | `/sync-starter` | Sync improvements back to starter template repo |

## Installation

Skills must be installed to `~/.claude/skills/` to be available globally:

```bash
# Create skills directory
mkdir -p ~/.claude/skills

# Symlink all skills (recommended for easy updates)
for skill in ~/Documents/GitHub/jl-claude-assistant/skills/*/; do
    ln -sf "$skill" ~/.claude/skills/
done

# Or symlink individually
ln -sf ~/Documents/GitHub/jl-claude-assistant/skills/security-audit ~/.claude/skills/
ln -sf ~/Documents/GitHub/jl-claude-assistant/skills/gitignore ~/.claude/skills/
# ... etc
```

## Usage

Once installed, invoke skills with `/` prefix:

```
/security-audit                    # Run full security audit
/gitignore                         # Generate .gitignore
/cleanup ~/Downloads               # Rename files in Downloads
/robots                            # Generate robots.txt
/kill-ports                        # Kill processes on ports
/create-new-project my-app         # Scaffold a new project
/create-new-project my-api --python # Scaffold with Python template
```

## Creating New Skills

Each skill is a directory containing:

```
skill-name/
├── SKILL.md          # Skill definition and instructions
├── *.sh              # Supporting shell scripts (optional)
├── *.py              # Supporting Python scripts (optional)
└── templates/        # Template files (optional)
```

The `SKILL.md` frontmatter defines metadata:

```yaml
---
name: skill-name
description: What the skill does
argument-hint: [optional-args]
disable-model-invocation: true  # For pure instruction skills
hooks:                          # Optional hook integrations
  PostToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "~/.claude/skills/skill-name/hook.sh"
---
```
