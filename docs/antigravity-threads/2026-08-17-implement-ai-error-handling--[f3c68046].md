---
title: "Implement AI Error Handling"
date: "2026-08-17"
conversation_id: "f3c68046-ea81-411e-8a11-dd7ddda00c49"
source: "antigravity"
---

# Implement AI Error Handling

## User

Implement the plan to fix silent AI errors, surface exact errors, and implement the fail-open clip finalizer across the following files in /Users/matt/projects/yt-highlight-reel:

1. Create /Users/matt/projects/yt-highlight-reel/api/lib/highlights.js:
```javascript
import { snapToUtterances, formatTime } from './timeline.js'

export function normalizeProviderError(status, bodyText) {
	if (!bodyText) return status ? `Provider error (${status})` : 'Unknown AI generation error'
	try {
		const parsed = typeof bodyText === 'string' ? JSON.parse(bodyText) : bodyText
		if (parsed.error?.message) return String(parsed.error.message).slice(0, 240)
		if (parsed.message) return String(parsed.message).slice(0, 240)
	} catch (e) {}
	const clean = String(bodyText).replace(/\s+/g, ' ').trim()
	return (status ? `Provider error (${status}): ` : '') + clean.slice(0, 240)
}

export function candidateToClip(c, videoId) {
	return {
		videoId: c.videoId || videoId,
		start: Math.max(0, Math.floor(c.start || 0)),
		end: Math.floor(c.end || ((c.start || 0) + 60)),
		title: c.title || c.why || 'Highlight Moment',
		quote: c.quote || '',
		role: c.role || 'soundbite'
	}
}

export function buildFallbackClips(candidates, { videoId, limit = 8 } = {}) {
	if (!Array.isArray(candidates)) return []
	return candidates.slice(0, limit).map(c => candidateToClip(c, videoId))
}

export function finalizeClips({ editorClips = [], candidates = [], utterances = [], totalDuration = 0, videoId = 'V1' }) {
	const validEditor = (Array.isArray(editorClips) ? editorClips : []).filter(c => c && typeof c.start === 'number' && typeof c.end === 'number' && c.end > c.start)
	
	let raw = validEditor.length > 0 ? validEditor.map(c => candidateToClip(c, videoId)) : buildFallbackClips(candidates, { videoId })
	let usedFallback = validEditor.length === 0

	let snapped = []
	if (raw.length > 0 && utterances.length > 0) {
		snapped = snapToUtterances({
			rawClips: raw,
			utterances,
			totalDuration,
			minDuration: 8,
			maxDuration: 75
		})
	} else if (ra
<truncated 6015 bytes>
tail += \` (Clip \${windowIndex || windowsDone} of \${windowsTotal})\``.
- In `src/style.css`:
  Add `.ai-progress-bar-fill.stalled { background: var(--color-accent-amber, #f59e0b) !important; }`
  Add `.ai-progress-bar-fill.error { background: var(--color-accent-red, #ef4444) !important; }`
  Ensure `--color-warning: #f59e0b;` is defined in `:root`.

6. Update /Users/matt/projects/yt-highlight-reel/src/main.js:
- In `renderPlayerView` (in-player regeneration) and `renderCreatorView` (universal form submit):
  Pass `mode: 'single'` (for single video) or `mode: 'multi'` (for topic).
  Wrap `requestAiHighlights` in try/catch:
  ```javascript
  try {
    const result = await requestAiHighlights({ ... })
    hideProgressModal()
    if (result && result.segments && result.segments.length > 0) {
      if (result.usedFallback) {
        showToast(`⚠️ Used fallback clips (${result.fallbackReason || 'snapping fallback'})`)
      }
      // Apply reel or navigate to share URL
      ...
    }
  } catch (err) {
    updateProgressModal({ error: true, message: err.message, stalled: false })
    showToast(`⚠️ ${err.message}`)
    setTimeout(() => hideProgressModal(), 1500)
  } finally {
    // Re-enable buttons and restore text
  }
  ```
  Remove generic `Could not generate AI highlights for this input` fallback toasts.

7. Create /Users/matt/projects/yt-highlight-reel/test/highlights.test.js:
- Tests for `normalizeProviderError` (JSON with error.message, JSON with message, raw text string, status codes).
- Tests for `buildFallbackClips`.
- Tests for `finalizeClips` (valid editor clips, empty editor with candidates fallback, clamped fallback, empty candidates throw).

8. Update /Users/matt/projects/yt-highlight-reel/test/progressStream.test.js:
- Convert to pure `node:test` + `node:assert/strict` (avoiding jest mocks).
- Test `writeEvent` returns promise and `end()` flushes all queued writes before ending.

---

## Assistant

I have successfully implemented the requested AI error handling, clip finalization, and progress stream improvements.

### Key Changes
*   **Library & Finalization**: Created [`highlights.js`](file:///Users/matt/projects/yt-highlight-reel/api/lib/highlights.js) to normalize errors and implement the fail-open `finalizeClips` logic.
*   **Progress Stream**: Updated `ProgressWriter` in [`progressStream.js`](file:///Users/matt/projects/yt-highlight-reel/api/lib/progressStream.js) to ensure `writeLock` is awaited during `end()`, preventing data loss on stream termination.
*   **API Logic**: Integrated `finalizeClips` and error normalization into [`generate.js`](file:///Users/matt/projects/yt-highlight-reel/api/generate.js), ensuring that even on failures, appropriate fallbacks are built.
*   **Client AI Handler**: Added [`AiHighlightError`](file:///Users/matt/projects/yt-highlight-reel/src/ai.js) and ensured all generation errors bubble up directly for UI handling.
*   **UI/UX**: Enhanced [`ui.js`](file:///Users/matt/projects/yt-highlight-reel/src/ui.js) to support error states and stall messaging in the progress modal, with corresponding styles in [`style.css`](file:///Users/matt/projects/yt-highlight-reel/src/style.css).
*   **Application Flow**: Refactored [`main.js`](file:///Users/matt/projects/yt-highlight-reel/src/main.js) to catch generation errors and display them via the UI instead of silent failures.
*   **Testing**: Added [`highlights.test.js`](file:///Users/matt/projects/yt-highlight-reel/test/highlights.test.js) and modernized [`progressStream.test.js`](file:///Users/matt/projects/yt-highlight-reel/test/progressStream.test.js) to use native `node:test`.

---
