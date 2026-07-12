## Goal
Organize Gemini archive threads into a folder hierarchy based on `hermes_collection_manifest.json` categories and inject YAML category tags into the frontmatter.

## User Feedback & Decisions
The user agreed to organize the files into both a folder hierarchy and via YAML tags. They wanted it to just "work" effortlessly inside the Hermes sidebar or any markdown viewer.

## Changes Made
- Updated `scripts/ingest_gemini_archives.py` to recursively glob (`rglob`) markdown files so it searches within category subfolders.
- Wrote and executed a script `tmp/organize_threads.py` that parsed `hermes_collection_manifest.json` and migrated 1,827 threads into `<Category>/<Collection>/` directories while injecting `category: ` and `collection: ` metadata into the YAML frontmatter.

## What Worked
- The updated ingester perfectly handles the nested tree structure.
- The bulk script accurately handled missing frontmatter keys, gracefully managed file moving, and synced both the active archive and the backup `stitched_markdown` folders in seconds.

## What Didn't Work / Known Issues
- Initial script parsed the JSON manifest incorrectly due to its nested `categories` array structure (was expecting a flat list), but this was immediately caught and fixed.

## Architecture Notes
- Injecting YAML tags natively into the markdown gives us search flexibility in the future if we move away from purely folder-based views.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity-ide/brain/4595288a-5805-47f5-b868-f101853438a1/.system_generated/logs/transcript.jsonl)

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity-ide/brain/4595288a-5805-47f5-b868-f101853438a1/.system_generated/logs/transcript.jsonl)
