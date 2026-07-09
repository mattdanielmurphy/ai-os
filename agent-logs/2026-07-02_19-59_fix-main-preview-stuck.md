## Goal
The user reported that sometimes the main preview stops updating and looks stuck when the agent finishes the task (even though the final output is visible in the TUI).

## Changes Made
- Modified `src/main.ts` in the Tauri listener for the `pause-status` event.
- Added a call to `renderCustomTuiLog(lastRenderedThreadLog)` whenever the `pause-status` changes for the active project.
- **Why**: The `renderCustomTuiLog` only gets called during polling if the content of the log file changes. If the agent finishes and the process completes cleanly, the log file might be fully written *before* the pause status changes from 'Running' to 'Paused'. If this happens, the UI renders the final log contents but retains the "thinking..." spinner because the status is still 'Running'. When the status subsequently becomes 'Paused', no file content change is detected, so the UI never re-renders, leaving the spinner stuck permanently.

## What Worked
- Forcing a re-render of the existing log data during the `pause-status` state change successfully re-evaluates the "thinking" spinner logic and removes it.

## What Didn't Work / Known Issues
- None. The fix cleanly delegates state re-evaluation without needing redundant file I/O.

## Architecture Notes
- The "thinking" indicator in the AI-OS frontend is dual-conditional: it checks both the step state from `transcript.jsonl` (e.g. `status !== 'DONE'`) AND the process-level `pauseStatus === 'Running'`.
- Due to race conditions between process termination/sleeping and file writes, state changes in the background PTY processes require explicit UI updates in `main.ts` to clear UI indicators.
