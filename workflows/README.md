# AI Dev Workflows

Structured workflows for AI-assisted feature development. Based on [snarktank/ai-dev-tasks](https://github.com/snarktank/ai-dev-tasks).

## Workflow

```
1. Create PRD  →  2. Generate Tasks  →  3. Execute Tasks
```

## Usage

### 1. Create a PRD

Tell Claude to use the PRD template:

```
Use @create-prd.md to help me build: [describe your feature]
```

Claude will ask clarifying questions, then generate `tasks/prd-[feature].md`.

### 2. Generate Tasks

Once your PRD is ready:

```
Take @tasks/prd-[feature].md and create tasks using @generate-tasks.md
```

Claude generates high-level tasks first, then sub-tasks after you confirm.

### 3. Execute Tasks

Work through tasks incrementally:

```
Start on task 1.1 from tasks/tasks-[feature].md
```

Check off tasks as you complete them.

## Setup in a Project

Copy workflows to your project or reference from this repo:

```bash
# Copy to project
cp -r ~/Documents/GitHub/claude/workflows /path/to/project/

# Create tasks directory
mkdir -p /path/to/project/tasks
```

Add to `.gitignore` if you don't want to track generated PRDs/tasks:

```
tasks/prd-*.md
tasks/tasks-*.md
```
