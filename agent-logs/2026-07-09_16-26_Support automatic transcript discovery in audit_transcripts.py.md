## Goal
Update `scripts/audit_transcripts.py` to audit the most recent transcript if no path is passed explicitly.

## User Feedback & Decisions
None.

## Changes Made
- Modified `scripts/audit_transcripts.py` to make the `transcript_path` argument optional and added recursive search using `rglob` across both IDE and CLI brain paths.
- Added `FEATURES.md` detailing the feature.

## What Worked
Automatically resolving and auditing the most recent transcript when calling `python3 scripts/audit_transcripts.py` without parameters.

## What Didn't Work / Known Issues
Using non-recursive `glob` missed nested transcript files, which was corrected to `rglob`.

## Architecture Notes
None.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity-ide/brain/4ec16e42-fb79-4de3-8622-a3b5dcd643ac/.system_generated/logs/transcript.jsonl)

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity-ide/brain/4ec16e42-fb79-4de3-8622-a3b5dcd643ac/.system_generated/logs/transcript.jsonl)
