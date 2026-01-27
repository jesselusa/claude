# MCP Server Configuration

## Installed Plugins

These plugins are installed via the official Claude Code marketplace. Run `/plugin` in Claude Code to install them.

| Plugin | Purpose |
|--------|---------|
| `supabase` | Database, auth, and realtime integration |
| `vercel` | Deployment and hosting |
| `github` | GitHub API integration |
| `playwright` | Browser automation and testing |
| `frontend-design` | UI/UX design assistance |
| `code-review` | PR and code review tools |

## Setup on New Machine

```bash
# In Claude Code, run:
/plugin supabase
/plugin vercel
/plugin github
/plugin playwright
/plugin frontend-design
/plugin code-review
```

## Custom MCP Servers

Add any custom MCP server configurations here. Example format:

```json
{
  "my-server": {
    "type": "stdio",
    "command": "node",
    "args": ["/path/to/server.js"]
  }
}
```

Place custom configs in project `.mcp.json` files or global `~/.claude/settings.json`.
