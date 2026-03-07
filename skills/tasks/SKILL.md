---
name: tasks
description: View and update outstanding tasks in the tasks/ directory
disable-model-invocation: true
---

# Tasks

View open tasks and update their status in the current project's `tasks/` directory.

---

## Steps

1. **Check for tasks/ directory** in the current project root. If it doesn't exist, offer to create it and exit.

2. **Read all `.md` files** in `tasks/`.

3. **Display open tasks** grouped by file:
   - Show each unchecked `[ ]` item with its file name as a header
   - Show a count of completed `[x]` items per file (e.g., "3 done") — don't list them
   - If no open tasks: output "All tasks complete ✓" and exit

4. **Ask user** using `AskUserQuestion`:
   - Question: "What would you like to do?"
   - Options:
     - Mark tasks complete
     - Add new tasks
     - Nothing, just viewing

5. **If marking complete:** Ask user which tasks to check off (use `AskUserQuestion` with `multiSelect: true`). Update the relevant file(s) by replacing `[ ]` with `[x]` for selected items.

6. **If adding tasks:** Ask which file to add to (or create a new file). Ask for the task description(s) and append as `- [ ] <description>`.

7. **Report** what was changed.
