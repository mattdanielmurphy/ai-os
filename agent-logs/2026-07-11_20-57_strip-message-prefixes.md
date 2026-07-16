## Goal
Strip datestamps and `[context...]` tracking strings from all user message bodies in the Hermes database, since they're redundant and clutter up the chat interface.

## User Feedback & Decisions
- The user noted that their userscript injects `[2026-07-11 16:17 MDT-6] [context to this point is 5300] ` into their prompts to Gemini.
- The user requested removing them, provided that the timestamp is securely stored as metadata for any future client.
- The Hermes `messages` table already has a `timestamp` column (REAL Unix epoch format), so the injected text date is fully redundant and safely stored as metadata.

## Changes Made
- Executed a Python script to scan the Hermes SQLite database (`~/.hermes/state.db`) and dynamically strip both the datestamp and `[context...]` prefixes from all 2,304 existing user messages that contained them.
- Updated `scripts/ingest_gemini_archives.py` to natively strip out these prefixes using RegEx directly in the `parse_messages()` function. This guarantees any future thread ingestions will also be perfectly clean.

## What Worked
- Message bodies are now clean in the UI, and the timestamp metadata is strictly preserved in the SQLite `timestamp` column.

## What Didn't Work / Known Issues
- None.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity-ide/brain/4595288a-5805-47f5-b868-f101853438a1/.system_generated/logs/transcript.jsonl)
