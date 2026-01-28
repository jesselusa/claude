---
name: create-readme
description: Generate README.md and LICENSE when initializing a git repo
hooks:
  PostToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "~/.claude/skills/create-readme/detect-git-init.sh"
        - type: command
          command: "~/.claude/skills/create-readme/check-readme-staleness.sh"
---

# Create README

Generate a comprehensive README.md for the current project.

## Workflow

1. Run the detection script to identify project type and metadata:
   ```bash
   bash ~/.claude/skills/create-readme/detect-project.sh
   ```

2. Review the detected information and prompt user for any missing details:
   - Project description (required)
   - License - select one:
     - **MIT** - permissive, attribution required
     - **GPL 3.0** - copyleft, derivatives must be open source
     - **All rights reserved** - no LICENSE file generated
   - Author (default: `github.com/dcnu`)

3. Generate README with these sections:
   - **Project Title** - from package.json/pyproject.toml name field
   - **Description** - infer from codebase
   - **Features** - infer from codebase
   - **Tech Stack** - from detected project type
   - **Prerequisites** - based on project type (Node.js version, Python version, etc.)
   - **Installation** - package manager commands based on detection
   - **Environment Setup** - if `.env.example` exists, document required variables
   - **Usage** - CLI commands, local server, or public URL (if applicable)
   - **Testing** - test commands based on project type
   - **Project Structure** - generate from directory tree
   - **License** - user-selected

4. If README.md already exists, prompt user:
   - **Update**: Refresh dynamic sections, preserve static sections
   - **Replace**: Overwrite with new README
   - **Cancel**: Abort operation

5. Generate LICENSE file (if license is not "All rights reserved"):
   - Check if LICENSE file already exists
   - If exists, prompt: **Replace** / **Skip**
   - Generate LICENSE file with full license text

## Detection Script Output

The script outputs JSON with detected project metadata:
```json
{
  "type": "nextjs|node|python|unknown",
  "name": "project-name",
  "version": "1.0.0",
  "description": "existing description if any",
  "packageManager": "pnpm|npm|yarn|uv|pip",
  "framework": "next|express|fastapi|flask|none",
  "database": "postgresql|mysql|sqlite|mongodb|none",
  "hasTests": true,
  "testCommand": "pnpm test",
  "hasPrisma": false,
  "hasEnvExample": true
}
```

## License Templates

### MIT License

```
MIT License

Copyright (c) [YEAR] [AUTHOR]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### GPL 3.0 License

Use the official GPL 3.0 license text from: https://www.gnu.org/licenses/gpl-3.0.txt
