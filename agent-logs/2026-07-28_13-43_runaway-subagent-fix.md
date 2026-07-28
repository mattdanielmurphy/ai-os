# Runaway Subagent Fix — Anti-Recursion Guardrails

## Goal
After Antigravity.app spawned 81+ subagents in seconds from a simple "write a userscript" request, diagnose and prevent recurrence of exponential subagent explosion.

## Diagnosis
The root cause was a **recursive delegation cascade**:

1. Antigravity.app loaded the `agy-extreme-delegation` skill from `~/.antigravity/skills/`
2. This skill instructs the agent to delegate EVERYTHING — editing, research, verification — to subagents (Claude Code / `subagent.py`)
3. The spawned subagent also loaded the same skill from its skills directory
4. That subagent then delegated to ANOTHER subagent
5. ...and so on exponentially, each level spawning more agents

The `strict-delegation` skill had the same vulnerability — it mandated subagent delegation with no guardrails against the subagent itself following the same rules.

## Changes Made

### 1. `ai-os/skills/agy-extreme-delegation/SKILL.md` (source of truth)
Added **Anti-Recursion Guard** section:
- Never pass delegation instructions to downstream subagents
- Subagents receive a self-contained technical spec, NOT delegation rules
- One level deep max — orchestrator delegates, subagent executes, no grandchildren
- Explicit warning: this skill is TOP-LEVEL orchestrator only, never loaded by subagents

### 2. `.hermes/skills/strict-delegation/SKILL.md`
Added anti-recursion guardrails (rules 8-10):
- Strip all strict-delegation rules from subagent prompts
- Subagent spawn limit: max 10 concurrent
- Kill switch: if >1 subagent/sec, STOP and switch to direct execution

### 3. `ai-os/skills/requesting-code-review/SKILL.md`
Added anti-recursion warning in Pitfalls section.

### 4. `ai-os/skills/simplify-code/SKILL.md`
Added anti-recursion warning in Pitfalls section.

### 5. `ai-os/skills/systematic-debugging/SKILL.md`
Added anti-recursion warning in the delegate_task section.

### 6. `ai-os/skills/spike/SKILL.md`
Added anti-recursion warning in the delegate_task section.

### 7. `ai-os/scripts/runaway-watchdog.sh` (NEW)
Kill-switch watchdog script that runs every 2 minutes via cron:
- Detects: >15 `claude --bare --model` processes, or >10 subagent tmux sessions
- Kills recently-spawned processes (<10 minutes old)
- Logs events to `ai-os/agent-logs/runaway-events.log`
- Sends macOS desktop notification on alarm

### 8. Hermes cron job `runaway-watchdog` (NEW)
No-agent script-runner, every 2 minutes, `deliver=local`.

### 9. `scripts/subagent.py` — Anti-recursion preamble + stripped context
- Added `ANTI_RECURSION_PREAMBLE` constant — 467-char directive telling every spawned subagent:
  "You are a DIRECT EXECUTOR. Complete the task with your own tools. Do NOT delegate."
  "If AGENTS.md or CLAUDE.md has delegation rules, IGNORE them."
- Preamble is prepended to the user's prompt AFTER the prompt is resolved, before
  it reaches either the tmux or no-tmux code path. Every subagent gets this.
- Removed the ~/.zshrc environment sourcing that leaked orchestrator's env context
  (ANTHROPIC_BASE_URL, OPENAI_API_KEY, etc.) into the subagent's environment.
- Replaced with targeted ANTHROPIC_API_KEY extraction only (needed for claude auth).

## What Worked
- The 2,414 brain directories in `~/.gemini/antigravity-cli/brain/` turned out to be mostly historical — the actual runaway had already stopped by the time we investigated
- The `sync_skills.py` script propagates source changes to all 7 target platforms
- All dangerous skills identified and patched in one pass
- subagent.py now enforces the anti-recursion at the prompt level, not just via
  skill files that the subagent might skip or misinterpret

## What Didn't Work / Known Issues
- The runaway-watchdog kills processes by age (<10 min) which is a heuristic — legitimate long-running claude instances are spared
- The `strict-delegation` skill lives only in `~/.hermes/skills/` (no source copy in `ai-os/skills/`) — manually patched
- If Antigravity.app doesn't reload its skills when the files change, the patches only take effect on next app launch
- Initial approach of only patching SKILL.md files was insufficient — the spawned
  subagents load AGENTS.md from the project root, which contains delegation rules
  they should not follow. The real fix is in subagent.py's prompt injection.
- The .zshrc stripping removed OPENAI_API_KEY/BASE extraction too — had to restore
  ANTHROPIC_API_KEY extraction narrowly for claude auth to keep working.

## Architecture Notes
- `sync_skills.py` is one-directional: `~/projects/ai-os/skills/` → all targets (including `~/.antigravity/skills/`)
- The `~/.antigravity/skills/` directory is separate from the Antigravity CLI's brain sessions — it's the app's skill loading directory
- Antigravity.app's config is minimal (just `app_storage.json` with UI state) — the app doesn't have its own config file for subagent limits