---
name: _fetch-youtube-transcript
description: "Fetch the complete transcript before discussing, analyzing, or summarizing a YouTube video. Prefer the active browser tab's native transcript export for speed; use captions or the transcript helper only as fallbacks."
---

# Fetch YouTube Transcript

## Transcript-first requirement

When a request concerns a YouTube video, obtain its transcript before forming an interpretation, summary, critique, or answer about the video's claims. Do not reason from the title, description, comments, or prior assumptions while transcript retrieval is still possible.

## Fast path: active YouTube tab

1. Identify the user's selected YouTube watch tab and preserve its current page state.
2. Use the browser integration's native transcript export (`tab.content.exportYouTubeTranscript()` when available). It returns a local UTF-8 text file with timestamps and transcript metadata; read that file during the same turn.
3. Confirm the file contains transcript text, and note its language and whether captions are auto-generated when the export reports them.
4. Use the transcript as the primary source for the discussion. Treat page comments, title, and description as separate context, not as transcript content.

## Fallbacks

- If native export is unavailable, first inspect the selected tab context. YouTube may already have its transcript panel open, in which case the transcript is included in the page context.
- If it is not present, open YouTube's transcript panel and retrieve the complete text, including any additional segments beyond the initially rendered viewport. Avoid fixed multi-second sleeps when an event or mutation observer can detect readiness.
- If browser retrieval fails, use the existing `youtube-content` helper script for public captions. Report if captions are disabled, unavailable, incomplete, or auto-generated. Do not silently substitute comments or a summary from another source.

## Discussion

After retrieval, answer the user's actual question directly. Use timestamps when they help identify passages. Distinguish what the speaker says from external fact checking; browse separately when the user asks whether a claim is true or current verification is needed.
