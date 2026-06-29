# `ai-os` Master Vision & Architecture Document

## 1. Project Vision & Philosophy

**Goal:** Transform the local macOS machine into an editable, interactive database of thoughts, files, and automation powered by local-first AI.

**Philosophy:**

* **Token Parsimony:** Context windows are sacred. Never send the LLM 1,000 lines if 10 will do.
* **Cost Efficiency:** Premium models orchestrate; economy/local models execute. Maximize high-ceiling "free" and flat-rate web quotas before touching paid API meters.
* **Fail-Safe Operations:** AI must not act with raw, unconstrained shell access. Edits must be deterministic, and destructive actions must be sandboxed.
* **Seamless UI:** The user shouldn't feel the terminal boundary. The interface should blend natural language, drag-and-drop file paths, and terminal output natively.
* **On-Request Autonomy:** High-density context datasets are explicitly *available* but strictly *lazy-loaded*. Agents selectively pull environmental state only when explicitly required by a task, preventing context ballooning and token pollution.

---

## 2. Core Architecture (The "Matryoshka Doll")

`ai-os` operates in concentric layers of control:

1. **Frontend (Tauri v1 + Vite + Tailwind):** Features a "Smart Passthrough" UI.

* Uses `xterm.js` for raw PTY rendering.
* Replaces standard terminal prompts with an auto-expanding native `<textarea>` supporting standard macOS navigation bindings (`Cmd+A`, `Cmd+C`).
* Supports drag-and-drop path resolution.
* Implements `/clear\r` queueing for context resets.
* **Unified Webview Runtime:** Embeds `gemini.google.com` directly within an isolated UI panel inside the Tauri app instance. This native framing shares its underlying JavaScript injection codebase with the external browser userscript, enforcing identical context scraping and disk-serialization behaviors across both entry points.

2. **Bridge Layer (Rust):** Maintains a persistent, native macOS `zsh` pseudoterminal (PTY).
3. **Agent Layer:** Native AI TUIs run *inside* the PTY. The frontend pipes user input directly into these active processes.
4. **Environment:** The absolute authoritative root is `/Users/matthewmurphy/projects/ai-os/`.

---

## 3. Dynamic Model Triage & Execution Modes

Instead of a rigid binary split, `ai-os` uses a **Multi-Tier Resource Triage Strategy**. Tasks are evaluated by complexity and routed to the most cost-efficient/quota-rich bucket available, defaulting to low-cost or flat-rate models (e.g., Gemini Flash or DeepSeek local/economical variants) unless a high-cognitive ceiling is explicitly required.

* **Orchestration Layer:** High-reasoning models manage sub-tasking, spec generation, and architectural design.
* **Execution Layer:** Commodity models handle code construction, boilerplate generation, and telemetry compilation.
* **Context Multipliers:** When multi-file context drops efficiency, the environment leverages the complex dual-rail web/subscription pipelines detailed in Section 8.

---

## 4. Context & Rules Engine

Agents are governed by strict, isolated markdown files to prevent context confusion:

* `~/.gemini/GEMINI.md`: The absolute Single Source of Truth for system behaviors, tool usage, and constraints.
* `CLAUDE.md`: Syncs global rules with Claude-specific directives.
* `AG_CONTEXT.md`: Strictly for repository structure and domain knowledge (No behavioral rules).
* `.zshrc_aios`: The custom shell environment containing safety hooks (e.g., alias `rm` to move to `~/.Trash/`) and custom wrappers.

---

## 5. The Tool Arsenal (`scripts/`)

Built to prevent "Token Ping-Pong" and enable autonomous execution.

### A. Context Protection & Reading

