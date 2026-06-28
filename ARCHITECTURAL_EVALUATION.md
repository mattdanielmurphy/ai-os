# Architectural Evaluation Report: ai-os Workspace

## Phase 1: Exhaustive File-by-File Audit & Gap Analysis

**[FULLY IMPLEMENTED]**
*   **Orchestration & Bootloading**: `bin/ai-os`, `.zshrc`, `.zshrc_aios`, `package.json`. The application correctly sets up a shell-wrapping bootloader that intercepts destructive commands (e.g., `rm`) and injects the `qr` (quiet run) wrapper. 
*   **Tauri GUI & PTY Layer**: `src/main.ts`, `src-tauri/src/main.rs`, `index.html`. Functional React/TS frontend utilizing `xterm.js` to render multiplexed background processes via Rust bindings.
*   **Cost & Quota Telemetry Engine**: `scripts/get_last_cost.py`, `scripts/telemetry_db.py`. Excellent implementation of complex sub-model cost math and undocumented Google gRPC token refresh flows.
*   **Triage Editing System**: `scripts/precision_edit.py`, `scripts/mechanical_editor.py`. Completely handles surgical text mutations and LLM-driven `patch` applications with JSON fallbacks.
*   **Git Memory Pipeline**: `scripts/memory_search.sh`, `scripts/memory_diff.sh`. Functional multi-layer indexing implementation for safe history retrieval.
*   **Dynamic Rules Injection**: `scripts/append_system_rule.py`. Successfully manages context routing to the active `CLAUDE.md` and global rulesets.
*   **Automated Context Handoff**: `scripts/context_handoff.py`. Creates standardized context log files in `.agent-logs/` conforming to the Indexed Handoff Protocol.

**[PARTIALLY IMPLEMENTED]**
*   **Rust API Bridge Layer**: `VISION.md` heavily specifies a loopback daemon (`axum` or `actix-web`) listening on `127.0.0.1` exposing endpoints like `/api/context/sync` and `/api/revision/commit`. **Reality**: `main.rs` is strictly a Tauri IPC command runner and contains zero HTTP server infrastructure for web-chat syncing. 
*   **Codebase Ingestion Parser**: `scripts/ingest_codebase`. While the Python AST implementation is highly effective and structurally robust, the curly-brace parsing (TypeScript, Rust, Go) relies on brittle custom `while` loop index scanning and regex mapping instead of a formal AST parser, which will break under complex token conditions.

**[NOT STARTED]**
*   **Browser Extension / Tampermonkey Script**: The shared injection framework designed to siphon `gemini.google.com` sessions directly into the local repo has zero source files in the current workspace.
*   **Automated Auth Rotation Daemon (`aios_rotate_auth`)**: No files exist for the headless account-swapping component designated to rotate Google Accounts for "Rail Alpha" and "Rail Beta".
*   **Semantic Thought Layer & macOS Native Automation**: Roadmap features outlined in the vision (JXA/AppleScript wrappers, local vector embeddings) are entirely absent from the codebase.

---

## Phase 2: Behavioral Rules Compliance Check

*   **Token Parsimony**: High compliance. `scripts/precision_edit.py` completely bypasses LLMs for static edits, and `scripts/ingest_codebase` brutally skeletonizes code to save context. Both perfectly match the strict token-saving mandate.
*   **Cost Efficiency**: High compliance. `scripts/mechanical_editor.py` effectively delegates high-token refactors to the local `deepseek` proxy, honoring the multi-tier triage strategy.
*   **Fail-Safe Operations**: Strict compliance. `.zshrc_aios` successfully neuters `rm` to prevent fatal deletions, and `mechanical_editor.py` uses aggressive 60-second timeouts and `patch --batch` to prevent interactive shell hangs.
*   **Behavioral Deviations & Context Leaks**: 
    *   *System Profile Bloat:* `bin/ai-os` dumps highly verbose, unfiltered system data (`system_profiler SPDisplaysDataType`) into `memory/macOS_profile.md`. If loaded automatically into agent contexts, this static noise will severely drain tokens over time.
    *   *Noisy Command Passing:* While the bash environment has the `qr` wrapper, `main.ts` routes commands by blindly sending strings like `agy --add-dir=$PWD -i "..."` straight to the PTY. It fails to default to the quiet run wrapper for background compilation tasks, exposing the terminal to output flooding.

---

## Phase 3: Structural Critique & Code Deficiencies

*   **Architectural Bottleneck: Blocking System Polling (`main.rs`)**:
    To determine if a process is busy, `toggle_process_pause` spawns a thread containing an infinite `while` loop that synchronously executes `lsof` and `ps` via standard shell subprocesses. `lsof` is notoriously CPU-intensive and slow on macOS. Polling this in a tight 50ms sleep loop is a severe anti-pattern that creates UI latency, battery drain, and race conditions.
*   **Command Injection Vulnerability (`main.ts`)**:
    The UI constructs commands via direct string concatenation:
    `commandToExecute = \`agy --add-dir=$PWD -i "\${escapedInput}"\`;`
    Despite basic quote escaping, evaluating user-supplied input directly inside bash shells via the Tauri bridge creates critical command injection risks. The bridge should leverage serialized argument vectors rather than raw string execution.
*   **Hardcoded Absolute Pathing (Portability Crisis)**:
    The codebase is severely coupled to a single environment. Hardcoded paths to `/Users/matthewmurphy/...` are scattered maliciously throughout the workspace, destroying portability:
    *   `bin/ai-os`: `export AI_OS_HOME="/Users/matthewmurphy/projects/ai-os"`
    *   `scripts/context_handoff.py`: `log_dir = "/Users/matthewmurphy/projects/ai-os/.agent-logs"`
    *   `src/main.ts`: Const injection of `obsidian` Vault paths and the `get_last_cost.py` execution path.
*   **Regex Structural Parsers**:
    The fallback logic in `mechanical_editor.py` attempts to sanitize JSON out of Markdown code blocks using primitive regex `replace`. The parsing matrix here is highly susceptible to formatting drift and will fail on unexpected markdown headers or malformed nested blocks.

---

## Phase 4: Vision Alignment & Simplification

**Critique of the Master Vision (`VISION.md`)**:
The vision document suffers from severe scope creep. It is overly prescriptive about the *how* (documenting literal Tampermonkey script headers and API loopback routing logic) for systems that do not yet exist, while minimizing the engineering reality of the system: a tightly constrained, highly effective CLI orchestration tool. 

**Strategic Simplification Recommendations**:
1.  **Decouple Vaporware from Core**: Erase the highly specific JavaScript headers, Axum API endpoints, and Tampermonkey DOM injection logic from `VISION.md`. Shift these architectural designs into isolated RFCs (e.g., `docs/rfc-01-web-sync.md`) to keep the root vision strictly focused on existing, executable realities.
2.  **Acknowledge CLI Primacy**: Rewrite the core architectural thesis to reflect what is actually working: a highly capable desktop GUI that multiplexes terminal sessions wrapped in strict Python-based cost/edit guards. The "Dual-Rail Cloud web scraping" is currently an experimental sidecar, not the bedrock.
3.  **Refocus on Abstraction**: Update `VISION.md` to dictate the *interface boundaries* of the tools (e.g., "Agents must use the local telemetry database") rather than dictating the specific internal HTTP routing or payload structure of incomplete integrations.
