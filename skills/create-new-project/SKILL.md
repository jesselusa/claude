---
name: create-new-project
description: Scaffold a new project with CLAUDE.md, .gitignore, and optional PRD workflow
argument-hint: [project-name] [--nextjs|--python|--minimal]
---

# Create New Project

Scaffold a new project folder with all the setup from this starter configuration, customized for the user's preferences.

**Argument:** $ARGUMENTS

**Modifiers:**
- `--nextjs`: Use Next.js template
- `--python`: Use Python template
- `--minimal`: Use minimal starter template
- (no modifier): Ask user to choose

---

## Step 1: Project Name

**Ask first** (if not provided in arguments):

```
What should this project be called?
```

Validate: lowercase, hyphens allowed, no spaces. If invalid, suggest a fixed version and confirm.

**Wait for response before proceeding.**

---

## Step 2: Tech Stack

**Ask second** (if no modifier like `--nextjs` provided):

```
What's the tech stack?

1. Next.js + Supabase + Tailwind (web apps)
2. Python (scripts, CLI, APIs)
3. Minimal (just CLAUDE.md + .gitignore)
4. Other (describe your stack)
```

If user selects 4 (Other), ask them to describe their stack, then adapt the CLAUDE.md template accordingly.

**Wait for response before proceeding.**

---

## Step 3: Project Location

**Ask third:**

```
Where should I create the project?

1. ~/Documents/GitHub/[project-name] (Recommended)
2. ~/Projects/[project-name]
3. Current directory ./[project-name]
4. Other (specify path)
```

If user selects 4 (Other), ask for the full path.

**Wait for response before proceeding.**

---

## Step 4: Project Description

**Ask fourth:**

```
Briefly describe what this project will do (1-2 sentences):
```

**Wait for response before proceeding.**

---

## Step 5: Create Project Structure

### 5.1 Create Directory

```bash
mkdir -p "[PROJECT_PATH]"
cd "[PROJECT_PATH]"
```

### 5.2 Initialize Git

```bash
git init
```

### 5.3 Copy Template Files

Based on project type, copy the appropriate template:

**Next.js:**
```bash
cp ~/Documents/GitHub/claude/templates/nextjs.md ./CLAUDE.md
```

**Python:**
```bash
cp ~/Documents/GitHub/claude/templates/python.md ./CLAUDE.md
```

**Minimal:**
```bash
cp ~/Documents/GitHub/claude/templates/starter.md ./CLAUDE.md
```

### 5.4 Generate .gitignore

Run the gitignore skill logic for the project type:

**Next.js:**
```
# Dependencies
node_modules/
.pnpm-store/

# Next.js
.next/
out/

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/

# OS
.DS_Store

# Debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Vercel
.vercel

# TypeScript
*.tsbuildinfo
```

**Python:**
```
# Virtual environments
venv/
.venv/
env/

# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/

# OS
.DS_Store

# Testing
.pytest_cache/
.coverage
htmlcov/
```

**Minimal:**
```
# Environment
.env
.env.local

# IDE
.vscode/
.idea/

# OS
.DS_Store
```

### 5.5 Customize CLAUDE.md

Update the CLAUDE.md template with project-specific info:

1. Replace `<!-- Brief description of what this project does -->` with user's description
2. Add any project-specific conventions mentioned

---

## Step 6: Project-Type Specific Setup

### If Next.js was selected:

**Ask:**
```
Do you want me to initialize the Next.js project now?

1. Yes, run create-next-app with recommended settings (Recommended)
2. No, I'll set it up manually later
```

**Wait for response.**

If 1, run:
```bash
pnpm create next-app . --typescript --tailwind --eslint --app --src-dir=false --import-alias="@/*" --use-pnpm
```

**Then ask:**
```
Will this project use Supabase?

1. Yes, install Supabase packages (Recommended)
2. No
```

**Wait for response.**

If 1:
```bash
pnpm add @supabase/supabase-js @supabase/ssr
```

Create `.env.local.example`:
```
NEXT_PUBLIC_SUPABASE_URL=your-project-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

### If Python was selected:

**Ask:**
```
How should I set up the Python environment?

1. Create venv + requirements.txt (Recommended)
2. Use uv (faster, modern)
3. Skip, I'll handle it
```

**Wait for response.**

If 1:
```bash
python3 -m venv venv
echo "# Add dependencies here" > requirements.txt
```

If 2:
```bash
uv init
```

### If Other was selected:

Use the user's described stack to create an appropriate CLAUDE.md with relevant sections filled in. Skip framework-specific initialization.

---

## Step 7: Optional PRD Workflow

**Ask:**
```
Do you want to create a PRD (Product Requirements Document) for your first feature?

1. Yes, let's plan what to build (Recommended for new projects)
2. No, I'll start coding directly
```

**Wait for response.**

If 1:

Create tasks directory:
```bash
mkdir -p tasks
mkdir -p workflows
```

Copy workflow files:
```bash
cp ~/Documents/GitHub/claude/workflows/create-prd.md ./workflows/
cp ~/Documents/GitHub/claude/workflows/generate-tasks.md ./workflows/
```

**Then ask:**
```
What feature or functionality do you want to build first?
```

**Wait for response.**

Follow the create-prd.md workflow step-by-step:
1. Ask clarifying questions (one set at a time)
2. Generate PRD to `tasks/prd-[feature].md`
3. Ask if user wants to generate tasks
4. If yes, generate `tasks/tasks-[feature].md`

---

## Step 8: Optional GitHub Setup

**Ask:**
```
Do you want to create a GitHub repository for this project?

1. Yes, create public repo and push (Recommended)
2. Yes, create private repo and push
3. No, keep local only for now
```

**Wait for response.**

If 1 or 2:

### 8.1 Check GitHub CLI

```bash
gh auth status
```

If not authenticated, inform user:
```
GitHub CLI not authenticated. Run `gh auth login` first, then re-run this step.
```

### 8.2 Create Initial Commit

```bash
git add .
git commit -m "$(cat <<'EOF'
feat: initial project setup

- CLAUDE.md with project configuration
- .gitignore for [project-type]
- [any other files created]

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### 8.3 Create GitHub Repo

```bash
# Public
gh repo create [project-name] --public --source=. --remote=origin --push

# Private
gh repo create [project-name] --private --source=. --remote=origin --push
```

### 8.4 Report Success

```
Repository created: https://github.com/[username]/[project-name]

Local path: [PROJECT_PATH]
```

---

## Step 9: Summary

Output a summary:

```
## Project Created: [project-name]

**Location:** [PROJECT_PATH]
**Type:** [Next.js / Python / Minimal]

### Files Created
- CLAUDE.md (project configuration)
- .gitignore ([X] patterns)
[- package.json (if Next.js)]
[- requirements.txt (if Python)]
[- tasks/prd-[feature].md (if PRD created)]
[- tasks/tasks-[feature].md (if tasks generated)]

### GitHub
[- Repository: https://github.com/[username]/[project-name]]
[- Local only (not pushed)]

### Next Steps
1. cd [PROJECT_PATH]
2. [Open in your editor]
3. [Start the first task / Start coding]
```

---

## Quick Start Examples

```bash
# Interactive mode - asks all questions
/create-new-project

# With project name
/create-new-project my-awesome-app

# Skip project type question
/create-new-project my-api --python
/create-new-project my-site --nextjs
/create-new-project my-tool --minimal
```