* **`ingest_codebase`**: Generates skeletonized ASTs/signatures, stripping logic out of files to give agents structure without bloat.
* **`qr` (Quiet Run):** A zsh wrapper for noisy commands (e.g., `npm install`). Pipes stdout/stderr to `/tmp`, returning only success/failure and the last 15 lines of errors to protect the PTY context.
* **`read_lines`:** A windowed file reader using `sed` to extract specific line ranges, preventing massive `cat` outputs in the terminal.
* **Native Shell Command Interception:** Instead of attempting to prompt-engineer the agent away from its natural muscle memory (e.g., running `git commit`), `ai-os` intercepts these commands natively via `zsh` function wrappers in `.zshrc_aios`. The command executes transparently, but the massive console output is silenced and replaced with a deterministic, minimal token-cost success string.

### B. The Triage Editing System

Governed by the dynamic `$AIOS_DELEGATE` toggle (`delegate_on` / `delegate_off`).

* **Quota Saving Mode (Delegated):** Agent generates a spec and hands it to `mechanical_editor.py`, which uses a local LiteLLM proxy to generate and apply a strict `.patch`.
* **Premium Speed Mode (Direct):** Agent writes code directly using **Quoted Heredocs** (`cat << 'EOF_SAFE' > file.tmp`) to prevent zsh escaping and string interpolation errors.
* **Fast-Path (`precision_edit.py`):** Zero-API-cost deterministic script for strict 1-line appends, inserts, or replacements.

### C. Multi-Layer Memory & Progressive Context Discovery

To prevent infinite context snowballing on long-term operations, historical text tracking utilizes a strict progressive-disclosure framework. Every layer of history is serialized exclusively in human-readable Markdown format to ensure universal local search via system tools or manual viewing.

```
┌────────────────────────────────────────────────────────┐
│ 1. Index Layer: .agent-logs/index.md                    │◀── Baseline Entry
│    - 1-sentence summaries and unique Thread IDs         │
└───────────────────────────┬────────────────────────────┘
                            │ (On Request)
                            ▼
┌────────────────────────────────────────────────────────┐
│ 2. Detail Layer: .agent-logs/details/[ID].md           │◀── Secondary Layer
│    - Nuanced logs, technical step outputs, prompt text │
└───────────────────────────┬────────────────────────────┘
                            │ (On Request)
                            ▼
┌────────────────────────────────────────────────────────┐
│ 3. Git Core Layer: Git Memory Scripts                  │◀── Deep Execution
│    - Annotated diffs showing EXACTLY what and WHY      │
└────────────────────────────────────────────────────────┘

```

1. **`context_handoff.py` (The Index Layer):** Appends brief structured handoff logs to a consolidated index document (`.agent-logs/index.md`). Freshly initialized threads pull only this lightweight timeline index, preserving zero-token baseline efficiency.
2. **The Detail Buffer:** Nuanced session logs, verbose console tracking, and intermediate reasoning trees are written separate to `.agent-logs/details/[ID].md`. The agent references the high-level index and explicitly requests detailed sub-logs *only* if historical relevance is identified.
3. **Git Memory Scripts:** Deep behavioral audit tools:

* `memory_search.sh`: Scans short commit hash patterns derived from deep logs.
* `memory_diff.sh`: Resolves precise code-line diffs via `git show` alongside rich metadata annotations explaining precisely *what* code was rewritten and *why*.

### D. Selective macOS & Browser Context Harvest

Context extraction operates strictly under the "Available but On-Request" philosophy. Tools compile deep environmental telemetry metrics into concise payloads only when an agent invokes them.

* **`get_system_inventory`:** Generates text summaries of installed macOS applications, local markdown note manifests, active configuration profiles, and unified cross-platform session history.
* **`get_automation_state`:** Audits local workspace shortcuts and daemon automation properties:
* Collects custom shell utility configurations, environment automation scripts, and localized user `LaunchAgents`.
* Evaluates system macro paths, mapping active Hammerspoon configs alongside any legacy Keyboard Maestro profiles currently being phased out.


* **`get_hardware_status`:** Extracts machine resource envelopes, tracking filesystem mounts and **available local disk space** constraints.
* **`get_browser_state`:** Telemetry pipeline extracting open browser tab names and web history metadata.
* Sub-flag `--active-only` isolates and streams the full DOM text string and active URL of the **foreground window/tab** natively.


