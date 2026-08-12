---
name: agy
description: "Delegate to agy CLI and use agy's LiteLLM proxy as a Hermes custom provider. Print mode, interactive mode, quoting, path conventions, and provider routing."
version: 1.2.0
author: Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [Agy, Subagent, Orchestration, CLI, Delegation]
    related_skills: [claude-code, opencode, ai-os-auto-commit]
---

# Agy — Local Orchestrator Agent

[Agy](https://github.com/nousresearch/hermes) is Matt's primary worker-bee orchestration agent. It runs locally via LiteLLM proxy on `localhost:8082` (inside tmux session `litellm`). Use it for cheap delegation — research, investigation, one-shot tasks, anything you'd rather not eat tokens for in your main thread.

## When to Use

- **Research tasks** — "find out why X is happening", "check system state", "investigate error Y"
- **Cheap parallel work** — agy uses tiered LiteLLM workers (cheaper models)
- **Fire-and-forget investigations** — start a background agy task and get results back
- **Anything the user explicitly asks you to delegate to agy** — don't over-engineer it, just call it
- **Triage mode: when running on a cheap/fast model** — check AGENTS.md triage rules. If the task is complex (multi-file analysis, cross-referencing repos, protocol research, reading large codebases) and you're on a cheap model, hand off to agy immediately instead of doing it yourself. Do NOT default to reading files yourself when you could delegate.

### CRITICAL: "Pass this to agy" means LITERAL delegation

When the user says "pass this to agy", "hand this off to agy", "give this to agy", or shares a URL/link saying "pass this off":

- **Do NOT research the link yourself first.** Do NOT open the URL. Do NOT form any opinion about the content.
- **Do NOT editorialize.** Do NOT add commentary, context, or your own observations. Do NOT explain what you're doing.
- **Do NOT do any prep work.** Do NOT read files, check state, or gather context before delegating.
- **Just pass the user's exact words to agy via `mcp__agymcp__agy`.** Include the URL/reference verbatim. Let agy do the reading.
- **If the user asks for a raw prompt** (not MCP delegation — they want text to paste themselves), just give them the prompt they described. No extra sections, no explanations, no "here's what this does". Just the prompt text.

**Why:** The user has explicitly designed agy as the research worker. When they route something there, they already know what they want. Any work you do first is wasted tokens and frustrates them.

## Prerequisites

- agy installed at `~/.local/bin/agy` (confirm with `which agy`)
- LiteLLM proxy running: `tmux has-session -t litellm 2>/dev/null` (agy connects automatically)
- AGENTS.md/CLAUDE.md in the cwd — agy loads these for project context

## Critical: Argument Order

**`-p` takes the NEXT ARGUMENT as the prompt text.** This is the #1 pitfall.

```
# WRONG — --dangerously-skip-permissions gets consumed as the prompt text
agy -p --dangerously-skip-permissions "do X"

# RIGHT — prompt text immediately after -p, flags after the prompt
agy -p "do X" --dangerously-skip-permissions
```

In the wrong order, agy reads `--dangerously-skip-permissions` as your prompt and responds about its permission configuration instead of doing the task.

## Print Mode (One-Shot Tasks)

Print mode runs a single prompt non-interactively, returns the result, and exits. No PTY needed. This is the default integration path:

```bash
agy -p "Your task description here" --dangerously-skip-permissions --print-timeout 5m
```

### When to use print mode:
- One-shot investigations and diagnostics
- Scripted automation
- Any task where you don't need multi-turn conversation

### Timeout notes:
- `--print-timeout` defaults to `5m0s` (5 minutes)
- Must use Go duration format: `5m`, `10m`, `30s` — bare numbers fail with `invalid value`
- Set a high timeout for complex investigations; the command returns instantly when done, timeout is only a cap

### Quoting Guide for Shell Invocation

| Prompt contains | Use | Example |
|---|---|---|
| Any text (short or long) | Single quotes (bash multiline) | `agy -p 'your whole prompt here'` — single quotes prevent ALL bash interpretation of backticks, $, and other special chars |
| Single quotes inside prompt | Double-quote the outer string | `agy -p "it's a permissions issue"` |

**Rule of thumb:** ALWAYS use a single-quoted string directly in the terminal command. Single quotes pass everything through verbatim — backticks, $ signs, newlines, all of it. If the prompt is very long, bash single-quoted strings can span multiple lines naturally.

**NEVER do any of these:**
- ❌ Write prompt to a file and read with `$(cat file)` — backticks and $ signs in the file get interpreted by bash
- ❌ Use Python subprocess wrappers — triggers permission prompts, wastes CPU and time
- ❌ Pipe stdin into agy (`cat prompt | agy -p`) — agy doesn't read stdin for the prompt
- ❌ Create temp scripts, heredocs, or intermediate layers

If the quoting is awkward, fix the quoting — don't escalate the infrastructure. The user notices and is frustrated by extra processes, permission dialogs, and fan noise from needless overhead.

**Long prompts:** Bash single-quoted strings span multiple lines naturally. This works fine:
```bash
agy -p 'First paragraph of instructions.

Second paragraph with more detail.

Third paragraph with even more context.
Final line.' --dangerously-skip-permissions --print-timeout 5m
```

## Interactive Mode (Multi-Turn)

Not typically needed for agy (it's a worker, not a conversational agent), but available if the task needs follow-up:

```bash
agy -i "initial prompt" --dangerously-skip-permissions
```

## Key Flags

| Flag | Effect |
|------|--------|
| `-p, --print` | Non-interactive one-shot mode (takes NEXT ARG as prompt text) |
| `-i, --prompt-interactive` | Start interactive session with initial prompt |
| `-c, --continue` | Resume the most recent conversation |
| `--dangerously-skip-permissions` | Auto-approve all tool permission requests without prompting |
| `--print-timeout <duration>` | Max wait in Go duration format (e.g., `5m`, `30s`) |
| `--model <name>` | Override model for the session |
| `--agent <name>` | Choose a specific agent profile |
| `--mode <mode>` | Set execution mode: `accept-edits`, `plan` |
| `--project <id>` | Project ID for session context |
| `--sandbox` | Run with terminal restrictions enabled |
| `--conversation <id>` | Resume a specific conversation by ID |

## Procedure

1. **Formulate a self-contained prompt** — agy knows nothing about your conversation history. Include all context: file paths, error messages, constraints, and what you've already confirmed/found.
2. **Call agy via a direct terminal command.** Single-quoted string. Full stop. No Python wrappers, no temp files, no intermediate layers, no heredocs. Just `agy -p 'prompt' --dangerously-skip-permissions --print-timeout 5m`.
3. **Wait for the result** — `--print-timeout` handles the wait. The response comes back in `stdout`.
4. **Report findings** — summarize what agy found or did.

## Verification

Smoke test that agy responds:
```bash
agy -p "hello world this is a test" --print-timeout 1m
```
Expected: a relevant reply (not about permissions configuration — if it responds about permissions, the argument order was wrong and `--dangerously-skip-permissions` was eaten as the prompt text).

### Agy Proxy Wrapper (OpenAI-Compatible Integration)

For high-performance integration that supports streaming and standard `custom_providers` configuration without patching the Hermes core, use the **Agy Proxy Wrapper** pattern. This involves a tiny FastAPI server that translates OpenAI API requests into `agy --print` calls.

### Benefits
- **Zero-patch integration**: Uses the standard `custom_providers` section in `config.yaml`.
- **Streaming support**: Proxies line-by-line output from the CLI to the WebUI.
- **Model routing**: The `request.model` field is passed through as `--model <name>` to agy, so switching models in Hermes routes to the right Antigravity tier.
- **Persistent configuration**: Survives Hermes updates and `git pull`.

### Available Models (via agy proxy)
The proxy exposes these models for Antigravity routing:

| Alias | Model Name | Description |
|---|---|---|
| `agy-flash-low` | `gemini-3.6-flash-low` | Default — cheapest Gemini tier |
| `agy-flash-med` | `gemini-3.6-flash-medium` | Mid-tier Gemini flash |
| `agy-flash-high` | `gemini-3.6-flash-high` | Best Gemini flash |
| `agy-pro-low` | `gemini-3.1-pro-low` | Gemini 3.1 Pro (low cost) |
| `agy-pro-high` | `gemini-3.1-pro-high` | Gemini 3.1 Pro (full) |
| `agy-sonnet` | `claude-sonnet-4-6` | Claude Sonnet via agy |
| `agy-opus` | `claude-opus-4-6-thinking` | Claude Opus via agy |
| `agy-oss` | `gpt-oss-120b-medium` | Open-source model via agy |

Use these with `hermes config set delegation.model <name>` or `/model agy-flash-low` in chat. The delegation config defaults to `gemini-3.6-flash-low`.

### Deployment (macOS)
1. **Service Path**: Usually `/Users/matt/projects/ai-os/services/agy-proxy/proxy.py`.
2. **Launch Agent**: Create `com.matt.agent.agy-proxy.plist` using `tmux-agent-wrapper.sh`.
3. **Registration**: Add to `KNOWN_AGENTS` in `~/.local/bin/la`.
4. **Hermes Config**:
   ```bash
   hermes config set custom_providers.agy.base_url "http://127.0.0.1:8080/v1"
   hermes config set custom_providers.agy.model "agy"
   hermes config set model.default "agy"
   ```

See `references/agy-proxy-implementation.md` for the reference FastAPI code.

## Pitfalls & Gotchas

1. **#1: `-p` eats the next argument as the prompt.** Flags placed right after `-p` (like `--dangerously-skip-permissions`) become prompt text instead of flags. Prompt text must come IMMEDIATELY after `-p`, then other flags follow.
2. **Never use Python wrappers, temp files, or heredocs.** Writing the prompt to a file and reading it back, or wrapping in Python subprocess, triggers permission prompts, spins up the CPU, wastes time, and frustrates the user. Single-quoted string in terminal. Full stop.
3. **Don't over-engineer.** The user's instruction was "just call agy the way I told you." A direct terminal command with a single-quoted prompt string is always the right answer. If the quoting is awkward, fix the quoting — don't add layers.
4. **Long prompts can timeout.** If agy doesn't respond within `--print-timeout`, it errors with `timeout waiting for response`. Increase the timeout or simplify the prompt.
5. **agy loads project context** (AGENTS.md, CLAUDE.md) from the cwd. If you want agy to follow your prompt exactly and not derail into project-specific knowledge, be explicit about what to ignore.
6. **No heredocs.** Do not use `cat << 'EOF'` in terminal to write files for agy — use write_file instead.
7. **agy is not conversational.** It's a worker. Use `-p` for one-shots. Don't try to have multi-turn conversations unless you need `-i`.
8. **Triage: check AGENTS.md triage rules before starting research.** If you're running on a cheap/fast model and the task is complex (multi-file analysis, cross-referencing, protocol research), delegate to agy instead of doing it yourself. Failing to do this burns tokens on the expensive model and frustrates the user.
9. **"Pass this to agy" means ZERO prep — not even file reads.** When the user says "pass this to agy", "hand this off to agy", or "you must pass this whole prompt off to agy": do NOTHING except dispatch. No read_file, no search_files, no terminal probes, no checking state, no "let me just look at X first." Every tool call you make before dispatching is wasted work the user explicitly routed to agy. Even if you think you're being helpful by gathering context first, you're burning tokens on the wrong model and frustrating the user. Dispatch verbatim, then report what agy produced. This rule applies even (especially) when you're running on a cheap triage model — the user's instruction to delegate overrides all efficiency heuristics.
10. **User wants a raw prompt, not analysis.** When they say "give me a prompt that I'll run myself", they want exactly the prompt text — no explanation, no "here's what this does", no preamble. Just the prompt.
11. **`include_hermes_prompt` MUST be `false` for MCP dispatches.** The default is `true`, which injects the full Hermes system prompt (~100KB including AGENTS.md, CLAUDE.md, memory, user profile) into agy's prompt. This wastes context, burns quota, and has caused worktree-mode jobs to hit context limits and fail after 48 minutes. Always set `include_hermes_prompt=false` on `mcp__agymcp__agy` and `mcp__agymcp__agy_start` unless you specifically need agy to follow Hermes rules.
12. **`model` parameter on agy MCP tools is silently ignored.** The agy MCP server (`agymcp`) uses its own tiered model routing regardless of what `model=` you pass. However, when using agy as a **custom provider** (via the agy-proxy at `http://127.0.0.1:8080/v1`), the `model` field IS passed through as `--model <name>` to agy — model selection works there. For MCP dispatches, dead model names (`gemini-1.5-pro-002`) produce zero output with exit code 0 — a silent failure with no error. Live model names are silently downgraded to the default tier (`Gemini 3.5 Flash (Low)` as of 2026-07). To verify the actual model used via MCP, read events with `agy_read(job_id=...)` and check the `init` event's `metadata.model` field. Do not rely on the `model` parameter to select a specific tier for MCP dispatches.
13. **Live UI Streaming vs MCP:** Using MCP tools (`mcp__agymcp__agy`) or `terminal` to run agy means output goes into the Hermes *context window* as a hidden block after execution finishes. It does NOT stream live to the WebUI. For real-time streaming of agy's thoughts (`reasoning.delta`) and execution steps to the user interface, agy cannot be just a tool — it must be integrated natively into the Hermes backend event loop.

## Agy MCP Tool (Hermes Integration)

Hermes provides `mcp__agymcp__agy` as a first-class MCP tool — no terminal command needed. This is the preferred way to delegate from Hermes to agy.

### Key behaviors

- **Creates a tmux session** for each agy task (session name contains the job ID). You can inspect it with `tmux capture-pane -t agy-mcp -p`.
- **Worktree mode**: when `allow_write=true` and `mode=execute`, agy creates a git worktree at `~/.agy-mcp/worktrees/job-<id>/` for isolated changes.
- **Synchronous call**: `mcp__agymcp__agy(PROMPT=..., cd=..., timeout=...)` waits for the result.
- **Background call**: `mcp__agymcp__agy_start(...)` to start, then `mcp__agymcp__agy_status` + `mcp__agymcp__agy_result` to poll.
- **Session resume**: `mcp__agymcp__agy_continue(SESSION_ID=..., PROMPT=...)` for multi-turn tasks.

### Inspecting a running agy task

When an agy MCP call returns with a job_id but no visible output, you can inspect the tmux session:

```bash
# List all tmux sessions to find agy-mcp sessions
tmux ls | grep agy

# Capture the last 100 lines of the agy-mcp pane
tmux capture-pane -t agy-mcp -p -S -100

# Check the worktree for changes
cd ~/.agy-mcp/worktrees/
ls -la
cd job-<id>/
git status
git diff
```

### When to use MCP tool vs. terminal command

| Use case | Method |
|---|---|
| Quick one-shot from Hermes | `mcp__agymcp__agy(PROMPT=..., cd=..., include_hermes_prompt=false)` |
| Task that needs to write files | `mcp__agymcp__agy(PROMPT=..., cd=..., allow_write=true, mode=execute, include_hermes_prompt=false)` |
| Background task with polling | `mcp__agymcp__agy_start(PROMPT=..., cd=..., include_hermes_prompt=false)` then `agy_result` |
| Multi-turn investigation | `mcp__agymcp__agy_start(...)` then `mcp__agymcp__agy_continue(...)` |
| Complex shell pipeline | Terminal `agy -p '...'` |
| Need to inspect intermediate state | Any method, then inspect tmux with `tmux capture-pane` |

### Architecture: tmux-based background, not synchronous capture

The agy MCP server does NOT capture output synchronously. It starts agy inside a **tmux session** that Hermes (or the Hermes Studio/Tauri desktop app) can attach to later. The synchronous `mcp__agymcp__agy` call returns a `SESSION_ID` / `job_id` handle — the actual agy output lives in the tmux buffer.

When the MCP call returns with empty `agent_messages`, that does NOT mean agy failed. It means the output wasn't captured through the MCP response path. To read it:

1. Use `tmux capture-pane -t agy-mcp -p -S -100` to see the last 100 lines
2. Or use the Hermes Studio/Tauri desktop app's built-in tools for reading in-progress agy tasks
3. Or call `agy_result(job_id=...)` / `agy_read(job_id=...)` MCP tools

The Tauri app (Hermes Studio / AI-OS desktop) has first-class support for polling in-progress agy tasks. The pattern is: start with `mcp__agymcp__agy_start(...)`, then poll with `mcp__agymcp__agy_status` and read results with `mcp__agymcp__agy_result`.

## Using LiteLLM as a Hermes Provider

agy's LiteLLM proxy (`localhost:8082`) is an OpenAI-compatible endpoint. Hermes can use it as a `custom` provider — Hermes builds the full system prompt (memory, skills, tool schemas) and sends API calls to LiteLLM, preserving the complete Hermes experience while changing only where inference lands.

### Configuration

```yaml
# ~/.hermes/config.yaml
model:
  default: "hy3-free"          # see references/litellm-routing.md for full model list
  provider: "custom"
  base_url: "http://localhost:8082/v1"
```

No `api_key` needed — Hermes trusts loopback URLs for custom providers (`_loopback_hostname` in `runtime_provider.py`).

### Free models (truly zero-cost)

Three models route through OpenRouter's free tier: `hy3-free` (Tencent 295B MoE, strong coding), `poolside-laguna-free` (terminal/SE optimized), `nemotron-ultra-free` (NVIDIA, 1M context).

### Quota Pitfall: Gemini models do NOT use Antigravity free quota

The `gemini-2.5-flash` and `gemini-2.5-pro` models in LiteLLM route through `gemini/gemini-2.5-*` — this hits Google's API directly using `GEMINI_API_KEY`. This is a **separate quota bucket** from the Antigravity consumer OAuth free tier (`~/.gemini/oauth_creds.json`). Do not assume free Antigravity quota applies to LiteLLM Gemini models.

Full routing table and comparison of approaches: `references/litellm-routing.md`.

### Provider Label Semantics (what `custom:agy` actually means)

The provider label in Hermes config determines where traffic goes, and **the label must be semantically honest**. Matt corrected `agy: deepseek-v4-flash` as wrong: `agy` means the agy MCP tool (Google-quota OAuth path), and deepseek actually goes through OpenRouter. Labeling an OpenRouter model `agy:` misleads everyone reading the config or UI.

- `custom:agy` (`base_url: http://127.0.0.1:8080/v1`) = the **hybrid agy-proxy**: requests WITHOUT `tools` go to the agy CLI (paid Google quota); requests WITH `tools` forward to LiteLLM (8082) → OpenRouter/upstream.
- A main-session agent (which always sends tool schemas) routed via `custom:agy` is therefore actually **OpenRouter via LiteLLM** — not agy at all. Labeling it `agy: deepseek-v4-flash` is doubly misleading.
- **For OpenRouter-native models (deepseek, muse-spark, grok, etc.), use `provider: openrouter` directly** — Hermes has `OPENROUTER_API_KEY`, model IDs resolve on OpenRouter (verify with `curl https://openrouter.ai/api/v1/models`), and there's zero reason to bounce through 8080 → 8082. The UI label then reads `openrouter: deepseek/deepseek-v4-flash-latest` — honest. Also clear any stale `model.base_url` (the agy-proxy URL) when switching provider, or it can keep routing through the proxy.
- Reserve `custom:agy` for sessions that should genuinely ride the agy CLI Google-quota path.
- `delegation.model` / `delegation.provider` (agy for subagents) is a SEPARATE config from `model.default` (main session) — changing one does not change the other.

### DeepSeek on OpenRouter — verified quirks

- `~deepseek/deepseek-v4-flash-latest` IS listed on OpenRouter and is the rolling-latest alias (the `~` is REQUIRED; versionless `deepseek/deepseek-v4-flash-latest` returns 400). It resolves to the newest snapshot (e.g. `deepseek/deepseek-v4-flash-0731`). "I don't see it listed" usually means the `~` prefix was dropped.
- `content: None` + `finish_reason: length` with a small `max_tokens` window is NOT a failure: DeepSeek emits `reasoning_content` before `content`, consuming the budget. Bump `max_tokens` to ~200 and re-request; content returns normally.
- DeepSeek official cache-read pricing is ~$0.0028/M (flash) — ~90x cheaper than resellers (DigitalOcean $0.0168/M, up to $0.33/M). To pin official within OpenRouter via LiteLLM: model id `openrouter/~deepseek/deepseek-v4-flash-latest` + `extra_body: {provider: {order: ["DeepSeek"], allow_fallbacks: true}}` nested INSIDE `litellm_params` (6-space indent). Model-level `provider:` blocks are IGNORED by LiteLLM.

See `references/deepseek-openrouter-quirks.md` for the full verification probe and transcripts.

## Rules for Hermes Agents

1. **Call agy directly in terminal** — `agy -p 'prompt' --dangerously-skip-permissions --print-timeout 5m`. Single-quoted string, multiline if needed. No Python wrappers, no temp files, no intermediate layers, ever.
2. **Or use the MCP tool** — `mcp__agymcp__agy(PROMPT=..., cd=..., timeout=...)` when you're already in Hermes and want to delegate without a terminal command. Use `allow_write=true` + `mode=execute` for tasks that write files.
3. **Prompt after `-p`, flags after prompt** — correct order is critical.
4. **Self-contained prompts** — include all context agy needs; it has no memory of your session.
5. **Set a generous timeout** — investigations can take several minutes.
6. **Report results** — summarize what agy found, don't just dump the raw output.
7. **Use single quotes always** — they prevent ALL bash interpretation of special characters. If you need a literal single quote in the prompt, use double quotes for the outer string. Never escalate to file-read or Python.
8. **Triage first: when on a cheap model, delegate research to agy** — before reading large files or doing cross-repo analysis, check if you're on a cheap/fast model. If so, delegate to agy. The user will correct you if you burn tokens on research they expected agy to handle.