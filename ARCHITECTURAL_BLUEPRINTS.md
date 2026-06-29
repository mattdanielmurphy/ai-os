# Technical Blueprint Menu (Refined)

## 1. Rust API Bridge Layer & Stateless Revision Loop

### 1.1 Architectural Prerequisites & Data State
* **State Hooks:** A local Axum or Actix-web server instance bound to `127.0.0.1` injected directly into the Tauri `main.rs` runtime loop.
* **Rust Backend Structs:** Defines for `/api/context/sync` and `/api/revision/commit` expecting JSON structs (Thread UUID, Target Filename, Content String).
* **Local Directories:** `.agent-logs/git/[thread_id]/`. Pathing must be dynamically resolved via `std::env::current_dir()` or `$AI_OS_HOME` rather than hardcoded `/Users/...` paths.

### 1.2 Step-by-Step Backend to Frontend Build Order
* **Phase A (System/Shell Scripts):** N/A for this module.
* **Phase B (Rust Bridge Core):** Spawn an asynchronous `axum` server inside a dedicated Tokio runtime thread on app startup. Implement CORS middleware allowing `https://gemini.google.com`. Implement the `/api/revision/commit` handler.
* **Phase C (Tauri IPC):** Integrate Tauri's `AppHandle` into the Axum server state so HTTP POST events can emit WebSocket/IPC events to the Vite frontend to update revision UI.
* **Phase D (Frontend Canvas):** The frontend receives the broadcasted commit hash and updates the timeline slider automatically without manual polling.

### 1.3 Technical "How" & Code-Level Design Patterns
* **Path Resolution Fix:** Resolve the project root dynamically. Instead of `"/Users/.../projects/ai-os"`, Rust must compute the relative path or respect the `AIOS_INITIAL_PROJECT` env variable.
* **Argument Vectors:** When Rust invokes Git via `std::process::Command`, it must use chained `.arg()` arrays to prevent command injection, avoiding any shell execution strings: `Command::new("git").arg("commit").arg("--allow-empty").arg("-m").arg("Web Sync")`.
* **Poller Mitigation:** Replace the slow `lsof`/`ps` 50ms CPU loop with asynchronous OS signals or named pipes where possible to detect process state.

### 1.4 Token & Quota Optimization
* Zero direct token impact. Enables shifting workload to "free" web endpoints and deduplicating storage via Git diffing natively.

---

## 2. Browser Extension / Web Context Sync

### 2.1 Architectural Prerequisites & Data State
* **State Hooks:** A Tampermonkey or Chrome extension injected into `gemini.google.com`.
* **Data State:** Active DOM node tracking for `[AIOS_DOC]...[/AIOS_DOC]` tag patterns.

### 2.2 Step-by-Step Backend to Frontend Build Order
* **Phase A (Local Scripts):** Generate the userscript header enforcing `@connect 127.0.0.1` to bypass CSP.
* **Phase B (Rust Bridge):** Ensure the `/api/revision/commit` endpoint is active (see Module 1).
* **Phase C (Tauri IPC):** N/A.
* **Phase D (Frontend Extension):** Write the DOM `MutationObserver` looking for newly generated chat bubbles containing the `[AIOS_DOC]` tags. Extract the text, wipe the conversational context, and hit the Axum loopback via `GM_xmlhttpRequest`.

### 2.3 Technical "How" & Code-Level Design Patterns
* **Extraction Isolation:** Only the raw inner text is extracted; conversational fluff is ignored.
* **Button Injection:** The script appends a "Save to Local OS" button explicitly into the chat DOM node.

### 2.4 Token & Quota Optimization
* Directly leverages the "independent web request bucket" from Google Gemini, bypassing API metering entirely for code construction while preserving the local disk state cleanly.

---

## 3. Codebase Ingestion Parser (AST Upgrades)

### 3.1 Architectural Prerequisites & Data State
* **Data State:** Existing source files (`.ts`, `.rs`, `.go`).
* **Local Scripts:** `scripts/ingest_codebase`.

