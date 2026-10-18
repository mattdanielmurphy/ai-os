# Handoff: /_handoff skill + context-alert mod (2026-10-17, seq 1)

Paste into a new thread: "Read /Users/matt/projects/ai-os/docs/handoffs/2026-10-17_handoff-and-context-alert.md and continue."

## Chain
- Seq 1 of `thread-hygiene`. Parent: none (first in chain).
- Threads so far (oldest first; reopen with `claude --resume <id>` or `threads.py show <id>`):
  - 2026-10-17 · ad1b3b1e-f89d-4270-9a1b-db6fb118bd88 · built /_handoff skill + context-size band · (this handoff)
- Side session: local_9e30b42f-f5ae-4c5e-bc7d-3cdcb7fafcdc ("Fix auto_commit message when --paths is used").
- Related, not parents: `2026-10-17_claude-onboarding.md` (overall ai-os Claude migration plan),
  `2026-10-17_quote-comment-tool.md` (Hammerspoon quote queue; its step 3 is a Claude mod).

## Chain summary
- Goal: keep threads short. Hand off at roughly 150–250k tokens instead of using `/compact`, with
  a brief that links every earlier thread in the chain.
- `/_handoff` skill exists and works (this file is its first real output).
- A Claude Code mod (`context-alert`) shows a band above the prompt once context passes 150k.
  Confirmed live by Matt in the desktop app ("Current context size: 155k / 1000k (getting long)").
- Mods turn out to be the way to customise Claude's own UI: bands, panes, toasts, status line,
  slash commands, message re-rendering, tool-call hooks.

## This thread
- **Skill** `skills/_handoff/SKILL.md` (commit 99dbacda, pushed). Adapted from
  REMvisual/claude-handoff (MIT). Kept chain links, the "what we tried" section and the paste prompt.
  Dropped beads, the 300–800 line target and multi-pass mining. Output goes to the project's
  `docs/handoffs/`. Synced to ~/.claude/skills via `scripts/sync_skills.py`.
- `~/.claude/CLAUDE.md` (not in git) line now says: suggest `/_handoff` at ~200k tokens.
- **Mod** `mods/context-alert/` (commit 472f4b59, pushed):
  - `hooks/register.tsx`: `session.measure` stores tokens in `$.state`; `ui.render` AbovePrompt band
    from WARN=150_000 (yellow), ALERT=200_000 (red, "hand off now"); "Write handoff" button does
    `$.prompt.fill('/_handoff')`; toast once per threshold 150k/200k/250k/300k.
  - `hooks/context-alert.test.tsx` passes on terminal + desktop; tsc clean.
  - Installed for the user via a local marketplace: `mods/.claude-plugin/marketplace.json`
    (`ai-os-mods`), `claude plugin install context-alert@ai-os-mods --scope user`. It reads straight
    from the repo folder, so edits apply on the next session load.
- **What didn't work / gotchas:**
  - `claude` on PATH is 2.1.212 and rejects mods ("hooks: expected record"). Use the app's CLI:
    `"$HOME/Library/Application Support/Claude/claude-code/2.1.299/4fa9694b7975/claude.app/Contents/MacOS/claude"`
    for `plugin validate|test|install`.
  - Session id: newest `.jsonl` gave the WRONG thread (parallel sessions). Use `$CLAUDE_CODE_SESSION_ID`.
  - Plugin tests need engine stubs: `on('session.measure', (_$, e) => ({ changed: e.changed }))`
    and a `ui.render` stub returning `<Box />` (test file must be `.tsx`).
  - `auto_commit.py --paths` commits the right files but its message names all dirty files
    (99dbacda, 472f4b59 messages are misleading). Fixed in side session, see below.

## Working on now
Nothing mid-flight. Last open question to Matt: merge the auto_commit fix into main? It is commit
538dce59 on `refs/heads/claude/strange-chatterjee-cc8cb5` (pushed; regression test passes, fails on old code).
Matt also asked "can we control EVERYTHING in this bar?". Answered yes; offered two small next ideas.

## Keep in mind
- Matt loved that the side bug was split off into its own session unasked. Keep doing that.
- He wants lean handoffs (links + chain summary + current work + things to keep in mind), not transcripts.
- One small step at a time, 2–3 options max; flag scope creep.
- Merge side-session branches only when Matt says so himself; never push those branches.
- Unrelated dirty files in ai-os (not this thread's; don't commit): `Discussions.html`,
  `scripts/.sync_skills_state.json`, `services/assistant/telegram_gateway/handlers.py`,
  `services/assistant/tests/test_assistant.py`, untracked `docs/handoffs/2026-10-17_quote-comment-tool.md`.
- A "hot reloading?" prompt may appear in thread ad1b3b1e. Ignore it: the dev copy was moved to Trash.

## Next steps
1. Ask Matt to confirm, then merge `refs/heads/claude/strange-chatterjee-cc8cb5` into main and run its test.
2. Optional (Matt's pick): show usage-limit % in the same band when close to the limit
   (`e.rateLimits` in `session.measure`), or move the Hammerspoon quote queue into an AbovePrompt band
   (see quote-comment handoff, step 3).

## Read first
- `mods/context-alert/hooks/register.tsx`: the mod, ~55 lines.
- `skills/_handoff/SKILL.md`: the handoff skill.
- `docs/handoffs/2026-10-17_quote-comment-tool.md`: if continuing with bar ideas.
- Load the `plugin-authoring` skill before touching any mod (API types, test kit).