* **`capture_environment_frame`:** Native terminal wrappers leveraging macOS screenshot binaries to inject visual context:
* `--fullscreen`: Captures the complete display arrangement canvas.
* `--window`: Crops visual capture explicitly to the boundaries of the frontmost application window container.



### E. Telemetry & Cost Tracking

* **`telemetry_db.py` / `get_last_cost.py`:** Tracks LiteLLM delegation costs and fetches real engine server quotas.
* Agents execute the cost script *only* when yielding to the user, echoing the output directly into their markdown response to bypass collapsed UI PTY blocks.

---

## 6. Interactive Workspace UI & Non-Linear UX

The frontend abstracts the terminal boundary, rendering streamed text as a structured, editable, multi-dimensional document canvas using a proportional typography system while restricting monospace exclusively to code blocks.

### A. 2D Interactive Document Layout & Progressive Disclosure

Traditional AI chat and document interfaces rely entirely on a **1D Linear Scroll**. As technical architecture documents grow in scope, this linear model scales poorly, creating scroll fatigue, cognitive overwhelm, context fragmentation, and token inefficiency during human consumption.

To resolve this, the workspace transforms document consumption into a **2D Interactive Hierarchy** mapped directly to native Markdown syntax.

```
[-] # System Architecture (Summary)
 └── [+] ## Storage Layer (Concise Hook)
 └── [-] ## TUI Interface Layer (Concise Hook)
      └── [###] Architecture Blueprint (Auto-Folded Data Dump)
      └── [###] State Hydration Logic (Auto-Folded Code Snippet)

```

Instead of changing the underlying document format, the interface alters how it *projects* visually:

* **Structural Abstraction:** Document headings (`#`, `##`) serve as a 2D navigational plane, giving an immediate, scannable overview of the entire system landscape.
* **On-Demand Density:** Deep subsections (`###` or lower) act as localized containers that hold heavy technical detail, code blocks, and minutiae, hidden behind interactive toggle states by default.
* **Spatial Navigation:** Users navigate the document structurally using dual-axis inputs (e.g., Up/Down to traverse parallel blocks, Left/Right to expand or collapse structural branches).

#### 1. Implementation Strategy: TUI Rendering Engine

* **AST Parsing:** Parse the incoming Markdown stream into an Abstract Syntax Tree (AST) rather than rendering it as raw text.
* **Dynamic Node Hydration:** Map Markdown headings to interactive tree nodes within the terminal layout.
* **State-Driven Visibility:** Initialize the UI state with a maximum visibility threshold set to `depth <= 2`. Any tokens parsed under `H3` or lower are dynamically appended to hidden child buffers until explicitly toggled by user interaction (e.g., `Spacebar` or `Right Arrow`).
* **Expansion Mechanics:** When a user explicitly expands a header node to reveal its nested text, expansion operates on a hybrid model:
* *Pre-rendered:* Hidden inline beneath a standard `<details>` element if generated during the initial prompt pass.
* *Just-in-Time (JIT):* Triggers an asynchronous execution script to query the agent for targeted expansion context only when requested.



#### 2. LLM Steering (System Prompt Integration)

To leverage this architecture during generation, the AI must be structurally incentivized to distribute density correctly. This minimal constraint block is injected into the core system prompt:

```markdown
## UI Rendering Constraints
The interface renders Markdown headers as a collapsible, 2D interactive tree. 
Deep subsections are hidden by default to preserve screen real estate.

- Maintain absolute brevity in H1 (`#`) and H2 (`##`) headers, using them strictly as high-level summaries and structural hooks.
- Anchor all exhaustive technical depth, code implementations, and minutiae within deeply nested headers (H3 `###` or lower).
- Assume the user will selectively expand H3+ nodes only when diving deep into that specific sub-component.

