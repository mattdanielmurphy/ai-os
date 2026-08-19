---
title: "Update DevTools Detection Logic"
date: "2026-08-01"
conversation_id: "47ba9590-3884-4e11-98b5-1dbbfa10b4c8"
source: "antigravity"
---

# Update DevTools Detection Logic

## User

Please update /Users/matt/projects/userscript-bundler/userscripts/control-center.js:

1. Update USCC_VERSION at line 11 from "2026-08-01-a" to "2026-08-01-b".
2. Add a `resize` event listener alongside `setInterval` to immediately react when window dimensions change due to toggling DevTools docked panel.

At the end of the file, after `setInterval(checkDevTools, 250);`, add:
`window.addEventListener("resize", checkDevTools);`

Also update `checkDevTools()` logic to properly handle state tracking:

```javascript
	const DEVTOOLS_THRESHOLD = 160; // px — smaller gaps are normal browser chrome
	let devToolsWasOpen = false; // default to false

	function checkDevTools() {
		const widthDiff = window.outerWidth - window.innerWidth;
		const heightDiff = window.outerHeight - window.innerHeight;
		const isOpen = widthDiff > DEVTOOLS_THRESHOLD || heightDiff > DEVTOOLS_THRESHOLD;

		if (isOpen && !devToolsWasOpen) {
			// DevTools just opened — show toast unless CC modal is already open
			if (!(shadowRoot && shadowRoot.querySelector(".overlay.open"))) {
				showToast();
			}
		}
		devToolsWasOpen = isOpen;
	}
```

---

## Assistant

