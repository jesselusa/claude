#!/usr/bin/env bash
# install-learning-agent.sh
# Installs the learning-agent launchd job so it runs daily at 9am.
#
# UNINSTALL:
#   launchctl unload ~/Library/LaunchAgents/com.jesselusa.learning-agent.plist
#   rm ~/Library/LaunchAgents/com.jesselusa.learning-agent.plist

set -euo pipefail

PLIST_SRC="$(cd "$(dirname "$0")" && pwd)/learning-agent.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/com.jesselusa.learning-agent.plist"
LOG_DIR="$HOME/.claude/learning-agent"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Ensure LaunchAgents directory exists
mkdir -p "$HOME/Library/LaunchAgents"

# Unload existing job if already loaded (ignore errors if not loaded)
launchctl unload "$PLIST_DEST" 2>/dev/null || true

# Copy plist to LaunchAgents
cp "$PLIST_SRC" "$PLIST_DEST"

# Load the job
launchctl load "$PLIST_DEST"

echo "Learning agent installed. Runs daily at 9am."