### 3.2 Step-by-Step Backend to Frontend Build Order
* **Phase A (System Scripts):** Refactor the brittle regex/while-loop logic in `ingest_codebase`. Instead of manual parsing, integrate `tree-sitter` (via a Python binding or a compiled Rust CLI tool) to formally parse ASTs for TypeScript, Rust, and Go.
* **Phase B (Rust Bridge):** Ensure the rust execution pipeline calls the updated parser cleanly.
* **Phase C & D:** N/A.

### 3.3 Technical "How" & Code-Level Design Patterns
* **Formal AST Parsing:** Use `tree-sitter` to accurately capture class definitions, function signatures, and exported constants while throwing out function bodies and docstrings, eliminating token counting failures caused by regex drift.

### 3.4 Token & Quota Optimization
* Perfects the "Token Parsimony" mandate by guaranteeing that deep structural context is safely compressed into minimal signatures without context window poisoning.

---

## 4. Automated Auth Rotation Daemon (`aios_rotate_auth`)

### 4.1 Architectural Prerequisites & Data State
* **State Hooks:** A credential tracking registry dynamically sourced relative to the user's home dir (`~/.gemini/auth_ledger.json`).
* **Local Scripts:** `scripts/aios_rotate_auth.py`.

### 4.2 Step-by-Step Backend to Frontend Build Order
* **Phase A (System Scripts):** Create `aios_rotate_auth.py` utilizing standard argument parsing. It reads the ledger, selects the next valid `Beta` or `Alpha` profile, and atomically copies the cached OAuth payload over the active token file.
* **Phase B (Rust Bridge Core):** Integrate automatic execution into the Rust PTY daemon loop. When the CLI agent returns a 429 quota exhaustion error, the Rust bridge pauses the PTY, fires the rotation script, and resumes the CLI instance seamlessly.
* **Phase C (Tauri IPC):** Forward a UI notification "Auth Rotated successfully."
* **Phase D:** Provide manual rotation overrides in the Vite UI.

### 4.3 Technical "How" & Code-Level Design Patterns
* **Atomic Filesystem Operations:** Use `os.replace()` in Python to swap token files. This ensures cross-platform atomicity and avoids corrupting the credential file if the system crashes mid-write.
* **Zero Hardcoded Paths:** Pathing targets `os.path.expanduser("~/.gemini/")`.

### 4.4 Token & Quota Optimization
* Directly implements the Dual-Rail multi-tier quota architecture, maintaining high-bandwidth logic orchestration across free-tier boundaries.

---

## 5. Semantic Thought Layer & macOS Native Automation

### 5.1 Architectural Prerequisites & Data State
* **State Hooks:** A local vector database engine (e.g., `lancedb` via python or `qdrant` embedded in Rust). Access permissions to macOS AppleEvents.
* **Local Directories:** `$AI_OS_HOME/.agent-logs/embeddings/`.

### 5.2 Step-by-Step Backend to Frontend Build Order
* **Phase A (System Scripts):** Build `embed_notes.py` using `sentence-transformers` for local embedding creation. Build `get_browser_state.js` (JXA) for tab telemetry.
* **Phase B (Rust Bridge):** Ensure strict subprocess invocation with `.arg()` array patterns (preventing injection vulnerabilities). Wrap AppleScript executions in rigid timeouts (e.g., 3000ms) to prevent UI deadlocks if the target macOS application is non-responsive.
* **Phase C (Tauri IPC):** Map endpoints for semantic search to the UI (`semantic_search_invoke(query)`).
* **Phase D (Frontend Canvas):** Build the omnibar CMD+K interface over the workspace for semantic querying.

### 5.3 Technical "How" & Code-Level Design Patterns
* **JXA Strict Sandboxing:** Hardcode the JXA queries. Do not pass LLM-generated string inputs directly into the AppleScript engine.
* **Dynamic Path Execution:** The embeddings path is derived strictly via environment variables, resolving the portability crisis identified in the audit.

### 5.4 Token & Quota Optimization
* RAG indexing isolates context retrieval, preventing bulk text injection and honoring the strict parsimony rules. Local models ensure zero network API cost.
