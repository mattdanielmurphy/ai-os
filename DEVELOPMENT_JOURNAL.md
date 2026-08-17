# Development Journal

## 2026-08-16
- **Strict Span-Only Styling Invariant & Multiline Markdown Fix:** Mandated `<span>` tags with `display: block;` exclusively across `thread.md` and custom markdown viewers. Resolved multiline prompt formatting degradation by converting prompt newlines to `<br>` / `<br><br>` within styled `<span>` containers, preserving continuous bubble styling across complex inputs. Updated `.rules/core_safety.md`, `AG_CONTEXT.md`, and compiled all agent rules.
- **Unified Single-Command Planner (`_plan-with-ai-os` / `query_aios.js --plan`):** Consolidated the two-step planning workflow (`generate_planner_prompt.py` + `query_proxima.js`) into a single-step `node ~/projects/ai-os/scripts/query_aios.js --plan "<request>"`. Removed legacy `query_proxima.js` and renamed the global workflow from `/proxima-planner` to `/_plan-with-ai-os`. Automatically inspects git context and matching agent logs, formats and writes `./tmp/planner_prompt.txt`, dispatches the query directly to Perplexity Sonnet Thinking (or ai-os companion), and writes the output to `./tmp/planner_output.txt`. Compiled all agent rules.
- **Default ai-os Model Switched to Grok Thinking:** Set xAI Grok Thinking (`grok46medium`) as the default engine across `query_aios.js`, `apps/gemini-companion/src-tauri/engines/perplexity-engine.js`, Tauri server defaults, `config/rules_config.json`, dynamic prompt compilers, and `/_plan-with-ai-os` workflow.

## 2026-08-13
- **Cost-Aware & Cache-Aware Thread Rotation System:** Implemented `scripts/thread_economics.py` calculating marginal financial breakeven against prompt cache write/read rates, hard context capacity caps (55% safety margin), and 1-hour cache TTL countdowns. Integrated live metrics into `scripts/postflight.py` and `scripts/check_thread_bloat.py`.

## 2026-08-10
- Re-architected Discussions.html into a Milestone & Suggestion tracker focused on user requests, context summaries, and decision resolutions.
- Fixed macOS Finder open link handler and styled clean dark-mode typography.
- Integrated automatic Discussions.html generation into auto_commit.py post-flight pipeline.
- **Production-Ready Discussions.html Generator & Watcher:** Completed `scripts/discussions_html.py` with inline markdown formatting, code folding, agent reply summarization heuristics, and project auto-detection. Integrated HTML rendering into `scripts/watch_transcripts.py` alongside `thread.md`. [[log]](agent-logs/2026-08-10_00-48_discussions-html-production-ready.md)

