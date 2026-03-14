#!/usr/bin/env python3
"""
Rename files to follow naming convention: Source-Title-date.ext

Usage:
    python3 rename-files.py --list [directory]        # Output JSON suggestions
    python3 rename-files.py --list --new-only [dir]   # Skip previously processed
    python3 rename-files.py --rename [directory]      # Execute renames
    python3 rename-files.py --rename --dry-run        # Preview renames
    python3 rename-files.py --rename --force          # Overwrite existing
    python3 rename-files.py --record-skip <file>      # Record file as skipped
    python3 rename-files.py --record-rename <old> <new>  # Record rename
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# History file location
HISTORY_FILE = Path.home() / ".claude" / "cleanup-history.json"

# Known abbreviations (kept uppercase)
KNOWN_ABBREVIATIONS = {
	# Consulting
	"BCG", "MCKINSEY", "BAIN", "DELOITTE", "PWC", "EY", "KPMG", "ATK",
	# Government
	"FBI", "CIA", "NASA", "EPA", "FDA", "SEC", "FTC", "IRS", "DOJ", "DOD",
	# Finance
	"JPM", "GS", "MS", "CITI", "BOA", "HSBC", "UBS", "CS", "DB", "BNP",
	# Tech
	"MSFT", "GOOG", "AAPL", "META", "AMZN", "IBM", "NVDA", "TSLA",
	# Other
	"MIT", "NYU", "UCLA", "USC", "HBS", "WSJ", "NYT", "BBC", "CNN",
}

# Month mappings
MONTHS = {
	"jan": "January", "january": "January",
	"feb": "February", "february": "February",
	"mar": "March", "march": "March",
	"apr": "April", "april": "April",
	"may": "May",
	"jun": "June", "june": "June",
	"jul": "July", "july": "July",
	"aug": "August", "august": "August",
	"sep": "September", "sept": "September", "september": "September",
	"oct": "October", "october": "October",
	"nov": "November", "november": "November",
	"dec": "December", "december": "December",
}


def load_history() -> dict:
	"""Load history from file."""
	if HISTORY_FILE.exists():
		try:
			with open(HISTORY_FILE) as f:
				return json.load(f)
		except (json.JSONDecodeError, IOError):
			pass
	return {"version": 1, "files": {}}


def save_history(history: dict) -> None:
	"""Save history to file."""
	HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
	with open(HISTORY_FILE, "w") as f:
		json.dump(history, f, indent=2)


def record_action(filepath: str, action: str, new_name: Optional[str] = None) -> None:
	"""Record an action in history."""
	history = load_history()
	path = Path(filepath)

	try:
		mtime = path.stat().st_mtime if path.exists() else None
	except OSError:
		mtime = None

	history["files"][str(path.resolve())] = {
		"mtime": mtime,
		"originalName": path.name,
		"action": action,
		"newName": new_name,
		"processedAt": datetime.now().isoformat(),
	}
	save_history(history)


def is_in_history(filepath: Path, history: dict) -> bool:
	"""Check if file is in history and hasn't changed."""
	resolved = str(filepath.resolve())
	if resolved not in history.get("files", {}):
		return False

	entry = history["files"][resolved]
	try:
		current_mtime = filepath.stat().st_mtime
		if entry.get("mtime") == current_mtime:
			return True
	except OSError:
		pass

	return False


def to_pascal_case(text: str) -> str:
	"""Convert text to PascalCase."""
	if text.upper() in KNOWN_ABBREVIATIONS:
		return text.upper()

	words = re.split(r"[_\-\s]+", text)
	result = []
	for word in words:
		if word:
			if word.upper() in KNOWN_ABBREVIATIONS:
				result.append(word.upper())
			else:
				result.append(word.capitalize())
	return "".join(result)


