---
title: "Fix TrustedHTML CSP Violation"
date: "2026-08-08"
conversation_id: "c811dd5c-b17c-4919-91e2-7d585606bc8c"
source: "antigravity"
---

# Fix TrustedHTML CSP Violation

## User

In `/Users/matt/projects/userscript-bundler/userscripts/youtube-master.user.js`:

Fix the TrustedHTML CSP violation by replacing all `innerHTML` assignments in `createHighlightHUD` and `updateHighlightHudUI` (around lines 916-976) with safe, direct DOM manipulation (createElement, textContent, appendChild, and styling via Object.assign or setProperty).

Specifically:
1. In `createHighlightHUD()`:
Construct the HUD DOM structure without `hud.innerHTML = ...`:
- Create the top row container with `header` span ("⚡ HIGHLIGHT REEL") and `toggleBtn` ("Active" / "Off").
- Create `status` div (id `yt-reel-status`, textContent "Idle").
- Create button row container with:
  - `pasteBtn` (id `yt-reel-paste`, textContent "📋 Paste JSON")
  - `prevBtn` (id `yt-reel-prev`, textContent "⏮")
  - `nextBtn` (id `yt-reel-next`, textContent "⏭")
- Append everything via `hud.appendChild(...)`.
- Attach click handlers directly to the created elements.

2. In `updateHighlightHudUI()`:
- Do NOT use `status.innerHTML = ...`.
- Clear status children with `status.textContent = ""` and create text nodes or spans for `Segment X/Y` and segment title.

Ensure no `innerHTML` is used anywhere in the Highlight Reel section.
Make sure the JavaScript syntax is valid.

---

## Assistant

Created At: 2026-08-08T00:31:42-06:00
Completed At: 2026-08-08T00:31:42-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/youtube-master.user.js`
Total Lines: 1701
Total Bytes: 58219
Showing lines 900 to 1000
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
900: 			Object.assign(bar.style, {
901: 				position: "absolute",
902: 				left: `${left}%`,
903: 				width: `${width}%`,
904: 				height: "100%",
905: 				background: "rgba(255, 215, 0, 0.8)",
906: 			})
907: 			container.appendChild(bar)
908: 		})
909: 	}
910: 
911: 	function removeHighlightHeatmap() {
912: 		const c = document.getElementById("yt-highlight-heatmap-container")
913: 		if (c) c.remove()
914: 	}
915: 
916: 	function createHighlightHUD() {
917: 		if (document.getElementById("yt-highlight-hud")) return
918: 		const hud = document.createElement("div")
919: 		hud.id = "yt-highlight-hud"
920: 		Object.assign(hud.style, {
921: 			position: "fixed",
922: 			bottom: "20px",
923: 			right: "20px",
924: 			width: "280px",
925: 			padding: "16px",
926: 			background: "rgba(18, 18, 18, 0.94)",
927: 			border: "1px solid rgba(255,215,0,0.3)",
928: 			borderRadius: "12px",
929: 			backdropFilter: "blur(10px)",
930: 			zIndex: "99999",
931: 			color: "white",
932: 			fontFamily: "Roboto, Arial, sans-serif",
933: 			fontSize: "13px",
934: 			boxShadow: "0 8px 32px rgba(0,0,0,0.5)",
935: 		})
936: 
937: 		hud.innerHTML = `
938:             <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
939:                 <span style="font-weight:bold; color:#FFD700;">⚡ HIGHLIGHT REEL</span>
940:                 <button id="yt-reel-toggle" style="background:none; border:none; color:white; cursor:pointer;">[Toggle]</button>
941:             </div>
942:             <div id="yt-reel-status" style="margin-bottom:10px;">Idle</div>
94
<truncated 714 bytes>
nc () => {
955: 			try {
956: 				const text = (await navigator.clipboard.readText()) || prompt("Paste highlight JSON:")
957: 				if (!text) return
958: 				window.loadHighlightReel(JSON.parse(text))
959: 			} catch (e) {
960: 				showToast("Failed to parse JSON")
961: 			}
962: 		}
963: 	}
964: 
965: 	function updateHighlightHudUI() {
966: 		const hud = document.getElementById("yt-highlight-hud")
967: 		if (!hud) return
968: 		const status = hud.querySelector("#yt-reel-status")
969: 		if (_highlightSegments.length > 0 && _isReelActive) {
970: 			const s = _highlightSegments[_currentSegmentIndex]
971: 			status.innerHTML = `Segment ${_currentSegmentIndex + 1}/${_highlightSegments.length}<br>${s.title}`
972: 		} else {
973: 			status.innerHTML = _isReelActive ? "Active" : "Off"
974: 		}
975: 	}
976: 
977: 	// Keyboard hotkeys
978: 	document.addEventListener("keydown", (e) => {
979: 		if (["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) return
980: 		if (e.key.toLowerCase() === "h") window.toggleHighlightReel()
981: 		if (e.key === "[") window.jumpHighlightRelative(-1)
982: 		if (e.key === "]") window.jumpHighlightRelative(1)
983: 	})
984: 
985: 	// --- 7. YOUTUBE SEARCH EXCLUDE TERMS (Search Page Only) ---
986: 
987: 	let resultsObserver = null
988: 	let _ytExclResizeHandler = null
989: 	let _ytExclScrollHandler = null
990: 
991: 	function ensureStyle() {
992: 		let style = document.getElementById("yt-search-exclusion-style")
993: 		if (style) return style
994: 		style = document.createElement("style")
995: 		style.id = "yt-search-exclusion-style"
996: 		style.appendChild(document.createTextNode('ytd-video-renderer[data-excluded="true"] { display: none !important; }\n            #yt-search-exclusion-tip { will-change: transform, opacity; }'))
997: 		document.head.appendChild(style)
998: 		return style
999: 	}
1000: 
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-08T00:31:46-06:00
Completed At: 2026-08-08T00:31:46-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/userscript-bundler/userscripts/youtube-master.user.js. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -934,24 +934,58 @@
 			boxShadow: "0 8px 32px rgba(0,0,0,0.5)",
 		})
 
