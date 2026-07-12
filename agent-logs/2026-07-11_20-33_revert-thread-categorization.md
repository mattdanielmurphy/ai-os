## Goal
Revert the previous Gemini thread folder categorization and document why it was abandoned.

## User Feedback & Decisions
The user realized that Hermes natively maps "projects" to 1-level deep physical directories. Creating folders for categories would pollute the Hermes "Projects" list with generic topics (like "Lifestyle") that are useless for day-to-day active work. They decided to scrap the folder-based categorization entirely.

## Changes Made
- Moved all 1,827 markdown files from their nested `Category/Collection/` folders back into the flat `threads/` and `stitched_markdown/` directories.
- Deleted the empty category folders.
- Reverted `scripts/ingest_gemini_archives.py` back to using `iterdir()` for flat scanning.
- Documented the abandoned concept and potential future tag-based approaches in `docs/ideas-on-hold/gemini_thread_categorization.md`.

## What Worked
- Reversion was perfectly seamless. The bash `find -exec mv` commands quickly flattened the directories, and the python script was restored to its previous state.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Hermes projects are rigidly tied to physical directories. For future metadata sorting, we must rely purely on YAML tags and database-level indexing rather than file system hierarchy.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity-ide/brain/4595288a-5805-47f5-b868-f101853438a1/.system_generated/logs/transcript.jsonl)

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity-ide/brain/4595288a-5805-47f5-b868-f101853438a1/.system_generated/logs/transcript.jsonl)
