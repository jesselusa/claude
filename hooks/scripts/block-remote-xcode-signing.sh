#!/bin/bash
# Block Xcode signing / App Store upload commands unless this session is a
# local interactive terminal on the dev Mac. Remote-control and cloud
# sessions can't complete Apple ID / keychain auth — xcodebuild
# -exportArchive fails with "Failed to Use Accounts" only AFTER a full
# archive build, wasting minutes. Fail fast with a clear reason instead.
#
# Local dev is defined as BOTH:
#   1. CLAUDE_CODE_ENTRYPOINT is a local Claude Code surface — "cli" (terminal)
#      or "claude-desktop" (the Mac desktop app). Both run on this Mac with
#      access to the GUI keychain. Cloud/remote-control daemons report other
#      entrypoints and are excluded.
#   2. A GUI console user is logged into this Mac (cloud containers and
#      headless hosts fail this; signing needs the GUI keychain anyway).
#      This is the real local-machine guard — #1 just rules out non-GUI surfaces.

input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // empty')

case "$cmd" in
  *exportArchive*|*altool*|*notarytool*) ;;
  *) exit 0 ;;
esac

console_user=$(stat -f%Su /dev/console 2>/dev/null)
case "$CLAUDE_CODE_ENTRYPOINT" in
  cli|claude-desktop) entry_ok=1 ;;
  *) entry_ok=0 ;;
esac
if [ "$entry_ok" = 1 ] && [ -n "$console_user" ] && [ "$console_user" != "root" ] && [ "$console_user" != "_windowserver" ]; then
  exit 0
fi

cat <<'EOF'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Xcode signing / App Store upload is blocked outside a local dev terminal. Remote control and cloud sessions cannot complete Apple ID / keychain auth (exportArchive fails with 'Failed to Use Accounts' after a full archive). Run this from Claude Code in a terminal on the Mac."}}
EOF
exit 0
