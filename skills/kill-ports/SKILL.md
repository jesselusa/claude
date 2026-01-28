---
name: kill-ports
description: Find and kill processes listening on TCP ports
disable-model-invocation: true
---

# Kill Ports

Find and kill processes listening on TCP ports.

---

## Steps

1. **List listening ports** (exclude system ports < 1024):

```bash
lsof -i -P -n 2>/dev/null | grep LISTEN
```

2. **If no ports found:** Output "No listening ports found." and exit.

3. **Display table** showing PORT, PID, PROCESS for each result.

4. **Prompt user** with `AskUserQuestion`:
   - `multiSelect: true`
   - Header: "Ports"
   - Question: "Which processes do you want to kill?"
   - Options: Each port as "Port <port> (<process>)" with PID in description

5. **Kill selected** with `kill -9 <pid>` and report results.
