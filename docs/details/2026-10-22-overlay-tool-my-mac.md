# Overlay tool for My Mac connector (2026-10-22)

## 20:50 overlay_on / overlay_off are live

Asked (voice task): a My_Mac connector tool so remote Claude sessions can turn Matt's orange "hands off" overlay on and off, with an auto-timeout, plus a server-instructions line telling Claude to use it before moving/resizing windows, clicking, typing or opening dialogs.

---

### Tools wrap claude-control

- `overlay_on(reason, light?)` runs `~/.hammerspoon/bin/claude-control ask "<reason>" 3 [--light]`, so it is the same banner + glow, same queue, same Esc / Esc Esc / Stop as local agents. Returns `granted`, or an error saying `cancelled` / `stopped` / failed, telling the caller not to act.
- `overlay_off()` runs `claude-control done <ticket>`.
- Rejected: a separate overlay. The take-control banner already is the global orange overlay, and reusing it keeps one queue so remote and local agents can't collide.

---

### Auto-timeout is the 60s hold

claude-control releases any holder after 60s (`MAX_HOLD` in `modules/claude_control.lua`), so a dead session can't leave it stuck. Longer actions call `overlay_on` again (it releases the old ticket first so it doesn't queue behind itself). The connector waits at most 45s in the queue so an MCP call never hangs for the wrapper's full 3 min.

---

### Fixed agent id

The connector passes `CLAUDE_CODE_SESSION_ID=my_mac_connector`. If Matt presses Stop, claude-control blocks that id for 2h, so every remote session using the connector stops asking. Undo: `claude-control unblock my_mac_connector`.

---

### Instructions line

Server instructions now say: before ANY action that moves or resizes windows, clicks, types or opens apps or dialogs on his Mac (any tool, e.g. Claude in Chrome), call overlay_on, wait for granted, overlay_off right after. claude.ai may cache connector instructions per chat; new chats pick it up.

---

### Coordination with the autosave thread

The "Voice call periodic autosave" thread had tested, staged but uncommitted changes in the same `server.ts` (note_call) and went offline mid-restart. I added my hunks around theirs (no overlap besides the instructions string, where I appended), ran all 10 tests (pass), restarted the connector (both tool sets live: tools/list shows note_call and overlay_on/off), and committed both together so nothing sits in limbo.

---

### Tested

- Unit test maps claude-control exit codes.
- Real smoke test: overlay showed, `granted t6`, `done` returned it to idle.
- Live server tools/list includes the new tools.
- Not tested: a real claude.ai chat calling it (needs Matt in a chat).

---

### Public MDMA export

The connector isn't part of the MDMA public export (mac-utilities only ships Hammerspoon modules; claude-control is already in it), so there was nothing to sync.

Undo: revert the commit and `launchctl kickstart -k gui/$(id -u)/com.matt.agent.mac-connector`.
