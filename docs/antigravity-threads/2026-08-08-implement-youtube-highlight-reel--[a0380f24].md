---
title: "Implement YouTube Highlight Reel"
date: "2026-08-08"
conversation_id: "a0380f24-dae5-4de6-a5c9-cd8269650b3f"
source: "antigravity"
---

# Implement YouTube Highlight Reel

## User

In `/Users/matt/projects/userscript-bundler/userscripts/youtube-master.user.js`:

In `setupTranscriptButton()` (around lines 420-435), right after setting up `shareBtn`, create and insert the `reelBtn` (`#yt-highlight-reel-btn`) as a sibling right next to `shareBtn` (`shareBtn.parentNode.insertBefore(reelBtn, shareBtn.nextSibling)`):

1. Check if `document.getElementById("yt-highlight-reel-btn")` exists. If not, create it.
2. Style `reelBtn` matching YouTube tonal buttons:
   - height: "36px", padding: "0 16px", borderRadius: "18px", marginLeft: "8px", border: "none", background: _isReelActive ? "rgba(255, 215, 0, 0.2)" : "rgba(255, 255, 255, 0.1)", color: "#fff", cursor: "pointer", fontSize: "14px", fontWeight: "500", fontFamily: "Roboto, Arial, sans-serif", display: "inline-flex", alignItems: "center", justifyContent: "center"
3. Text:
   `reelBtn.textContent = _isReelActive && _highlightSegments.length > 0 ? `⚡ Reel: ON (${_currentSegmentIndex + 1}/${_highlightSegments.length})` : "⚡ Highlight reel"`
4. `onclick`:
   - If `_highlightSegments.length === 0`: read clipboard via `navigator.clipboard.readText()` or fallback `prompt("Paste highlight JSON:")` and call `window.loadHighlightReel(JSON.parse(text))`.
   - If `_highlightSegments.length > 0`: call `window.toggleHighlightReel()`.
5. Remove any leftover call to `createHighlightHUD()` from `initPageFeatures()`.

Ensure JavaScript syntax is valid and no `innerHTML` is used.

---

## Assistant

Created At: 2026-08-08T00:58:49-06:00
Completed At: 2026-08-08T00:58:49-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/youtube-master.user.js`
Total Lines: 1699
Total Bytes: 58564
Showing lines 400 to 450
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
400: 	let _transcriptInterval = null
401: 
402: 	async function setupTranscriptButton() {
403: 		if (!isWatchPage()) return
404: 
405: 		const shareBtnContainer = document.querySelector("#above-the-fold #top-level-buttons-computed, #top-level-buttons-computed, #actions-inner #top-level-buttons-computed")
406: 		if (!shareBtnContainer) {
407: 			console.log("[Transcript] Share button container not found yet.")
408: 			return
409: 		}
410: 
411: 		const shareBtn = shareBtnContainer.querySelector('button[aria-label="Share"]')
412: 
413: 		if (!shareBtn) {
414: 			console.log("[Transcript] Share button not found yet.")
415: 			return
416: 		}
417: 
418: 		if (shareBtn.hasAttribute("data-transcript-button-processed")) {
419: 			return
420: 		}
421: 
422: 		console.log("[Transcript] Found Share button, applying 'Get transcript' override.")
423: 		shareBtn.setAttribute("data-transcript-button-processed", "true")
424: 
425: 		// Change button text
426: 		const textDiv = shareBtn.querySelector(".yt-spec-button-shape-next__button-text-content")
427: 		if (textDiv) {
428: 			textDiv.innerText = "Get transcript"
429: 		} else {
430: 			shareBtn.innerText = "Get transcript"
431: 		}
432: 
433: 		shareBtn.onclick = async function (e) {
434: 			e.preventDefault()
435: 			e.stopPropagation()
436: 
437: 			console.log("[Transcript] 'Get transcript' clicked. Starting search...")
438: 
439: 			// 1. Trigger functionality to show transcript
440: 			let showTranscriptBtn = document.querySelector('button[aria-label="Show transcript"]')
441: 			if (!showTranscriptBtn) {
442: 				console.log("[Transcript] 'Show transcript' button not found in main view. Checking description...")
443: 				const description = document.querySelector("#description")
444: 				if (description) {
445: 					showTranscriptBtn = description.querySelector('button[aria-label="Show transcript"]')
446: 				}
447: 			}
448: 
449: 			if (showTranscriptBtn) {
450: 				console.log("[Transcript] Clicking 'Show transcript' button...")
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-08T00:58:50-06:00
Completed At: 2026-08-08T00:58:50-06:00
{"File":"/Users/matt/projects/userscript-bundler/userscripts/youtube-master.user.js","LineNumber":1669,"LineContent":"            createHighlightHUD()"}

Created At: 2026-08-08T00:58:50-06:00
Completed At: 2026-08-08T00:58:50-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/youtube-master.user.js`
Total Lines: 1699
Total Bytes: 58564
Showing lines 1660 to 1675
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1660: 			initMaxQuality()
1661: 
1662: 			// Start Transcript Button polling (needs polling to wait for button to appear)
1663: 			if (!_transcriptInterval) {
1664: 				_transcriptInterval = setInterval(setupTranscriptButton, 500)
1665: 			}
1666:             
1667:             // Highlight Reel
1668:             initHighlightReelVideoListener()
1669:             createHighlightHUD()
1670: 		}
1671: 
1672: 	}
1673: 
1674: 	// 1. Initial setup for features that need to run immediately
1675: 	toggleAllThumbnails(thumbnailsHidden) // Initial thumbnail state
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-08T00:58:53-06:00
Completed At: 2026-08-08T00:58:53-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/projects/userscript-bundler/userscripts/youtube-master.user.js. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -430,6 +430,44 @@
 			shareBtn.innerText = "Get transcript"
 		}
 
