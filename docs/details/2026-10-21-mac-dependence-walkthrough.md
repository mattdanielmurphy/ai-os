# Mac dependence walkthrough (thread)

## 19:45 Walkthrough result and step 1 start

Asked: present the last reply of "Less Mac dependence for agents" as a tap-menu walkthrough, then act on his comments.

Did: one AskUserQuestion call, 4 pages (Big picture, Gaps, Steps, Threads), multiSelect, short descriptions (no documented char limit; kept each under ~150 chars). Matt ticked everything.

---

### Format verdict

Matt: tap menus don't cut it. Wants an HTML artifact instead, built as a shared module with the morning check-in phase 1 quiz artifact. Likes: ticking sections as read/agree. Dislikes: no real commenting, no formatting, page sits until Next. Sent to the coordinator as a new thread (out of this thread's scope). Not saved as a skill, since the format failed.

---

### All four steps approved

Steps 1-3 go ahead. Step 4 (iCloud to OneDrive) is opportunistic: iCloud mostly works, the vault stays there for phone Obsidian, move pieces off when a chance comes.

---

### Claude Code on the VPS

Installed Claude Code native build on oracle-vps (aarch64, 2.1.307), added ~/.local/bin to PATH in ~/.bashrc. `claude remote-control` exists with --name and --permission-mode, so an always-on host can run under tmux or a systemd user service.

---

### VPS GitHub access blocked

The VPS has no GitHub key (`Permission denied (publickey)`), so it can't clone ai-os or his projects. Options: (a) generate a key on the VPS and add it to his GitHub account with `gh ssh-key add` from the Mac (recommended: one key covers all private repos); (b) per-repo deploy keys (doesn't scale to ~30 projects); (c) rsync from the Mac (keeps the Mac as a dependency, rejected). Adding a key to his account is an account security change, so I'm asking first.

Undo: `~/.local/bin/claude` and `~/.local/share/claude` on the VPS can be moved to ~/.Trash-like folder; PATH line is the last line of ~/.bashrc.
