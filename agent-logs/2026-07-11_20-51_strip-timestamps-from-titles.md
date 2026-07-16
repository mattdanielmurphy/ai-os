## Goal
Remove datestamp prefixes (like `[2026-07-10 10:37 MDT-6] `) from thread titles in the Hermes database and prevent them from being saved in the future.

## User Feedback & Decisions
- The user uses a userscript to prepend timestamps to user messages in the Gemini UI, which causes Gemini to generate thread titles that include these timestamps.
- The user wanted an easy fix to remove these datestamps from the titles.

## Changes Made
- Executed an `UPDATE` query on `~/.hermes/state.db` using `ltrim` and `substr` to instantly clean up all existing thread titles that started with `[202...`.
- Updated `userscripts/gemini.js`'s `getArchiveTitle()` function to strip the timestamp prefix using a regex. This ensures that new threads exported via the userscript will not have the timestamp embedded in their markdown frontmatter.
- Updated `scripts/ingest_gemini_archives.py` to strip the timestamp prefix during ingestion. This acts as a fallback or cleanup step for any previously exported threads that might be re-ingested.

## What Worked
- The SQL query successfully cleaned the titles in the Hermes database.
- The regex correctly identifies and removes the timestamp formats without affecting the core thread titles.

## What Didn't Work / Known Issues
- The actual `.md` files on disk still retain the long kebab-case filenames (which include the date slug), but since Hermes uses the cleaned `title` column, this doesn't impact the UI. The user didn't request a bulk file rename, which would be unnecessary and risky.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity-ide/brain/4595288a-5805-47f5-b868-f101853438a1/.system_generated/logs/transcript.jsonl)