-		hud.innerHTML = `
-            <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
-                <span style="font-weight:bold; color:#FFD700;">⚡ HIGHLIGHT REEL</span>
-                <button id="yt-reel-toggle" style="background:none; border:none; color:white; cursor:pointer;">[Toggle]</button>
-            </div>
-            <div id="yt-reel-status" style="margin-bottom:10px;">Idle</div>
-            <div style="display:flex; gap:5px;">
-                <button id="yt-reel-paste" style="flex:1;">📋 Paste JSON</button>
-                <button id="yt-reel-prev" style="flex:1;">⏮</button>
-                <button id="yt-reel-next" style="flex:1;">⏭</button>
-            </div>
-        `
+		const headerRow = document.createElement("div")
+		Object.assign(headerRow.style, { display: "flex", justifyContent: "space-between", marginBottom: "10px" })
+		
+		const header = document.createElement("span")
+		header.textContent = "⚡ HIGHLIGHT REEL"
+		Object.assign(header.style, { fontWeight: "bold", color: "#FFD700" })
+		
+		const toggleBtn = document.createElement("button")
+		toggleBtn.id = "yt-reel-toggle"
+		toggleBtn.textContent = "[Toggle]"
+		Object.assign(toggleBtn.style, { background: "none", border: "none", color: "white", cursor: "pointer" })
+		
+		headerRow.appendChild(header)
+		headerRow.appendChild(toggleBtn)
+		hud.appendChild(headerRow)
+
+		const status = document.createElement("div")
+		status.id = "yt-reel-status"
+		status.style.marginBottom = "10px"
+		status.textContent = "Idle"
+		hud.appendChild(status)
+
+		const btnRow = document.c
<truncated 332 bytes>
		prevBtn.textContent = "⏮"
+		prevBtn.style.flex = "1"
+		
+		const nextBtn = document.createElement("button")
+		nextBtn.id = "yt-reel-next"
+		nextBtn.textContent = "⏭"
+		nextBtn.style.flex = "1"
+		
+		btnRow.appendChild(pasteBtn)
+		btnRow.appendChild(prevBtn)
+		btnRow.appendChild(nextBtn)
+		hud.appendChild(btnRow)
+
 		document.body.appendChild(hud)
 
-		document.getElementById("yt-reel-toggle").onclick = window.toggleHighlightReel
-		document.getElementById("yt-reel-prev").onclick = () => window.jumpHighlightRelative(-1)
-		document.getElementById("yt-reel-next").onclick = () => window.jumpHighlightRelative(1)
-		document.getElementById("yt-reel-paste").onclick = async () => {
+		toggleBtn.onclick = window.toggleHighlightReel
+		prevBtn.onclick = () => window.jumpHighlightRelative(-1)
+		nextBtn.onclick = () => window.jumpHighlightRelative(1)
+		pasteBtn.onclick = async () => {
 			try {
 				const text = (await navigator.clipboard.readText()) || prompt("Paste highlight JSON:")
 				if (!text) return
@@ -965,11 +965,14 @@
 		const hud = document.getElementById("yt-highlight-hud")
 		if (!hud) return
 		const status = hud.querySelector("#yt-reel-status")
+		status.textContent = ""
 		if (_highlightSegments.length > 0 && _isReelActive) {
 			const s = _highlightSegments[_currentSegmentIndex]
-			status.innerHTML = `Segment ${_currentSegmentIndex + 1}/${_highlightSegments.length}<br>${s.title}`
-		} else {
-			status.innerHTML = _isReelActive ? "Active" : "Off"
+			status.appendChild(document.createTextNode(`Segment ${_currentSegmentIndex + 1}/${_highlightSegments.length}`))
+			status.appendChild(document.createElement("br"))
+			status.appendChild(document.createTextNode(s.title))
+		} else {
+			status.textContent = _isReelActive ? "Active" : "Off"
 		}
 	}
 
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-08T00:31:47-06:00
Completed At: 2026-08-08T00:31:47-06:00
Message sent to "4aac32dc-cc32-416a-874d-4de452ac5d7a".

The TrustedHTML CSP violation in `/Users/matt/projects/userscript-bundler/userscripts/youtube-master.user.js` has been resolved by replacing all `innerHTML` assignments in `createHighlightHUD` and `updateHighlightHudUI` with safe, direct DOM manipulation (`createElement`, `textContent`, `appendChild`, and `Object.assign` for styling).

---
