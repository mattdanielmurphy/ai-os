# Agents triggering dictation (2026-10-22)

## 16:20 Can an agent start dictation?

Matt said agents keep claiming they can't trigger dictation, and that anything is possible via the ai-os URL router.

---

### TypeWhisper has a dictation API

TypeWhisper 1.7.1 ships a local HTTP API (Settings > Advanced > API server; off by default, 127.0.0.1 only, port 8978). `POST /v1/dictation/start` and `/stop` start and stop dictation exactly like the hotkey; text goes into the focused field. Auth: bearer token TypeWhisper writes to `~/Library/Application Support/TypeWhisper/api-discovery.json` while the server runs. Found via the app's binary strings, confirmed against the project README on GitHub.

---

### Why not the URL router

`AIOSURLRouter.app` intercepts http clicks to 127.0.0.1:8643 for the old Antigravity listener; that listener (`services/url_action_listener`) no longer exists in the repo. The `typewhisper://` URL scheme exists, but artifact pages can't launch app schemes (tested 2026-10-19 with claude://). The HTTP API needs no keypress, no focus change and no router, so it's the robust route. A review-page tap can reach it through a new mac-connector `/act/.../dictate` route that calls `scripts/dictate.sh start` (not built; review-page thread's call).

---

### What I built

`scripts/dictate.sh start|stop|toggle|status`. Reads port + token from the discovery file, never prints the token. Agents take `claude-control ask ... --light` first because it turns on the mic. AG_CONTEXT line added so every agent finds it.

---

### Untested part

Not tested end to end: the API server is off, and turning it on is a TypeWhisper setting Matt flips (I didn't toggle an app's security setting myself). Script syntax and the "API off" path are tested. Undo: delete the script and AG_CONTEXT line; turn the API server off.