Created At: 2026-08-01T17:13:43-06:00
Completed At: 2026-08-01T17:13:43-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/control-center.js`
Total Lines: 763
Total Bytes: 24383
Showing lines 1 to 763
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: /**
2:  * Userscript Control Center
3:  * 
4:  * Embedded cross-site control center for runtime enablement, Git history,
5:  * and targeted rollback.
6:  */
7: 
8: (function () {
9: 	"use strict";
10: 
11: 	const USCC_VERSION = "2026-08-01-a";
12: 	console.log(
13: 		`%c[USCC v${USCC_VERSION}] Userscript Control Center loaded.`,
14: 		"color:#6366f1;font-weight:bold;font-size:12px"
15: 	);
16: 	console.log(
17: 		"%c[USCC] DevTools detection active. Toast appears when DevTools opens (docked). Alt+I = manual trigger.",
18: 		"color:#888;font-size:11px"
19: 	);
20: 
21: 	// ── Toast state ────────────────────────────────────────────────
22: 	let ccToastEl = null;
23: 	let ccToastTimer = null;
24: 	const TOAST_DURATION = 5000; // ms
25: 
26: 	function showToast() {
27: 		removeToast();
28: 
29: 		ccToastEl = document.createElement("div");
30: 		ccToastEl.id = "uscc-toast";
31: 		Object.assign(ccToastEl.style, {
32: 			position: "fixed", bottom: "24px", right: "24px",
33: 			background: "#1e1e2e", color: "#e2e2f0",
34: 			padding: "12px 20px 6px 20px",
35: 			borderRadius: "10px", fontSize: "14px", fontFamily: "sans-serif",
36: 			cursor: "pointer", zIndex: "2147483647",
37: 			boxShadow: "0 6px 24px rgba(0,0,0,0.6)",
38: 			border: "1px solid #333346", minWidth: "220px",
39: 			overflow: "hidden", userSelect: "none",
40: 		});
41: 
42: 		const label = document.createElement("div");
43: 		label.textContent = "⚙️ Userscript Control Center";
44: 		label.
<truncated 24546 bytes>
on't
713: 	// trigger a size change but is rare; Alt+I is the manual fallback.
714: 	const DEVTOOLS_THRESHOLD = 160; // px — smaller gaps are normal browser chrome
715: 	let devToolsWasOpen = null; // null = not yet initialized
716: 
717: 	function checkDevTools() {
718: 		const widthDiff = window.outerWidth - window.innerWidth;
719: 		const heightDiff = window.outerHeight - window.innerHeight;
720: 		const isOpen = widthDiff > DEVTOOLS_THRESHOLD || heightDiff > DEVTOOLS_THRESHOLD;
721: 
722: 		if (devToolsWasOpen === null) {
723: 			// Initial check: if DevTools is already open when page loads, show toast!
724: 			devToolsWasOpen = isOpen;
725: 			if (isOpen && !(shadowRoot && shadowRoot.querySelector(".overlay.open"))) {
726: 				showToast();
727: 			}
728: 			return;
729: 		}
730: 
731: 		if (isOpen && !devToolsWasOpen) {
732: 			// DevTools just opened — show toast unless CC modal is already open
733: 			if (!(shadowRoot && shadowRoot.querySelector(".overlay.open"))) {
734: 				showToast();
735: 			}
736: 		}
737: 		devToolsWasOpen = isOpen;
738: 	}
739: 
740: 	// Poll at ~4fps — cheap, imperceptible
741: 	setInterval(checkDevTools, 250);
742: 
743: 	// Alt+I = manual trigger (in case DevTools is undocked or detection missed)
744: 	window.addEventListener("keydown", (e) => {
745: 		if (e.altKey && !e.metaKey && !e.ctrlKey && (e.key === "i" || e.key === "I")) {
746: 			if (shadowRoot && shadowRoot.querySelector(".overlay.open")) {
747: 				closeUI();
748: 			} else {
749: 				showToast();
750: 			}
751: 		}
752: 		// Escape while modal is open → close
753: 		if (e.key === "Escape" && shadowRoot && shadowRoot.querySelector(".overlay.open")) {
754: 			closeUI();
755: 		}
756: 	}, { capture: true });
757: 
758: 	// Expose globally for dispatcher invocation if needed
759: 	window.__USCC_OPEN__ = openUI;
760: 	window.__USCC_VERSION__ = USCC_VERSION;
761:     console.log(`USCC Initialized (v${USCC_VERSION})`);
762: })();
763: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-01T17:13:46-06:00
Completed At: 2026-08-01T17:13:46-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/projects/userscript-bundler/userscripts/control-center.js. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -8,7 +8,7 @@
 (function () {
 	"use strict";
 
-	const USCC_VERSION = "2026-08-01-a";
+	const USCC_VERSION = "2026-08-01-b";
 	console.log(
 		`%c[USCC v${USCC_VERSION}] Userscript Control Center loaded.`,
 		"color:#6366f1;font-weight:bold;font-size:12px"
@@ -711,7 +711,7 @@
 	// This covers docked DevTools (bottom or side). Undocked DevTools won't
 	// trigger a size change but is rare; Alt+I is the manual fallback.
 	const DEVTOOLS_THRESHOLD = 160; // px — smaller gaps are normal browser chrome
-	let devToolsWasOpen = null; // null = not yet initialized
+	let devToolsWasOpen = false; // default to false
 
 	function checkDevTools() {
 		const widthDiff = window.outerWidth - window.innerWidth;
@@ -718,14 +718,5 @@
 		const isOpen = widthDiff > DEVTOOLS_THRESHOLD || heightDiff > DEVTOOLS_THRESHOLD;
 
-		if (devToolsWasOpen === null) {
-			// Initial check: if DevTools is already open when page loads, show toast!
-			devToolsWasOpen = isOpen;
-			if (isOpen && !(shadowRoot && shadowRoot.querySelector(".overlay.open"))) {
-				showToast();
-			}
-			return;
-		}
-
 		if (isOpen && !devToolsWasOpen) {
 			// DevTools just opened — show toast unless CC modal is already open
 			if (!(shadowRoot && shadowRoot.querySelector(".overlay.open"))) {
@@ -736,6 +736,7 @@
 
 	// Poll at ~4fps — cheap, imperceptible
 	setInterval(checkDevTools, 250);
+	window.addEventListener("resize", checkDevTools);
 
 	// Alt+I = manual trigger (in case DevTools is undocked or detection missed)
 	window.addEventListener("keydown", (e) => {
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-01T17:13:47-06:00
Completed At: 2026-08-01T17:13:47-06:00
Message sent to "f275218d-32af-4188-b6b1-3de294fb2a33".

The changes to `/Users/matt/projects/userscript-bundler/userscripts/control-center.js` have been successfully implemented:

1.  **Version Update**: `USCC_VERSION` was updated from `"2026-08-01-a"` to `"2026-08-01-b"`.
2.  **Resize Listener**: A `window.addEventListener("resize", checkDevTools);` was added to ensure immediate UI reactions when DevTools are toggled.
3.  **Refactored `checkDevTools()`**: The function now uses a simplified state tracking approach (`devToolsWasOpen = false`) and directly handles opening detection as per your requirements.

I have notified the parent agent of these changes.

---
