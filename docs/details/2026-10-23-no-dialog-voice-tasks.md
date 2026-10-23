# No dialog for incoming voice tasks (2026-10-23)

## 13:20 Where the send_task dialog comes from

Matt (voice, 12:58): a dialog asks whether it's OK to open or start a remote thread whenever send_task fires. Wants tasks to just go through.

---

### Mac side is clean

- `~/Library/Logs/Claude/remote-control.log` around 12:58-12:59: the coordinator's new threads were admitted with no consent step ("admitted (new, nudge poll)" then "attached"). No consent/pending_consent lines today in that log or main.log.
- `scripts/voice_task_inbox.py` delivered both 12:58 tasks via `claude -p --cloud` (no paste, no take-control banner). Unified log around 12:58:14-12:58:45 shows no consent UI (CoreServicesUIAgent, SecurityAgent) from that run.
- So the coordinator's guess (Remote Control folder consent) didn't fire for these tasks.

---

### Likely cause: claude.ai tool approval

- send_task is the My_Mac connector's only write tool that fires on every task. claude.ai asks "Allow Claude to use send_task?" for connector tools left on "Needs approval". That matches "whenever send_task fires", and it happens in the Claude app before anything reaches the Mac.
- Fix is an account setting only Matt can flip: claude.ai Settings > Connectors > My_Mac > send_task > Always allow.
- Not verified: the browser pane isn't signed in to claude.ai, so I couldn't read the current per-tool setting. If the dialog looked different, a screenshot pins it.
- Rejected: adding MCP annotations to send_task; they don't skip claude.ai's approval.

### Undo
- Set the tool back to "Needs approval" in the same place.
