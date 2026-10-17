# Handoff: Claude onboarding + ai-os audit (2026-10-17)

Paste into a new thread: "Read ~/projects/ai-os/docs/handoffs/2026-10-17_claude-onboarding.md and continue."

## Context
- Matt switched to Claude.app. Antigravity trial ended: treat `agy`, agy-mcp, ag-quota as SHELVED (keep, don't use). Avoid query_aios.
- Wants things shelved visibly, not forgotten: proposed top-level `shelf/` folder, one README per shelved thing (what / why / how to revive). Not built yet.
- Hates git: recommended GitButler (undo timeline) or Fork; don't build a git GUI.
- Session runs in a cloud container linked to his Mac (device_bash = Linux VM; can't run macOS binaries like osascript or ag-quota).

## Done this session (commit 33f62948, NOT pushed)
- PII (DOB, student IDs, ASN, PEN, phone) removed from .rules/core_safety.md and all compiled rule files (CLAUDE/HERMES/LEAF.md, ~/.gemini/GEMINI.md, ~/.hermes/HERMES.md, codex policies). Now in gitignored `private/identity.md`.
- Untracked tmp/ (51MB dump) + 7 agy worktree gitlinks that were committed despite .gitignore.
- Moved 4.6GB target/ + copied browser-history DBs to `_to_delete/` (gitignored) for Matt to trash.
- Left alone: uncommitted changes in services/assistant/* and Discussions.html (not ours).

## Open decisions / next steps (in Matt's preferred order)
1. **Quote→comment tool** (top priority): Hammerspoon hotkey (e.g. ⌥R) on highlighted text → floating comment box → pastes `> quote` + comment into Claude's prompt. Alternative: Claude mod with `/quote` using $.ui.selection + $.prompt.fill (unverified whether desktop surface supports selection).
2. **Thread archive, de-Hermes**: plain files are the archive (docs/gemini-threads 633, docs/antigravity-threads 1622 already exist as md). Export Hermes-only + Codex (19 sessions) + ChatGPT export to same format; small rebuildable search index + MCP/connector; then shelve Hermes (state.db 700MB, ~3,400 sessions).
3. **Scrub PII from git history?** Needs history rewrite + force push. Matt hasn't answered. Also PII in ~30 docs/antigravity-threads admissions/housing files.
4. **Rewrite rules for Claude**: compiled CLAUDE.md (28KB) mandates preflight/postflight/auto_commit every turn, agy handoffs, query_aios, HTML <details> formatting — mostly wrong now. Want a lean user-level ~/.claude/CLAUDE.md (no ~/.claude exists on the Mac yet).
5. **preflight v2**: today it reads only Antigravity brain dirs (newest thread Sep 10 = stale), scans ~3,650 dirs + ~16MB transcripts before its timer starts, ag-quota (5s) + :3031 planner checks are dead, statuses report OK on exceptions, log has no per-step timing. Plan: per-step JSONL timing, honest OK/WARN/FAIL/SKIP, `preflight report`, drop agy/quota/planner, <1s.
6. **Cleanup + shelf/**: shelve agy (≈13 scripts), query_aios (138 refs), Tauri GUI docs; stale README/todo.md; 9 agy-mcp/job-* branches; 121 skills dirs mostly Hermes-bundled.
7. **Claude.app projects**: no API; could create via computer use. Top-10 by last commit: ai-os, qwerty-midi-plugin, daily-mini-crossword, chrome-devtools-mcp-lazy, mattmurphy.ca, qwerty-midi-hammerspoon, ps5-controller-hammerspoon, userscript-bundler, agy-mcp (maybe swap for hermes-agent), karabiner-chatgpt-dictation. Matt hasn't said which "projects list" he means.
8. **Thread-size awareness**: wants agents to notice big threads and suggest/make handoffs; idea: a Claude mod showing context size in the status line + nudge at a threshold, plus a /handoff skill that writes files like this one.

## UX notes from Matt
- Don't use the multiple-choice question menu for big questions: it drops quoted text/attachments from his answer and hides the thread. Ask in plain text.
