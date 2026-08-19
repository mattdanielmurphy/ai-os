---
title: "Update Userscript Shortcut Functionality"
date: "2026-08-01"
conversation_id: "35310eca-c86a-4a4e-bcb5-3da5ab9544ca"
source: "antigravity"
---

# Update Userscript Shortcut Functionality

## User

Please update /Users/matt/projects/userscript-bundler/userscripts/control-center.js:

1. Update `USCC_VERSION` at line 11 to `"2026-08-01-e"`.
2. Re-instantiate `showToast()` and keep the trigger pill as well.
3. Add capture-phase event listeners for `keydown` and `keyup` specifically targeting `Cmd+Option+I` (`e.metaKey && e.altKey && (e.code === 'KeyI' || e.key.toLowerCase() === 'i')`), `Cmd+Option+J`, `Cmd+Option+C`, and `F12`.

Add the following event handler logic to the bottom of `control-center.js`:

```javascript
	// ── Piggyback on Cmd+Option+I / Cmd+Option+J / Cmd+Option+C / F12 ───────────
	let lastShortcutTrigger = 0;

	function handleDevToolsShortcut(e) {
		const isCmdAltI = e.metaKey && e.altKey && (e.code === "KeyI" || e.key.toLowerCase() === "i");
		const isCmdAltJ = e.metaKey && e.altKey && (e.code === "KeyJ" || e.key.toLowerCase() === "j");
		const isCmdAltC = e.metaKey && e.altKey && (e.code === "KeyC" || e.key.toLowerCase() === "c");
		const isF12 = e.key === "F12";

		if (isCmdAltI || isCmdAltJ || isCmdAltC || isF12) {
			const now = Date.now();
			if (now - lastShortcutTrigger > 300) {
				lastShortcutTrigger = now;
				if (!(shadowRoot && shadowRoot.querySelector(".overlay.open"))) {
					showToast();
				}
			}
		}
	}

	window.addEventListener("keydown", handleDevToolsShortcut, { capture: true, passive: true });
	window.addEventListener("keyup", handleDevToolsShortcut, { capture: true, passive: true });
```

---

## Assistant

Created At: 2026-08-01T17:15:50-06:00
Completed At: 2026-08-01T17:15:50-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/control-center.js`
Total Lines: 758
Total Bytes: 24305
Showing lines 1 to 758
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
11: 	const USCC_VERSION = "2026-08-01-d";
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
<truncated 24443 bytes>
"uscc-trigger-pill")) return;
712: 		const pill = document.createElement("div");
713: 		pill.id = "uscc-trigger-pill";
714: 		pill.textContent = "⚙️ Control Center";
715: 		Object.assign(pill.style, {
716: 			position: "fixed", bottom: "20px", right: "20px",
717: 			background: "#1e1e2e", color: "#a6adc8",
718: 			border: "1px solid #313244", borderRadius: "20px",
719: 			padding: "6px 12px", fontSize: "12px", fontFamily: "sans-serif",
720: 			cursor: "pointer", zIndex: "2147483646",
721: 			boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
722: 			userSelect: "none", opacity: "0.7",
723: 			transition: "opacity 0.2s ease, border-color 0.2s ease, transform 0.2s ease",
724: 		});
725: 
726: 		pill.onmouseenter = () => { pill.style.opacity = "1"; pill.style.borderColor = "#6366f1"; };
727: 		pill.onmouseleave = () => { pill.style.opacity = "0.7"; pill.style.borderColor = "#313244"; };
728: 		pill.onclick = () => openUI();
729: 
730: 		document.body ? document.body.appendChild(pill) : window.addEventListener("DOMContentLoaded", () => document.body.appendChild(pill));
731: 	}
732: 
733: 	if (document.readyState === "loading") {
734: 		window.addEventListener("DOMContentLoaded", createTriggerPill);
735: 	} else {
736: 		createTriggerPill();
737: 	}
738: 
739: 	// Alt+I = manual keyboard trigger
740: 	window.addEventListener("keydown", (e) => {
741: 		if (e.altKey && !e.metaKey && !e.ctrlKey && (e.key === "i" || e.key === "I")) {
742: 			if (shadowRoot && shadowRoot.querySelector(".overlay.open")) {
743: 				closeUI();
744: 			} else {
745: 				openUI();
746: 			}
747: 		}
748: 		if (e.key === "Escape" && shadowRoot && shadowRoot.querySelector(".overlay.open")) {
749: 			closeUI();
750: 		}
751: 	}, { capture: true });
752: 
753: 	// Expose globally for dispatcher invocation if needed
754: 	window.__USCC_OPEN__ = openUI;
755: 	window.__USCC_VERSION__ = USCC_VERSION;
756:     console.log(`USCC Initialized (v${USCC_VERSION})`);
757: })();
758: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-01T17:15:52-06:00
Completed At: 2026-08-01T17:15:52-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/projects/userscript-bundler/userscripts/control-center.js. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -8,7 +8,7 @@
 (function () {
 	"use strict";
 
-	const USCC_VERSION = "2026-08-01-d";
+	const USCC_VERSION = "2026-08-01-e";
 	console.log(
 		`%c[USCC v${USCC_VERSION}] Userscript Control Center loaded.`,
 		"color:#6366f1;font-weight:bold;font-size:12px"
@@ -753,5 +753,28 @@
 	window.__USCC_OPEN__ = openUI;
 	window.__USCC_VERSION__ = USCC_VERSION;
     console.log(`USCC Initialized (v${USCC_VERSION})`);
+
+	// ── Piggyback on Cmd+Option+I / Cmd+Option+J / Cmd+Option+C / F12 ───────────
+	let lastShortcutTrigger = 0;
+
+	function handleDevToolsShortcut(e) {
+		const isCmdAltI = e.metaKey && e.altKey && (e.code === "KeyI" || e.key.toLowerCase() === "i");
+		const isCmdAltJ = e.metaKey && e.altKey && (e.code === "KeyJ" || e.key.toLowerCase() === "j");
+		const isCmdAltC = e.metaKey && e.altKey && (e.code === "KeyC" || e.key.toLowerCase() === "c");
+		const isF12 = e.key === "F12";
+
+		if (isCmdAltI || isCmdAltJ || isCmdAltC || isF12) {
+			const now = Date.now();
+			if (now - lastShortcutTrigger > 300) {
+				lastShortcutTrigger = now;
+				if (!(shadowRoot && shadowRoot.querySelector(".overlay.open"))) {
+					showToast();
+				}
+			}
+		}
+	}
+
+	window.addEventListener("keydown", handleDevToolsShortcut, { capture: true, passive: true });
+	window.addEventListener("keyup", handleDevToolsShortcut, { capture: true, passive: true });
 })();
 
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-01T17:15:54-06:00
Completed At: 2026-08-01T17:15:54-06:00
Message sent to "f275218d-32af-4188-b6b1-3de294fb2a33".

The requested updates to `/Users/matt/projects/userscript-bundler/userscripts/control-center.js` have been completed successfully.

**Summary of changes:**
*   Updated `USCC_VERSION` to `"2026-08-01-e"`.
*   Retained the existing `showToast()` and trigger pill functionality.
*   Added capture-phase `keydown` and `keyup` event listeners for `Cmd+Option+I`, `Cmd+Option+J`, `Cmd+Option+C`, and `F12` with a 300ms throttling mechanism to trigger the toast notification when DevTools shortcuts are used.

---
