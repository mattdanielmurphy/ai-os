---
title: "Monorepo Restructuring And Decoupling"
date: "2026-08-15"
conversation_id: "60d8c4c3-732c-460a-80a7-f38a482e6593"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 80px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

✅ **Approved Plan/Artifact**: [implementation_plan.md](file:///Users/matt/.gemini/antigravity/brain/60d8c4c3-732c-460a-80a7-f38a482e6593/implementation_plan.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/60d8c4c3-732c-460a-80a7-f38a482e6593/implementation_plan.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/60d8c4c3-732c-460a-80a7-f38a482e6593/implementation_plan.md)

</span>



<span title="Responded at 8:15am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

### Stage 1 Monorepo Restructuring & Severing Complete

The `ai-os` repository has been restructured into an `apps/` and `crates/` monorepo layout, separating the Tauri webview automation harness from the headless terminal harness, and decoupling shared core primitives into an independent library crate.

### Summary of Completed Deliverables
1. **Established `apps/` Architecture**:
   - **`apps/gemini-companion/`**: Moved `tauri-gui` via `git mv` (preserving git commit history), keeping the dedicated Tauri webview shell, Axum IPC loopback sync endpoints (`/api/context/sync`, `/api/notes/save`, `/api/revision/commit`), automation userscript injection, and native macOS window controls.
   - **`apps/aios-tui/`**: Created a standalone Ratatui/Crossterm terminal UI harness that operates completely headless over SSH or tmux without Tauri/webview display dependencies.
2. **Extracted Shared Core (`crates/aios-core/`)**:
   - Extracted session maps, PTY helper routines, and thread tracking structures into a zero-Tauri Rust library crate.
3. **Workspace Configuration & Hygiene**:
   - Created root [`Cargo.toml`](file:///Users/matt/projects/ai-os/Cargo.toml) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/Cargo.toml) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/Cargo.toml) workspace (`crates/aios-core`, `apps/gemini-companion/src-tauri`, `apps/aios-tui`).
   - Updated root [`package.json`](file:///Users/matt/projects/ai-os/package.json) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/package.json) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/package.json) workspaces (`apps/*`, `services/*`).
   - Updated [`bin/ai-os`](file:///Users/matt/projects/ai-os/bin/ai-os) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/bin/ai-os) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/bin/ai-os) launcher to direct `--gui` to `apps/gemini-companion` and added the `--tui` option.
   - Moved stale lockfiles (`pnpm-lock.yaml`), empty database files (`test.db`), and stray root artifacts to `~/.Trash/`.
   - Updated [`AG_CONTEXT.md`](file:///Users/matt/projects/ai-os/AG_CONTEXT.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/AG_CONTEXT.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/AG_CONTEXT.md) and [`DEVELOPMENT_JOURNAL.md`](file:///Users/matt/projects/ai-os/DEVELOPMENT_JOURNAL.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/DEVELOPMENT_JOURNAL.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/DEVELOPMENT_JOURNAL.md).

### Verification
- **Cargo Workspace**: `cargo check --workspace` passed across all 3 targets with 0 errors.
- **Bun Workspaces**: `bun install` passed and generated clean lockfile definitions.
- **Test Suite**: `python3 run_tests.py` ran 55 unit tests successfully (`OK`).
- **CLI Flags**: `bin/ai-os --help` verified and operational.

For full details, refer to the [walkthrough.md](file:///Users/matt/.gemini/antigravity/brain/60d8c4c3-732c-460a-80a7-f38a482e6593/walkthrough.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/60d8c4c3-732c-460a-80a7-f38a482e6593/walkthrough.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/60d8c4c3-732c-460a-80a7-f38a482e6593/walkthrough.md) artifact and the conversation log [thread.md](file:///Users/matt/.gemini/antigravity/brain/60d8c4c3-732c-460a-80a7-f38a482e6593/thread.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/60d8c4c3-732c-460a-80a7-f38a482e6593/thread.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/60d8c4c3-732c-460a-80a7-f38a482e6593/thread.md).

</span>



</span>

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 15, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

# Objective: Stage 1 Monorepo Restructuring & Severing for `ai-os`

Please review `AG_CONTEXT.md` and `DEVELOPMENT_JOURNAL.md` before starting.

### Context & Goal
`ai-os` has accumulated overlapping tools, watchers, and monolithic GUI code. We need to restructure the repository into clean sub-applications under `apps/`, decouple the experimental Gemini/Perplexity webview harness from the legacy TUI/terminal harness, and clean up the root project structure.

### Key Deliverables for Stage 1
1. **Establish `apps/` Directory Structure**:
   - Create `apps/` in `~/projects/ai-os/`.
   - Sever `tauri-gui` into two isolated targets:
     - `apps/gemini-companion/` (or `apps/proxima-lite`): Dedicated, minimal Tauri shell for the Gemini/Perplexity webview + injected automation hooks.
     - `apps/aios-tui/`: Archive/preserve the legacy agy/claude/hermes terminal harness without dependencies on the webview.
2. **Decouple Shared Services**:
   - Ensure `services/`, `scripts/`, and `tools/` remain accessible without cross-polluting app configurations.
3. **Workspace Cleanup**:
   - Clean up stale temporary files, redundant locks, or orphaned scratch artifacts from the root directory.
   - Update `AG_CONTEXT.md` and `package.json` / workspace configs to reflect the new `apps/` monorepo layout.

Please inspect the directory, generate an implementation plan, and guide the restructuring cleanly using subagents and Bun.

See the bigger picture here and include any context missing from here.
@[conversation:"Proxima Error Debugging Refactor"] 
/proxima-planner

</span>



<span title="Responded at 8:08am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

Please review the implementation plan artifact:
- [implementation_plan.md](file:///Users/matt/.gemini/antigravity/brain/60d8c4c3-732c-460a-80a7-f38a482e6593/implementation_plan.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/60d8c4c3-732c-460a-80a7-f38a482e6593/implementation_plan.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/60d8c4c3-732c-460a-80a7-f38a482e6593/implementation_plan.md)

### Key Structural Highlights
- **Apps Monorepo Layout (`apps/`)**:
  - `apps/gemini-companion/`: Tauri webview shell, Axum IPC loopback sync endpoints, and automation userscript injection.
  - `apps/aios-tui/`: Headless terminal harness (Ratatui/Crossterm) designed for local/SSH/tmux usage without webview dependencies.
- **Shared Rust Primitives (`crates/aios-core`)**: Extracts PTY management and session/thread tracking logic into a dedicated Tauri-free library crate.
- **Workspace Hygiene**: Clean isolation for `services/`, `scripts/`, and `tools/`, removing stale lockfiles and temporary artifacts.

Reference thread: [thread.md](file:///Users/matt/.gemini/antigravity/brain/60d8c4c3-732c-460a-80a7-f38a482e6593/thread.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/60d8c4c3-732c-460a-80a7-f38a482e6593/thread.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/60d8c4c3-732c-460a-80a7-f38a482e6593/thread.md)

Please review the plan and click **Proceed** (or provide feedback) to begin execution.

</span>



</span>

</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">



**Thread Metrics:**

| Total Tokens | Cache Expiry | Financial Rotation | Perplexity Quota |
| :--- | :--- | :--- | :--- |
| ~70k | 3:20am | ~70k / ~403k 🟢 (optimal) | 108, 20 🔬, 16 📤 |

</span>