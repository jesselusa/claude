#!/usr/bin/env python3
"""
Analyze project structure and generate gitignore recommendations.
Outputs JSON for Claude to process.
"""

import json
import os
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent
TEMPLATES_DIR = SCRIPT_DIR / "templates"


PROJECT_DETECTORS = [
	{
		"name": "nodejs",
		"files": ["package.json"],
		"dirs": [],
		"template": "nodejs.gitignore",
	},
	{
		"name": "nextjs",
		"files": ["next.config.js", "next.config.ts", "next.config.mjs"],
		"dirs": [],
		"template": "nextjs.gitignore",
	},
	{
		"name": "python",
		"files": ["pyproject.toml", "requirements.txt", "setup.py", "Pipfile"],
		"dirs": [],
		"template": "python.gitignore",
	},
	{
		"name": "prisma",
		"files": [],
		"dirs": ["prisma"],
		"template": "prisma.gitignore",
	},
	{
		"name": "docker",
		"files": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"],
		"dirs": [],
		"template": "docker.gitignore",
	},
	{
		"name": "go",
		"files": ["go.mod"],
		"dirs": [],
		"template": "go.gitignore",
	},
	{
		"name": "rust",
		"files": ["Cargo.toml"],
		"dirs": [],
		"template": "rust.gitignore",
	},
]


CRITICAL_PATTERNS = [
	{"pattern": ".env", "reason": "Environment secrets", "severity": "critical"},
	{"pattern": ".env.local", "reason": "Local environment secrets", "severity": "critical"},
	{"pattern": ".env.development.local", "reason": "Development secrets", "severity": "critical"},
	{"pattern": ".env.production.local", "reason": "Production secrets", "severity": "critical"},
	{"pattern": "*.pem", "reason": "Private keys", "severity": "critical"},
	{"pattern": "*.key", "reason": "Private keys", "severity": "critical"},
	{"pattern": "credentials.json", "reason": "API credentials", "severity": "critical"},
	{"pattern": "service-account*.json", "reason": "Service account credentials", "severity": "critical"},
]


TRADEOFFS = [
	{
		"id": "ide-files",
		"question": "Ignore IDE-specific files?",
		"options": [
			{"value": "vscode", "label": "VS Code only", "patterns": [".vscode/"]},
			{"value": "all", "label": "All IDEs", "patterns": [".vscode/", ".idea/", "*.sublime-*"]},
			{"value": "none", "label": "Keep IDE files", "patterns": []},
		],
		"default": "vscode",
	},
	{
		"id": "os-files",
		"question": "Ignore OS-specific files?",
		"options": [
			{"value": "macos", "label": "macOS only", "patterns": [".DS_Store", "._*"]},
			{"value": "all", "label": "All OS (macOS, Windows, Linux)", "patterns": [".DS_Store", "._*", "Thumbs.db", "Desktop.ini", "*~"]},
		],
		"default": "macos",
	},
]


def detect_project_types(project_dir: Path) -> list[str]:
	"""Detect what types of project this is based on files/dirs present."""
	detected = []
	for detector in PROJECT_DETECTORS:
		for filename in detector["files"]:
			if (project_dir / filename).exists():
				detected.append(detector["name"])
				break
		else:
			for dirname in detector["dirs"]:
				if (project_dir / dirname).is_dir():
					detected.append(detector["name"])
					break
	return detected


def parse_gitignore(gitignore_path: Path) -> list[str]:
	"""Parse existing .gitignore and return list of patterns."""
	if not gitignore_path.exists():
		return []
	patterns = []
	with open(gitignore_path, "r") as f:
		for line in f:
			line = line.strip()
			if line and not line.startswith("#"):
				patterns.append(line)
	return patterns


def load_template(template_name: str) -> list[str]:
	"""Load patterns from a template file."""
	template_path = TEMPLATES_DIR / template_name
	if not template_path.exists():
		return []
	return parse_gitignore(template_path)


def get_recommended_patterns(project_types: list[str]) -> dict:
	"""Get recommended patterns based on project types."""
	mandatory = load_template("base.gitignore")

	project_specific = []
	for ptype in project_types:
		for detector in PROJECT_DETECTORS:
			if detector["name"] == ptype:
				patterns = load_template(detector["template"])
				project_specific.extend(patterns)
				break

	macos_patterns = load_template("macos.gitignore")

	return {
		"mandatory": [{"pattern": p, "reason": "Base configuration"} for p in mandatory],
		"projectSpecific": [{"pattern": p, "reason": f"Project: {', '.join(project_types)}"} for p in project_specific],
		"macos": [{"pattern": p, "reason": "macOS system files"} for p in macos_patterns],
	}


def check_missing_critical(existing_patterns: list[str], project_dir: Path) -> list[dict]:
	"""Check for critical patterns that are missing from .gitignore."""
	missing = []

	for critical in CRITICAL_PATTERNS:
		pattern = critical["pattern"]
		pattern_covered = False
		for existing in existing_patterns:
			if existing == pattern:
				pattern_covered = True
				break
			if pattern.startswith(".env") and existing == ".env*":
				pattern_covered = True
				break
			if existing.startswith("*") and pattern.endswith(existing[1:]):
				pattern_covered = True
				break

		if not pattern_covered:
			if "*" in pattern:
				import glob
				matches = list(project_dir.glob(pattern))
				if matches:
					missing.append({
						"pattern": pattern,
						"severity": critical["severity"],
						"reason": critical["reason"],
						"files_at_risk": [str(m.relative_to(project_dir)) for m in matches[:5]],
					})
			else:
				if (project_dir / pattern).exists():
					missing.append({
						"pattern": pattern,
						"severity": critical["severity"],
						"reason": critical["reason"],
						"files_at_risk": [pattern],
					})

	return missing


def analyze_project(project_dir: Path) -> dict:
	"""Main analysis function. Returns comprehensive JSON output."""
	gitignore_path = project_dir / ".gitignore"

	project_types = detect_project_types(project_dir)
	existing_patterns = parse_gitignore(gitignore_path)
	recommended = get_recommended_patterns(project_types)
	missing = check_missing_critical(existing_patterns, project_dir)

	output = {
		"projectDir": str(project_dir),
		"projectTypes": project_types,
		"existingGitignore": {
			"exists": gitignore_path.exists(),
			"patterns": existing_patterns,
		},
		"recommended": recommended,
		"tradeoffs": TRADEOFFS,
		"missing": missing,
	}

	return output


def main():
	if len(sys.argv) > 1:
		project_dir = Path(sys.argv[1]).resolve()
	else:
		project_dir = Path.cwd()

	if not project_dir.is_dir():
		print(json.dumps({"error": f"Not a directory: {project_dir}"}))
		sys.exit(1)

	result = analyze_project(project_dir)
	print(json.dumps(result, indent=2))


if __name__ == "__main__":
	main()
