---
title: "Update Gemini Table Styling"
date: "2026-08-09"
conversation_id: "c9a5c730-3573-41f9-8251-44b656222821"
source: "antigravity"
---

# Update Gemini Table Styling

## User

In `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js`, replace:

```javascript
    /* Full-width and Compact Table Layout dynamically accounting for Gemini sidebar */
    .horizontal-scroll-wrapper {
        width: calc(100vw - var(--mat-sidenav-content-left-margin, 280px)) !important;
        max-width: calc(100vw - var(--mat-sidenav-content-left-margin, 280px)) !important;
        position: relative !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        box-sizing: border-box !important;
        padding: 0 48px !important;
        display: block !important;
        overflow-x: auto !important;
    }
    .table-block-component, .table-block, .table-content {
        width: auto !important;
        max-width: 100% !important;
    }
    table {
        width: auto !important;
        max-width: 100% !important;
        border-collapse: collapse !important;
        table-layout: auto !important;
    }
    table th, table td {
        padding: 8px 12px !important;
        white-space: normal !important;
        word-break: break-word !important;
        width: auto !important;
        min-width: 0 !important;
    }
    
    /* Responsive adjustments for narrower viewports */
    @media (max-width: 1400px) {
        table th, table td {
            padding: 6px 10px !important;
            font-size: 14px !important;
        }
    }
```

with:

```javascript
    /* Centered Table & Responsive Breakout Layout */
    .horizontal-scroll-wrapper {
        width: 100% !important;
        max-width: 100% !important;
        position: relative !important;
        box-sizing: border-box !important;
        display: flex !important;
        justify-content: center !important;
        overflow-x: auto !important;
        margin: 16px 0 !important;
    }

    @media (min-width: 1024px) {
        .horizontal-scroll-wrapper {
            width: calc(100vw - var(--mat-sidenav-content-left-margin, 280px)) !important;
            max-width: calc(100vw - var(--mat-sidenav-content-left-margin, 280px)) !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            padding: 0 48px !important;
        }
    }

    .table-block-component, .table-block, .table-content {
        width: auto !important;
        max-width: 100% !important;
        margin: 0 auto !important;
    }

    table {
        width: auto !important;
        max-width: none !important;
        margin: 0 auto !important;
        border-collapse: collapse !important;
        table-layout: auto !important;
    }

    table th, table td {
        padding: 8px 12px !important;
        white-space: normal !important;
        overflow-wrap: break-word !important;
        word-break: normal !important;
        width: auto !important;
        min-width: 120px !important;
    }

    /* Responsive adjustments for narrower viewports */
    @media (max-width: 1400px) {
        table th, table td {
            padding: 6px 10px !important;
            font-size: 14px !important;
            min-width: 100px !important;
        }
    }
```

Use replace_file_content tool.

---

## Assistant

Created At: 2026-08-09T02:44:04-06:00
Completed At: 2026-08-09T02:44:04-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js`
Total Lines: 1308
Total Bytes: 45286
Showing lines 1 to 800
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: // ═══════════════════════════════════════════════════════════
2: // PROMPT TIMESTAMP PREPEND & PROMPT TOOLS UI
3: // ═══════════════════════════════════════════════════════════
4: 
5: function getNowTimestamp() {
6: 	const now = new Date()
7: 	const date = now.toLocaleDateString("en-CA")
8: 	const hh = String(now.getHours()).padStart(2, "0")
9: 	const mm = String(now.getMinutes()).padStart(2, "0")
10: 	const tz = getLocalTzAbbr()
11: 	const off = getLocalTzOffsetHours()
12: 	return `[${date} ${hh}:${mm} ${tz}${off >= 0 ? "+" + off : off}]`
13: }
14: 
15: function getSendButton(target) {
16: 	if (!target) return null
17: 	const btn = target.closest("button")
18: 	if (!btn) return null
19: 	const ariaLabel = (btn.getAttribute("aria-label") || "").toLowerCase()
20: 	const title = (btn.getAttribute("title") || "").toLowerCase()
21: 	const dataTestId = (
22: 		btn.getAttribute("data-test-id") ||
23: 		btn.getAttribute("data-testid") ||
24: 		""
25: 	).toLowerCase()
26: 	const hasSendClass = Array.from(btn.classList).some(
27: 		(c) =>
28: 			c.toLowerCase().includes("send") || c.toLowerCase().includes("submit"),
29: 	)
30: 
31: 	if (
32: 		ariaLabel.includes("send") ||
33: 		ariaLabel.includes("submit") ||
34: 		title.includes("send") ||
35: 		title.includes("submit") ||
36: 		dataTestId.includes("sen
<truncated 29856 bytes>
", "14")
745: 		planSvg.setAttribute("height", "14")
746: 		planSvg.setAttribute("viewBox", "0 0 24 24")
747: 		planSvg.setAttribute("fill", "none")
748: 		planSvg.setAttribute("stroke", "currentColor")
749: 		planSvg.setAttribute("stroke-width", "2")
750: 		planSvg.setAttribute("stroke-linecap", "round")
751: 		planSvg.setAttribute("stroke-linejoin", "round")
752: 		planSvg.style.marginRight = "4px"
753: 		planSvg.style.verticalAlign = "-2px"
754: 
755: 		const planPath = document.createElementNS(
756: 			"http://www.w3.org/2000/svg",
757: 			"path",
758: 		)
759: 		planPath.setAttribute(
760: 			"d",
761: 			"M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z",
762: 		)
763: 
764: 		const planPoly1 = document.createElementNS(
765: 			"http://www.w3.org/2000/svg",
766: 			"polyline",
767: 		)
768: 		planPoly1.setAttribute("points", "14 2 14 8 20 8")
769: 
770: 		const planLine1 = document.createElementNS(
771: 			"http://www.w3.org/2000/svg",
772: 			"line",
773: 		)
774: 		planLine1.setAttribute("x1", "16")
775: 		planLine1.setAttribute("y1", "13")
776: 		planLine1.setAttribute("x2", "8")
777: 		planLine1.setAttribute("y2", "13")
778: 
779: 		const planLine2 = document.createElementNS(
780: 			"http://www.w3.org/2000/svg",
781: 			"line",
782: 		)
783: 		planLine2.setAttribute("x1", "16")
784: 		planLine2.setAttribute("y1", "17")
785: 		planLine2.setAttribute("x2", "8")
786: 		planLine2.setAttribute("y2", "17")
787: 
788: 		const planPoly2 = document.createElementNS(
789: 			"http://www.w3.org/2000/svg",
790: 			"polyline",
791: 		)
792: 		planPoly2.setAttribute("points", "10 9 9 9 8 9")
793: 
794: 		planSvg.appendChild(planPath)
795: 		planSvg.appendChild(planPoly1)
796: 		planSvg.appendChild(planLine1)
797: 		planSvg.appendChild(planLine2)
798: 		planSvg.appendChild(planPoly2)
799: 
800: 		btnSpan.appendChild(planSvg)
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-09T02:44:05-06:00
Completed At: 2026-08-09T02:44:05-06:00
{"File":"/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js","LineNumber":533,"LineContent":"    /* Centered Table \u0026 Responsive Breakout Layout */"}

---
