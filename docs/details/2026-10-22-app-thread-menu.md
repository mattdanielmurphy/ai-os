# App → Claude threads menu (idea, 2026-10-22)

## 05:35 Recorded the idea and sketched designs

**Asked:** right-click one of Matt's apps → recent Claude threads about it, with state (resolved / idle /
waiting for input / cache expired); click opens the thread; a "prod" switch hides it. Record in IDEAS.md,
sketch 2–3 designs, build nothing until "make it".

**Done:** IDEAS.md entry; this file. No code.

---

### Where state comes from

Checked on his Mac today:
- `~/.claude/sessions/<pid>.json` (live sessions): `cwd`, `status` ("busy"/idle), `hostSessionId`
  (`local_…`, the desktop app's id), `name`. Gives **busy vs idle** and **which folder**.
- Transcripts `~/.claude/projects/<cwd-slug>/<session>.jsonl`: last assistant turn time + tokens.
  `mods/context-alert` already turns that into **cache expired / minutes left** (`status <session>` in its
  script; 1-hour TTL, worth showing only above ~30k tokens). Reuse that, don't re-derive.
- **Waiting for input**: last transcript entry is an assistant turn that asked something / a permission
  prompt pending. Heuristic; needs testing.
- **Resolved**: only the Projects server knows (hearthbot `list_thread_sessions` has `status_bucket` and
  resolved). Not readable from a plain script on the Mac without an API; a project-thread agent could
  write a snapshot file. Weakest link.

---

### Mapping apps to threads

Default: **by folder.** Every session's `cwd` (incl. `.claude/worktrees/*` under it) maps to the repo
root via `git rev-parse --show-toplevel`; the app declares its repo path. No manual tagging.
Fallback/override: a tiny `~/.config/app-threads.json` `{ "trackpad-mixer": ["~/projects/trackpad-mixer",
"~/.hammerspoon/modules/mixer*"] }` for apps whose code lives in a shared repo (Hammerspoon modules,
ai-os scripts). Rejected: keyword search of thread titles (noisy).

---

### Design A: one daemon + JSON file (recommended)

A small `thread-index` script (launchd, every 60s, or on Claude hooks) writes
`~/.claude/state/app-threads.json`: per repo, the last ~5 sessions with state + cache minutes.
Each app's right-click menu just reads the file (Swift via hud-kit `ThreadMenu.swift`, Hammerspoon via a
Lua module, web apps via a local endpoint). Pro: one source of truth, apps stay dumb, cheap. Con: up to
60s stale.

---

### Design B: a Claude mod writes state

Extend context-alert (it already tracks cache per session) to write each session's state to the same JSON
on every turn/idle. Pro: real-time, exact busy/waiting from inside Claude. Con: only covers sessions with
the mod loaded; mods run from a cached install (bump + update needed); closed sessions go stale.

---

### Design C: on demand, no daemon

The menu runs `thread-index --repo <path>` when opened (~100–300 ms over recent transcripts). Pro:
nothing running in the background, always fresh. Con: small lag on right-click; same code as A, so A can
start as C and add the timer later.

---

### Opening a thread and the prod switch

- Open: desktop app session via its `hostSessionId`; exact deep-link scheme (`claude://…`) **unverified**,
  must check before building. Project threads open via their claude.ai thread URL.
- Prod switch: one global flag in `~/.config/app-threads.json` (`"prod": true` hides the menu everywhere),
  plus a per-app override. Toggle from the ⚙︎ AI-OS Hammerspoon menu.

---

### Risks / untested

- Deep-link format for opening a desktop session: unknown.
- "Resolved" needs a Projects snapshot; may show only for project threads an agent recently touched.
- "Waiting for input" detection is a heuristic.
- Existing tools: none found that index Claude Code sessions per app; nearest is the desktop sidebar itself.

Undo: delete the IDEAS.md section and this file.
