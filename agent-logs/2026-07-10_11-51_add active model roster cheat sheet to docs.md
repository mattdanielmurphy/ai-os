## Goal
Add the scannable cheat sheet of the active `model_list` roster, broken down by why each model exists in the configuration and when they should be deployed, to the project's documentation.

## User Feedback & Decisions
None.

## Changes Made
- Created new documentation file [model-roster.md](file:///Users/matt/projects/ai-os/docs/model-roster.md) containing the complete active model list roster cheat sheet.
- Modified [VISION.md](file:///Users/matt/projects/ai-os/docs/VISION.md) to add a link referencing the roster cheat sheet.
- Appended a durable knowledge log entry referencing the roster cheat sheet to [AG_CONTEXT.md](file:///Users/matt/projects/ai-os/docs/AG_CONTEXT.md).
- Added new feature entry describing the change in root [FEATURES.md](file:///Users/matt/projects/ai-os/FEATURES.md) and [FEATURES.md](file:///Users/matt/projects/ai-os/docs/FEATURES.md).
- Created a devtool feature file [.devtool/features/add-model-list-cheat-sheet-to-docs.md](file:///Users/matt/projects/ai-os/.devtool/features/add-model-list-cheat-sheet-to-docs.md) and marked it with status `review`.

## What Worked
- Documentation files and references successfully added and linked.
- Precision edit script used for targeted insertions/modifications.

## What Didn't Work / Known Issues
- \`mechanical_editor.py\` failed when creating a non-existent file directly. Solved by touching the file first.

## Architecture Notes
- The project documentation is structured with high-level conceptual summaries in H2/H1 headers, while deeper details are housed in linked files or H3+ blocks.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity-cli/brain/b2c2416f-1cd0-40e6-b39a-b84521c454cc/.system_generated/logs/transcript.jsonl)

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity-cli/brain/b2c2416f-1cd0-40e6-b39a-b84521c454cc/.system_generated/logs/transcript.jsonl)
