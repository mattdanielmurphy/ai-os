---
title: "Automate YouTube Transcript Processing"
date: "2026-08-08"
conversation_id: "14d1a738-f71f-42e9-bc5b-0dfd44b4e3b8"
source: "antigravity"
---

# Automate YouTube Transcript Processing

## User

In `/Users/matt/projects/userscript-bundler/userscripts/youtube-master.user.js`:

Implement the automated transcript-to-prompt and clipboard-to-reel flow:

1. Create helper `async function getCompleteTranscript()`:
   - Contains the transcript retrieval logic (finds transcript container, waits for segments, extracts timestamp + text lines sorted by seconds, and returns the joined string).
   - `shareBtn.onclick` can call `const t = await getCompleteTranscript(); if (t) { await navigator.clipboard.writeText(t); showToast("Transcript copied!"); }`.

2. Update `reelBtn.onclick` in `setupTranscriptButton()`:
   - If `_highlightSegments.length === 0`:
     - `showToast("⏳ Extracting transcript & building prompt...")`
     - `const transcriptText = await getCompleteTranscript()`
     - If (!transcriptText) { showToast("Could not extract transcript"); return; }
     - Construct `fullPrompt`:
`You are a Video Editor creating a tight, high-signal "Highlight Reel / Supercut" of a YouTube video using its transcript.

### Goal:
Select the most essential soundbites and insights that summarize the video's core arguments, demonstrations, and conclusions.

### Constraints:
1. Target Cumulative Duration: ~3 to 5 minutes (or ~10-15% of total runtime).
2. Continuous Soundbites: Each segment must start at the beginning of a complete sentence and end after the thought is fully expressed (do not cut mid-sentence).
3. Cut Fluff: Completely omit sponsor reads, channel intros/outros, repetitive filler, and low-information chit-chat.
4. Output Format: Return ONLY a raw JSON array of objects (no markdown code fences, no extra commentary).

### JSON Schema:
[
  {
    "start": 42,
    "end": 85,
    "title": "The Core Problem Explained",
    "tier": 1
  }
]

* Note: "start" and "end" MUST be integer seconds from the start of the video.

### Transcript to Analyze:
` + transcriptText;
     - `await navigator.clipboard.writeText(fullPrompt)`
     - Call `startClipboardWatcher(fullPrompt)`
   - If `_highlightSegments.length > 0`:
     - `window.toggleHighlightReel()`

3. Create `function startClipboardWatcher(originalPrompt)`:
   - Displays a floating gold banner at the top center of the screen (`#yt-clipboard-waiting-banner`):
     - Displays text: `📋 Prompt + transcript copied! Paste into your LLM. Waiting for JSON on clipboard...`
     - Style: dark glassmorphic `background: rgba(28,28,28,0.95)`, `color: #fff`, `border: 1px solid #ffd700`, `padding: 10px 20px`, `border-radius: 20px`, `z-index: 100000`, `position: fixed`, `top: 20px`, `left: 50%`, `transform: translateX(-50%)`, `box-shadow: 0 8px 32px rgba(0,0,0,0.6)`.
   - Starts polling interval (every 800ms) and `window.addEventListener('focus', checkCb)`.
   - Checks `navigator.clipboard.readText()`:
     - If text !== originalPrompt:
       - Try parsing `JSON.parse(text)`.
       - If `Array.isArray(parsed) && parsed.length > 0 && parsed[0].start !== undefined`:
         - Clear polling interval.
         - Update banner style: `cursor: pointer`, `background: #ffd700`, `color: #000`, `font-weight: 700`.
         - Set text: `✨ JSON ready on clipboard! [▶ Activate Highlight Reel (${parsed.length} segments)]`
         - `banner.onclick = () => { window.loadHighlightReel(parsed); banner.remove(); }`
         - Also listen for `keydown` with `Enter`: if pressed, activates reel and removes banner.
   - Self-dismisses after 120 seconds if no JSON is copied.

4. Ensure NO `innerHTML` is used anywhere. Pure DOM node creation.

Make sure the file syntax is 100% valid JavaScript.

---

## Assistant

