## Goal
Allow stdout/stderr from the background `hermes serve` daemon to print to the main development server console when debugging or running locally.

## User Feedback & Decisions
- Change the `hermes serve` child process configuration to inherit standard output and standard error streams.

## Changes Made
- Modified [main.rs](file:///Users/matt/projects/ai-os/tauri-gui/src-tauri/src/main.rs):
  - Changed `.stdout(Stdio::null())` and `.stderr(Stdio::null())` to `.stdout(Stdio::inherit())` and `.stderr(Stdio::inherit())` for the spawned `/Users/matt/.local/bin/hermes` command.

## What Worked
- Rebuilding the Rust backend compiles cleanly.
- Terminated the stale background daemon instance to force it to spawn anew on the next Tauri launch/engine switch, binding stdout/stderr output successfully.

## What Didn't Work / Known Issues
None.

## Architecture Notes
- Using `Stdio::inherit()` enables the host environment of the Tauri application in development to print uvicorn and FastAPI logs directly to the launch shell context, showing all live message frames and RPC activities.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/066be666-bc5b-4bce-a3bd-5bb7b36e4cb5/.system_generated/logs/transcript.jsonl)

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/066be666-bc5b-4bce-a3bd-5bb7b36e4cb5/.system_generated/logs/transcript.jsonl)
