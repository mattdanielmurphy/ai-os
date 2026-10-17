# Antigravity.app & CLI Ingestion — Session Detail

Ingested 557 Antigravity.app sessions (12,637 messages) and 408 Antigravity CLI sessions (9,635 messages) into Hermes' `state.db`.

## Source Format

Antigravity sessions live in:
- `~/.gemini/antigravity/brain/<session_id>/` (Antigravity.app / GUI)
- `~/.gemini/antigravity-cli/brain/<session_id>/` (Antigravity CLI)

Key files within each session directory:
- `.system_generated/logs/transcript.jsonl` or `transcript_full.jsonl` — JSONL events (`USER_INPUT`, `PLANNER_RESPONSE`, `ASSISTANT_RESPONSE`)
- `history/turn_*.md` — fallback markdown user turns
- `thread.md` — fallback thread summary

## Ingestion Strategy

1. Read `transcript.jsonl` line by line.
2. Extract `USER_INPUT` (clean `<USER_REQUEST>` wrapper tags) as `user` messages.
3. Extract `PLANNER_RESPONSE` / `ASSISTANT_RESPONSE` / `source == "MODEL"` (clean `<THREAD_NAME>` tags) as `assistant` messages.
4. Fall back to `history/turn_*.md` or `thread.md` if transcript is missing/empty.
5. Derive session `started_at` from ISO timestamp of first message, or directory `st_mtime`.
6. Enforce unique title constraint (`idx_sessions_title_unique`) by appending a short session ID suffix `[{session_id[:6]}]` on title collisions.
7. Set source tag to `antigravity-app` for GUI sessions and `antigravity-cli` for CLI sessions.
8. `INSERT OR IGNORE INTO sessions` + `INSERT INTO messages`. SQLite triggers (`messages_fts_insert`, `messages_fts_trigram_insert`) automatically populate dual FTS5 virtual tables.

## Script Location

- Script: `~/projects/ai-os/scripts/ingest_antigravity_sessions.py`
- Usage: `python3 scripts/ingest_antigravity_sessions.py --write`
- Backup: `~/.hermes/state.db.bak.antigravity-import`
