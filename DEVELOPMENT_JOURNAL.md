# Development Journal

A running narrative of key decisions, pivots, and direction changes. One entry per session. **Agents MUST append to this at the end of every conversation.**

---

## 2026-07-20

## 2026-07-22

- **Quota Pre-Flight Check & Minimal-Token Mode Rule:** Added pre-flight quota inspection rule to `AGENTS.md`. Antigravity calls evaluate quota via `ag-quota -j` (or `codexbar status`/`list`) and automatically switch to Minimal-Token Mode (Strict Orchestrator Mode 3) under low quota or rapid burn velocity, delegating code generation to `claude code` or cheap subagents. [[log]](agent-logs/2026-07-22_02-08_preflight-quota-check-minimal-token-mode.md)
- **Gemini Floating Webview Auto-Transformation:** Updated `floating_init_script` in `tauri-gui/src-tauri/src/main.rs` to detect when a message is sent in the floating input bar and immediately transform the window back to a full, normal webview (restoring background, unhiding DOM elements, and expanding size to 1000x850) so responses are fully readable. [[log]](agent-logs/2026-07-22_02-34_gemini-floating-webview-transform.md)

- **Strategic Pivot: Minimal Fork + litellm Bridge.** Hit breaking point with the current approach — monkey-patching `interruptible_api_call` in `aios_hermes_wrapper.py` plus a separate `sitecustomize.py` for the WebUI is too fragile. Hermes WebUI "cancel" drops thread context, which defeats the purpose of interactive agent loop. Decided to pivot to a **minimal fork of Hermes Agent** that adds agy as a real *provider* (not a faked tool call), with ~30 lines of changes instead of 190 lines of monkey-patching. Fork retains upstream merge compatibility. Architecture: `User → Launcher/Shell Wrapper → Triage → litellm → Model`. Claude Code handles Ctrl+C correctly with full context preservation. [[agent-log]](agent-logs/2026-07-20_00-30_strategic-pivot-minimal-fork-triage.md)
- **Created this dev journal.** Agent logs are too detailed for human consumption. This file is the human-readable timeline. All agents must append here at session end. [[agent-log]](agent-logs/2026-07-20_00-30_strategic-pivot-minimal-fork-triage.md)
- **Phase 1: Split Tauri backend `main.rs` into modules.** Extracted the 3,188-line monolith into 5 focused modules: `types.rs` (148 lines), `pty.rs` (630), `threads.rs` (1,107), `server.rs` (402), `session.rs` (1,142). Main is now 299 lines. Zero behavior changes, clean compile with zero warnings. This makes the codebase debuggable and sets up Phase 2 (cutting unused complexity). [[agent-log]](agent-logs/2026-07-20_00-30_strategic-pivot-minimal-fork-triage.md)
- **Fixed rules-watcher & Improved `la` tool:** Updated `la` to show `oneshot` agents as "watching" and improved `la logs` to find logs in plists. Fixed `rules-watcher` plist. [[agent-log]](agent-logs/2026-07-20_02-15_fix-la-status-and-logs-for-oneshots.md)
- **Fixed rules-watcher Launch Agent & Bidirectional Sync:** Replaced AGENTS.md with a symlink to .gemini/GEMINI.md, upgraded sync script to bidirectional newer-wins, and removed the tmux wrapper from plist to resolve TCC sandbox blocks. [[agent-log]](agent-logs/2026-07-20_01-40_fix-rules-watcher-and-bidirectional-sync.md)
- **Fixed Tauri Backend Bugs:** Resolved the WebSocket host reconnect race via connection IDs, resolved tab switching terminal output interleaving via thread-specific buffer keys, and fixed thread naming/chain resolution pathing. [[agent-log]](agent-logs/2026-07-20_13-38_fix-tauri-backend-bugs.md)

## 2026-07-19

- **Implemented Zero-Fork Hermes Triage Interceptor** (`aios_hermes_wrapper.py`) — monkey-patches `chat_completion_helpers.interruptible_api_call` to inject fake `agy_start` tool calls for coding prompts. TUI works. [[agent-log]](agent-logs/2026-07-19_18-36_implemented-zero-fork-hermes-triage-interceptor.md)
- **Fixed WebUI triage** — the WebUI runs as a separate Python process that never touches the wrapper. Had to create `webui-patches/sitecustomize.py` and set `PYTHONPATH` in hermes-webui `.env` to get the same interception working. This complexity is what triggered the July 20 pivot. [[agent-log]](agent-logs/2026-07-19_22-54_webui-triage-sitecustomize-fix.md)

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
