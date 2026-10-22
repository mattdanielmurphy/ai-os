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
