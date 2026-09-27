# AI-OS Dynamic Codex Hook-Based Policy Engine

This subsystem replaces the static 24 KB monolithic global `~/.codex/AGENTS.md` with an event-driven, dynamic policy engine powered by Codex native hooks.

## Key Goals & Architectural Invariants
1. **Zero Overhead for Casual Queries**: Ephemeral, projectless chats (e.g. asking for chocolate recommendations or summarizing pickleball rules in `~/Documents/Codex/...`) bypass policy injection entirely (< 1ms latency, 0 injected tokens).
2. **Deterministic Hard Guardrails**: Model instructions alone are probabilistic. Hard constraints (blocking `rm`, blocking `.env` reads, enforcing `bun`, blocking `git init ~`) are intercepted and enforced deterministically at the execution layer via `PreToolUse`.
3. **Just-In-Time Policy Injection**: Substantive tasks and git repositories dynamically receive modular policy packs compiled from `.rules/` via `UserPromptSubmit`.
4. **Conditional Mem0 Recall**: Durable user facts from local Mem0 are retrieved ONLY when personal preferences, setup history, or user context could matter.
5. **Completely Decoupled from `preflight.py`**: Runs in sub-millisecond execution loops without invoking network requests, git pulls, or slow daemon probes.

---

## Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   CODEX ENGINE RUNTIME                                 │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
                    ┌───────────────────────────────────────────────┐
                    │    Event 1: UserPromptSubmit Hook (Prompt)     │
                    │   Input: { prompt, cwd, model, session_id }   │
                    └───────────────────────┬───────────────────────┘
                                            │
               ┌────────────────────────────┴───────────────────────────┐
               ▼                                                         ▼
     [Ephemeral / Casual Gate]                                 [Project / Intent Gate]
     CWD == ~/Documents/Codex/...                              CWD == Git repo OR
     Prompt == "What is...", "Translate..."                    Prompt has code/system keywords
               │                                                         │
               ▼                                                         ▼
     Fast Exit (< 2ms)                                         Dynamic Policy Assembly
     additionalContext: null                                   - Slices relevant .rules/ packs
     0 Mem0 lookups                                            - Conditional Mem0 fact recall
     0 prompt token bloat                                                │
               │                                                         │
               └────────────────────────────┬────────────────────────────┘
                                            ▼
                       ┌─────────────────────────────────────────┐
                       │           LLM Model Reasoning           │
                       │    (Minimal AGENTS.md + Context)        │
                       └────────────────────┬────────────────────┘
                                            │ Emits Tool Call
                                            ▼
                    ┌───────────────────────────────────────────────┐
                    │       Event 2: PreToolUse Hook (Execution)     │
                    │   Input: { tool_name, tool_input, cwd }       │
                    └───────────────────────┬───────────────────────┘
                                            │
                    ┌───────────────────────┴───────────────────────┐
                    ▼                                               ▼
         [Violation Detected]                              [Sanitized & Safe]
         - 'rm' command used                               - 'mv' to ~/.Trash/
         - Raw .env / secret read                          - 'aios-env check'
         - 'npm'/'pnpm' instead of 'bun'                   - 'bun run' / 'bun add'
         - 'git init ~' in home root                       - Scoped project dir
                    │                                               │
                    ▼                                               ▼
         decision: "block" (deny)                          decision: "approve" (allow)
         Tool call HALTED before OS execution              Tool call executes normally
         Corrective feedback fed to model
```

---

## Component Inventory

- **`classifier.py`**: Implements the 3-tier routing architecture:
  - *Tier 0*: Heuristic CWD & regex filter for casual chats (< 2ms).
  - *Tier 1*: Slices pre-compiled policy packs from `~/.codex/policies/`.
  - *Tier 2*: Conditional semantic recall from local Mem0 vector database (`aios_memory.py`).
- **`tool_guard.py`**: Intercepts tool calls in `PreToolUse` and enforces hard security rules:
  - Destructive commands (`rm`, `rmdir`) -> blocked (instructs `mv <path> ~/.Trash/`).
  - Secret isolation (`.env*`, `*credentials*`, `id_rsa`, `*.pem`, `*.key`) -> blocked (instructs `aios-env`).
  - Tooling policy (`npm`, `pnpm`, `yarn`) -> blocked (instructs `bun`).
  - Home directory repo guard (`git init ~`) -> blocked.
  - System temp guard (`/tmp/`) -> blocked (instructs `./tmp/`).
- **`on_user_prompt.py`**: Executable CLI adapter for `UserPromptSubmit` event.
- **`on_pre_tool_use.py`**: Executable CLI adapter for `PreToolUse` event.
- **`rollout.py`**: CLI to monitor metrics and switch operating modes (`shadow`, `enforce`, `disabled`).
- **`rollback.py`**: Instant 1-second recovery tool restoring monolithic `AGENTS.md.bak`.
- **`test_hooks.py`**: Standalone automated test and benchmark suite (27/27 test cases).

---

## Operating Modes

Operating modes are configured in `~/.codex/hooks_config.json`:

1. **`shadow`**:
   - Hooks inspect all prompt submissions and tool executions.
   - Guardrail violations are recorded to `~/.codex/hooks_audit.log`.
   - Tool calls are **not blocked** (returns `approve`), allowing risk-free verification.
2. **`enforce`**:
   - Hard guardrails actively halt offending tool executions before touching the OS.
   - Explanatory feedback is passed back to the model so it can correct its tool call.
3. **`disabled`**:
   - Hooks return immediate pass-throughs without evaluation.

### Managing Modes with `rollout.py`
```bash
# View current status, AGENTS.md size, and audit events
python3 scripts/codex_hooks/rollout.py --status

# Switch to shadow mode
python3 scripts/codex_hooks/rollout.py --mode shadow

# Switch to enforce mode
python3 scripts/codex_hooks/rollout.py --mode enforce
```

---

## Instant Rollback

If any unexpected behavior occurs:
```bash
python3 scripts/codex_hooks/rollback.py
```
This restores `~/.codex/AGENTS.md` from `~/.codex/AGENTS.md.bak` and disables hooks in under 1 second.

---

## Verification & Testing

Run the full automated test suite at any time:
```bash
python3 scripts/codex_hooks/test_hooks.py
```
Verifies sub-millisecond casual chat latency, project policy injection, Mem0 semantic retrieval, and all deterministic guardrails.
