# 2026-07-10 LiteLLM Launch Agent Monitoring

## Goal
Configure a macOS Launch Agent for LiteLLM that runs the server inside a `tmux` session for easy console monitoring, attaching/detaching, and restarting.

## Changes Made
- **Created run wrapper script**: Created [run_litellm.sh](file:///Users/matt/litellm/run_litellm.sh) to source the shell environment (providing `OPENROUTER_API_KEY`) and launch LiteLLM inside a detached tmux session named `litellm`.
- **Created Launch Agent**: Created [com.mattmurphy.litellm.plist](file:///Users/matt/Library/LaunchAgents/com.mattmurphy.litellm.plist) to handle loading and auto-relaunching.
- **Updated Environment & Feature Ledgers**: Added launch agent row to [MAC_ENVIRONMENT.md](file:///Users/matt/projects/ai-os/docs/MAC_ENVIRONMENT.md) and documented the capability in [FEATURES.md](file:///Users/matt/projects/ai-os/docs/FEATURES.md).
- **Completed Feature File**: Moved [monitor-litellm-launch-agent.md](file:///Users/matt/projects/ai-os/.devtool/features/monitor-litellm-launch-agent.md) to `review` status.

## What Worked
- Running a loop in `run_litellm.sh` checking `tmux has-session -t litellm` allows launchd to accurately trace if the service is running, while still housing the server process in standard tmux.

## What Didn't Work / Known Issues
- Sourcing `.zshrc` inside non-interactive shells can sometimes print warnings if the shell configuration has interactive TUI commands, but it works reliably for environment extraction here.

## Architecture Notes
- Running services in tmux controlled by launchd is a robust way to have daemonized processes that are still interactive.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity-cli/brain/d22d7b8d-92a7-4c46-8230-a8e281903fe9/.system_generated/logs/transcript.jsonl)

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity-cli/brain/d22d7b8d-92a7-4c46-8230-a8e281903fe9/.system_generated/logs/transcript.jsonl)
