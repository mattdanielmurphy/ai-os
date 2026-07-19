## Goal
Fix empty workspace/no prompt response in the Hermes GUI view by passing the project directory (`cwd`) to session creation and tearing down old sessions when switching project workspaces.

## User Feedback & Decisions
- Pass `activeProject` as the `cwd` when starting a new session so `hermes serve` executes the agent in the correct workspace.
- Detect when `activeProject` changes in the Hermes engine and cleanly release the old session before establishing a new one.

## Changes Made
- Modified [hermesChat.ts](file:///Users/matt/projects/ai-os/tauri-gui/src/hermesChat.ts):
  - Added `_cwd` state and a `cwd` getter to track the workspace path of the active session.
  - Modified `createSession()` to accept a `cwd` string parameter and include it in the `session.create` JSON-RPC parameters.
  - Updated `closeSession()` and `disconnect()` to clear `_cwd`.
- Modified [main.ts](file:///Users/matt/projects/ai-os/tauri-gui/src/main.ts):
  - Updated `initHermesChat(cwd)` to accept a workspace directory.
  - If a session is already active but has a different workspace path than `cwd`, it cleanly closes the old session first.
  - Passed `activeProject` to `initHermesChat()` during eager auto-connection and manual prompt fallback connection.

## What Worked
- Rebuild via `bun run build` completed successfully.
- Correct workspace scope is now bound on session creation.

## What Didn't Work / Known Issues
None.

## Architecture Notes
- The `cwd` parameter in `session.create` is critical to ensuring that the spawned agent knows the context of the workspace and can locate and edit the project's codebase. Without it, the agent defaults to the server's launch directory (which may not contain the git repository, resulting in failed tool calls and prompt execution silences).

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/066be666-bc5b-4bce-a3bd-5bb7b36e4cb5/.system_generated/logs/transcript.jsonl)

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/066be666-bc5b-4bce-a3bd-5bb7b36e4cb5/.system_generated/logs/transcript.jsonl)