```

### B. Inline Sidebar Threads (Dimensional Layering)

To prevent sidebar tangents and hyper-specific clarification loops from corrupting the core chat history, the workspace employs a branching model:

* **The Interaction:** Highlighting a text block within an AI response exposes an anchor popover. Submitting a question here encapsulates the text in a custom inline wrapper: `<span class="has-sidebar" data-sidebar-id="sb_msg[X]_[Hash]">`
* **The Presentation:** The clarification conversation is offloaded to a slide-out drawer or absolute-positioned popover component, maintaining a clean primary scroll track.
* **Context Isolation:** Sidebars are stripped from the main context vector sent to the primary agent unless explicit retrieval is triggered by a tool execution call.

### C. The Editable Canvas & Split-Screen Revision Workspace

Instead of treating LLM text streams as immutable histories or allowing web chat outputs to flood the terminal state with redundant text walls, every response component is a directly mutable document block. The UI partitions generation into an interactive, side-by-side workspace split to manage document state updates cleanly.

* **The Split-View Layout:**
* **Left Pane (Chat Stream):** Displays the conversation flow, including the `[AIOS_INTRO]` and `[AIOS_OUTRO]` framing text blocks. The massive `[AIOS_DOC]` payload is automatically stripped from the visible chat track and replaced with a compact telemetry token link (e.g., `[Document Revision v4 Attached]`).
* **Right Pane (Live Document Canvas):** A clean, editable rendered Markdown canvas dedicated entirely to the active state of the generated document.


* **The Revision Timeline Slider:** The top header of the right-hand document canvas features a hardware-accelerated slider interface mapped directly to the active thread's local Git commit history.
* Sliding backward dynamically checks out previous versions of the `[AIOS_DOC]` state within the view pane.
* Provides instant visual diffs (additions/deletions) highlighting historical changes between revisions without altering the active state of the primary chat log.


* **Block Mutation & The Perfected State Loop:** Users can backspace, correct, or restyle an agent's output directly inside the workspace view. If an agent needs to continue text or code generation based on edited responses, the frontend injects the user's *modified* text back into the context buffer. The agent builds on the curated version, completely blind to its own initial draft.
* **Three-Tier Response Segmentation:** To facilitate instant extraction, system prompts force the agent to partition document/script responses into 3 explicit semantic tokens parsed by the frontend into distinct UI elements:
1. `[AIOS_INTRO]`: Short contextual framing, overview, or design choices.
2. `[AIOS_DOC]`: The raw target document, configuration, or code block. This element features a persistent, single-click "Save to Notes" action targeting the local Markdown notes directory via native Rust commands.
3. `[AIOS_OUTRO]`: Concluding remarks, operational caveats, or suggested prompts for execution.



---

## 7. Storage, State Serialization & Schema Contracts

### A. Markdown-First Storage Constraints

To ensure absolute transparency and allow simple text searches, all internal tracking systems (thread sessions, agent outcomes, and clipboard memory buffers) must serialize into standardized Markdown syntax. Raw structured data structures (like metadata objects or runtime telemetry statistics) must be wrapped inside standard fenced code blocks within the target document.

### B. Scalability & System Footprint Analysis

Because text features a minimal storage footprint, exponential historical growth is highly manageable. However, raw volume is mitigated via structural design constraints:

| Data Class                   | Local Storage Mechanism                  | Scale Projections (Est.)                         | Mitigation Mechanism                                                                                    |
| ---------------------------- | ---------------------------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| **Handoff Logs / Indexing**  | Human-readable Markdown (`.agent-logs/`) | ~2–5 KB per complex operational thread           | Strict split between minimal `.md` high-level indexes and dense detailing directories.                  |
| **Scraped Browser Text**     | Markdown containing source text blocks   | Variable; ~50–200 KB per detailed DOM extraction | Strictly transient processing. Raw HTML targets are deleted post-extraction, keeping only target texts. |
| **Environmental Frame Maps** | Highly compressed binary blobs           | ~300 KB–1.5 MB per local capture event           | Storage window pruning. Assets are managed via a rolling queue on disk; aging captures are dropped.     |

---

## 8. Multi-Provider Token Arbitrage & Quota Inventory

To minimize standard pay-per-token API consumption, `ai-os` tracks, switches, and exploits multiple overlapping subscription-based, credit-based, and flat-rate accounts.

The core architectural asset here is a **Dual-Rail Google Infrastructure**: the user maintains two entirely separate Google Accounts, each backed by an active **Google AI Pro** subscription. Rather than acting as a separate tool channel, the AI Pro status functions as an infrastructure multiplier that scales up the usage limits across all underlying Google agent endpoints simultaneously.

### A. The Symmetrical Dual-Rail Google Grid

By incorporating an automated account-swapping component (`aios_rotate_auth --provider google`), the app seamlessly moves between **Rail Alpha (Account 1)** and **Rail Beta (Account 2)**, effectively doubling the high-ceiling quotas for the following integrated channels:

| Google Channel (Pro Multiplied) | Quota Metrics per Rail (Combined Total)      | Strategic Caveats & Mechanics                                                                                                                                                                                   |
| ------------------------------- | -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Google Jules (Cloud)**        | 100 Tasks/Day per rail **(200 Tasks Total)** | **Zero Token Cost.** Spins up a 2-hour remote Linux VM. Best for heavy autonomous batch tasks. Requires an active Git lifecycle (Fetch -> Execute -> Push). 5-minute boot latency makes it strictly async-only. |
| **Antigravity CLI**             | Dual-Bucket per rail (Sonnet/Opus + Gemini)  | 5hr/Weekly premium limits. Managed via configuration rotation scripts embedded in the Rust bridge layer.                                                                                                        |
| **Google Gemini (Web)**         | Independent Web Request Bucket               | Separate from API allocations. Scraped/automated session endpoints for zero-marginal-cost interactive triage. Shared injection layer handles both Tauri frame and browser sessions.                             |
| **Google AI Studio (Web)**      | Independent Developer Bucket                 | High compute/rate limits. High-throughput overflow pipeline when main API structures bottleneck due to network load.                                                                                            |

### B. Supplementary Ecosystem Channels

| Alternative Provider       | Quota Metrics                      | Strategic Caveats & Mechanics                                                                                                                                |
| -------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Perplexity Pro**         | Prompt-Based (Rolling 24hr Buffer) | **No Token Penalty.** Ideal for multi-step reasoning. Features character caps on raw text prompts; bypassed via file uploads or segmented context injection. |
| **Google AI API (Direct)** | Pay-per-Call Meter                 | Final tier fallback. Charged on credits derived from tokens. Subject to peak-hour concession errors and concurrency drops under high public demand.          |
| **Cursor Workspace**       | ~12 Free Accounts                  | High-speed composer logic. Maintained as a secondary fallback pipeline requiring automated authentication rotation scripts.                                  |

### C. Strategic Context Injection Routing (Perplexity Pro)

To maximize the prompt-based Perplexity Pro allocation without consuming scarce file upload allowances (50/week rolling buffer), `ai-os` defines specific handling profiles:

1. **Thread Chunking (Compactification Mitigation):** For small-to-medium files, code blocks are injected into the thread *in sequential parts* as raw messages rather than files. The frontend manages thread length strictly to ensure backend compactification loops do not truncate critical lines before processing.
2. **File Monopolization:** If code size outpaces safe message tracking limits, the frontend falls back to a unified single-file compile to consume exactly one file-upload slot.

### D. Shared Injection Framework & Versioned Revision Pipeline

To sync live interactive triage sessions without manual intervention, a single JavaScript script runs across both the local in-app Tauri-framed `gemini.google.com` panel and standard external browser instances. This script binds Google's cloud interface directly to the local `ai-os` database asset layer, managing stateless web-chat updates using a local Git versioning pipeline to avoid duplication.

```
 ┌────────────────────────────────────────────────────────┐
 │            Gemini Web UI / Tauri Webview               │
 │  - Receives response with [AIOS_DOC] structural tags   │
 └───────────────────────────┬────────────────────────────┘
                             │
            [Extracts Clean Document Block Only]
                             │
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │                 Shared Script Engine                   │
 │  - Forwards payload + Thread ID to Local Bridge        │
 └───────────────────────────┬────────────────────────────┘
                             │
                   [HTTP POST to /api/revision]
                             │
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │                   Rust Bridge Layer                    │
 │  - Resolves Thread ID to a dedicated Git worktree      │
 │  - Writes file -> Executes deterministic Git Commit    │
 └────────────────────────────────────────────────────────┘