+		let reelBtn = document.getElementById("yt-highlight-reel-btn")
+		if (!reelBtn) {
+			reelBtn = document.createElement("button")
+			reelBtn.id = "yt-highlight-reel-btn"
+			Object.assign(reelBtn.style, {
+				height: "36px",
+				padding: "0 16px",
+				borderRadius: "18px",
+				marginLeft: "8px",
+				border: "none",
+				background: _isReelActive ? "rgba(255, 215, 0, 0.2)" : "rgba(255, 255, 255, 0.1)",
+				color: "#fff",
+				cursor: "pointer",
+				fontSize: "14px",
+				fontWeight: "500",
+				fontFamily: "Roboto, Arial, sans-serif",
+				display: "inline-flex",
+				alignItems: "center",
+				justifyContent: "center"
+			})
+
+			reelBtn.onclick = async () => {
+				if (_highlightSegments.length === 0) {
+					try {
+						const text = await navigator.clipboard.readText()
+						window.loadHighlightReel(JSON.parse(text))
+					} catch (err) {
+						const text = prompt("Paste highlight JSON:")
+						if (text) window.loadHighlightReel(JSON.parse(text))
+					}
+				} else {
+					window.toggleHighlightReel()
+				}
+			}
+			shareBtn.parentNode.insertBefore(reelBtn, shareBtn.nextSibling)
+		}
+		reelBtn.textContent = _isReelActive && _highlightSegments.length > 0 ? `⚡ Reel: ON (${_currentSegmentIndex + 1}/${_highlightSegments.length})` : "⚡ Highlight reel"
+
 		shareBtn.onclick = async function (e) {
 			e.preventDefault()
 			e.stopPropagation()
@@ -1665,7 +1665,6 @@
             
             // Highlight Reel
             initHighlightReelVideoListener()
-            createHighlightHUD()
 		}
 
 	}
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-08T00:58:53-06:00
Completed At: 2026-08-08T00:58:53-06:00
Message sent to "4aac32dc-cc32-416a-874d-4de452ac5d7a".

The `reelBtn` has been added to `setupTranscriptButton()` and the redundant `createHighlightHUD()` call has been removed from `initPageFeatures()` in `/Users/matt/projects/userscript-bundler/userscripts/youtube-master.user.js`.

---
