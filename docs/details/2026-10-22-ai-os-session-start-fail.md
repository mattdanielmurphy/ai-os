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

---

## 11:02 APFS-clone worktrees via a WorktreeCreate hook

### Hook found
The Claude desktop app (app.asar, `[WorktreeHooks]` module) runs a `WorktreeCreate` command hook from settings instead of its own `git worktree add` when one is configured for new branches. Contract: JSON on stdin `{session_id, cwd: <base repo>, hook_event_name, name}`; the last stdout line must be the absolute path of a new directory (not the base repo). Hooks in user settings (`~/.claude/settings.json`) always run; project-level ones can be skipped. `WorktreeRemove` gets `{worktree_path}`.

### How the clone hook works
`scripts/clone_worktree.py`: `git worktree add --no-checkout -b claude/<name>` from origin's default branch (same as the app), then clonefile() every tracked file whose base-checkout content matches that commit, then `git reset` + `checkout -- .` so git writes only files that differ. Any error in the clone step falls back to a normal checkout.

### Test results
Test worktree: 4 MB of disk (vs 450 MB before today, 112 MB after untracking node_modules), 3 s, `git status` clean, right branch, an edit in the copy did not touch the main checkout.

### Not switched on yet
Rejected switching it on silently: it would run for every repo's new threads on the Mac, and it relies on undocumented app behaviour; if the hook errors, threads can't start. Also, the app's own pool/cleanup skips hook-made worktrees (fine at ~0 MB each). Switch on = add WorktreeCreate/WorktreeRemove entries in `~/.claude/settings.json` pointing at the script; undo = remove them.

---

## 11:17 Clone hook switched on

### Switched on
Matt 👍'd. Added `WorktreeCreate` (timeout 120 s) and `WorktreeRemove` (60 s) hooks to `~/.claude/settings.json`, both running `python3 ~/projects/ai-os/scripts/clone_worktree.py`. Backup of the old settings: `ai-os/tmp/settings.json.bak-*`.

### Hardening before switch-on
Fetch timeout no longer raises; an existing `claude/<name>` branch is reused instead of failing; remove no longer uses `--force`, so a worktree with uncommitted changes is kept (hook exits 1). Tested create + remove via the stdin contract on ai-os (4,431 files cloned in 2.4 s) and ~/.hammerspoon; dirty remove kept the folder, clean remove deleted it.

### Undo
Delete the two entries under `hooks` in `~/.claude/settings.json`. Log: `~/Library/Logs/clone_worktree.log`.

---

## 11:47 Rolled back: the hook broke non-repo folders

### What broke
At 11:44 a thread in ~/projects (not a git repo) failed: `worktree_hook_failed`. Without a hook, the app skips worktrees for non-repo folders and runs in the folder itself. With a user-level WorktreeCreate hook it calls the hook for every new thread, including non-repo folders, and aborts the session if the hook fails; it also rejects a hook that prints the base folder, so a user-level hook can't fall back to "no copy". The clone part worked: ai-os and ~/.hammerspoon threads started fine from 11:21.

### Rolled back
11:47: removed both hooks from `~/.claude/settings.json`. Threads everywhere are back to the app's normal behaviour (plain git copies, 112 MB for ai-os).

### Proposed fix
Put the hook in ai-os's own `.claude/settings.json` instead of user settings. The app reads project hooks only from the repo the thread starts in (when that folder is the repo's top level), so ~/projects and other folders keep their normal behaviour. Writing that file was blocked by the auto-mode permission check (it changes how Claude starts), so it needs Matt's go. Unverified: whether a project-level hook runs under the same conditions as a user-level one in Remote Control starts; the plan is to test one ai-os and one ~/projects start right after.

---

## 14:10 Clone hook live for ai-os only

### Scoped to ai-os
Matt 👍'd. Added `ai-os/.claude/settings.json` (committed) with WorktreeCreate/WorktreeRemove hooks running `"$CLAUDE_PROJECT_DIR"/scripts/clone_worktree.py`. User settings unchanged, so other folders and repos keep the app's normal behaviour.

### Both starts verified
14:07:57: a ~/projects thread started the old way ("using base directory"). 14:08:25: an ai-os thread started via the hook, 4,436 files cloned in 2.5 s. Coordinator confirmed both sessions active.

### Undo ai-os hook
Delete `ai-os/.claude/settings.json` (or its two hook entries) and push.
