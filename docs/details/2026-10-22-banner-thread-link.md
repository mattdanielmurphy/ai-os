# Banner click → open thread

## 16:55 Banner opened the thread list, not the thread

**Asked:** the claude-control banner's "Click: open thread" landed on the project's thread list.

---

### Root cause: the app drops the query

The banner, and the expiry toast too, built `claude://claude.ai/epitaxy/project/<chan>?thread=<cmsg>`. The Claude desktop app's deep-link handler (in `app.asar`, `case pu.Epitaxy`) rebuilds the target as `new URL(pathname)` and copies back only OAuth params, so `?thread=` is thrown away and you land on `/epitaxy/project/<chan>`, the thread list. The toast's "project threads open correctly" was never click-tested.

---

### Fix: path-form link

Links are now `claude://claude.ai/epitaxy/project/thread/<cmsg>`. That path is a known app route (it's in the app's route table, and claude.ai redirects it to `/code/project/thread/<cmsg>`). The cmsg id embeds the project, so `--project` is no longer needed (still accepted). Changed: `~/.hammerspoon/bin/claude-control`, `modules/claude_warm.lua` (test link), `ai-os/scripts/warm_threads.py` (toast link). Pushed; Hammerspoon reloaded.

---

### Not yet click-tested

I couldn't check the actual landing page: the browser pane isn't signed in, and clicking a link in the app changes Matt's screen. Test: `~/.hammerspoon/bin/claude-control ask "test: click me to open the AA email thread" 20 --light --thread cmsg_01CUPXyY9oUwKVDFREVDpYDrJXdbMrJNDem8K1zUM3nfzS`. If it still lands wrong, check `~/Library/Logs/Claude/main.log` for "Reloading current URL" / "claudeURLHandler".

**Undo:** revert hammerspoon commit f53e028 and ai-os c6de7e56.

## 17:10 Shared link helper (path form 404'd too)

**Asked:** Matt got a 404 from the toast test, and wants the banner and the expiry toast on the same notification module and the same link technique. The expiry-toast thread went cold, so I own both.

---

### Real link: claude://code/project

The path form (`epitaxy/project/thread/<id>`) is the web app's *shared-thread* route (`CodeSharedThreadRoute`, takes a share id), so a cmsg id 404s. Reading the app's deep-link handler again: the `claude://code/...` host runs `/code<path>` through a project-link parser (`/^\/(code|epitaxy)\/project\/(chan_…)$/` plus `thread` and `msg` params) and navigates to `/epitaxy/project/<chan>?thread=<cmsg>`, the URL the app itself shows for an open thread. So the link is `claude://code/project/<chan>?thread=<cmsg>`. Caveat: a feature flag can turn that handler off (then it logs "unrecognized code path").

---

### One helper: claude_links.lua

`~/.hammerspoon/modules/claude_links.lua` builds and opens every thread link. The project id is read from the cmsg id (its first 24 chars after `cmsg_` are the project's), so it works in any project. Users: the claude-control banner (`--thread` now just passes the id; Hammerspoon builds the link), `claude_notify` toast clicks, and `claude_warm` nudges. `warm_threads.py` now emits `thread`/`project` ids instead of a URL. Tests: `tests/claude_links_test.lua`, `claude_warm_test.lua`, `ai-os/tests/test_warm_threads.py`, all passing.

**Same module question:** the banner stays its own UI (it's a control queue with Esc/Stop, not a toast), but both now open threads through the same helper.

---

### Click still untested

Opening a link in the app changes Matt's screen, so he tests: toast `hs -c 'require("modules.claude_warm").test("cmsg_01CUPXyY9oUwKVDFREVDpYDrJXdbMrJNDem8K1zUM3nfzS")'`, banner `~/.hammerspoon/bin/claude-control ask "test: click to open AA email thread" 20 --light --thread cmsg_01CUPXyY9oUwKVDFREVDpYDrJXdbMrJNDem8K1zUM3nfzS`.

**Undo:** revert hammerspoon cf6ee8d and the ai-os warm_threads commit.
