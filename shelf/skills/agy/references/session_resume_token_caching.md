# Session Resume & Token Caching Pattern for Agy Delegation

## Problem
Using one-shot `agy -p` or `mcp__agymcp__agy` repeatedly for multi-turn threads flattens conversation history into a single text block (`USER: ... ASSISTANT: ...`). This alters token boundaries, breaks server-side KV prompt caching (Google Gemini / Anthropic), and adds process boot overhead (~500ms) on every turn.

## Solution: Persistent `SESSION_ID` Resume Pattern

When delegating multi-turn investigations or complex subtasks to `agy`:

1. **Initial Task Dispatch**:
   Use `mcp__agymcp__agy_start` to initialize the task:
   ```json
   mcp__agymcp__agy_start(
     PROMPT="Investigate the audio rendering latency bug in CockBand",
     model="gemini-3.6-flash-high",
     include_hermes_prompt=false
   )
   ```
   Save the returned `job_id` (this is the `SESSION_ID`).

2. **Follow-Up Instructions**:
   Use `mcp__agymcp__agy_continue` passing the `SESSION_ID`:
   ```json
   mcp__agymcp__agy_continue(
     SESSION_ID="job-20260809-123456",
     PROMPT="Now test with audio buffer size set to 128 frames",
     include_hermes_prompt=false
   )
   ```

3. **Benefits**:
   - `agy` retains conversation context in `~/.agy-mcp/sessions/`.
   - Only the delta prompt is transmitted to the model backend.
   - Provider KV cache prefix is preserved (100% prompt cache hits).
   - Eliminates process re-initialization overhead.