Created At: 2026-08-08T01:01:49-06:00
Completed At: 2026-08-08T01:01:49-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/youtube-master.user.js`
Total Lines: 1736
Total Bytes: 59787
Showing lines 1 to 800
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: // ==UserScript==
2: // @name         YouTube Master Script (Consolidated)
3: // @namespace    http://tampermonkey.net/
4: // @version      1.0
5: // @description  Consolidated script for all YouTube userscript features with a single MutationObserver for efficiency.
6: // @author       Gemini CLI Agent
7: // @match        https://www.youtube.com/*
8: // @grant        GM.getValue
9: // @grant        GM.setValue
10: // @run-at       document-start
11: // ==/UserScript==
12: 
13: ;(function () {
14: 	"use strict"
15: 
16: 	console.log("new version loaded")
17: 
18: 	// --- 0. CUSTOM APP STYLE (Background & Variables) ---
19: 	// NOTE: We strictly use inline style application via JS. 
20: 	// YouTube uses Trusted Types CSP which blocks setting style.textContent in userscripts.
21: 	// Using pure el.style.setProperty bypasses CSP entirely and beats Polymer's DOM updates.
22: 	function enforceDarkThemeBg() {
23: 		try {
24: 			const isDarkActive = isDarkMode();
25: 
26: 			const vars =[
27: 				'--yt-spec-base-background', 
28: 				'--yt-spec-brand-background-solid', 
29: 				'--yt-spec-brand-background-primary',
30: 				'--yt-spec-general-background-a',
31: 				'--yt-spec-general-background-b',
32: 				'--yt-spec-general-background-c',
33: 				'--yt-spec-raised-background',
34: 				'--yt-spec-menu-background'
35: 			];
36: 			
37: 			const applyVars = (el) => {
38: 				if (!el) return;
39: 				
40: 				if (isDarkActive) {
41: 					// Avoid DOM thrashing: Check if it's already #131313 before writing
42: 					if (el.style.getPropertyValue('--yt-spec-b
<truncated 30144 bytes>
#segments-container") || transcriptContainer.closest("ytd-transcript-segment-list-renderer") || transcriptContainer
762: 
763: 				scrollable.scrollTop = 0
764: 				await new Promise((res) => setTimeout(res, 50))
765: 
766: 				let allSegments = new Map()
767: 				let lastSize = -1
768: 				let sameSizeCount = 0
769: 				const maxSteps = 200
770: 				const sweepDelay = 25
771: 				const jumpMultiplier = 4.0
772: 
773: 				for (let i = 0; i < maxSteps; i++) {
774: 					const nodes = transcriptContainer.querySelectorAll("ytd-transcript-segment-renderer, transcript-segment-view-model, ytw-transcript-segment-view-model, .ytw-transcript-segment-view-model")
775: 
776: 					nodes.forEach((n) => {
777: 						const d = n.data || n.segmentsViewModel
778: 						let time = "",
779: 							text = ""
780: 						if (d && d.timestampText && d.bodyText) {
781: 							time = d.timestampText.simpleText || d.timestampText.runs?.map((r) => r.text).join("")
782: 							text = d.bodyText.simpleText || d.bodyText.runs?.map((r) => r.text).join("")
783: 						} else {
784: 							time = (n.querySelector("#segment-timestamp, .ytwTranscriptSegmentViewModelTimestamp, .timestamp")?.innerText || "").trim()
785: 							text = (n.querySelector(".segment-text, #segment-text, .segment-text-content, [role='text']")?.innerText || "").trim()
786: 						}
787: 						if (time && !allSegments.has(time)) {
788: 							allSegments.set(time, { text, sec: tsToSec(time) })
789: 						}
790: 					})
791: 
792: 					if (allSegments.size === lastSize) {
793: 						sameSizeCount++
794: 						if (sameSizeCount > 12 || scrollable.scrollTop + scrollable.clientHeight >= scrollable.scrollHeight - 10) break
795: 					} else {
796: 						lastSize = allSegments.size
797: 						sameSizeCount = 0
798: 					}
799: 
800: 					scrollable.scrollTop += scrollable.clientHeight * jumpMultiplier
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-08T01:01:59-06:00
Completed At: 2026-08-08T01:01:59-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/projects/userscript-bundler/userscripts/youtube-master.user.js. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -399,6 +399,86 @@
 	// --- 6. YOUTUBE GET TRANSCRIPT BUTTON (Watch Page Only) ---
 	let _transcriptInterval = null
 
+	async function getCompleteTranscript() {
+		// Ensure transcript panel is active
+		let showTranscriptBtn = document.querySelector('button[aria-label="Show transcript"]')
+		if (showTranscriptBtn) showTranscriptBtn.click()
+		
+		await new Promise(r => setTimeout(r, 1000))
+		
+		const container = document.querySelector("#segments-container")
+		if (!container) return null
+		
+		const nodes = container.querySelectorAll("ytd-transcript-segment-renderer, transcript-segment-view-model, ytw-transcript-segment-view-model")
+		const segments = []
+		
+		nodes.forEach(n => {
+			const timeEl = n.querySelector(".timestamp, .ytw-transcript-segment-view-model-timestamp")
+			const textEl = n.querySelector(".segment-text, .ytw-transcript-segment-view-model-body")
+			if (timeEl && textEl) {
+				const time = timeEl.innerText.trim()
+				const text = textEl.innerText.trim()
+				const p = time.split(":").map(Number)
+				const sec = p.length === 3 ? p[0]*3600 + p[1]*60 + p[2] : (p.length === 2 ? p[0]*60 + p[1] : p[0])
+				segments.push({ sec, text })
+			}
+		})
+		
+		return segments.sort((a,b) => a.sec - b.sec).map(s => `[${s.sec}s] ${s.text}`).join("\n")
+	}
+
+	function startClipboardWatcher(originalPrompt) {
+		const banner = document.createElement("div")
+		banner.id = "yt-clipboard-waiting-banner"
+		Object.assign(banner.style, {
+			background: "rgba(28,28,28,0.95)",
+			color: "#fff",
+			border: "1px solid #ffd700",
+			padding: "10px 20px",
+			borderRadius: "20px",
+			zIndex: "100000",
+			position: "fixed",
+			top: "20px",
+			left: "50%",
<truncated 1602 bytes>
ext()
-						window.loadHighlightReel(JSON.parse(text))
-					} catch (err) {
-						const text = prompt("Paste highlight JSON:")
-						if (text) window.loadHighlightReel(JSON.parse(text))
-					}
-				} else {
-					window.toggleHighlightReel()
+					showToast("⏳ Extracting transcript & building prompt...")
+					const transcriptText = await getCompleteTranscript()
+					if (!transcriptText) {
+						showToast("Could not extract transcript")
+						return
+					}
+					const fullPrompt = `You are a Video Editor creating a tight, high-signal "Highlight Reel / Supercut" of a YouTube video using its transcript.
+
+### Goal:
+Select the most essential soundbites and insights that summarize the video's core arguments, demonstrations, and conclusions.
+
+### Constraints:
+1. Target Cumulative Duration: ~3 to 5 minutes (or ~10-15% of total runtime).
+2. Continuous Soundbites: Each segment must start at the beginning of a complete sentence and end after the thought is fully expressed (do not cut mid-sentence).
+3. Cut Fluff: Completely omit sponsor reads, channel intros/outros, repetitive filler, and low-information chit-chat.
+4. Output Format: Return ONLY a raw JSON array of objects (no markdown code fences, no extra commentary).
+
+### JSON Schema:
+[
+  {
+    "start": 42,
+    "end": 85,
+    "title": "The Core Problem Explained",
+    "tier": 1
+  }
+]
+
+* Note: "start" and "end" MUST be integer seconds from the start of the video.
+
+### Transcript to Analyze:
+` + transcriptText
+					await navigator.clipboard.writeText(fullPrompt)
+					startClipboardWatcher(fullPrompt)
+				} else {
+					if (typeof window.toggleHighlightReel === 'function') {
+						window.toggleHighlightReel()
+					}
 				}
 			}
 			shareBtn.parentNode.insertBefore(reelBtn, shareBtn.nextSibling)
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-08T01:02:00-06:00
Completed At: 2026-08-08T01:02:00-06:00
Message sent to "4aac32dc-cc32-416a-874d-4de452ac5d7a".

The requested transcript-to-prompt and clipboard-to-reel flow has been implemented in `/Users/matt/projects/userscript-bundler/userscripts/youtube-master.user.js`.

### Summary of Changes:

*   **Transcript Extraction:** Added a helper `getCompleteTranscript()` that identifies the transcript container, extracts segments (timestamps and text), and returns a formatted string.
*   **Prompt Generation & Clipboard:** Updated the Highlight Reel button's `onclick` handler to:
    *   Extract the transcript when no reel segments are active.
    *   Construct the requested LLM prompt.
    *   Copy the prompt to the clipboard.
    *   Initiate a `startClipboardWatcher()`.
*   **Clipboard Watcher:** Implemented `startClipboardWatcher()` which:
    *   Displays a gold, glassmorphic floating banner (`#yt-clipboard-waiting-banner`) to notify the user.
    *   Polls the clipboard every 800ms (and listens for browser focus) for valid JSON output.
    *   Once valid JSON is detected, it transforms the banner into a clickable action button that triggers `window.loadHighlightReel(parsed)`.
    *   Includes a 120-second self-dismissal timer.
*   **Compliance:** All UI elements are created using pure DOM node methods to avoid `innerHTML` and ensure security/compatibility.

---