```

#### 1. Functional Requirements

* **Automated Thread Tracking:** The script listens to DOM mutations and page navigation events. When a chat session deepens, the full text sequence of the active thread is serialized and transmitted as raw JSON via a loopback request to the Rust bridge at `[http://127.0.0.1](http://127.0.0.1):YOUR_PORT/api/context/sync`.
* **Delineated Block Extraction:** The user script monitors DOM updates specifically for incoming `[AIOS_DOC]` tags. Once generation concludes, the engine extracts *only* the raw string enclosed within the document boundaries. This isolated block is shipped to the local daemon along with the unique session `Thread ID`.
* **State Deduplication:** Decoupling the document body from conversational text textually prevents multi-megabyte duplication within local log databases. The chat history track remains lean, recording only short conversational context, while the file growth is cleanly tracked by Git diffs.
* **DOM Button Injection:** The script targets Gemini’s response text containers, dynamically adding a native-looking `[Save to Local Notes]` button alongside standard UI actions (like copy or thumbs up).
* **Context Isolation Handling:** Code blocks and long markdown strings are parsed directly from pre-rendered elements to preserve structural indents before being dispatched to the native disk.

#### 2. Architecture Spec: The Runtime Contract

The script uses a standardized header block for the browser extension environment, matching the loopback address permission schemes to bypass strict web-app Content Security Policy (CSP) blocking.

```javascript
// ==UserScript==
// @name         ai-os Gemini Context Sync
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Siphons web UI threads and custom code blocks directly into the local ai-os ecosystem
// @author       Matthew Murphy
// @match        https://gemini.google.com/*
// @grant        GM_xmlhttpRequest
// @connect      127.0.0.1
// @run-at       document-end
// ==/UserScript==

// Core shared logic hooks into text containers, grabs innerText,
// and routes payload back to the Rust bridge tracking layer.

```

#### 3. Rust Bridge Adaptation & Revision Pipeline

To support this reverse flow, the Rust bridge layer runs a minimal local loopback daemon (via `axum` or `actix-web`) listening exclusively on `127.0.0.1`.

* **`/api/context/sync`**: Receives structural updates of the current conversation to maintain historical alignment.
* **`/api/notes/save`**: Accepts individual document payloads triggered by the injected user buttons, dumping clean markdown files directly into `/Users/matthewmurphy/projects/ai-os/.agent-logs/details/`.
* **`/api/revision/commit`**: Coordinates stateless web-chat updates into localized version histories:
1. **Worktree Isolation:** Receives a payload containing `thread_id`, `filename`, and the raw `content` string. It references or initializes a hidden local Git directory assigned exclusively to that thread context (`.agent-logs/git/[thread_id]/`).
2. **Deterministic Commit Execution:** Overwrites the target file locally and fires an automated Git sequence:
```bash
git add .
git commit -m "Revision executed via Web UI Sync" --allow-empty

```


3. **UI Sync Broadcast:** Emits a WebSocket event back to the Tauri frontend containing the new short commit hash, automatically updating the revision slider array in the UI view.



---

## 9. Future Roadmap & Planned Features

1. **Semantic Thought Layer:** Integrating local vector embeddings for user notes, allowing the OS to recall abstract thoughts and link them to code commits automatically.
2. **Automated Auth Rotation Daemon:** Fully implementing the headless account switcher for the underlying developer accounts and session clients to bypass user-facing login screens entirely.
3. **Deeper macOS Automation:** Expanding permissions safely to interact with native macOS apps via JXA/AppleScript wrappers.