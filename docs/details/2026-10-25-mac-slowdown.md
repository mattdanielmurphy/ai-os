# Mac slowdown, 2026-10-25 evening

## 22:25 What was slowing the Mac and what I cleaned up

Matt said the Mac felt very bogged down. I measured before touching anything.

### Before

- 16 GB of RAM, swap 15.3 of 16 GB used, load average 55-64 (normal is under 10), up 6 days.
- `accountsd` (Apple's accounts service) was using **7.6 GB** (almost all compressed/swapped) and 97% CPU for four days. This is the same leak noted on 2026-10-21 (1.3 GB then).
- 126 `git fsmonitor--daemon` processes, one per ai-os worktree, alive for up to 4 days. They come from `core.fsmonitor=true` in ai-os `.git/config`: every git command in a new worktree starts a watcher that never exits.
- ai-os had 120 worktrees under `.claude/worktrees` (21 GB), which Spotlight (`mds_stores`, 60% CPU) also keeps indexing.
- Two Antigravity `agy --hub` processes orphaned 2-3 days ago, each with a chrome-devtools MCP, an Ableton MCP and an agy MCP.
- Chrome: 55 tabs, about 70 renderer processes, roughly 4-5 GB including swapped memory. The biggest single consumer after accountsd.
- Only 4 Claude Code sessions were running, so the many-threads theory was not the cause.

---

### Killed accountsd leak

`killall -9 accountsd` (it ignores SIGTERM). launchd restarted it at once; the new one uses 52 MB. Nothing user-facing is lost; it only manages account logins and reloads them.

---

### Stopped git watchers

Killed all 126 fsmonitor daemons and ran `git config --unset core.fsmonitor` in ai-os, so new worktrees no longer start them. Cost: git status in ai-os is a little slower on a huge tree; it is fast enough without it. Undo: `git -C ~/projects/ai-os config core.fsmonitor true`.

---

### Removed merged worktrees

Removed 40 worktrees with `git worktree remove` that were clean (no changes), fully merged into main, and idle more than 6 hours. 80 remain (14 GB): 64 have uncommitted files, 11 have unmerged commits, 3 were in use, 2 were recent. I left all of those alone because they might hold work.

---

### Killed orphaned Antigravity hubs

Stopped the two `agy --hub` trees whose parent app had closed. Three other agy hubs belong to VS Code's running extension, so I left those.

---

### New memory guard

`scripts/memory_guard.py`, run every 10 minutes by launchd (`com.matt.agent.memory-guard`). It kills accountsd when it passes 1 GB and kills orphaned agy hubs. Every kill is logged in `~/projects/ai-os/tmp/memory-guard.log`. Tested with `--dry-run` (found nothing to kill, correct after cleanup) and one real launchd run (exit 0). Undo: `launchctl bootout gui/$(id -u)/com.matt.agent.memory-guard`.

---

### Nightly restart is broken

The 04:30 nightly restart has not restarted the Mac in 6 days. On Oct 22-23 it logged "restarting" but the Mac stayed up. On Oct 24-25 it waited all night because it treats the Claude app's "Electron" keep-awake assertion as "a turn is running", and that assertion has been held for 43 hours straight. So the check always says busy. This needs its own fix (a better busy check, and verifying the restart command actually works). A restart is the only thing that clears the remaining ~13 GB of swap.

---

### After

Swap 13.3 GB (it drains slowly; only a restart clears it fully), free memory 33-40% (was 30%), load falling (43 and dropping). Chrome tabs not touched: Matt may be using them.
