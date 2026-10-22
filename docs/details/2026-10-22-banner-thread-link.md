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
