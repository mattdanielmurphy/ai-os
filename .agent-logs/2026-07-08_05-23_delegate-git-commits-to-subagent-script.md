## Goal
Delegate git commits to a cheaper subagent or script to conserve premium tokens for the costly orchestrator agent.

## User Feedback & Decisions
- Move the git commit generation to a subagent script.
- Execute it seamlessly within the auto-commit protocol.

## Changes Made
- **[NEW] [auto_commit.py](file:///Users/matt/projects/ai-os/scripts/auto_commit.py)**: Python utility that stages changes, gets the cached diff, queries the local LiteLLM proxy (`localhost:8082`) using the low-cost `claude-haiku*` model (DeepSeek V4 Flash) to generate a concise message, and executes `git commit`.
- **[MODIFY] [CLAUDE.md](file:///Users/matt/projects/ai-os/CLAUDE.md)**: Updated `<AUTO_COMMIT_PROTOCOL>` to invoke the new script rather than manually generating messages and running `git commit`.

## What Worked
- Direct completions API requests to `http://localhost:8082/v1/chat/completions` run successfully and are extremely fast compared to launching a full Claude Code terminal session.
- Increasing `max_tokens` to `400` ensures that thinking/reasoning tokens do not truncate the generated git commit message.

## What Didn't Work / Known Issues
- Initializing `max_tokens` at `100` resulted in truncated messages like `[Auto-Com` because reasoning/thinking tokens consumed most of the budget.

## Architecture Notes
- Local LiteLLM proxy is running on port `8082`.
- `claude-haiku*` maps to `openrouter/deepseek/deepseek-v4-flash`, which returns both reasoning and content blocks. Safely extracting `content` requires handling `NoneType` values since the first chunks of reasoning completions might contain `None` in the content key.
