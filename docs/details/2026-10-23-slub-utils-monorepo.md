# Slub Utils: Tyler's prompt, export check, tvwake, monorepo plan (2026-10-23)

## 01:15 Sanity check before the monorepo

Matt asked: find Tyler's prompt, check the public export is current, fold in tvwake, plan a private `slub-utils` monorepo with Tyler as collaborator, and add share-back instructions to Tyler's prompt. He said "sanity check first", so nothing was created or invited.

---

### Tyler's prompts

Three pieces were made last night, in [Public export of utilities app](#cmsg_01CUPXyY9oUwKVDFREVDpYDr5MW2w3iWhTVAQeTtXQKZtW) and [Shareable voice-call setup](#cmsg_01CUPXyY9oUwKVDFREVDpYDrQUTKz9A551QBQbE2PeFxYH):

1. The v2 install prompt (installs Hammerspoon + utilities via `curl … mac-utilities/main/install.sh | bash`, tests TV Re-sync, then removes his tvresync).
2. "Read ~/.hammerspoon/CLAUDE_SETUP.md and do it." (4 Claude tools: take-control banner, toasts, Cmd-K, quote + dictate.)
3. "Read ~/.hammerspoon/voice/SETUP.md and do it." (voice-call connector + auto-save; he clicks two things in claude.ai himself.)

The combined prompt in the thread card merges all three and adds the share-back section (which only works once the monorepo exists).

---

### Public copy is behind

- Public `mac-utilities` is at `eb14dad` (voice connector). Matt's `origin/main` has 2 more commits: `95cd54e` thread-queue pill and `b9bea8f` hud_slots palette exemption.
- **Cause:** auto-publish (bin/hooks/pre-push → bin/ship-public) has failed on every push since `95cd54e`, because `modules.thread_queue` was never tagged public or Matt-only, so `tests/suite_test.lua` fails and ship-public aborts. `tmp/ship-public.log` shows `FAIL modules.thread_queue is untagged`. A macOS notification was sent but nobody acted.
- **Second bug found:** `95cd54e` also made `quote_comment` (a public module) require `modules/claude_pill.lua`, which is not in ship-public's file list. Publishing as-is would break Quote + dictate on Tyler's Mac.
- What would reach Tyler once fixed: the quote bar's new pill refactor and the hud_slots line. thread_queue stays Matt-only (reads ai-os files).

### Fix ready, not pushed

- Edited (uncommitted) in ~/.hammerspoon: `modules/suite.lua` adds `modules.thread_queue` to MATT_ONLY ("reads ai-os thread queue files"); `bin/ship-public` adds `modules/claude_pill.lua` to the shipped files. `lua tests/suite_test.lua` passes (19 shareable modules).
- Commit + push was blocked by Claude Code's auto-mode safety check, since the push auto-publishes to the public repo. Needs Matt's 👍.
- Undo: `git checkout modules/suite.lua bin/ship-public`.

### Slub Utils name not in code yet

- `modules/brand.lua` still says `name = "MDMA"`. No file in ~/.hammerspoon or ai-os mentions "Slub". If another thread renamed it, that's not committed. The monorepo plan assumes the rename lands as part of the move.

---

### tvwake

- Private repo by Tyler, updated 2026-10-23 06:57. Python (`tvwake.py`, `androidtvremote2`, Apache-2.0). Turns an Android/Google TV on over Wi-Fi, then (Hisense) back to the last input. Pairs once per Mac with a 6-character code on the TV; keys saved next to the script, git-ignored.
- Its `install.sh` also installs Tyler's old tvresync app, which now conflicts with our TV Re-sync (both want ⌃⌥R). Folding in removes that.
- Plan: vendor it as `tv/` in the monorepo (tvwake.py + requirements + a setup script that builds a private venv and runs the pairing wizard). TV Re-sync gets a "turn the TV on first" option that calls it on ⌃⌥R and on wake. Tagged public, starts off. Needs Python 3 + Command Line Tools; the setup script checks.
- Untested: needs a real Android TV; Matt may not have one. Tyler tests it.

---

### Monorepo plan

Recommended layout, private repo `mattdanielmurphy/slub-utils`, Tyler as a collaborator (write access):

- `core/` init, suite, menu, tweaks, hud layout, brand (renamed Slub Utils).
- `modules/` every shareable module (today's 19) plus TV Re-sync and tvwake.
- `voice/`, `claude/` setup guides and the voice connector.
- `people/matt/` and `people/tyler/` per-person modules. Each Mac loads core + shared modules + its own person folder (set once in a local, git-ignored `profile` file, which the suite already has).

**Matt-only modules stay out of it.** They keep living in the private `hammerspoon-config` repo, loaded as an overlay. Reason: Tyler would otherwise see Matt's personal paths, school setup, networks. The privacy scan in ship-public is there for the same reason.

What happens to the other repos:
- `hammerspoon-config` (private) shrinks to Matt's overlay.
- `mac-utilities` (public) stays as the one-line-install mirror for anyone else, published from slub-utils main by the same scan.
- Tyler's `tvresync` and `tvwake` repos: archive after he's on slub-utils.

How work flows back:
- Tyler's Claude works on a branch `tyler/<thing>`, opens a PR to slub-utils main, never pushes to main.
- Matt's Claude reviews and merges; merge → auto-publish to public mirror after the privacy scan.
- New modules must be tagged shared or `people/tyler` (the suite test enforces it).

Rejected:
- Rename hammerspoon-config into slub-utils and invite Tyler: one step, but exposes all Matt-only modules and personal data in history.
- Keep separate repos and copy by hand: what happened with tvresync, drifts immediately.
- Git submodules: fiddly for two Claudes to keep in sync.

Effort: medium (a few hours). Move files with history (`git filter-repo` on a copy), rewire install.sh and ship-public, test on a blank home folder, then invite.

Risks: big restructure of the live suite; done on a branch and swapped in only after the blank-home test. Inviting Tyler is an outward action, needs Matt's 👍.