def extract_date(filename: str) -> tuple[Optional[str], str, str]:
	"""Extract date from filename."""
	name = Path(filename).stem

	# Pattern: YYYY-MM-DD or YYYY/MM/DD
	match = re.search(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", name)
	if match:
		year, month, day = match.groups()
		return f"{year[2:]}{month.zfill(2)}{day.zfill(2)}", "full", "high"

	# Pattern: DD-MM-YYYY or DD/MM/YYYY (European)
	match = re.search(r"(\d{1,2})[-/](\d{1,2})[-/](\d{4})", name)
	if match:
		day, month, year = match.groups()
		if int(month) <= 12 and int(day) <= 31:
			return f"{year[2:]}{month.zfill(2)}{day.zfill(2)}", "full", "medium"

	# Pattern: YYYYMMDD
	match = re.search(r"(?<!\d)(\d{4})(\d{2})(\d{2})(?!\d)", name)
	if match:
		year, month, day = match.groups()
		if int(month) <= 12 and int(day) <= 31:
			return f"{year[2:]}{month}{day}", "full", "high"

	# Pattern: Q1 2024, Q1-2024, 2024 Q1, 2024-Q1
	match = re.search(r"Q([1-4])[\s\-_]*(\d{4})|(\d{4})[\s\-_]*Q([1-4])", name, re.I)
	if match:
		if match.group(1):
			quarter, year = match.group(1), match.group(2)
		else:
			year, quarter = match.group(3), match.group(4)
		return f"{year}-Q{quarter}", "quarter", "high"

	# Pattern: Month YYYY or YYYY Month
	for month_str, month_name in MONTHS.items():
		pattern = rf"(?<![a-z]){month_str}[\s\-_]*(\d{{4}})|(\d{{4}})[\s\-_]*{month_str}(?![a-z])"
		match = re.search(pattern, name, re.I)
		if match:
			year = match.group(1) or match.group(2)
			return f"{year}-{month_name}", "month", "high"

	# Pattern: Just YYYY (4 digit year between 1990-2099)
	match = re.search(r"(?<!\d)(19\d{2}|20\d{2})(?!\d)", name)
	if match:
		return match.group(1), "year", "medium"

	return None, "none", "low"


def extract_name_pattern(text: str) -> tuple[Optional[str], str]:
	"""Detect if text contains a person's name pattern."""
	common_words = {
		"report", "document", "file", "form", "scan", "statement", "invoice",
		"receipt", "letter", "memo", "note", "draft", "final", "copy", "input",
		"output", "data", "info", "list", "summary", "analysis", "review",
		"foods", "inc", "corp", "llc", "ltd", "company", "group", "services",
		"tax", "organizer", "unknown", "untitled", "new", "old", "top", "best",
	}

	match = re.match(r"^([a-z]+)[_]([a-z]+)", text, re.I)
	if match:
		first, last = match.groups()
		if (len(first) >= 3 and len(last) >= 3 and
			first.lower() not in common_words and
			last.lower() not in common_words):
			return f"{last.capitalize()}{first.capitalize()}", "medium"

	match = re.match(r"^([A-Z][a-z]+)([A-Z][a-z]+)(?:-|$)", text)
	if match:
		part1, part2 = match.groups()
		if (part1.lower() not in common_words and
			part2.lower() not in common_words):
			return f"{part1}{part2}", "high"

	return None, "low"


def extract_source(filename: str) -> tuple[Optional[str], str]:
	"""Extract source from filename."""
	stem = Path(filename).stem
	name_upper = stem.upper()

	for abbr in KNOWN_ABBREVIATIONS:
		if name_upper.startswith(abbr) and (len(name_upper) == len(abbr) or not name_upper[len(abbr)].isalpha()):
			return abbr, "high"

	person_name, confidence = extract_name_pattern(stem)
	if person_name and confidence != "low":
		return person_name, confidence

	return None, "low"


def extract_title(filename: str, source: Optional[str], date_str: Optional[str]) -> tuple[str, str]:
	"""Extract and format the title portion of the filename."""
	name = Path(filename).stem

	if source:
		pattern = rf"^{re.escape(source)}[\s\-_]*"
		name = re.sub(pattern, "", name, flags=re.I)

	date_patterns = [
		r"\d{4}[-/]\d{1,2}[-/]\d{1,2}",
		r"\d{1,2}[-/]\d{1,2}[-/]\d{4}",
		r"\d{8}",
		r"Q[1-4][\s\-_]*\d{4}",
		r"\d{4}[\s\-_]*Q[1-4]",
		r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*[\s\-_]*\d{4}",
		r"\d{4}[\s\-_]*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*",
		r"(?<!\d)(19|20)\d{2}(?!\d)",
	]

	for pattern in date_patterns:
		name = re.sub(pattern, "", name, flags=re.I)

	if source and re.match(r"^[A-Z][a-z]+[A-Z][a-z]+$", source):
		name = re.sub(r"[a-z]+[_\-][a-z]+", "", name, flags=re.I)

	name = re.sub(r"[\s\-_]+", " ", name).strip()

	if not name:
		return "", "low"

	cleaned = re.sub(r"[\s\-_\(\)\[\]]+", "", name)
	if len(cleaned) < 2 or cleaned.isdigit():
		return "", "low"

	return to_pascal_case(name), "high"


def is_already_formatted(stem: str) -> bool:
	"""Check if stem already follows Source-Title-date convention."""
	parts = stem.split("-")

	if len(parts) < 2:
		return False

	last = parts[-1]

	def is_pascal_or_abbr(s: str) -> bool:
		if s.upper() in KNOWN_ABBREVIATIONS:
			return True
		return bool(re.match(r"^[A-Z][a-zA-Z0-9]*$", s))

	if re.match(r"^\d{6}$", last):
		non_date_parts = parts[:-1]
		return all(is_pascal_or_abbr(p) for p in non_date_parts)

	if len(parts) >= 3 and re.match(r"^\d{4}$", parts[-2]) and re.match(r"^Q[1-4]$", last):
		non_date_parts = parts[:-2]
		return all(is_pascal_or_abbr(p) for p in non_date_parts)

	if len(parts) >= 3 and re.match(r"^\d{4}$", parts[-2]) and last in MONTHS.values():
		non_date_parts = parts[:-2]
		return all(is_pascal_or_abbr(p) for p in non_date_parts)

	if re.match(r"^(19|20)\d{2}$", last):
		non_date_parts = parts[:-1]
		if non_date_parts and all(is_pascal_or_abbr(p) for p in non_date_parts):
			return True

	return False


def get_extension(filepath: Path) -> str:
	"""Get file extension, handling compound extensions."""
	name = filepath.name
	compound_exts = [".tar.gz", ".tar.xz", ".tar.bz2"]
	for ext in compound_exts:
		if name.lower().endswith(ext):
			return ext
	return filepath.suffix


def is_trivial_change(original: str, suggested: str, source: Optional[str], title: str, date_str: Optional[str]) -> bool:
	"""Determine if the change is trivial (auto-renameable)."""
	orig_stem = Path(original).stem
	sugg_stem = Path(suggested).stem

	orig_normalized = re.sub(r"[_\s]+", "-", orig_stem).lower()
	sugg_normalized = sugg_stem.lower()

	if orig_normalized == sugg_normalized:
		return True

	orig_no_date = re.sub(r"\d{6,8}", "", orig_normalized)
	sugg_no_date = re.sub(r"\d{6,8}", "", sugg_normalized)
	if orig_no_date == sugg_no_date:
		return True

	if not date_str:
		return False

	if not title or title.lower() == orig_stem.lower():
		return False

	return True


def analyze_file(filepath: Path) -> Optional[dict]:
	"""Analyze a file and suggest a new name."""
	filename = filepath.name
	ext = get_extension(filepath)

	if ext and len(ext) > 1:
		stem = filename[:-len(ext)]
	else:
		stem = filepath.stem

	if is_already_formatted(stem):
		return None

	source, source_confidence = extract_source(stem + ".tmp")
	date_str, date_format, date_confidence = extract_date(stem + ".tmp")
	title, title_confidence = extract_title(stem + ".tmp", source, date_str)

	parts = []
	if source:
		parts.append(source)
	if title:
		parts.append(title)
	if date_str:
		parts.append(date_str)

	if not parts:
		return None

	if len(parts) == 1 and not date_str:
		return None

	suggested = "-".join(parts) + ext

	if suggested == filename:
		return None

	is_auto = is_trivial_change(filename, suggested, source, title, date_str)

	if not is_auto and date_confidence == "high" and (source_confidence == "high" or title_confidence == "high"):
		is_auto = True

	return {
		"original": filename,
		"suggested": suggested,
		"classification": "auto" if is_auto else "needs-review",
		"source": source,
		"title": title if title else None,
		"date": date_str,
		"path": str(filepath),
	}


def list_suggestions(directory: Path, recursive: bool = False, new_only: bool = False) -> dict:
	"""List rename suggestions for files in directory."""
	history = load_history() if new_only else {"files": {}}

	auto = []
	needs_review = []
	already_processed = 0
	total_files = 0

	if recursive:
		files = directory.rglob("*")
	else:
		files = directory.glob("*")

	for filepath in files:
		if filepath.is_file() and not filepath.name.startswith("."):
			total_files += 1

			if new_only and is_in_history(filepath, history):
				already_processed += 1
				continue

			result = analyze_file(filepath)
			if result:
				if result["classification"] == "auto":
					auto.append(result)
				else:
					needs_review.append(result)

	return {
		"auto": auto,
		"needsReview": needs_review,
		"alreadyProcessed": already_processed,
		"newFiles": total_files - already_processed,
		"totalFiles": total_files,
	}


def execute_renames(
	suggestions: list[dict],
	dry_run: bool = False,
	force: bool = False,
) -> dict:
	"""Execute file renames."""
	results = {
		"renamed": [],
		"skipped": [],
		"errors": [],
	}

	for item in suggestions:
		src = Path(item["path"])
		dst = src.parent / item["suggested"]

		if dst.exists() and not force:
			results["skipped"].append({
				"file": item["original"],
				"reason": "target exists",
			})
			continue

		if dry_run:
			results["renamed"].append({
				"from": item["original"],
				"to": item["suggested"],
				"dry_run": True,
			})
		else:
			try:
				src.rename(dst)
				record_action(str(dst), "renamed", item["suggested"])
				results["renamed"].append({
					"from": item["original"],
					"to": item["suggested"],
				})
			except Exception as e:
				results["errors"].append({
					"file": item["original"],
					"error": str(e),
				})

	return results


def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description="Rename files to Source-Title-date.ext format"
	)
	parser.add_argument(
		"directory",
		nargs="?",
		default=str(Path.home() / "Downloads"),
		help="Target directory (default: ~/Downloads)",
	)
	parser.add_argument("--list", action="store_true", help="Output JSON suggestions")
	parser.add_argument("--rename", action="store_true", help="Execute renames")
	parser.add_argument("--dry-run", action="store_true", help="Preview changes")
	parser.add_argument("--force", action="store_true", help="Overwrite existing")
	parser.add_argument("--recursive", action="store_true", help="Process subdirs")
	parser.add_argument("--new-only", action="store_true", help="Skip processed files")
	parser.add_argument("--record-skip", metavar="FILE", help="Record file as skipped")
	parser.add_argument("--record-rename", nargs=2, metavar=("OLD", "NEW"), help="Record rename")
	parser.add_argument("--clear-history", action="store_true", help="Clear history")

	args = parser.parse_args()

	if args.clear_history:
		if HISTORY_FILE.exists():
			HISTORY_FILE.unlink()
		print(json.dumps({"status": "history cleared"}))
		return

	if args.record_skip:
		record_action(args.record_skip, "skipped")
		print(json.dumps({"status": "recorded", "action": "skipped", "file": args.record_skip}))
		return

	if args.record_rename:
		old, new = args.record_rename
		record_action(old, "renamed", new)
		print(json.dumps({"status": "recorded", "action": "renamed", "from": old, "to": new}))
		return

	directory = Path(args.directory).expanduser()
	if not directory.is_dir():
		print(json.dumps({"error": f"Not a directory: {directory}"}))
		sys.exit(1)

	result = list_suggestions(directory, args.recursive, args.new_only)

	if args.list:
		print(json.dumps(result, indent=2))
	elif args.rename:
		all_suggestions = result["auto"] + result["needsReview"]
		rename_results = execute_renames(all_suggestions, dry_run=args.dry_run, force=args.force)
		print(json.dumps(rename_results, indent=2))
	else:
		all_suggestions = result["auto"] + result["needsReview"]
		if not all_suggestions:
			print("No files to rename.")
			if result["alreadyProcessed"] > 0:
				print(f"({result['alreadyProcessed']} files previously processed)")
		else:
			print(f"Auto-rename ({len(result['auto'])} files):")
			for item in result["auto"]:
				print(f"  {item['original']}")
				print(f"    -> {item['suggested']}")

			if result["needsReview"]:
				print(f"\nNeeds review ({len(result['needsReview'])} files):")
				for item in result["needsReview"]:
					print(f"  {item['original']}")
					print(f"    -> {item['suggested']}")


if __name__ == "__main__":
	main()