## 2026-08-09
- **Fix agy Antigravity Models, Labels, and Resolution:** Cleaned `services/agy-proxy/proxy.py` and `~/.hermes/config.yaml` to strictly expose the 8 actual Antigravity models with human-friendly labels (fixing "LOW" capitalization and removing Claude 5 / DeepSeek / Muse Spark / Grok / 3.5 Flash Lite from agy's catalog). Updated `_build_cmd_and_prompt()` to cleanly split base model and `--effort` flags for the `agy` CLI. All 13 tests pass and Hermes WebUI models list is clean without modifying `hermes-webui` source code. [[log]](agent-logs/2026-08-09_19-58_fix-agy-models-and-labels.md)
- **Fixed agy-proxy Real-time Streaming & Timeout Bugs:** Rewrote `_proxy_to_litellm_stream` in `services/agy-proxy/proxy.py` to use `httpx.AsyncClient` with live SSE line-by-line yielding instead of blocking `urllib` in-memory buffering that caused 120s `[Proxy Error]: timed out` crashes. Added model name normalization (`@custom:agy:` / `agy/`), synchronized full lean coding model stack in `~/.hermes/config.yaml`, and verified all 13 unit tests pass. [[log]](agent-logs/2026-08-09_19-22_fix-agy-proxy-streaming-timeout.md)


A running narrative of key decisions, pivots, and direction changes. One entry per session. **Agents MUST append to this at the end of every conversation.**

## 2026-08-05
- **Marked Gemini Userscript as GENERATED & Made It Impossible to Edit:** The ai-os webview userscript (`userscripts/gemini.js`) was a symlink to a generated file from the separate `userscript-bundler` project, but nothing made that clear. Added a `GENERATED FILE — DO NOT EDIT` banner (naming source modules + rebuild command) to the bundler's compiled output, made the compiled file read-only (`chmod 0444`) after each build, renamed the ai-os symlink to `gemini-DO-NOT-EDIT.js`, updated `main.rs` to read it, and documented the full workflow in `docs/memory/userscripts-directory.md` + `AG_CONTEXT.md`. [[log]](agent-logs/2026-08-05_04-15_mark-gemini-userscript-generated.md)
- **2026-08-05**: Reorganized documentation into 6 clear domain boundaries and integrated Quartz 4.0 off-the-shelf Markdown wiki engine accessible via `ai-os wiki` on `http://localhost:3333`.
- **Stripped thread.md Artifact Link Clutter:** Added `clean_agent_content()` to `scripts/gen_conversation_md.py` and expanded unit tests in `tests/test_gen_conversation_md.py`. Automatically cleans redundant `thread.md` / `conversation_response.md` links and orphan prefixes from rendered transcripts. [[log]](agent-logs/2026-08-05_01-24_strip-thread-md-links.md)
- **Robust thread.md Transcript Engine & Test Suite Expansion:** Fixed multi-USER_INPUT turn fragmentation and system tag leaks in `gen_conversation_md.py`, added in-process rendering in `watch_transcripts.py`, resolved syntax error in `triage_task.py`, and expanded unit test suite to 38 tests (all passing in 0.2s). [[log]](agent-logs/2026-08-05_01-13_robust-thread-md-and-unit-tests.md)
- **Comprehensive Script & Service Unit Test Suite:** Created a zero-dependency Python `unittest` suite in `tests/` and root `run_tests.py` covering `gen_conversation_md.py`, `watch_transcripts.py`, `swap_turn.py`, dynamic prompt compilation, triage routing, subagent handoff, precision editing, and the agy proxy. All 33 tests pass in 6ms. [[log]](agent-logs/2026-08-05_00-44_created-test-suite-for-scripts-and-services.md)

## 2026-07-31
- **Resolved agy-mcp model resolution and thread spawning:** Fixed empirical issues with model resolution and verified spawning threads for `gemini-3.6-flash`, `gemini-3.1-pro`, `claude-sonnet-4.6`, `claude-opus-4.6`, and `gpt-oss-120b`. [[log]](agent-logs/2026-07-31_21-22_fix-agy-mcp-models-and-spawning.md)

## 2026-07-27
- **Model-override via `{MODEL=...}` in proxy prompt, and subagent model routing.** Fixed the broken `_resolve_model()` stub in the agy-proxy (dead duplicate loop, wrong docstring, no cross-message stripping). Added `_resolve_model()` calls and `"subagent"` fallback guard in both `run_agy_sync()` and `run_agy_stream()`. Added `"subagent"` to `AVAILABLE_MODELS`. All unit tests pass (7/7). **Requires manual step:** run `hermes config set delegation.model subagent` to enable. [[plan]](plans/model-override-proxy/plan.md) [[log]](agent-logs/2026-07-27_23-29_model-override-proxy.md)
- **Fixed agy-proxy tool support & added agy subagent mode.** The custom agy-proxy on port 8080 was silently dropping `tools` from OpenAI-format requests, breaking `delegate_task` subagents (they couldn't see tool schemas, responded with text only). Added full tool schema support: when tools are present, proxy forwards to the real LiteLLM proxy on 8082 (which supports tool calling natively); when no tools, preserves existing `agy --print` path for Google OAuth quota. Also added `--use-agy` flag to `scripts/subagent.py` to spawn agy in tmux with brain-directory log monitoring. Set `delegation.max_spawn_depth=2`. [[log]](agent-logs/2026-07-27_22-41_agy-proxy-tool-fix-subagent-integration.md)

## 2026-07-25
- **Subagent Tmux Monitoring Integration:** Upgraded `scripts/subagent.py` to launch `claude` subagent calls in dedicated windows inside a `subagents` tmux session (`remain-on-exit on`), providing synchronous live stdout streaming while enabling real-time terminal monitoring. [[log]](agent-logs/2026-07-25_15-30_subagent-tmux-monitoring-integration.md)
- **Subagent Log Monitoring for End Turn:** Updated `scripts/subagent.py` to poll Claude Code JSONL logs for `stop_reason == 'end_turn'`, printing final text response and auto-closing tmux subagent pane upon completion. [[log]](agent-logs/2026-07-25_16-36_subagent-log-monitoring.md)
- **Thread Compactifying & Reset Automation:** Built dynamic token evaluator `scripts/check_thread_bloat.py`, context handoff script `scripts/context_handoff.py`, `/resume` skill (`~/.gemini/config/skills/resume/SKILL.md`), and automated thread reset trigger `scripts/trigger_thread_reset.py`. Archived `thread-compactifying` plan. [[log]](agent-logs/2026-07-25_06-50_thread-compactifying-execution.md)

## 2026-07-24
- **Reverted In-Agent Quota Delta Check:** Removed verbose model-side post-flight quota delta check from `auto_commit.py` and restored quiet `preflight.py` status. Quota delta tracking will be handled natively in `ai-os` app UI/wrapper rather than model context window tools. [[log]](agent-logs/2026-07-24_00-25_quota-preflight-decimal-postflight-delta.md)

## 2026-07-23
- **Quiet Preflight Quota Check:** Updated `scripts/preflight.py` and `AGENTS.md` so that `ag-quota --all -j` checks quota status quietly without outputting raw JSON details into the model context window on every turn. [[log]](agent-logs/2026-07-23_20-35_quiet-preflight-quota-check.md)
- **Clinical Trial Scraper & AI Evaluator Pipeline:** Implemented Bun/TypeScript pipeline under `services/clinical-trials/` querying ClinicalTrials.gov REST API v2, evaluating study eligibility against `context/clinical-profile.md` using Jules/rules engine, outputting Obsidian notes to `Financial/Clinical Trials/`, and dispatching Hermes alerts. [[log]](agent-logs/2026-07-23_16-26_clinical-trial-scraper-pipeline.md)

## 2026-07-20

## 2026-07-22
- **Standard macOS Menu & Shortcuts:** Added full native macOS menu bar (App, File, Edit, View, Actions, Window, Help) and native hotkeys across all windows. See [2026-07-22_04-14_standard-mac-app-menu-shortcuts.md](file:///Users/matt/projects/ai-os/agent-logs/2026-07-22_04-14_standard-mac-app-menu-shortcuts.md).
- **Standard macOS Menu & Shortcuts:** Added full native macOS menu bar (App, File, Edit, View, Actions, Window, Help) and native hotkeys across all windows. See [2026-07-22_04-14_standard-mac-app-menu-shortcuts.md](file:///Users/matt/projects/ai-os/agent-logs/2026-07-22_04-14_standard-mac-app-menu-shortcuts.md).

- **Quota Pre-Flight Check & Minimal-Token Mode Rule:** Added pre-flight quota inspection rule to `AGENTS.md`. Antigravity calls evaluate quota via `ag-quota -j` (or `codexbar status`/`list`) and automatically switch to Minimal-Token Mode (Strict Orchestrator Mode 3) under low quota or rapid burn velocity, delegating code generation to `claude code` or cheap subagents. [[log]](agent-logs/2026-07-22_02-08_preflight-quota-check-minimal-token-mode.md)
- **Gemini Floating Webview Native macOS Decorations & Screen-Bounded Resizing:** Replaced HTML pseudo-toolbar with native macOS window decorations (`appWin.setDecorations(true)`), giving standard title bar and stoplights. Bounded window dimensions dynamically to 80% of `window.screen.availHeight` centered on screen to ensure the bottom edge never goes off screen. [[log]](agent-logs/2026-07-22_02-38_native-decorations-and-screen-bounded-resizing.md)

- **Strategic Pivot: Minimal Fork + litellm Bridge.** Hit breaking point with the current approach — monkey-patching `interruptible_api_call` in `aios_hermes_wrapper.py` plus a separate `sitecustomize.py` for the WebUI is too fragile. Hermes WebUI "cancel" drops thread context, which defeats the purpose of interactive agent loop. Decided to pivot to a **minimal fork of Hermes Agent** that adds agy as a real *provider* (not a faked tool call), with ~30 lines of changes instead of 190 lines of monkey-patching. Fork retains upstream merge compatibility. Architecture: `User → Launcher/Shell Wrapper → Triage → litellm → Model`. Claude Code handles Ctrl+C correctly with full context preservation. [[agent-log]](agent-logs/2026-07-20_00-30_strategic-pivot-minimal-fork-triage.md)
- **Created this dev journal.** Agent logs are too detailed for human consumption. This file is the human-readable timeline. All agents must append here at session end. [[agent-log]](agent-logs/2026-07-20_00-30_strategic-pivot-minimal-fork-triage.md)
- **Phase 1: Split Tauri backend `main.rs` into modules.** Extracted the 3,188-line monolith into 5 focused modules: `types.rs` (148 lines), `pty.rs` (630), `threads.rs` (1,107), `server.rs` (402), `session.rs` (1,142). Main is now 299 lines. Zero behavior changes, clean compile with zero warnings. This makes the codebase debuggable and sets up Phase 2 (cutting unused complexity). [[agent-log]](agent-logs/2026-07-20_00-30_strategic-pivot-minimal-fork-triage.md)
- **Fixed rules-watcher & Improved `la` tool:** Updated `la` to show `oneshot` agents as "watching" and improved `la logs` to find logs in plists. Fixed `rules-watcher` plist. [[agent-log]](agent-logs/2026-07-20_02-15_fix-la-status-and-logs-for-oneshots.md)
- **Fixed rules-watcher Launch Agent & Bidirectional Sync:** Replaced AGENTS.md with a symlink to .gemini/GEMINI.md, upgraded sync script to bidirectional newer-wins, and removed the tmux wrapper from plist to resolve TCC sandbox blocks. [[agent-log]](agent-logs/2026-07-20_01-40_fix-rules-watcher-and-bidirectional-sync.md)
- **Fixed Tauri Backend Bugs:** Resolved the WebSocket host reconnect race via connection IDs, resolved tab switching terminal output interleaving via thread-specific buffer keys, and fixed thread naming/chain resolution pathing. [[agent-log]](agent-logs/2026-07-20_13-38_fix-tauri-backend-bugs.md)

## 2026-07-19

- **Implemented Zero-Fork Hermes Triage Interceptor** (`aios_hermes_wrapper.py`) — monkey-patches `chat_completion_helpers.interruptible_api_call` to inject fake `agy_start` tool calls for coding prompts. TUI works. [[agent-log]](agent-logs/2026-07-19_18-36_implemented-zero-fork-hermes-triage-interceptor.md)
- **Fixed WebUI triage** — the WebUI runs as a separate Python process that never touches the wrapper. Had to create `webui-patches/sitecustomize.py` and set `PYTHONPATH` in hermes-webui `.env` to get the same interception working. This complexity is what triggered the July 20 pivot. [[agent-log]](agent-logs/2026-07-19_22-54_webui-triage-sitecustomize-fix.md)

## 2026-08-09
- **Fix Infinite Span Nesting Bug:** Refactored `gen_conversation_md.py` layout elements from `<span>` to `<div>` and fixed HTML stripping in `extract_user_input` to allow raw HTML/Markdown in prompts. Expanded unit tests in `tests/test_gen_conversation_md.py`. [[log]](agent-logs/2026-08-09_02-57_fix-infinite-span-nesting-bug.md)

- **Phase 2: Cut dead complexity** — Removed prepare_spare_engine, elaborate lsof-based pause/resume loop, execution staging/payload system, hardcoded skills API, browser context, gemini dispatch, thread notes, and recent workspaces. Backend down from ~3,578 to 3,018 lines. All cuts verified against frontend invoke() calls. Phase 3 bugfix prompt saved to .devtool/features/. [[log]](agent-logs/2026-07-20_01-30_phase-2-cut-complexity.md)

## 2026-07-18

- **Hermes Agent GUI Integration** — integrated Hermes WebSocket backend into the Tauri app, with PTY terminal spawning and engine switching. Massive session with many small fixes for websocket races, thread clearing, auto-reconnect, etc. [[logs]](agent-logs/2026-07-18_17-50_Hermes Agent Integration & Bun Migration.md)
- **Migrated Tauri GUI from pnpm to Bun.** [[log]](agent-logs/2026-07-18_19-53_migrate-tauri-to-bun.md)
- **DeepSeek V4 Flash Low Triage System** — set up cheap-model-first routing with handoff to pro models for complex tasks. [[log]](agent-logs/2026-07-18_14-19_deepseek-v4-flash-low-triage.md)

## 2026-07-16

- **Wails Thread Browser** — built a desktop app for searching Hermes SQLite + filesystem transcripts with Mantine UI. [[log]](agent-logs/2026-07-16_00-02_wails-thread-browser.md)

## 2026-07-13

- Fixed context handoff mechanism and terminal output attachment. [[logs]](agent-logs/2026-07-13_02-11_handoff.md)

## 2026-07-11

- Fixes to Gemini thread ingestion, markdown rendering, and orchestrator mode. First session logs appear. [[logs]](agent-logs/)

- **App Reliability & Quick Prompt Fixes:** Added Rust panic hook logging to , deferred thread scanning to when the Coding window is visible, and resolved Quick Prompt context pasting loops. See [agent log](file:///Users/matt/projects/ai-os/agent-logs/2026-07-22_13-26_app-reliability-crash-logging.md).## 2026-07-23

- **Hammerspoon QWERTY MIDI Controller:** Added modular  script to Hammerspoon with global anchoring and key swallowing, and documented it in the Obsidian wiki.
- **Fast-Path Direct Command Execution:** Added `try_direct_execution` in `triage_router.py` to intercept simple OS commands (`open google chrome`, URLs, app launch, process termination) instantly without model latency or starting `agy`. [[log]](agent-logs/2026-07-23_22-21_fast-path-direct-command-execution.md)
- **Gemini Webview Thread Escalation:** Updated `triage_router.py` and `userscripts/gemini.js` so AI queries automatically open a new `gemini.google.com` webview thread with the prompt auto-populated and sent, replacing terminal `agy` CLI output. [[log]](agent-logs/2026-07-23_22-26_gemini-webview-thread-escalation.md)
- **Tauri App Direct IPC Prompt Dispatch:** Added Axum HTTP endpoint `/api/prompt` (`127.0.0.1:3031`) and `pending_prompt.txt` cold-start handler in `tauri-gui/src-tauri` to focus the `ai-os` Gemini webview window and inject/execute prompts of unlimited length directly from CLI. [[log]](agent-logs/2026-07-23_22-35_tauri-app-direct-ipc-prompt-dispatch.md)
- **Native Mac App Cold-Start:** Fixed `triage_router.py` cold-start routine to launch the compiled `/Applications/ai-os.app` bundle via macOS `open` instead of starting `bun run tauri dev`. [[log]](agent-logs/2026-07-23_22-38_launch-native-mac-app-bundle-on-cold-start.md)
- **Dual-Route Triage (Antigravity vs Gemini Webview):** Refined `triage_router.py` to route coding/file/codebase prompts to a new interactive Antigravity session in Terminal via AppleScript, while routing general non-coding questions to the Gemini Webview in `ai-os`. [[log]](agent-logs/2026-07-23_23-23_dual-route-triage-antigravity-vs-gemini-webview.md)
- **Antigravity Desktop App Launch (`/Applications/Antigravity.app`):** Updated `triage_router.py` to target the `/Applications/Antigravity.app` desktop app via AppleScript for coding and file search tasks, copying the prompt to clipboard and initializing a new chat. [[log]](agent-logs/2026-07-23_23-24_launch-antigravity-desktop-app-for-coding-prompts.md)
- **Antigravity App Shortcut Fix (`Shift+Cmd+O` twice):** Updated AppleScript keystroke sequence in `launch_antigravity_app` to send `Shift+Cmd+O` twice to trigger a new unattached global conversation thread before pasting and executing the prompt. [[log]](agent-logs/2026-07-23_23-27_fix-antigravity-app-new-conversation-shortcut.md)
2026-07-25
- **Simplified tmux subagent integration:** Rewrote `subagent.py` to launch claude TUI directly in one pane (no pipe, preserves PTY for frames). Captures output from claude session JSONL logs after user exits with `/exit`. Added mandatory preflight/commit rules to `claude_only.md`. [agent-log](agent-logs/2026-07-25_15-40_fix-claude-rules-tmux-subagent.md)
- **qwerty-midi shift labels:** Implemented dynamic visual label toggling for Shift Mode in qwerty-midi-hammerspoon web UI. Links to [2026-07-25_16-00_qwerty-midi-shift-labels.md](agent-logs/2026-07-25_16-00_qwerty-midi-shift-labels.md)

## 2026-07-26
- **Concurrent Subagents:** Updated subagent.py to allocate and clean up tmux panes dynamically, allowing multiple subagents to run simultaneously in the same window. [[log]](agent-logs/2026-07-26_13-57_concurrent-subagents.md)

## 2026-07-28
- **Flash Lite Recursion Fix:** Fixed an infinite subagent recursion loop by clarifying leaf agent delegation rules in gemini_only.md. Link to agent log: [2026-07-28_17-50_fix-flash-lite-recursion.md](agent-logs/2026-07-28_17-50_fix-flash-lite-recursion.md)
- **Dynamic System Prompt & Unified Triage Gateway:** Implemented modular rule decomposition in `.rules/` and created `scripts/compile_dynamic_prompt.py`. Reduces system prompt token overhead from ~40k tokens to ~600-1,200 tokens per turn, and strips leaf subagent context of orchestrator bloat. [[log]](agent-logs/2026-07-28_21-07_dynamic-system-prompt-gateway.md)
- Restarted LiteLLM proxy to apply DeepSeek official OpenRouter pin fix and verified live traffic.

## 2026-08-13
- **2026-08-13**: Configured Caddy reverse proxy as a macOS Launch Agent (`com.matt.agent.caddy`) providing HTTPS on `https://localhost:8082` for LLM backends.
- **Postflight Thread Size & Perplexity Quota Injection:** Fixed `postflight.py` non-blocking stdin handling and thread token metrics calculation. Created `scripts/pplx_quota.py` to inject live Perplexity Pro/Research quota into `postflight.py` and `preflight.py`. Documented userscript directory locations in `AG_CONTEXT.md` and `macOS Environment.md`. [[log]](agent-logs/2026-08-13_18-36_postflight-thread-size-and-perplexity-quota.md)
- **Atomic Thread Finalization & Self-Healing Watchdog:** Implemented atomic write-locking and integrity checksums for `thread.md` to prevent partial-save corruption, paired with a new `scripts/watchdog_sync.py` to auto-reconcile desynchronized states. Integrated Proxima Perplexity IPC for live-token quota tracking across all sub-agent threads. [[log]](agent-logs/2026-08-13_20-04_atomic-thread-watchdog-pplx-ipc.md)
