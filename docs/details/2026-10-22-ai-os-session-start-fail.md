# ai-os sessions failing to start (2026-10-22)

## 10:35 Cause and fix

### Cause
Claude app log (`~/Library/Logs/Claude/main.log`, 10:19–10:26 MDT): `Worktree creation failed with error: disk_full`. Disk had 4.6 GB free; the app refuses a new worktree under 5.4 GB. Only ai-os broke because its threads use worktrees (~0.5 GB each); ~/projects has no git repo so it skips worktrees. Not a hook or settings problem.

### What used the space
`ai-os/.claude/worktrees/`: 85 worktrees, 37 GB, 26 GB of it `node_modules` (~300 MB each).

### Fix
Deleted `node_modules` in 37 worktrees with no open files (lsof) and no file changes in 12 h. Free space 4.4 → 16 GB. Rejected: app's "Clean up inactive sessions" tool (blocked for remote sessions; Matt can run it in Settings › This computer › Storage); removing worktrees themselves (could lose uncommitted work).

### Undo / risk
Resuming one of those sessions needs `bun install` in its worktree. Space will run out again as worktrees pile up; a scheduled cleanup would prevent it.

---

## 10:55 Root cause: node_modules was committed to git

### Committed packages
Matt asked why copies cost real space on APFS. Tests: `bun install` in a fresh worktree used ~1 MB (bun already clones from its cache). `git worktree add` used 450 MB, because 301 MB of `node_modules` (4,652 files) plus a 23 MB Hermes index cache were tracked in git (added by an auto-commit, `0e301781`). Git writes real files on checkout, so every thread copied them.

### Fix applied
Added `node_modules/` and `skills/.hub/index-cache/` to `.gitignore`, `git rm --cached` (local files kept). New worktree now costs 112 MB instead of 450 MB (measured). Threads in a worktree need `bun install` before running JS scripts; that costs ~0 disk.

### Still open
The remaining ~110 MB per copy is real git-checkout files; APFS clones would make it ~0, but the app creates worktrees, not us. Existing old copies keep their checked-out packages until a dedupe or cleanup.
Undo: `git revert 5f1a33a9`.
