---
title: "Update Userscript DevTools Detection"
date: "2026-08-01"
conversation_id: "0cd2d6b7-be1f-4684-94a6-bf125673d2a1"
source: "antigravity"
---

# Update Userscript DevTools Detection

## User

Please update /Users/matt/projects/userscript-bundler/userscripts/control-center.js:

1. Update `USCC_VERSION` at line 11 to `"2026-08-01-c"`.
2. Update the DevTools detection mechanism (lines 709-734) to use `console.table` getter inspection / `debugger` getter timing / window size diff combined:

```javascript
	// ── DevTools open detection ─────────────────────────
	const DEVTOOLS_THRESHOLD = 160;
	let devToolsWasOpen = false;

	// Fire getter when console evaluates an object (happens continuously when DevTools is open)
	const devtoolsDetector = {
		get id() {
			triggerDevToolsOpen();
			return "";
		}
	};

	function triggerDevToolsOpen() {
		if (!devToolsWasOpen) {
			devToolsWasOpen = true;
			if (!(shadowRoot && shadowRoot.querySelector(".overlay.open"))) {
				showToast();
			}
		}
	}

	function checkDevTools() {
		// Method 1: Window outer vs inner dimensions (docked DevTools)
		const widthDiff = window.outerWidth - window.innerWidth;
		const heightDiff = window.outerHeight - window.innerHeight;
		const isDockedOpen = widthDiff > DEVTOOLS_THRESHOLD || heightDiff > DEVTOOLS_THRESHOLD;

		if (isDockedOpen) {
			triggerDevToolsOpen();
		} else {
			// Method 2: Trigger console inspection for undocked or zero-diff DevTools
			console.log("%c", devtoolsDetector);
			console.clear();
			
			// If neither condition triggered, reset state so future opens re-trigger
			if (!isDockedOpen) {
				devToolsWasOpen = false;
			}
		}
	}

	setInterval(checkDevTools, 500);
	window.addEventListener("resize", checkDevTools);
```

---

## Assistant

Created At: 2026-08-01T17:14:41-06:00
Completed At: 2026-08-01T17:14:58-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/projects/userscript-bundler/userscripts/control-center.js. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -8,7 +8,7 @@
 (function () {
 	"use strict";
 
-	const USCC_VERSION = "2026-08-01-b";
+	const USCC_VERSION = "2026-08-01-c";
 	console.log(
 		`%c[USCC v${USCC_VERSION}] Userscript Control Center loaded.`,
 		"color:#6366f1;font-weight:bold;font-size:12px"
@@ -705,30 +705,48 @@
 		GM_registerMenuCommand("Open Userscript Control Center", openUI);
 	}
 
-	// ── DevTools open detection via window size delta ─────────────────
-	// Cmd+Opt+I is intercepted by Chrome before keydown reaches the page,
-	// so we detect DevTools opening by watching the inner/outer size gap.
-	// This covers docked DevTools (bottom or side). Undocked DevTools won't
-	// trigger a size change but is rare; Alt+I is the manual fallback.
-	const DEVTOOLS_THRESHOLD = 160; // px — smaller gaps are normal browser chrome
-	let devToolsWasOpen = false; // default to false
+	// ── DevTools open detection ─────────────────────────
+	const DEVTOOLS_THRESHOLD = 160;
+	let devToolsWasOpen = false;
+
+	// Fire getter when console evaluates an object (happens continuously when DevTools is open)
+	const devtoolsDetector = {
+		get id() {
+			triggerDevToolsOpen();
+			return "";
+		}
+	};
+
+	function triggerDevToolsOpen() {
+		if (!devToolsWasOpen) {
+			devToolsWasOpen = true;
+			if (!(shadowRoot && shadowRoot.querySelector(".overlay.open"))) {
+				showToast();
+			}
+		}
+	}
 
 	function checkDevTools() {
+		// Method 1: Window outer vs inner dimensions (docked DevTools)
 		const widthDiff = window.outerWidth - window.innerWidth;
 		const heightDiff = window.outerHeight - window.innerHeight;
-		const isOpen = widthDiff > DEVTOOLS_THRESHOLD || heightDiff > DEVTOOLS_THRESHOLD;
-
-		if (isOpen && !devToolsWasOpen) {
-			// DevTools just opened — show toast unless CC modal is already open
-			if (!(shadowRoot && shadowRoot.querySelector(".overlay.open"))) {
-				showToast();
-			}
-		}
-		devToolsWasOpen = isOpen;
-	}
-
-	// Poll at ~4fps — cheap, imperceptible
-	setInterval(checkDevTools, 250);
+		const isDockedOpen = widthDiff > DEVTOOLS_THRESHOLD || heightDiff > DEVTOOLS_THRESHOLD;
+
+		if (isDockedOpen) {
+			triggerDevToolsOpen();
+		} else {
+			// Method 2: Trigger console inspection for undocked or zero-diff DevTools
+			console.log("%c", devtoolsDetector);
+			console.clear();
+			
+			// If neither condition triggered, reset state so future opens re-trigger
+			if (!isDockedOpen) {
+				devToolsWasOpen = false;
+			}
+		}
+	}
+
+	setInterval(checkDevTools, 500);
 	window.addEventListener("resize", checkDevTools);
 
 	// Alt+I = manual trigger (in case DevTools is undocked or detection missed)
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

We did our best to apply changes despite some inaccuracies. Double check if the edit applied is what you intended.

Created At: 2026-08-01T17:14:59-06:00
Completed At: 2026-08-01T17:14:59-06:00
Message sent to "f275218d-32af-4188-b6b1-3de294fb2a33".

The requested updates to `/Users/matt/projects/userscript-bundler/userscripts/control-center.js` have been successfully completed:

1.  **Version Update**: `USCC_VERSION` was updated from `"2026-08-01-b"` to `"2026-08-01-c"`.
2.  **DevTools Detection Logic**: The detection block was replaced with the requested implementation, combining window dimension checks (for docked DevTools) with a `console` log getter trigger (for undocked/zero-diff DevTools).

I have notified the parent agent of these changes.

---
