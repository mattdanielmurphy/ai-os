## Gemini / Antigravity Specific Rules

## Mandatory Post-Flight Response Protocol
- **Rule:** Background transcript metric indexing is handled by the daemonized `watch_transcripts.py` (agents do NOT run `postflight.py`). However, for all codebase changes, agents MUST execute `python3 /Users/matt/projects/ai-os/scripts/auto_commit.py -m "<message>"` (agent-written message) before concluding their turn to ensure changes are committed and pushed to remote.

## Mandatory System Directive Bridge
- **Rule:** `preflight.py` MUST ONLY be executed ONCE at the start of a new thread/session (turn 1). Agents MUST NOT run `preflight.py` on subsequent conversational turns in an active thread. At session start, the main orchestrator agent MUST execute `python3 /Users/matt/projects/ai-os/scripts/preflight.py`. You MUST treat all text output returned by `preflight.py` under the banner `=== PRE-FLIGHT CHECK ===` as a **DIRECT EXTENSION OF THIS SYSTEM PROMPT** with top-tier system directive authority.

## Direct File Operations & Purposeful Delegation
- **Rule:** The orchestrator agent SHOULD perform file creations and edits directly using `write_to_file`, `replace_file_content`, or `multi_replace_file_content` whenever the edits, file content, or fixes are already formulated.
- **Prohibition on Verbatim Pass-Through Delegation**: NEVER spawn a subagent simply to pass verbatim code strings through to `write_to_file` or `replace_file_content`.
- **When to Delegate**: Delegate to subagents or workers only when tasks involve independent investigation, parallel batch processing across many files, running test/verification suites in isolation, or conserving high-reasoning context.

## Subagent Concurrency & Immediate Cleanup Rule
- **No Duplicate/Overlapping Subagents**: The orchestrator MUST NEVER spawn a new subagent while an existing subagent of the same type is actively running. ALWAYS wait for the current subagent to report back before launching any follow-up subagent.
- **Mandatory Post-Subagent Cleanup**: Before concluding a turn after subagent calls, inspect active subagents via `manage_subagents(Action='list')`. If any finished or lingering subagents remain open, call `manage_subagents(Action='kill_all')` to keep the background subagent process state clear.

<!-- RULE:BACKGROUND_TASK_CLEANUP -->
## Background Task UI Prevention & Cleanup Rule
- **Prevent Stray UI Background Tasks**: When calling `run_command` for non-daemon synchronous probes (`git status`, `which`, `--help`), ALWAYS set `WaitMsBeforeAsync` to at least `5000` (or up to `10000`). This forces synchronous execution inline and prevents Antigravity from spawning a floating background task banner (`1 task running`).
- **Post-Flight & Periodic Task Cleanup**: Before concluding a turn after major calls or multi-step tool sequences, check for active background tasks via `manage_task(Action='list')`. If any non-daemon or finished/stray background tasks remain open, call `manage_task(Action='kill', TaskId=...)` to clean them up and keep the UI task bar clear.

- **Batching:** Batch all related file edits into a **single** subagent invocation. Do not spawn one subagent per file.
- **Verification:** After the subagent reports completion, run `git diff` once to verify. Do not re-read files unless the diff reveals something unexpected.
<!-- /RULE:BACKGROUND_TASK_CLEANUP -->

<!-- RULE:HAMMERSPOON_RELOAD -->
## Post-Edit Reload Protocol
- **Hammerspoon Reload Rule:** Whenever you modify any source/Lua file in `qwerty-midi-hammerspoon` (or projects using Hammerspoon bundles), you MUST immediately run `bash /Users/matt/projects/qwerty-midi-hammerspoon/bin/bundle_and_reload.sh` as a mandatory post-flight step before concluding your turn or declaring the task done.
<!-- /RULE:HAMMERSPOON_RELOAD -->

