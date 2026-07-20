## Goal
Set up a tmux-accessible launch agent to watch `~/Documents/gemini-archive/threads/` and auto-ingest new Gemini chat threads into Hermes Agent's FTS5 search database.

## Changes Made
- `scripts/ingest_gemini_archives.py` — New: parses Gemini archive markdown (YAML frontmatter + gemini-message HTML comments), inserts into Hermes' sessions/messages tables, backed by auto-triggered FTS5. Idempotent via conversation_id PK.
- `scripts/gemini-ingest-watch.sh` — New: fswatch-based watchdog that monitors the archive dir and runs the ingester on Created/Updated .md events.
- `~/Library/LaunchAgents/com.matt.agent.gemini-ingest.plist` — New: launchd plist wrapping the watchdog via tmux-agent-wrapper.sh (keepalive mode).
- `docs/MAC_ENVIRONMENT.md` — Updated agent table with gemini-ingest entry.

## What Worked
- Dry-run parsed all 13 files, 170 messages correctly (0 errors)
- Live run inserted all 13 sessions
- Idempotent: second run skipped all 13
- End-to-end: dropped a test file, fswatch detected it within seconds, ingester processed it, DB confirmed
- FTS5 and FTS5 trigram search both return hits against ingested content

## Architecture Notes
- Follows the existing tmux-agent-wrapper pattern (keepalive mode, `agent-gemini-ingest` session)
- `tmux attach -t agent-gemini-ingest` for live log viewing
- Launchd restart: `launchctl kickstart gui/$(id -u)/com.matt.agent.gemini-ingest`