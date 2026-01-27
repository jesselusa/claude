# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a personal Claude Code configuration repository containing:
- Global preferences and coding style
- MCP server configurations
- Custom hooks
- Project templates for CLAUDE.md files

## Structure

```
jl-claude-assistant/
├── CLAUDE.md          # This file - global preferences
├── mcp-servers/       # MCP server configurations
├── hooks/             # Custom automation hooks
├── templates/         # CLAUDE.md templates for different project types
└── workflows/         # AI dev workflow templates (PRD → Tasks → Execute)
```

## Personal Preferences

### Languages & Stack
- **Primary**: TypeScript/JavaScript, Python
- **Frontend**: Next.js (App Router) with React
- **Styling**: Tailwind CSS
- **Backend**: Supabase (Postgres, Auth, Realtime)
- **Deployment**: Vercel

### Code Style
- Concise and minimal - avoid unnecessary boilerplate
- Comments only when logic isn't self-evident
- Prefer simple solutions over clever ones
- Keep files focused and small

### Design
- Mobile-first responsive design - always optimize for phone use

## Development Workflow

For non-trivial features, follow this structured process:

1. **Create PRD** - `Use @workflows/create-prd.md to build: [feature description]`
2. **Generate Tasks** - `Create tasks from @tasks/prd-[feature].md using @workflows/generate-tasks.md`
3. **Execute** - Work through tasks incrementally, checking off as completed

This ensures clear requirements before coding and manageable incremental progress.
