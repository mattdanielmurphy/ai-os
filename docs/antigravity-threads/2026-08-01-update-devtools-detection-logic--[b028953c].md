---
title: "Update DevTools Detection Logic"
date: "2026-08-01"
conversation_id: "b028953c-6cb0-4f8a-9678-bf385cb8453b"
source: "antigravity"
---

# Update DevTools Detection Logic

## User

Please update /Users/matt/projects/userscript-bundler/userscripts/control-center.js:

Replace the DevTools detection section (lines 717-738):
```javascript
	function checkDevTools() {
		const widthDiff = window.outerWidth - window.innerWidth;
		const heightDiff = window.outerHeight - window.innerHeight;
		const isOpen = widthDiff > DEVTOOLS_THRESHOLD || heightDiff > DEVTOOLS_THRESHOLD;

		if (devToolsWasOpen === null) {
			// First tick: record baseline, never show toast on initial load
			devToolsWasOpen = isOpen;
			return;
		}

		if (isOpen && !devToolsWasOpen) {
			// DevTools just opened — show toast unless CC modal is already open
			if (!(shadowRoot && shadowRoot.querySelector(".overlay.open"))) {
				showToast();
			}
		}
		devToolsWasOpen = isOpen;
	}
```

With:
```javascript
	function checkDevTools() {
		const widthDiff = window.outerWidth - window.innerWidth;
		const heightDiff = window.outerHeight - window.innerHeight;
		const isOpen = widthDiff > DEVTOOLS_THRESHOLD || heightDiff > DEVTOOLS_THRESHOLD;

		if (devToolsWasOpen === null) {
			// Initial check: if DevTools is already open when page loads, show toast!
			devToolsWasOpen = isOpen;
			if (isOpen && !(shadowRoot && shadowRoot.querySelector(".overlay.open"))) {
				showToast();
			}
			return;
		}

		if (isOpen && !devToolsWasOpen) {
			// DevTools just opened — show toast unless CC modal is already open
			if (!(shadowRoot && shadowRoot.querySelector(".overlay.open"))) {
				showToast();
			}
		}
		devToolsWasOpen = isOpen;
	}
```

And update USCC_VERSION at line 11 from "2026-07-27-b" to "2026-08-01-a".

---

## Assistant

Created At: 2026-08-01T17:05:26-06:00
Completed At: 2026-08-01T17:05:26-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/projects/userscript-bundler/userscripts/control-center.js. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -8,7 +8,7 @@
 (function () {
 	"use strict";
 
-	const USCC_VERSION = "2026-07-27-b";
+	const USCC_VERSION = "2026-08-01-a";
 	console.log(
 		`%c[USCC v${USCC_VERSION}] Userscript Control Center loaded.`,
 		"color:#6366f1;font-weight:bold;font-size:12px"
@@ -719,8 +719,11 @@
 		const isOpen = widthDiff > DEVTOOLS_THRESHOLD || heightDiff > DEVTOOLS_THRESHOLD;
 
 		if (devToolsWasOpen === null) {
-			// First tick: record baseline, never show toast on initial load
+			// Initial check: if DevTools is already open when page loads, show toast!
 			devToolsWasOpen = isOpen;
+			if (isOpen && !(shadowRoot && shadowRoot.querySelector(".overlay.open"))) {
+				showToast();
+			}
 			return;
 		}
 
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-01T17:05:27-06:00
Completed At: 2026-08-01T17:05:27-06:00
Message sent to "f275218d-32af-4188-b6b1-3de294fb2a33".

The requested updates have been applied to `/Users/matt/projects/userscript-bundler/userscripts/control-center.js`:

1.  `USCC_VERSION` was updated from `"2026-07-27-b"` to `"2026-08-01-a"`.
2.  The `checkDevTools()` function was updated to trigger `showToast()` on the initial load if DevTools is already detected, provided the control center modal is not currently open.

---
