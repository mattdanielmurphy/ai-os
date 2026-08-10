# AGY Proxy Service (`services/agy-proxy`)

## 1. Overview & Purpose
`agy-proxy` is a local OpenAI-compatible FastAPI proxy server running on `http://127.0.0.1:8080`. 
Its primary role is to bridge HTTP OpenAI API callers (specifically **Hermes WebUI**, **Hermes Studio**, or custom scripts) to the local `/Users/matt/.local/bin/agy` CLI binary, utilizing your **Google subscription quota** directly without hitting paid API billing endpoints.

---

## 2. Strict Model Routing Rules

To protect your subscription quota and prevent accidental billing against Vertex AI or paid OpenRouter endpoints, `proxy.py` enforces a **strict model isolation policy**:

### A. Strict AGY Models (`/Users/matt/.local/bin/agy` CLI)
Any request for the following models is **STRICTLY HARD-LOCKED** to invoke the local `agy` CLI binary directly:
- `gemini-3.6-flash-low`, `gemini-3.6-flash-medium`, `gemini-3.6-flash-high`
- `gemini-3.1-pro-low`, `gemini-3.1-pro-high`
- Models prefixed with `agy/` or `@custom:agy:`
- Alias strings `agy` or `subagent`

> ⚠️ **STRICT GUARANTEE**: Under NO circumstance will requests for `agy` or `gemini-*` models be routed to `LiteLLM`, Vertex AI, or paid Google API keys, even if tools or complex payloads are present.

### B. Non-AGY Models (`LiteLLM` Proxy Path)
Only non-agy models (such as `sonnet`, `opus`, `fable`, `deepseek-v4-flash`) that explicitly require third-party provider access will route to local `LiteLLM` (`http://127.0.0.1:8082`).

---

## 3. Session Persistence & Thread Resume Protocol

When a user interacts with Hermes WebUI across multiple turns in a thread, `agy-proxy` maintains stateful session persistence:

1. **Stable Session Hash (`_get_session_key`)**:
   - `proxy.py` extracts the anchor message (the first user or system message content in the conversation array) and computes a stable 16-character SHA256 key.
   - Hashing on the anchor message content ensures the session key remains **100% identical** across initial and follow-up turns in Hermes WebUI.

2. **Session Persistence File (`~/.hermes/agy_proxy_sessions.json`)**:
   - Maps the 16-character session key to the `agy` conversation UUID (`conversation_id`).
   - Example: `"eee704fc1198359d": "1fc3e61d-7ec3-4137-a3ca-451a757717cb"`

3. **Resuming Threads**:
   - When a follow-up turn is received, `proxy.py` looks up the session key in `agy_proxy_sessions.json`.
   - If found, it appends `--conversation <conv_id>` to the `agy` command line.
   - `agy` resumes execution inside `~/.gemini/antigravity-cli/brain/<conv_id>/` with complete prior history intact.

---

## 4. Streaming & Text Formatting

- **Stream Output Format**: `agy` is launched with `--output-format stream-json`.
- **SSE Chunk Encoding**: `proxy.py` parses `agy` events and yields standard SSE OpenAI completion chunks (`data: {"object": "chat.completion.chunk", ...}`).
- **Paragraph Separation**: Double newlines (`\n\n`) are prepended to new step text deltas to ensure clean, readable paragraph formatting in Hermes UI without text collisions.

---

## 5. Daemon & Process Lifecycle

- **Process Wrapper**: Managed as a persistent daemon via `tmux` in session `agent-agy-proxy`.
- **Launch Command**: `bash /Users/matt/Library/Scripts/tmux-agent-wrapper.sh keepalive agent-agy-proxy /Users/matt/projects/hermes-agent/venv/bin/python3 /Users/matt/projects/ai-os/services/agy-proxy/README.md`
- **Virtual Environment**: Uses `/Users/matt/projects/hermes-agent/venv/bin/python3`.
- **Health Check**: `curl http://localhost:8080/v1/models`
