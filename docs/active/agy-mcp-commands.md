# Antigravity MCP Server Commands (agy-mcp)

The `agy-mcp` server exposes a suite of tools for connecting to and interacting with the Antigravity agent CLI. Below is a breakdown of the available tools and their capabilities.

## Tools Overview

### Core Interaction
- **`agy`**: Run the `agy --print` command synchronously and return the assistant text + metadata. This serves as a compatible drop-in replacement for the legacy `gemini` tool. Supports PROMPT, cd, sandbox, SESSION_ID, return_all_messages, and model fields, along with mode, timeout, allow_write, worktree, backend, and output_protocol options.
- **`agy_continue`**: Continue an existing agy session. Identical to `agy` but explicitly requires a `SESSION_ID` to resume the specific Antigravity conversation via the adapter.

### Background Job Execution
- **`agy_start`**: Start an agy session asynchronously in the background. Returns an envelope with `status='running'` and a `job_id` which you can poll for status.
- **`agy_status`**: Retrieve the `JobRecord` (status, exit code, error messages, timestamps) for a specific `job_id`.
- **`agy_read`**: Read events from a background job's event log. Accepts a `since` 0-based offset. A `translate` parameter allows translating events into `raw`, `claude`, or `codex` wire formats.
- **`agy_result`**: Fetch the captured output of a finished background job. If `job_id` is omitted, it fetches the latest finished job. Include `include_events=true` to also return the stored events.
- **`agy_cancel`**: Signal a running background job to terminate. Returns whether the worker was successfully signalled.

### Session Management
- **`agy_sessions`**: List recent jobs and sessions, starting from the newest. Takes an optional `limit` parameter (defaults to 50, pass 0 for all).
- **`agy_purge`**: Delete session-store job directories that are older than the specified number of `days`. Returns a count of removed jobs and remaining jobs. `days` must be a positive integer.

### Diagnostic & Administration
- **`agy_doctor`**: Run capability, authentication, and session-store diagnostic probes. Returns a structured JSON report. Pass `force_refresh=true` to drop cached binary checks (useful after an upgrade).
- **`agy_install_skill`**: Install the `agy-mcp` collaboration skill bundle across one or more agent platforms. Targets include `claude`, `codex`, `antigravity`, or `all`.

## Example Usage

To run a health check locally via MCP CLI:
```bash
mcp-cli cmd --tool agymcp:agy_doctor --tool-args "{}"
```
