# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

<!-- Brief description of what this project does -->

## Tech Stack

- **Language**: Python 3.11+
- **Package Manager**: pip / uv
- **Linting**: ruff
- **Type Checking**: pyright (optional)

## Commands

```bash
python -m venv venv           # Create virtual environment
source venv/bin/activate      # Activate (macOS/Linux)
pip install -r requirements.txt

python main.py                # Run main script
python -m pytest              # Run tests
ruff check .                  # Lint
ruff format .                 # Format
```

## Project Structure

```
src/
├── __init__.py
├── main.py           # Entry point
└── utils/            # Utility modules
tests/
└── test_*.py         # Test files
requirements.txt      # Dependencies
```

## Conventions

- Use type hints for function signatures
- One class per file for major classes
- Keep functions small and focused
