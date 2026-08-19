---
title: "Refactor Userscript Timestamp Processing"
date: "2026-08-05"
conversation_id: "0d7d4f3a-3fc5-4f3d-a82f-f19da68017f2"
source: "antigravity"
---

# Refactor Userscript Timestamp Processing

## User

In /Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js:

Modify `processEmbeddedTimestamps` to automatically strip/clean the injected system directive and timestamp/context headers from user query text elements in the DOM.

Specifically:
1. `EMBED_RE` matches timestamps like `[2026-08-05 05:03 PST-7]`.
2. The context match matches `\[context to this point is (\d+|\*)\]\s*`.
3. System directive header matches `\[SYSTEM CONTEXT & DIRECTIVES:[\s\S]*?\]\s*`.

Update `processEmbeddedTimestamps` so that when inspecting each `p.query-text-line` (or checking the full user message text), if system directives or timestamp/context headers are present:
- Store any contextAnchor if present (`\[context to this point is (\d+|\*)\]`).
- Strip `[SYSTEM CONTEXT & DIRECTIVES: ...]` (including the double newlines or trailing whitespace).
- Strip `EMBED_RE` and `[context to this point is ...]`.
- Update `p.innerText = cleanText.trim()` (or remove empty `p.query-text-line` paragraphs if cleaning leaves them empty).

Ensure the cleanText removal works robustly across single or multi-paragraph user query lines.

Here is the current function in `03-timestamps.js`:
```javascript
function processEmbeddedTimestamps() {
	const nodes = document.querySelectorAll("p.query-text-line")
	if (nodes.length === 0) return
	nodes.forEach((p, i) => {
		const raw = p.innerText || p.textContent || ""
		const match = raw.match(EMBED_RE)
		if (!match) return
		const userQuery = p.closest("user-query")
		if (!userQuery) {
			console.warn(`[GMT] [${i}] no user-query ancestor`)
			return
		}
		const container = userQuery.parentElement
		if (!container) {
			console.warn(`[GMT] [${i}] no container`)
			return
		}
		if (
			exactContainers.has(container) ||
			container.querySelector(".gm-timestamp")
		)
			return
		const unix = parseEmbeddedUnix(match[1], match[2], parseFloat(match[4]))

		const contextMatch = raw.match(/\[context to this point is (\d+|\*)\]/)
		const queryTextEl = p.closest(".query-text")
		i
<truncated 561 bytes>
```
Also handle case where `processEmbeddedTimestamps` should run even if `[SYSTEM CONTEXT & DIRECTIVES:]` is present without a timestamp on that specific node or across nodes in the same user-query element. Let's make sure any `p.query-text-line` inside `user-query` that has `[SYSTEM CONTEXT & DIRECTIVES:]` gets stripped as well!

Specifically, in `03-timestamps.js`:
```javascript
const SYSTEM_DIRECTIVE_RE = /\[SYSTEM CONTEXT & DIRECTIVES:[\s\S]*?\]\s*/

function processEmbeddedTimestamps() {
	const nodes = document.querySelectorAll("p.query-text-line")
	if (nodes.length === 0) return
	nodes.forEach((p, i) => {
		const raw = p.innerText || p.textContent || ""
		const sysMatch = raw.match(SYSTEM_DIRECTIVE_RE)
		const match = raw.match(EMBED_RE)
		if (!match && !sysMatch) return

		const userQuery = p.closest("user-query")
		if (!userQuery) {
			console.warn(`[GMT] [${i}] no user-query ancestor`)
			return
		}
		const container = userQuery.parentElement

		let cleanText = raw
		if (sysMatch) {
			cleanText = cleanText.replace(SYSTEM_DIRECTIVE_RE, "")
		}
		if (match) {
			if (container && !exactContainers.has(container) && !container.querySelector(".gm-timestamp")) {
				const unix = parseEmbeddedUnix(match[1], match[2], parseFloat(match[4]))
				exactContainers.add(container)
				injectTimestamp(container, unix, false)
			}
			const contextMatch = cleanText.match(/\[context to this point is (\d+|\*)\]/)
			const queryTextEl = p.closest(".query-text")
			if (contextMatch && queryTextEl) {
				queryTextEl.dataset.contextAnchor = contextMatch[1]
			}
			cleanText = cleanText.replace(EMBED_RE, "")
			cleanText = cleanText.replace(/\[context to this point is (\d+|\*)\]\s*/, "")
		}

		p.innerText = cleanText.trim()
	})
}
```
Check line range around lines 180 to 225 of `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js` and use `replace_file_content` to edit the file.

