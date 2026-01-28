# Claude Code Skills

Custom skills (slash commands) for Claude Code.

## Available Skills

| Skill | Command | Description |
|-------|---------|-------------|
| Security Audit | `/security-audit` | Comprehensive 7-phase security audit (deps, secrets, logs) |

## Installation

Skills must be installed to `~/.claude/skills/` to be available globally:

```bash
# Create skills directory
mkdir -p ~/.claude/skills

# Symlink all skills (recommended for easy updates)
ln -sf ~/Documents/GitHub/jl-claude-assistant/skills/* ~/.claude/skills/

# Or copy (requires manual updates)
cp -r ~/Documents/GitHub/jl-claude-assistant/skills/* ~/.claude/skills/
```

## Usage

Once installed, invoke skills with `/` prefix:

```
/security-audit           # Audit current directory
/security-audit ./path    # Audit specific path
```

## Creating New Skills

Each skill is a directory containing:

```
skill-name/
├── SKILL.md          # Skill definition and instructions
└── *.sh              # Supporting shell scripts (optional)
```

The `SKILL.md` frontmatter defines metadata:

```yaml
---
name: skill-name
description: What the skill does
argument-hint: [optional-args]
disable-model-invocation: true  # For pure instruction skills
---
```
