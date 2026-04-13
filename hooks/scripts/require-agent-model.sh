#!/usr/bin/env bash
# PreToolUse hook for the Agent tool — requires an explicit `model` param so
# subagent calls follow the Model Routing rule in CLAUDE.md (Sonnet for
# execution/search, Opus for reasoning/review). Exit 1 blocks; Claude retries
# with the model set.

input=$(cat)
model=$(echo "$input" | jq -r '.tool_input.model // empty')
subagent=$(echo "$input" | jq -r '.tool_input.subagent_type // "general-purpose"')
desc=$(echo "$input" | jq -r '.tool_input.description // ""')

if [ -z "$model" ]; then
	cat >&2 <<EOF
🛑 Agent call missing required \`model\` param (subagent_type: $subagent, description: "$desc").

Per CLAUDE.md Model Routing:
  • model: "sonnet"  → execution, search, mechanical work
                       (Explore, pr-comment-resolver, bug-reproduction-validator,
                        framework-docs-researcher, git-history-analyzer, etc.)
  • model: "opus"    → reasoning, planning, review
                       (Plan, architecture-strategist, kieran-*-reviewer,
                        spec-flow-analyzer, performance-oracle, security-sentinel)

Rule of thumb: finding/doing → sonnet. Deciding/reviewing → opus.
Default to sonnet when unsure.

Retry the Agent call with an explicit \`model\` param.
EOF
	exit 1
fi

# Guard against haiku for code work (CLAUDE.md: "Never haiku for code work")
if [ "$model" = "haiku" ]; then
	echo "🛑 CLAUDE.md forbids haiku for code work. Use sonnet (execution) or opus (reasoning)." >&2
	exit 1
fi

exit 0