---

## Assistant

Created At: 2026-08-05T05:03:37-06:00
Completed At: 2026-08-05T05:03:37-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js`
Total Lines: 225
Total Bytes: 7190
Showing lines 170 to 225
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
170: 	})
171: }
172: 
173: setInterval(injectHeuristicTimes, 2000)
174: 
175: // ═══════════════════════════════════════════════════════════
176: // EMBEDDED TIMESTAMP EXTRACTION FROM USER MESSAGES
177: // ═══════════════════════════════════════════════════════════
178: 
179: function parseEmbeddedUnix(dateStr, timeStr, offsetHours) {
180: 	const ms = new Date(`${dateStr}T${timeStr}:00Z`).getTime()
181: 	return Math.floor((ms - offsetHours * 3600000) / 1000)
182: }
183: 
184: function processEmbeddedTimestamps() {
185: 	const nodes = document.querySelectorAll("p.query-text-line")
186: 	if (nodes.length === 0) return
187: 	nodes.forEach((p, i) => {
188: 		const raw = p.innerText || p.textContent || ""
189: 		const match = raw.match(EMBED_RE)
190: 		if (!match) return
191: 		const userQuery = p.closest("user-query")
192: 		if (!userQuery) {
193: 			console.warn(`[GMT] [${i}] no user-query ancestor`)
194: 			return
195: 		}
196: 		const container = userQuery.parentElement
197: 		if (!container) {
198: 			console.warn(`[GMT] [${i}] no container`)
199: 			return
200: 		}
201: 		if (
202: 			exactContainers.has(container) ||
203: 			container.querySelector(".gm-timestamp")
204: 		)
205: 			return
206: 		const unix = parseEmbeddedUnix(match[1], match[2], parseFloat(match[4]))
207: 
208: 		const contextMatch = raw.match(/\[context to this point is (\d+|\*)\]/)
209: 		const queryTextEl = p.closest(".query-text")
210: 		if (contextMatch && queryTextEl) {
211: 			queryTextEl.dataset.contextAnchor = contextMatch[1]
212: 		}
213: 
214: 		let cleanText = raw.replace(EMBED_RE, "")
215: 		cleanText = cleanText.replace(
216: 			/\[context to this point is (\d+|\*)\]\s*/,
217: 			"",
218: 		)
219: 		p.innerText = cleanText.trim()
220: 
221: 		exactContainers.add(container)
222: 		injectTimestamp(container, unix, false)
223: 	})
224: }
225: 
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-05T05:03:37-06:00
Completed At: 2026-08-05T05:03:37-06:00
{"File":"/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js","LineNumber":5,"LineContent":"const EMBED_RE ="}

Created At: 2026-08-05T05:03:38-06:00
Completed At: 2026-08-05T05:03:38-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js`
Total Lines: 225
Total Bytes: 7190
Showing lines 1 to 10
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: // ═══════════════════════════════════════════════════════════
2: // EMBED REGEX + MESSAGE TIMESTAMP STATE
3: // ═══════════════════════════════════════════════════════════
4: 
5: const EMBED_RE =
6: 	/^\s*\[(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}) ([A-Z]{2,5})([+-]\d+(?:\.\d+)?)\]\s*/
7: const idToTimeMap = new Map()
8: const exactContainers = new WeakSet()
9: 
10: function buildMessageDisplay(unix, isEstimate) {
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

---
