---
title: "Remove System Directive Context"
date: "2026-08-05"
conversation_id: "f23d177a-b263-4944-b215-97939ff6801d"
source: "antigravity"
---

# Remove System Directive Context

## User

@[gemini-enhancements] we have to remove the system directive and all the other injected context automatically from the user message field like is done for the timestamps.

---

## Assistant

Created At: 2026-08-05T05:03:11-06:00
Completed At: 2026-08-05T05:03:11-06:00
{"name":"00-bootstrap.js","sizeBytes":"888"}
{"name":"01-shared.js","sizeBytes":"3538"}
{"name":"02-token-usage.js","sizeBytes":"13125"}
{"name":"03-timestamps.js","sizeBytes":"7190"}
{"name":"04-sidebar-dates.js","sizeBytes":"8434"}
{"name":"05-prompt-tools.js","sizeBytes":"42972"}
{"name":"06-archive.js","sizeBytes":"6438"}
{"name":"07-terminal.js","sizeBytes":"18774"}
{"name":"08-model-optimizer.js","sizeBytes":"9936"}
{"name":"09-page-observer.js","sizeBytes":"5117"}
{"name":"10-tool-calls.js","sizeBytes":"20983"}

Summary: This directory contains 0 subdirectories and 11 files.

Created At: 2026-08-05T05:03:12-06:00
Completed At: 2026-08-05T05:03:12-06:00
{"File":"/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/01-shared.js"}
{"File":"/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/02-token-usage.js"}
{"File":"/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js"}
{"File":"/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js"}
{"File":"/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/06-archive.js"}

Created At: 2026-08-05T05:03:13-06:00
Completed At: 2026-08-05T05:03:13-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js`
Total Lines: 225
Total Bytes: 7190
Showing lines 1 to 200
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
11: 	const rel = getRelativeDateLabel(unix, false)
12: 	const time = formatTime(new Date(unix * 1000))
13: 	const prefix = isEstimate ? "~ " : ""
14: 	return rel === null ? `${prefix}${time}` : `${prefix}${rel}, ${time}`
15: }
16: 
17: function injectTimestamp(container, unix, isEstimate) {
18: 	if (container.querySelector(".gm-timestamp")) return
19: 	const stamp = document.createElement("span")
20: 	stamp.className = "gm-timestamp"
21: 	stamp.innerText = buildMessageDisplay(unix, isEstimate)
22: 	stamp.setAttribute(
23: 		"data-timestamp",
24: 		formatAbsoluteTime(new Date(unix * 1000)),
25: 	)
26: 	stamp.style.cssText = `
27:       font-size: 1rem;
28:       color: #555;
29:       font-family: ${FONT};
30:       width: 100%;
31:       margin-bottom: 8px;
32:       display: block;
33:       text-align: right;
34:     `
35: 	attachTooltip(stamp, () => formatFullDateTime(new Date(unix * 1000)))
36:
<truncated 4013 bytes>
")
151: 		) {
152: 			el = null
153: 		}
154: 		if (el && !el.querySelector(".gm-timestamp") && !exactContainers.has(el))
155: 			pending.push({ container: el, unix })
156: 	})
157: 	pending.sort((a, b) =>
158: 		(
159: 			a.container.compareDocumentPosition(b.container) &
160: 			Node.DOCUMENT_POSITION_FOLLOWING
161: 		) ?
162: 			-1
163: 		:	1,
164: 	)
165: 	let floor = 0
166: 	pending.forEach(({ container, unix }) => {
167: 		const clamped = Math.max(unix, floor)
168: 		floor = clamped
169: 		injectTimestamp(container, clamped, true)
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
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-05T05:03:13-06:00
Completed At: 2026-08-05T05:03:13-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js`
Total Lines: 225
Total Bytes: 7190
Showing lines 180 to 225
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
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

Created At: 2026-08-05T05:03:14-06:00
Completed At: 2026-08-05T05:03:14-06:00
{"File":"/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/02-token-usage.js"}
{"File":"/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js"}
{"File":"/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js"}

Created At: 2026-08-05T05:03:15-06:00
Completed At: 2026-08-05T05:03:15-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js`
Total Lines: 1235
Total Bytes: 42972
Showing lines 1 to 150
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
<truncated 4044 bytes>
 		replaceEditorContent(editor, newText)
94: 	}
95: }
96: 
97: let isPrependingPrompt = false
98: 
99: function hasAlreadyPrepended(text) {
100: 	if (!text) return false
101: 	return (
102: 		text.includes("[SYSTEM CONTEXT & DIRECTIVES:") ||
103: 		text.includes("[context to this point is") ||
104: 		EMBED_RE.test(text)
105: 	)
106: }
107: 
108: document.addEventListener(
109: 	"click",
110: 	function (e) {
111: 		if (e.isTrusted === false) return
112: 		if (isPrependingPrompt) return
113: 
114: 		const btn = getSendButton(e.target)
115: 		if (!btn) return
116: 		const editor = document.querySelector(
117: 			'.ql-editor[contenteditable="true"]',
118: 		)
119: 		if (!editor) return
120: 
121: 		// Avoid the read-replace cycle that can double newlines in contenteditable
122: 		let currentText = editor.innerText || ""
123: 		if (!currentText.trim() || hasAlreadyPrepended(currentText)) return
124: 
125: 		isPrependingPrompt = true
126: 		setTimeout(() => {
127: 			isPrependingPrompt = false
128: 		}, 500)
129: 
130: 		e.stopImmediatePropagation()
131: 		e.preventDefault()
132: 
133: 		// Run decoy/replacement substitution
134: 		processCommandReplacement(editor)
135: 
136: 		// Prepend timestamp by moving cursor to start and inserting text
137: 		editor.focus()
138: 		const sel = window.getSelection()
139: 		const range = document.createRange()
140: 		range.setStart(editor, 0)
141: 		range.collapse(true)
142: 		sel.removeAllRanges()
143: 		sel.addRange(range)
144: 
145: 		const tokenUsage = calculateThreadTokens()
146: 		const tokenStr = tokenUsage.isPrecise ? tokenUsage.total : "*"
147: 		const timestamp = `${getNowTimestamp()} [context to this point is ${tokenStr}] `
148: 
149: 		// Dynamic New Thread Instruction Injection
150: 		const userMessages = document.querySelectorAll("user-query, .user-query, [data-test-id='user-query']")
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-05T05:03:16-06:00
Completed At: 2026-08-05T05:03:16-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js`
Total Lines: 1235
Total Bytes: 42972
Showing lines 150 to 250
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
150: 		const userMessages = document.querySelectorAll("user-query, .user-query, [data-test-id='user-query']")
151: 		const isNewThread = userMessages.length === 0
152: 
153: 		let systemPrefix = ""
154: 		if (isNewThread) {
155: 			systemPrefix = `[SYSTEM CONTEXT & DIRECTIVES:
156: 1. Primary User Vault: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/
157: 2. Strict Media & Story Spoilers Directive: STRICT NO SPOILERS POLICY. You MUST NOT under any circumstances reveal plot twists, endings, key character fates, deaths, betrayals, secret identities, major narrative developments, or unreleased details for movies, TV shows, books, anime, games, or story-driven media. If asked about media, err heavily on the side of caution. Give zero hints or foreshadowing of major events unless the user explicitly requests spoilers with confirmation.
158: 3. Tone, Sycophancy & Banned Buzzwords: No sycophantic praise or routine filler ("that's very insightful", "great question", "I understand..."). NEVER use banned buzzwords: "glitch in the matrix", "nuclear option", "final boss", "game changer", "level up", "cheat code", "you've hit on", "unlocking the potential".
159: 4. Tool Call Directive: You can output JSON tool calls inside a \`\`\`tool_call codeblock. Schema: {"tool":"save_note","run_automatically":true,"args":{"title":"...","content":"..."}}. Set "run_automatically": true ONLY if the tool should execute immediately without user confirmation (e.g. proactive note-taking). Set to false if it's a suggested action for
<truncated 3024 bytes>
s, books, anime, games, or story-driven media. If asked about media, err heavily on the side of caution. Give zero hints or foreshadowing of major events unless the user explicitly requests spoilers with confirmation.
230: 3. Tone, Sycophancy & Banned Buzzwords: No sycophantic praise or routine filler ("that's very insightful", "great question", "I understand..."). NEVER use banned buzzwords: "glitch in the matrix", "nuclear option", "final boss", "game changer", "level up", "cheat code", "you've hit on", "unlocking the potential".
231: 4. Tool Call Directive: You can output JSON tool calls inside a \`\`\`tool_call codeblock. Schema: {"tool":"save_note","run_automatically":true,"args":{"title":"...","content":"..."}}. Set "run_automatically": true ONLY if the tool should execute immediately without user confirmation (e.g. proactive note-taking). Set to false if it's a suggested action for the user to trigger manually.
232: 5. Fact-Checking Directive: When asked to verify/fact-check claims, perform Information Sufficiency Check, Source & Context Audit, and define Explicit Assumptions & Boundaries.
233: 6. Local Environment & Tooling Rules: Default JS package manager is Bun (never npm/pnpm). Use ./tmp for local script files. Safe file removal via mv ~/.Trash/ (never rm).
234: 7. No YouTube links in responses.]\n\n`
235: 		}
236: 
237: 		document.execCommand("insertText", false, systemPrefix + timestamp)
238: 		console.log(`[GMT] keydown prepended (isNewThread=${isNewThread}): "${systemPrefix + timestamp}"`)
239: 
240: 		// Dispatch enter key to trigger angular submission
241: 		setTimeout(() => {
242: 			const event = new KeyboardEvent("keydown", {
243: 				key: "Enter",
244: 				code: "Enter",
245: 				keyCode: 13,
246: 				which: 13,
247: 				bubbles: true,
248: 				cancelable: true,
249: 			})
250: 			editor.dispatchEvent(event)
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-05T05:03:16-06:00
Completed At: 2026-08-05T05:03:16-06:00
{"File":"/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js"}
{"File":"/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/09-page-observer.js"}

Created At: 2026-08-05T05:03:31-06:00
Completed At: 2026-08-05T05:03:31-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/09-page-observer.js`
Total Lines: 197
Total Bytes: 5117
Showing lines 1 to 197
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: // ═══════════════════════════════════════════════════════════
2: // PAGE OBSERVERS & TOP-LEVEL ORCHESTRATION
3: // ═══════════════════════════════════════════════════════════
4: 
5: function updateTabTitle() {
6: 	const titleEl = document.querySelector(
7: 		'[data-test-id="conversation-title"]',
8: 	)
9: 	if (titleEl) {
10: 		const newTitle = titleEl.innerText.trim()
11: 		if (newTitle && document.title !== newTitle) {
12: 			document.title = newTitle
13: 		}
14: 	}
15: }
16: 
17: function removeAdvUpsell(warnIfMissing = false) {
18: 	const upsellContainer = document.querySelector(
19: 		".right-section > .buttons-container.adv-upsell",
20: 	)
21: 	if (upsellContainer) {
22: 		upsellContainer.remove()
23: 	}
24: }
25: 
26: let lastSidebarClickTime = 0
27: function ensureSidebarOpen() {
28: 	const now = Date.now()
29: 	if (now - lastSidebarClickTime < 3000) return
30: 	const openButton = document.querySelector(
31: 		'button.side-nav-sparkle-button[aria-label="Open sidebar"]',
32: 	)
33: 	if (openButton && openButton.offsetParent !== null) {
34: 		lastSidebarClickTime = now
35: 		openButton.click()
36: 		console.log("[GMT] Sidebar persistence: Sidebar was closed. Opening it now.")
37: 	}
38: }
39: 
40: let lastUrl = location.href
41: 
42: let syncTimeout = null
43: let observerTimeout = null
44: f
<truncated 2471 bytes>
						) {
123: 							shouldExport = true
124: 							break
125: 						}
126: 					}
127: 				}
128: 				if (shouldExport) break
129: 			}
130: 		}
131: 
132: 		if (shouldExport && autoThreadSync) {
133: 			if (syncTimeout) clearTimeout(syncTimeout)
134: 
135: 			const isCurrentlyGenerating = () => {
136: 				const stopButton = document.querySelector(
137: 					'button[aria-label*="Stop"], button[aria-label*="stop"]',
138: 				)
139: 				if (stopButton) {
140: 					const label = stopButton.getAttribute("aria-label") || ""
141: 					if (
142: 						/stop/i.test(label) &&
143: 						(/generat/i.test(label) ||
144: 							/respons/i.test(label) ||
145: 							/stream/i.test(label))
146: 					) {
147: 						return true
148: 					}
149: 				}
150: 				const msgElements = document.querySelectorAll(
151: 					"user-query, model-response",
152: 				)
153: 				if (msgElements.length > 0) {
154: 					const lastMsg = msgElements[msgElements.length - 1]
155: 					if (lastMsg.tagName.toLowerCase() === "user-query") {
156: 						return true
157: 					}
158: 				}
159: 				return false
160: 			}
161: 
162: 			if (!isCurrentlyGenerating()) {
163: 				syncTimeout = setTimeout(() => {
164: 					exportThreadWithTimestamps()
165: 				}, 3000)
166: 			}
167: 		}
168: 	}).observe(document.body, {
169: 		childList: true,
170: 		subtree: true,
171: 		characterData: true,
172: 	})
173: 
174: 	processEmbeddedTimestamps()
175: 	updateSidebarDOM()
176: 	updateTabTitle()
177: 	removeAdvUpsell(true)
178: 
179: 	// Initial AI-OS integrations
180: 	injectUI()
181: 	scanExecutionPayloads()
182: 	injectRunButtons()
183: 	if (typeof window.scanToolCalls === "function") window.scanToolCalls()
184: 	setTimeout(() => {
185: 		if (autoThreadSync) {
186: 			exportThreadWithTimestamps()
187: 		}
188: 	}, 1500)
189: 
190: 	console.log("[GMT] observers started")
191: }
192: 
193: startObservers()
194: 
195: // Close the outer IIFE started in 00-bootstrap.js
196: })();
197: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-05T05:03:33-06:00
Completed At: 2026-08-05T05:03:33-06:00
Subagent "file_editor" defined successfully. It can now be invoked via invoke_subagent.

Created At: 2026-08-05T05:03:36-06:00
Completed At: 2026-08-05T05:03:36-06:00
Created the following subagents:
{
  "conversationId": "0d7d4f3a-3fc5-4f3d-a82f-f19da68017f2",
  "logAbsoluteUri": "file:///Users/matt/.gemini/antigravity/brain/0d7d4f3a-3fc5-4f3d-a82f-f19da68017f2/.system_generated/logs/transcript.jsonl",
  "workspaceUris": [
    "file:///Users/matt/projects/userscript-bundler",
    "file:///Users/matt/projects/userscript-bundler/userscripts"
  ]
}
The subagents will send you a message when they have completed their task or require guidance. There is no need to poll for their responses.

Created At: 2026-08-05T05:03:36-06:00
Completed At: 2026-08-05T05:03:36-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js`
Total Lines: 225
Total Bytes: 7190
Showing lines 180 to 225
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
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

Created At: 2026-08-05T05:03:38-06:00
Completed At: 2026-08-05T05:03:38-06:00
Created the following subagents:
{
  "conversationId": "c7111f01-96a8-4400-bc39-e352018192e2",
  "logAbsoluteUri": "file:///Users/matt/.gemini/antigravity/brain/c7111f01-96a8-4400-bc39-e352018192e2/.system_generated/logs/transcript.jsonl",
  "workspaceUris": [
    "file:///Users/matt/projects/userscript-bundler",
    "file:///Users/matt/projects/userscript-bundler/userscripts"
  ]
}
The subagents will send you a message when they have completed their task or require guidance. There is no need to poll for their responses.

Created At: 2026-08-05T05:03:38-06:00
Completed At: 2026-08-05T05:03:39-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js`
Total Lines: 225
Total Bytes: 7190
Showing lines 180 to 225
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
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

Created At: 2026-08-05T05:03:39-06:00
Completed At: 2026-08-05T05:03:39-06:00
You have 2 active subagent(s):
{
  "spec": {
    "typeName": "file_editor",
    "role": "File Editor",
    "initialPrompt": "In /Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js:\n\nModify `processEmbeddedTimestamps` to automatically strip/clean the injected system directive and timestamp/context headers from user query text elements in the DOM.\n\nSpecifically:\n1. `EMBED_RE` matches timestamps like `[2026-08-05 05:03 PST-7]`.\n2. The context match matches `\\[context to this point is (\\d+|\\*)\\]\\s*`.\n3. System directive header matches `\\[SYSTEM CONTEXT & DIRECTIVES:[\\s\\S]*?\\]\\s*`.\n\nUpdate `processEmbeddedTimestamps` so that when inspecting each `p.query-text-line` (or checking the full user message text), if system directives or timestamp/context headers are present:\n- Store any contextAnchor if present (`\\[context to this point is (\\d+|\\*)\\]`).\n- Strip `[SYSTEM CONTEXT & DIRECTIVES: ...]` (including the double newlines or trailing whitespace).\n- Strip `EMBED_RE` and `[context to this point is ...]`.\n- Update `p.innerText = cleanText.trim()` (or remove empty `p.query-text-line` paragraphs if cleaning leaves them empty).\n\nEnsure the cleanText removal works robustly across single or multi-paragraph user query lines.\n\nHere is the current function in `03-timestamps.js`:\n```javascript\nfunction processEmbeddedTimestamps() {\n\tconst nodes = document.querySelectorAll(\"p.query-text-line\")\n\tif (nodes.length === 0) return\n\tnodes.forEach((p, i) => {\n\t\tconst raw = p.innerText || p.textContent || \"\"\n\t\tconst match = raw.match(EMBED_RE)\n\t\tif (!match) return\n\t\tconst userQuery = p.closest(\"user-query\")\n\t\tif (!userQuery) {\n\t\t\tconsole.warn(`[GMT] [${i}] no user-query ancestor`)\n\t\t\treturn\n\t\t}\n\t\tconst container = userQuery.parentElement\n\t\tif (!container) {\n\t\t\tconsole.warn(`[GMT] [${i}] no container`)\n\t\t\treturn\n\t\t}\n\t\tif (\n\t\t\texactCont
<truncated 4047 bytes>
 0) return\n\tnodes.forEach((p, i) => {\n\t\tconst raw = p.innerText || p.textContent || \"\"\n\t\tconst sysMatch = raw.match(SYSTEM_DIRECTIVE_RE)\n\t\tconst match = raw.match(EMBED_RE)\n\t\tif (!match && !sysMatch) return\n\n\t\tconst userQuery = p.closest(\"user-query\")\n\t\tif (!userQuery) {\n\t\t\tconsole.warn(`[GMT] [${i}] no user-query ancestor`)\n\t\t\treturn\n\t\t}\n\t\tconst container = userQuery.parentElement\n\n\t\tlet cleanText = raw\n\t\tif (sysMatch) {\n\t\t\tcleanText = cleanText.replace(SYSTEM_DIRECTIVE_RE, \"\")\n\t\t}\n\t\tif (match) {\n\t\t\tif (\n\t\t\t\tcontainer &&\n\t\t\t\t!exactContainers.has(container) &&\n\t\t\t\t!container.querySelector(\".gm-timestamp\")\n\t\t\t) {\n\t\t\t\tconst unix = parseEmbeddedUnix(\n\t\t\t\t\tmatch[1],\n\t\t\t\t\tmatch[2],\n\t\t\t\t\tparseFloat(match[4]),\n\t\t\t\t)\n\t\t\t\texactContainers.add(container)\n\t\t\t\tinjectTimestamp(container, unix, false)\n\t\t\t}\n\t\t\tconst contextMatch = cleanText.match(\n\t\t\t\t/\\[context to this point is (\\d+|\\*)\\]/,\n\t\t\t)\n\t\t\tconst queryTextEl = p.closest(\".query-text\")\n\t\t\tif (contextMatch && queryTextEl) {\n\t\t\t\tqueryTextEl.dataset.contextAnchor = contextMatch[1]\n\t\t\t}\n\t\t\tcleanText = cleanText.replace(EMBED_RE, \"\")\n\t\t\tcleanText = cleanText.replace(\n\t\t\t\t/\\[context to this point is (\\d+|\\*)\\]\\s*/,\n\t\t\t\t\"\",\n\t\t\t)\n\t\t}\n\n\t\tp.innerText = cleanText.trim()\n\t})\n}\n```\n\nMake the change in `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js` immediately.",
    "inherit": true,
    "model": "MODEL_PLACEHOLDER_M50",
    "modelTier": "MODEL_TIER_FLASH_LITE"
  },
  "result": {
    "conversationId": "c7111f01-96a8-4400-bc39-e352018192e2",
    "logAbsoluteUri": "file:///Users/matt/.gemini/antigravity/brain/c7111f01-96a8-4400-bc39-e352018192e2/.system_generated/logs/transcript.jsonl",
    "workspaceUris": [
      "file:///Users/matt/projects/userscript-bundler",
      "file:///Users/matt/projects/userscript-bundler/userscripts"
    ]
  }
}

Created At: 2026-08-05T05:03:40-06:00
Completed At: 2026-08-05T05:03:40-06:00
Successfully killed 2 subagent(s) and their descendants.
Killed roles: File Editor, File Editor

Created At: 2026-08-05T05:03:41-06:00
Completed At: 2026-08-05T05:03:41-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js`
Total Lines: 225
Total Bytes: 7190
Showing lines 180 to 225
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
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

Created At: 2026-08-05T05:03:43-06:00
Completed At: 2026-08-05T05:03:43-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -181,6 +181,8 @@
 	return Math.floor((ms - offsetHours * 3600000) / 1000)
 }
 
+const SYSTEM_DIRECTIVE_RE = /\[SYSTEM CONTEXT & DIRECTIVES:[\s\S]*?\]\s*/
+
 function processEmbeddedTimestamps() {
 	const nodes = document.querySelectorAll("p.query-text-line")
 	if (nodes.length === 0) return
@@ -187,6 +187,8 @@
 		const raw = p.innerText || p.textContent || ""
+		const sysMatch = raw.match(SYSTEM_DIRECTIVE_RE)
 		const match = raw.match(EMBED_RE)
-		if (!match) return
+		if (!match && !sysMatch) return
+
 		const userQuery = p.closest("user-query")
 		if (!userQuery) {
 			console.warn(`[GMT] [${i}] no user-query ancestor`)
@@ -193,31 +193,39 @@
 		}
 		const container = userQuery.parentElement
-		if (!container) {
-			console.warn(`[GMT] [${i}] no container`)
-			return
-		}
-		if (
-			exactContainers.has(container) ||
-			container.querySelector(".gm-timestamp")
-		)
-			return
-		const unix = parseEmbeddedUnix(match[1], match[2], parseFloat(match[4]))
-
-		const contextMatch = raw.match(/\[context to this point is (\d+|\*)\]/)
-		const queryTextEl = p.closest(".query-text")
-		if (contextMatch && queryTextEl) {
-			queryTextEl.dataset.contextAnchor = contextMatch[1]
-		}
-
-		let cleanText = raw.replace(EMBED_RE, "")
-		cleanText = cleanText.replace(
-			/\[context to this point is (\d+|\*)\]\s*/,
-			"",
-		)
+
+		let cleanText = raw
+		if (sysMatch) {
+			cleanText = cleanText.replace(SYSTEM_DIRECTIVE_RE, "")
+		}
+		if (match) {
+			if (
+				container &&
+				!exactContainers.has(container) &&
+				!container.querySelector(".gm-timestamp")
+			) {
+				const unix = parseEmbeddedUnix(
+					match[1],
+					match[2],
+					parseFloat(match[4]),
+				)
+				exactContainers.add(container)
+				injectTimestamp(container, unix, false)
+			}
+			const contextMatch = cleanText.match(
+				/\[context to this point is (\d+|\*)\]/,
+			)
+			const queryTextEl = p.closest(".query-text")
+			if (contextMatch && queryTextEl) {
+				queryTextEl.dataset.contextAnchor = contextMatch[1]
+			}
+			cleanText = cleanText.replace(EMBED_RE, "")
+			cleanText = cleanText.replace(
+				/\[context to this point is (\d+|\*)\]\s*/,
+				"",
+			)
+		}
+
 		p.innerText = cleanText.trim()
-
-		exactContainers.add(container)
-		injectTimestamp(container, unix, false)
 	})
 }
 
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-05T05:03:44-06:00
Completed At: 2026-08-05T05:03:44-06:00

				The command exited with code 0.
				Output:
				$ node bundler.cjs
🚀 Starting userscript bundling process...
📋 Auto-generating manifest from userscript files...
📋 Loading manifest from: script_manifest.json
🔍 Scanning userscripts directory for standalone scripts: ./userscripts/
📋 Parsing standalone userscript: livebench-frontier.user.js
✅ Parsed: "LiveBench Efficient Frontier Highlight" -> matches [https://livebench.ai/*]
📋 Parsing standalone userscript: perplexity.js
✅ Parsed: "Perplexity Thread Saver" -> matches [https://www.perplexity.ai/*]
📊 Final manifest has 24 script entries
✅ Generated manifest with 24 script entries
🧩 Prepending compatibility layer (compat.js)...
📦 Processing script 1/24: control-center.js
✅ Wrapped control-center.js as script_func_0 (run-at: document-idle)
📦 Processing script group 2/24: Gemini Enhancements (11 files)
✅ Wrapped group Gemini Enhancements (11 files) as script_func_1 (run-at: document-start)
📦 Processing script 3/24: Perplexity.ai Improvements.user.js
✅ Wrapped Perplexity.ai Improvements.user.js as script_func_2 (run-at: document-start)
📦 Processing script 4/24: d2l-content-tools.user.js
✅ Wrapped d2l-content-tools.user.js as script_func_3 (run-at: document-idle)
📦 Processing script 5/24: youtube-master.user.js
✅ Wrapped youtube-master.user.js as script_func_4 (run-at: document-start)
📦 Processing script 6/24: contentconnections.js
✅ Wrapped contentconnections.js as script_func_5 (run-at: document-idle)
📦 Processing script 7/24: studyforge-frame-downloader.user.js
✅ Wrapped studyforge-frame-downloader.user.js as script_func_6 (run-at: document-idle)
📦 Processing script 8/24: m3u8-capture.user.js
✅ Wrapped m3u8-capture.user.js as script_func_7 (run-at: document-idle)
📦 Processing script 9/24: amazon filter.js
✅ Wrapped amazon filter.js as script_func_8 (run-at: document-idle)
📦 Processing script 10/24: custom-youtub
<truncated 1261 bytes>
 script_func_18 (run-at: document-idle)
📦 Processing script 20/24: openrouter-credit-reminder.user.js
✅ Wrapped openrouter-credit-reminder.user.js as script_func_19 (run-at: document-idle)
📦 Processing script 21/24: auto-redirect-paywalls.user.js
✅ Wrapped auto-redirect-paywalls.user.js as script_func_20 (run-at: document-idle)
📦 Processing script 22/24: xkcd-explain.user.js
✅ Wrapped xkcd-explain.user.js as script_func_21 (run-at: document-idle)
📦 Processing script 23/24: livebench-frontier.user.js
✅ Wrapped livebench-frontier.user.js as script_func_22 (run-at: document-idle)
📦 Processing script 24/24: perplexity.js
✅ Wrapped perplexity.js as script_func_23 (run-at: document-start)
🔧 Adding execution dispatcher...
🗺️  Generating Source Map...
💾 Writing bundle to: userscript_bundle.js
🎉 Bundling completed successfully!
📊 Stats: 1702.22 KB, 24 scripts

📦 Compiling 1 multi-module userscript(s) into standalone files in: /Users/matt/projects/userscript-bundler/compiled
  ✅ Compiled: gemini-enhancements.user.js (143.80 KB, read-only)

📖 Master Userscript Configuration:
---------------------------------------
// ==UserScript==
// @name         Local Userscript Bundle Loader
// @match        *://*/*
// @run-at       document-start
// @grant        GM.getValue
// @grant        GM.setValue
// @grant        GM.xmlHttpRequest
// @grant        GM_addElement
// @grant        GM_addStyle
// @grant        GM_getResourceText
// @grant        GM_getValue
// @grant        GM_registerMenuCommand
// @grant        GM_setClipboard
// @grant        GM_setValue
// @grant        GM_unregisterMenuCommand
// @grant        GM_xmlhttpRequest
// @grant        unsafeWindow
// @require      file:///Users/matt/projects/userscript-bundler/userscript_bundle.js
// ==/UserScript==
---------------------------------------
⚠️ Make sure to update your loader script in Tampermonkey with the grants above!
3. The bundle will automatically detect the current page URL and execute the appropriate scripts

Created At: 2026-08-05T05:03:45-06:00
Completed At: 2026-08-05T05:03:45-06:00

				The command exited with code 0.
				Output:
				<truncated 1 lines>
+			--gmt-btn-hover: rgba(64, 160, 43, 0.3);
+			
+			--gmt-error-bg: rgba(210, 40, 40, 0.12);
+			--gmt-error-border: rgba(210, 40, 40, 0.35);
+			--gmt-error-text: #b31d1d;
+			--gmt-error-hover: rgba(210, 40, 40, 0.22);
+			
+			--gmt-auto-bg: rgba(26, 115, 232, 0.12);
+			--gmt-auto-border: rgba(26, 115, 232, 0.35);
+			--gmt-auto-text: #174ea6;
+			--gmt-auto-hover: rgba(26, 115, 232, 0.22);
+
+			--gmt-success-bg: rgba(128, 128, 128, 0.1);
+			--gmt-success-border: rgba(128, 128, 128, 0.25);
+			--gmt-success-text: #5f6368;
+			--gmt-success-hover: rgba(128, 128, 128, 0.15);
+		}
+		
+		body.dark-theme, html.dark-theme, .dark-theme-active {
+			--gmt-pill-bg: rgba(166, 227, 161, 0.12);
+			--gmt-pill-border: rgba(166, 227, 161, 0.35);
+			--gmt-pill-text: #a6e3a1;
+			--gmt-pill-hover: rgba(166, 227, 161, 0.22);
+			
+			--gmt-btn-bg: rgba(166, 227, 161, 0.15);
+			--gmt-btn-border: rgba(166, 227, 161, 0.4);
+			--gmt-btn-hover: rgba(166, 227, 161, 0.3);
+
+			--gmt-error-bg: rgba(243, 139, 168, 0.12);
+			--gmt-error-border: rgba(243, 139, 168, 0.35);
+			--gmt-error-text: #f38ba8;
+			--gmt-error-hover: rgba(243, 139, 168, 0.22);
+			
+			--gmt-auto-bg: rgba(137, 180, 250, 0.12);
+			--gmt-auto-border: rgba(137, 180, 250, 0.35);
+			--gmt-auto-text: #89b4fa;
+			--gmt-auto-hover: rgba(137, 180, 250, 0.22);
+
+			--gmt-success-bg: rgba(166, 173, 188, 0.1);
+			--gmt-success-border: rgba(166, 173, 188, 0.2);
+			--gmt-success-text: #a6adc8;
+			--gmt-success-hover: rgba(166, 173, 188, 0.15);
+		}
+		
+		@media (prefers-color-scheme: dark) {
+			body:not(.light-theme) {
+				--gmt-pill-bg: rgba(166, 227, 161, 0.12);
+				--gmt-pill-border: rgba(166, 227, 161, 0.35);
+				--gmt-pill-text: #a6e3a1;
+				--gmt-pill-hover: rgba(166, 227, 161, 0.22);
+				
+				--gmt-btn-bg: rgba(166, 227, 161, 0.15);
+				--gmt-btn-border: rgba(166, 227, 161, 0.4);
+				--gmt-btn-
<truncated 4242 bytes>
 () => {
+				if (isRunning) {
+					runBtn.textContent = "Running…"
+					runBtn.disabled = true
+				} else if (hasErrored) {
+					runBtn.textContent = "Retry"
+					runBtn.disabled = false
+				} else if (hasRun) {
+					runBtn.textContent = "Run Again"
+					runBtn.disabled = false
+				} else {
+					runBtn.textContent = parsed.run_automatically ? "Auto-Run" : "Run"
+					runBtn.disabled = false
+				}
+			}
+			updateBtnState();
+			
+			const triggerExecution = () => {
+				if (isRunning) return;
+				isRunning = true;
+				hasErrored = false;
+				updateBtnState();
+				
+				window.executeToolCall(parsed.tool, parsed.args)
+					.then(() => {
+						isRunning = false;
+						hasRun = true;
+						updateBtnState();
+						pill.className = "gmt-tool-call-pill success"
+					})
+					.catch(() => {
+						isRunning = false;
+						hasErrored = true;
+						updateBtnState();
+						pill.className = "gmt-tool-call-pill error"
+					});
+			}
+
 			runBtn.onclick = (e) => {
 				e.stopPropagation()
-				runBtn.textContent = "Running…"
-				runBtn.disabled = true
-				window.executeToolCall(parsed.tool, parsed.args)
+				triggerExecution()
 			}
 			pill.appendChild(runBtn)
 
@@ -286,13 +584,16 @@ window.scanToolCalls = function() {
 				wrapper.remove()
 			}
 
-			// Auto-execute if not initial scan and explicitly allowed
-			if (!isInitialScan && parsed.run_automatically === true) {
-				window.executeToolCall(parsed.tool, parsed.args)
+			// Only auto-execute if we explicitly witnessed the AI streaming this block (failed to parse previously)
+			// This prevents historical messages from auto-executing when the page is refreshed or history is loaded.
+			if (!isInitialScan && parsed.run_automatically === true && wasSeenIncomplete) {
+				triggerExecution()
 			}
 
 		} catch (e) {
 			// Not valid JSON or still streaming — skip
+			// Flag it so we know it was actively streaming when it finally succeeds
+			pre.dataset.wasSeenIncomplete = "true"
 		}
 	})
 	// Mark initial scan done after first pass

I have updated `03-timestamps.js` in `gemini-enhancements` to automatically remove `[SYSTEM CONTEXT & DIRECTIVES: ...]` as well as timestamp and token context headers from user query paragraphs in the UI DOM, while maintaining hidden dataset attributes and timestamp display logic.

### Summary of Changes:
1. **Added `SYSTEM_DIRECTIVE_RE`**: A regular expression (`/\[SYSTEM CONTEXT & DIRECTIVES:[\s\S]*?\]\s*/`) to match injected system prompt directives.
2. **Updated `processEmbeddedTimestamps`**: Cleaned user message nodes (`p.query-text-line`) of both system context directives and timestamp/context metadata headers automatically.
3. **Rebuilt Bundle**: Executed `bun run build` to update `userscript_bundle.js` and standalone output.

---

## User

excellent. It would be good to be able to enable a kind or "raw payload" mode that shows the exact message sent to gemini.

---

## Assistant

Created At: 2026-08-05T05:05:28-06:00
Completed At: 2026-08-05T05:05:28-06:00
{"File":"/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js"}
{"File":"/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/06-archive.js"}

Created At: 2026-08-05T05:05:29-06:00
Completed At: 2026-08-05T05:05:29-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js`
Total Lines: 237
Total Bytes: 7446
Showing lines 1 to 237
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
11: 	const rel = getRelativeDateLabel(unix, false)
12: 	const time = formatTime(new Date(unix * 1000))
13: 	const prefix = isEstimate ? "~ " : ""
14: 	return rel === null ? `${prefix}${time}` : `${prefix}${rel}, ${time}`
15: }
16: 
17: function injectTimestamp(container, unix, isEstimate) {
18: 	if (container.querySelector(".gm-timestamp")) return
19: 	const stamp = document.createElement("span")
20: 	stamp.className = "gm-timestamp"
21: 	stamp.innerText = buildMessageDisplay(unix, isEstimate)
22: 	stamp.setAttribute(
23: 		"data-timestamp",
24: 		formatAbsoluteTime(new Date(unix * 1000)),
25: 	)
26: 	stamp.style.cssText = `
27:       font-size: 1rem;
28:       color: #555;
29:       font-family: ${FONT};
30:       width: 100%;
31:       margin-bottom: 8px;
32:       display: block;
33:       text-align: right;
34:     `
35: 	attachTooltip(stamp, () => formatFullDateTime(new Date(unix * 1000)))
36:
<truncated 4997 bytes>
════════════════════
178: 
179: function parseEmbeddedUnix(dateStr, timeStr, offsetHours) {
180: 	const ms = new Date(`${dateStr}T${timeStr}:00Z`).getTime()
181: 	return Math.floor((ms - offsetHours * 3600000) / 1000)
182: }
183: 
184: const SYSTEM_DIRECTIVE_RE = /\[SYSTEM CONTEXT & DIRECTIVES:[\s\S]*?\]\s*/
185: 
186: function processEmbeddedTimestamps() {
187: 	const nodes = document.querySelectorAll("p.query-text-line")
188: 	if (nodes.length === 0) return
189: 	nodes.forEach((p, i) => {
190: 		const raw = p.innerText || p.textContent || ""
191: 		const sysMatch = raw.match(SYSTEM_DIRECTIVE_RE)
192: 		const match = raw.match(EMBED_RE)
193: 		if (!match && !sysMatch) return
194: 
195: 		const userQuery = p.closest("user-query")
196: 		if (!userQuery) {
197: 			console.warn(`[GMT] [${i}] no user-query ancestor`)
198: 			return
199: 		}
200: 		const container = userQuery.parentElement
201: 
202: 		let cleanText = raw
203: 		if (sysMatch) {
204: 			cleanText = cleanText.replace(SYSTEM_DIRECTIVE_RE, "")
205: 		}
206: 		if (match) {
207: 			if (
208: 				container &&
209: 				!exactContainers.has(container) &&
210: 				!container.querySelector(".gm-timestamp")
211: 			) {
212: 				const unix = parseEmbeddedUnix(
213: 					match[1],
214: 					match[2],
215: 					parseFloat(match[4]),
216: 				)
217: 				exactContainers.add(container)
218: 				injectTimestamp(container, unix, false)
219: 			}
220: 			const contextMatch = cleanText.match(
221: 				/\[context to this point is (\d+|\*)\]/,
222: 			)
223: 			const queryTextEl = p.closest(".query-text")
224: 			if (contextMatch && queryTextEl) {
225: 				queryTextEl.dataset.contextAnchor = contextMatch[1]
226: 			}
227: 			cleanText = cleanText.replace(EMBED_RE, "")
228: 			cleanText = cleanText.replace(
229: 				/\[context to this point is (\d+|\*)\]\s*/,
230: 				"",
231: 			)
232: 		}
233: 
234: 		p.innerText = cleanText.trim()
235: 	})
236: }
237: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-05T05:05:31-06:00
Completed At: 2026-08-05T05:05:31-06:00
{"File":"/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/04-sidebar-dates.js"}
{"File":"/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js"}
{"File":"/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/07-terminal.js"}
{"File":"/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/10-tool-calls.js"}

Created At: 2026-08-05T05:05:33-06:00
Completed At: 2026-08-05T05:05:34-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -182,6 +182,21 @@
 }
 
 const SYSTEM_DIRECTIVE_RE = /\[SYSTEM CONTEXT & DIRECTIVES:[\s\S]*?\]\s*/
+let isRawPayloadMode = false
+
+window.toggleRawPayloadMode = function(enable) {
+	isRawPayloadMode = enable !== undefined ? enable : !isRawPayloadMode
+	console.log(`[GMT] Raw payload mode set to: ${isRawPayloadMode}`)
+	document.querySelectorAll("p.query-text-line").forEach((p) => {
+		if (!p.dataset.rawContent) return
+		if (isRawPayloadMode) {
+			p.innerText = p.dataset.rawContent
+		} else if (p.dataset.cleanContent !== undefined) {
+			p.innerText = p.dataset.cleanContent
+		}
+	})
+	return isRawPayloadMode
+}
 
 function processEmbeddedTimestamps() {
 	const nodes = document.querySelectorAll("p.query-text-line")
@@ -188,11 +188,14 @@
 	nodes.forEach((p, i) => {
-		const raw = p.innerText || p.textContent || ""
+		const raw = p.dataset.rawContent || p.innerText || p.textContent || ""
+		if (!p.dataset.rawContent) {
+			p.dataset.rawContent = raw
+		}
 		const sysMatch = raw.match(SYSTEM_DIRECTIVE_RE)
 		const match = raw.match(EMBED_RE)
-		if (!match && !sysMatch) return
 
 		const userQuery = p.closest("user-query")
 		if (!userQuery) {
+			if (!match && !sysMatch) return
 			console.warn(`[GMT] [${i}] no user-query ancestor`)
 			return
 		}
@@ -229,7 +229,12 @@
 			)
 		}
 
-		p.innerText = cleanText.trim()
+		p.dataset.cleanContent = cleanText.trim()
+		if (isRawPayloadMode) {
+			p.innerText = p.dataset.rawContent
+		} else {
+			p.innerText = p.dataset.cleanContent
+		}
 	})
 }
 
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-05T05:05:35-06:00
Completed At: 2026-08-05T05:05:35-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js`
Total Lines: 1235
Total Bytes: 42972
Showing lines 500 to 600
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
500:     .table-block-component, .table-block, .table-content {
501:         width: auto !important;
502:         max-width: 100% !important;
503:     }
504:     table {
505:         width: auto !important;
506:         max-width: 100% !important;
507:         border-collapse: collapse !important;
508:         table-layout: auto !important;
509:     }
510:     table th, table td {
511:         padding: 8px 12px !important;
512:         white-space: normal !important;
513:         word-break: break-word !important;
514:         width: auto !important;
515:         min-width: 0 !important;
516:     }
517:     
518:     /* Responsive adjustments for narrower viewports */
519:     @media (max-width: 1400px) {
520:         table th, table td {
521:             padding: 6px 10px !important;
522:             font-size: 14px !important; /* reduce font size slightly from default 17px */
523:             max-width: 160px !important; /* help trigger wrapping when space is constrained */
524:         }
525:     }
526: `
527: 
528: function appendStyle(styleEl) {
529: 	const doAppend = () => {
530: 		const target = document.head || document.documentElement || document.body
531: 		if (target) {
532: 			target.appendChild(styleEl)
533: 			return true
534: 		}
535: 		return false
536: 	}
537: 
538: 	if (!doAppend()) {
539: 		if (document.readyState === "loading") {
540: 			document.addEventListener("DOMContentLoaded", doAppend)
541: 		} else {
542: 			const observer = new MutationObserver(() => {
543: 				if (doAppend()) observer.disconnect()
544: 			})
545: 			observer.observe(document, { childList: true, subtree: true })
546: 		}
547: 	}
548: }
549: 
550: appendStyle(aiosStyle)
551: 
552: // Autocomplete Menu logic
553: let autocompleteMenu = null
554: let selectedIndex = 0
555: 
556: function createAutocompleteMenu() {
557: 	if (autocompleteMenu) return
558: 	autocompleteMenu = document.createElement("div")
559: 	autocompleteMenu.className = "aios-dropdown aios-autocomplete-menu"
560: 	document.body.appendChild(autocompleteMenu)
561: }
562: 
563: function renderAutocomplete(inputEl, query) {
564: 	createAutocompleteMenu()
565: 	const rect = inputEl.getBoundingClientRect()
566: 
567: 	const phaseSkills = [
568: 		{
569: 			name: "phase0",
570: 			description: "Brainstorming - Explore edges conceptually",
571: 			prompt: PHASE_PROMPTS[0],
572: 		},
573: 		{
574: 			name: "phase1",
575: 			description: "Product Map - Synthesize plan into product map",
576: 			prompt: PHASE_PROMPTS[1],
577: 		},
578: 		{
579: 			name: "phase2",
580: 			description: "Tech Architecture - Technical plan & components",
581: 			prompt: PHASE_PROMPTS[2],
582: 		},
583: 		{
584: 			name: "phase3",
585: 			description: "Execution Payload - Instruction set for local agent",
586: 			prompt: PHASE_PROMPTS[3],
587: 		},
588: 	]
589: 
590: 	const allOptions = [...phaseSkills, ...localSkills]
591: 	const filtered = allOptions.filter(
592: 		(s) =>
593: 			s.name.toLowerCase().includes(query.toLowerCase()) ||
594: 			s.description.toLowerCase().includes(query.toLowerCase()),
595: 	)
596: 
597: 	if (filtered.length === 0) {
598: 		autocompleteMenu.style.display = "none"
599: 		return
600: 	}
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-05T05:05:35-06:00
Completed At: 2026-08-05T05:05:35-06:00
{"File":"/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js"}
{"File":"/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/09-page-observer.js"}

Created At: 2026-08-05T05:05:37-06:00
Completed At: 2026-08-05T05:05:37-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js`
Total Lines: 1235
Total Bytes: 42972
Showing lines 750 to 850
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
750: 	svg.setAttribute("viewBox", "0 0 10 6")
751: 	svg.setAttribute("fill", "none")
752: 	svg.style.marginLeft = "4px"
753: 	svg.style.transition = "transform 0.2s"
754: 
755: 	const path = document.createElementNS("http://www.w3.org/2000/svg", "path")
756: 	path.setAttribute("d", "M1 1L5 5L9 1")
757: 	path.setAttribute("stroke", "currentColor")
758: 	path.setAttribute("stroke-width", "1.5")
759: 	path.setAttribute("stroke-linecap", "round")
760: 	path.setAttribute("stroke-linejoin", "round")
761: 
762: 	svg.appendChild(path)
763: 	btn.appendChild(svg)
764: 
765: 	btn.addEventListener("click", (e) => {
766: 		e.preventDefault()
767: 		e.stopPropagation()
768: 		togglePhaseDropdown(container, btn)
769: 	})
770: 
771: 	container.appendChild(btn)
772: 
773: 	const switchBtn = promptContainer.querySelector(
774: 		'button.input-area-switch, button[aria-label*="Send"], button.send-button',
775: 	)
776: 	if (switchBtn) {
777: 		switchBtn.parentNode.style.setProperty(
778: 			"flex-direction",
779: 			"row",
780: 			"important",
781: 		)
782: 		switchBtn.parentNode.insertBefore(container, switchBtn)
783: 	} else {
784: 		promptContainer.appendChild(container)
785: 	}
786: }
787: 
788: function togglePhaseDropdown(container, btn) {
789: 	if (phaseDropdownMenu && phaseDropdownMenu.style.display === "block") {
790: 		phaseDropdownMenu.style.display = "none"
791: 		btn.querySelector("svg").style.transform = "rotate(0deg)"
792: 		return
793: 	}
794: 
795: 	if (!phaseDropdownMenu) {
796: 		phaseDropdownMenu = document.createElement("div")
797: 		phaseDropdownMenu.className = "aios-dropdown"
798: 		document.body.appendChild(phaseDropdownMenu)
799: 
800: 		document.addEventListener("click", (e) => {
801: 			if (
802: 				!container.contains(e.target) &&
803: 				!phaseDropdownMenu.contains(e.target)
804: 			) {
805: 				phaseDropdownMenu.style.display = "none"
806: 				btn.querySelector("svg").style.transform = "rotate(0deg)"
807: 			}
808: 		})
809: 	}
810: 
811: 	phaseDropdownMenu.textContent = ""
812: 
813: 	const phases = [
814: 		{
815: 			id: 0,
816: 			name: "Phase 0: Brainstorming",
817: 			desc: "Explore the edges of the idea conceptually",
818: 		},
819: 		{
820: 			id: 1,
821: 			name: "Phase 1: High-Level Plan",
822: 			desc: "Synthesize concept into product map",
823: 		},
824: 		{
825: 			id: 2,
826: 			name: "Phase 2: Tech Architecture",
827: 			desc: "Translate plan into technical plan",
828: 		},
829: 		{
830: 			id: 3,
831: 			name: "Phase 3: Execution Payload",
832: 			desc: "Generate strict instruction set for local agent",
833: 		},
834: 	]
835: 
836: 	phases.forEach((p) => {
837: 		const item = document.createElement("div")
838: 		item.className = `aios-dropdown-item ${p.id === currentPhase ? "active" : ""}`
839: 
840: 		const check = document.createElement("div")
841: 		check.className = "aios-dropdown-checkmark"
842: 		check.textContent = "✓"
843: 
844: 		const content = document.createElement("div")
845: 		content.className = "aios-dropdown-content"
846: 
847: 		const nameEl = document.createElement("div")
848: 		nameEl.className = "aios-dropdown-name"
849: 		nameEl.textContent = p.name
850: 
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-05T05:05:37-06:00
Completed At: 2026-08-05T05:05:37-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js`
Total Lines: 1235
Total Bytes: 42972
Showing lines 730 to 786
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
730: 			"polyline",
731: 		)
732: 		planPoly2.setAttribute("points", "10 9 9 9 8 9")
733: 
734: 		planSvg.appendChild(planPath)
735: 		planSvg.appendChild(planPoly1)
736: 		planSvg.appendChild(planLine1)
737: 		planSvg.appendChild(planLine2)
738: 		planSvg.appendChild(planPoly2)
739: 
740: 		btnSpan.appendChild(planSvg)
741: 		btnSpan.appendChild(document.createTextNode("Plan"))
742: 	} else {
743: 		btnSpan.textContent = `Phase ${currentPhase}`
744: 	}
745: 	btn.appendChild(btnSpan)
746: 
747: 	const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg")
748: 	svg.setAttribute("width", "10")
749: 	svg.setAttribute("height", "6")
750: 	svg.setAttribute("viewBox", "0 0 10 6")
751: 	svg.setAttribute("fill", "none")
752: 	svg.style.marginLeft = "4px"
753: 	svg.style.transition = "transform 0.2s"
754: 
755: 	const path = document.createElementNS("http://www.w3.org/2000/svg", "path")
756: 	path.setAttribute("d", "M1 1L5 5L9 1")
757: 	path.setAttribute("stroke", "currentColor")
758: 	path.setAttribute("stroke-width", "1.5")
759: 	path.setAttribute("stroke-linecap", "round")
760: 	path.setAttribute("stroke-linejoin", "round")
761: 
762: 	svg.appendChild(path)
763: 	btn.appendChild(svg)
764: 
765: 	btn.addEventListener("click", (e) => {
766: 		e.preventDefault()
767: 		e.stopPropagation()
768: 		togglePhaseDropdown(container, btn)
769: 	})
770: 
771: 	container.appendChild(btn)
772: 
773: 	const switchBtn = promptContainer.querySelector(
774: 		'button.input-area-switch, button[aria-label*="Send"], button.send-button',
775: 	)
776: 	if (switchBtn) {
777: 		switchBtn.parentNode.style.setProperty(
778: 			"flex-direction",
779: 			"row",
780: 			"important",
781: 		)
782: 		switchBtn.parentNode.insertBefore(container, switchBtn)
783: 	} else {
784: 		promptContainer.appendChild(container)
785: 	}
786: }
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-05T05:05:38-06:00
Completed At: 2026-08-05T05:05:38-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js`
Total Lines: 1235
Total Bytes: 42972
Showing lines 680 to 730
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
680: 		const planSvg = document.createElementNS(
681: 			"http://www.w3.org/2000/svg",
682: 			"svg",
683: 		)
684: 		planSvg.setAttribute("width", "14")
685: 		planSvg.setAttribute("height", "14")
686: 		planSvg.setAttribute("viewBox", "0 0 24 24")
687: 		planSvg.setAttribute("fill", "none")
688: 		planSvg.setAttribute("stroke", "currentColor")
689: 		planSvg.setAttribute("stroke-width", "2")
690: 		planSvg.setAttribute("stroke-linecap", "round")
691: 		planSvg.setAttribute("stroke-linejoin", "round")
692: 		planSvg.style.marginRight = "4px"
693: 		planSvg.style.verticalAlign = "-2px"
694: 
695: 		const planPath = document.createElementNS(
696: 			"http://www.w3.org/2000/svg",
697: 			"path",
698: 		)
699: 		planPath.setAttribute(
700: 			"d",
701: 			"M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z",
702: 		)
703: 
704: 		const planPoly1 = document.createElementNS(
705: 			"http://www.w3.org/2000/svg",
706: 			"polyline",
707: 		)
708: 		planPoly1.setAttribute("points", "14 2 14 8 20 8")
709: 
710: 		const planLine1 = document.createElementNS(
711: 			"http://www.w3.org/2000/svg",
712: 			"line",
713: 		)
714: 		planLine1.setAttribute("x1", "16")
715: 		planLine1.setAttribute("y1", "13")
716: 		planLine1.setAttribute("x2", "8")
717: 		planLine1.setAttribute("y2", "13")
718: 
719: 		const planLine2 = document.createElementNS(
720: 			"http://www.w3.org/2000/svg",
721: 			"line",
722: 		)
723: 		planLine2.setAttribute("x1", "16")
724: 		planLine2.setAttribute("y1", "17")
725: 		planLine2.setAttribute("x2", "8")
726: 		planLine2.setAttribute("y2", "17")
727: 
728: 		const planPoly2 = document.createElementNS(
729: 			"http://www.w3.org/2000/svg",
730: 			"polyline",
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-05T05:05:40-06:00
Completed At: 2026-08-05T05:05:40-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js`
Total Lines: 1235
Total Bytes: 42972
Showing lines 630 to 680
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
630: 		nameEl.className = "aios-dropdown-name"
631: 		nameEl.textContent = "/" + skill.name
632: 
633: 		const descEl = document.createElement("div")
634: 		descEl.className = "aios-dropdown-desc"
635: 		descEl.textContent = skill.description
636: 
637: 		content.appendChild(nameEl)
638: 		content.appendChild(descEl)
639: 
640: 		item.appendChild(check)
641: 		item.appendChild(content)
642: 
643: 		item.addEventListener("click", () => {
644: 			applySkill(inputEl, skill.name)
645: 		})
646: 		autocompleteMenu.appendChild(item)
647: 	})
648: }
649: 
650: function applySkill(inputEl, skillName) {
651: 	const text = inputEl.innerText || inputEl.value || ""
652: 	const queryStart = text.lastIndexOf("/")
653: 	if (queryStart !== -1) {
654: 		const before = text.substring(0, queryStart)
655: 		const after = text.substring(
656: 			queryStart + text.substring(queryStart).split(/\s/)[0].length,
657: 		)
658: 		const newText = before + "/" + skillName + after
659: 		replaceEditorContent(inputEl, newText)
660: 	}
661: 	if (autocompleteMenu) autocompleteMenu.style.display = "none"
662: 	inputEl.focus()
663: }
664: 
665: // Phase Selection dropdown
666: let phaseDropdownMenu = null
667: 
668: function injectPhaseDropdown(promptContainer) {
669: 	if (promptContainer.querySelector(".aios-phase-select-container")) return
670: 
671: 	const container = document.createElement("div")
672: 	container.className = "aios-phase-select-container"
673: 	container.style.cssText = "position: relative; display: inline-block;"
674: 
675: 	const btn = document.createElement("button")
676: 	btn.className = "aios-phase-select-btn"
677: 
678: 	const btnSpan = document.createElement("span")
679: 	if (currentPhase === null) {
680: 		const planSvg = document.createElementNS(
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-05T05:05:41-06:00
Completed At: 2026-08-05T05:05:41-06:00
{"File":"/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js"}

Created At: 2026-08-05T05:05:41-06:00
Completed At: 2026-08-05T05:05:41-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js`
Total Lines: 1235
Total Bytes: 42972
Showing lines 880 to 950
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
880: 	} else {
881: 		phaseDropdownMenu.classList.remove("aios-dark")
882: 	}
883: 
884: 	const rect = btn.getBoundingClientRect()
885: 	phaseDropdownMenu.style.display = "block"
886: 	phaseDropdownMenu.style.top = `${window.scrollY + rect.top - phaseDropdownMenu.offsetHeight - 6}px`
887: 	phaseDropdownMenu.style.left = `${rect.left}px`
888: 	btn.querySelector("svg").style.transform = "rotate(180deg)"
889: }
890: 
891: // Inject Phase Controls & Listeners
892: function injectUI() {
893: 	const promptContainer = document.querySelector(
894: 		".input-area-container, .prompt-box-container, form .input-area",
895: 	)
896: 	if (!promptContainer) return
897: 
898: 	// 1. Inject Phase Selection Pill Dropdown
899: 	injectPhaseDropdown(promptContainer)
900: 
901: 	// 1.5 Inject Quick Actions Pill Dropdown
902: 	injectQuickActionsDropdown(promptContainer)
903: 
904: 	// 2. Hook Input elements for `/` Autocomplete
905: 	const inputEl = promptContainer.querySelector(
906: 		'textarea, [contenteditable="true"]',
907: 	)
908: 	if (inputEl && !inputEl.dataset.aiosHooked) {
909: 		inputEl.dataset.aiosHooked = "true"
910: 		inputEl.addEventListener("input", (e) => {
911: 			const text = inputEl.value || inputEl.innerText || ""
912: 			const slashIdx = text.lastIndexOf("/")
913: 			if (slashIdx !== -1 && slashIdx === text.length - 1) {
914: 				renderAutocomplete(inputEl, "")
915: 			} else if (slashIdx !== -1 && slashIdx < text.length - 1) {
916: 				const query = text.substring(slashIdx + 1)
917: 				if (!query.includes(" ") && !query.includes("\n")) {
918: 					renderAutocomplete(inputEl, query)
919: 				} else {
920: 					if (autocompleteMenu) autocompleteMenu.style.display = "none"
921: 				}
922: 			} else {
923: 				if (autocompleteMenu) autocompleteMenu.style.display = "none"
924: 			}
925: 		})
926: 
927: 		inputEl.addEventListener("keydown", (e) => {
928: 			if (autocompleteMenu && autocompleteMenu.style.display === "block") {
929: 				const items = autocompleteMenu.querySelectorAll(".aios-dropdown-item")
930: 				if (e.key === "ArrowDown") {
931: 					e.preventDefault()
932: 					selectedIndex = (selectedIndex + 1) % items.length
933: 					renderAutocomplete(
934: 						inputEl,
935: 						inputEl.innerText
936: 							.substring(inputEl.innerText.lastIndexOf("/") + 1)
937: 							.trim(),
938: 					)
939: 				} else if (e.key === "ArrowUp") {
940: 					e.preventDefault()
941: 					selectedIndex = (selectedIndex - 1 + items.length) % items.length
942: 					renderAutocomplete(
943: 						inputEl,
944: 						inputEl.innerText
945: 							.substring(inputEl.innerText.lastIndexOf("/") + 1)
946: 							.trim(),
947: 					)
948: 				} else if (e.key === "Enter") {
949: 					e.preventDefault()
950: 					const activeItem = items[selectedIndex]
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-05T05:05:42-06:00
Completed At: 2026-08-05T05:05:42-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js`
Total Lines: 1235
Total Bytes: 42972
Showing lines 900 to 990
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
900: 
901: 	// 1.5 Inject Quick Actions Pill Dropdown
902: 	injectQuickActionsDropdown(promptContainer)
903: 
904: 	// 2. Hook Input elements for `/` Autocomplete
905: 	const inputEl = promptContainer.querySelector(
906: 		'textarea, [contenteditable="true"]',
907: 	)
908: 	if (inputEl && !inputEl.dataset.aiosHooked) {
909: 		inputEl.dataset.aiosHooked = "true"
910: 		inputEl.addEventListener("input", (e) => {
911: 			const text = inputEl.value || inputEl.innerText || ""
912: 			const slashIdx = text.lastIndexOf("/")
913: 			if (slashIdx !== -1 && slashIdx === text.length - 1) {
914: 				renderAutocomplete(inputEl, "")
915: 			} else if (slashIdx !== -1 && slashIdx < text.length - 1) {
916: 				const query = text.substring(slashIdx + 1)
917: 				if (!query.includes(" ") && !query.includes("\n")) {
918: 					renderAutocomplete(inputEl, query)
919: 				} else {
920: 					if (autocompleteMenu) autocompleteMenu.style.display = "none"
921: 				}
922: 			} else {
923: 				if (autocompleteMenu) autocompleteMenu.style.display = "none"
924: 			}
925: 		})
926: 
927: 		inputEl.addEventListener("keydown", (e) => {
928: 			if (autocompleteMenu && autocompleteMenu.style.display === "block") {
929: 				const items = autocompleteMenu.querySelectorAll(".aios-dropdown-item")
930: 				if (e.key === "ArrowDown") {
931: 					e.preventDefault()
932: 					selectedIndex = (selectedIndex + 1) % items.length
933: 					renderAutocomplete(
934: 						inputEl,
935: 						inputEl.innerText
936: 							.substring(inputEl.innerText.lastIndexOf("/") + 1)
937: 							.trim(),
938: 					)
939: 				} else if (e.key === "ArrowUp") {
940: 					e.preventDefault()
941: 					selectedIndex = (selectedIndex - 1 + items.length) % items.length
942: 					renderAutocomplete(
943: 						inputEl,
944: 						inputEl.innerText
945: 							.substring(inputEl.innerText.lastIndexOf("/") + 1)
946: 							.trim(),
947: 					)
948: 				} else if (e.key === "Enter") {
949: 					e.preventDefault()
950: 					const activeItem = items[selectedIndex]
951: 					if (activeItem) {
952: 						const name = activeItem
953: 							.querySelector(".aios-dropdown-name")
954: 							.innerText.substring(1) // strip leading slash
955: 						applySkill(inputEl, name)
956: 					}
957: 				} else if (e.key === "Escape") {
958: 					autocompleteMenu.style.display = "none"
959: 				}
960: 			}
961: 		})
962: 	}
963: }
964: 
965: // Quick Actions Dropdown Logic
966: let quickActionsMenu = null
967: 
968: function injectQuickActionsDropdown(promptContainer) {
969: 	if (promptContainer.querySelector(".aios-quick-actions-container")) return
970: 
971: 	const container = document.createElement("div")
972: 	container.className = "aios-quick-actions-container"
973: 	container.style.cssText = "position: relative; display: inline-block;"
974: 
975: 	const btn = document.createElement("button")
976: 	btn.className = "aios-phase-select-btn"
977: 	btn.style.marginRight = "8px"
978: 
979: 	const btnSpan = document.createElement("span")
980: 	btnSpan.textContent = "⚡ Quick Actions"
981: 	btn.appendChild(btnSpan)
982: 
983: 	btn.addEventListener("click", (e) => {
984: 		e.preventDefault()
985: 		e.stopPropagation()
986: 		toggleQuickActionsDropdown(container, btn)
987: 	})
988: 
989: 	container.appendChild(btn)
990: 
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-05T05:05:43-06:00
Completed At: 2026-08-05T05:05:43-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js`
Total Lines: 1235
Total Bytes: 42972
Showing lines 991 to 1040
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
991: 	const phaseContainer = promptContainer.querySelector(".aios-phase-select-container")
992: 	if (phaseContainer && phaseContainer.nextSibling) {
993: 		phaseContainer.parentNode.insertBefore(container, phaseContainer.nextSibling)
994: 	} else if (phaseContainer) {
995: 		phaseContainer.parentNode.appendChild(container)
996: 	} else {
997: 		promptContainer.appendChild(container)
998: 	}
999: }
1000: 
1001: function toggleQuickActionsDropdown(container, btn) {
1002: 	if (quickActionsMenu && quickActionsMenu.style.display === "block") {
1003: 		quickActionsMenu.style.display = "none"
1004: 		return
1005: 	}
1006: 
1007: 	if (!quickActionsMenu) {
1008: 		quickActionsMenu = document.createElement("div")
1009: 		quickActionsMenu.className = "aios-dropdown"
1010: 		document.body.appendChild(quickActionsMenu)
1011: 
1012: 		document.addEventListener("click", (e) => {
1013: 			if (!container.contains(e.target) && !quickActionsMenu.contains(e.target)) {
1014: 				quickActionsMenu.style.display = "none"
1015: 			}
1016: 		})
1017: 	}
1018: 
1019: 	quickActionsMenu.textContent = ""
1020: 
1021: 	const actions = [
1022: 		{
1023: 			id: "save_last",
1024: 			name: "Save a note (last response)",
1025: 			desc: "Saves the last AI response. Add instructions in chatbox first to customize.",
1026: 		},
1027: 		{
1028: 			id: "save_summary",
1029: 			name: "Save a note (thread summary)",
1030: 			desc: "Prompts Gemini to summarize this thread and save as a note.",
1031: 		}
1032: 	]
1033: 
1034: 	actions.forEach((a) => {
1035: 		const item = document.createElement("div")
1036: 		item.className = "aios-dropdown-item"
1037: 
1038: 		const content = document.createElement("div")
1039: 		content.className = "aios-dropdown-content"
1040: 		
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-05T05:05:44-06:00
Completed At: 2026-08-05T05:05:44-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -1020,6 +1020,11 @@
 
 	const actions = [
 		{
+			id: "toggle_raw_payload",
+			name: isRawPayloadMode ? "✓ Raw Payload Mode (Active)" : "Raw Payload Mode",
+			desc: "Toggle showing exact injected context/directives in user query text.",
+		},
+		{
 			id: "save_last",
 			name: "Save a note (last response)",
 			desc: "Saves the last AI response. Add instructions in chatbox first to customize.",
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-05T05:05:45-06:00
Completed At: 2026-08-05T05:05:45-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js`
Total Lines: 1240
Total Bytes: 43173
Showing lines 1040 to 1075
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1040: 		const item = document.createElement("div")
1041: 		item.className = "aios-dropdown-item"
1042: 
1043: 		const content = document.createElement("div")
1044: 		content.className = "aios-dropdown-content"
1045: 		
1046: 		const nameEl = document.createElement("div")
1047: 		nameEl.className = "aios-dropdown-name"
1048: 		nameEl.textContent = a.name
1049: 		
1050: 		const descEl = document.createElement("div")
1051: 		descEl.className = "aios-dropdown-desc"
1052: 		descEl.textContent = a.desc
1053: 		
1054: 		content.appendChild(nameEl)
1055: 		content.appendChild(descEl)
1056: 		item.appendChild(content)
1057: 
1058: 		item.addEventListener("click", () => {
1059: 			quickActionsMenu.style.display = "none"
1060: 			handleQuickAction(a.id)
1061: 		})
1062: 
1063: 		quickActionsMenu.appendChild(item)
1064: 	})
1065: 
1066: 	if (isDarkTheme()) quickActionsMenu.classList.add("aios-dark")
1067: 	else quickActionsMenu.classList.remove("aios-dark")
1068: 
1069: 	const rect = btn.getBoundingClientRect()
1070: 	quickActionsMenu.style.display = "block"
1071: 	quickActionsMenu.style.top = `${window.scrollY + rect.top - quickActionsMenu.offsetHeight - 6}px`
1072: 	quickActionsMenu.style.left = `${rect.left}px`
1073: }
1074: 
1075: function handleQuickAction(actionId) {
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-05T05:05:45-06:00
Completed At: 2026-08-05T05:05:46-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js`
Total Lines: 1240
Total Bytes: 43173
Showing lines 1075 to 1110
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1075: function handleQuickAction(actionId) {
1076: 	const editor = document.querySelector('.ql-editor[contenteditable="true"]')
1077: 	if (!editor) return
1078: 	const instruction = editor.innerText.trim()
1079: 
1080: 	if (actionId === "save_last" && instruction === "") {
1081: 		// Directly scrape and save
1082: 		const responses = document.querySelectorAll("model-response")
1083: 		if (responses.length === 0) {
1084: 			alert("No AI response found to save.")
1085: 			return
1086: 		}
1087: 		const lastResponse = responses[responses.length - 1]
1088: 		
1089: 		let content = lastResponse.innerText
1090: 		// Try to find the inner text of the actual response body
1091: 		const body = lastResponse.querySelector(".message-content, .model-response-text")
1092: 		if (body) content = body.innerText
1093: 		
1094: 		let title = "Gemini Note - " + new Date().toLocaleDateString("en-CA") + " " + Date.now().toString().slice(-4)
1095: 
1096: 		const pseudoToolCall = {
1097: 			tool: "save_note",
1098: 			args: {
1099: 				title: title,
1100: 				content: content + "\\n\\n---\\nThread Link: " + location.href,
1101: 				update: false
1102: 			}
1103: 		}
1104: 		
1105: 		if (window.executeToolCall) {
1106: 			window.executeToolCall(pseudoToolCall.tool, pseudoToolCall.args)
1107: 		} else {
1108: 			console.warn("Tool call executor not ready")
1109: 		}
1110: 	} else {
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-05T05:05:46-06:00
Completed At: 2026-08-05T05:05:47-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -1073,6 +1073,14 @@
 }
 
 function handleQuickAction(actionId) {
+	if (actionId === "toggle_raw_payload") {
+		if (typeof window.toggleRawPayloadMode === "function") {
+			const active = window.toggleRawPayloadMode()
+			console.log(`Raw payload mode toggled: ${active}`)
+		}
+		return
+	}
+
 	const editor = document.querySelector('.ql-editor[contenteditable="true"]')
 	if (!editor) return
 	const instruction = editor.innerText.trim()
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-05T05:05:47-06:00
Completed At: 2026-08-05T05:05:47-06:00

				The command exited with code 0.
				Output:
				$ node bundler.cjs
🚀 Starting userscript bundling process...
📋 Auto-generating manifest from userscript files...
📋 Loading manifest from: script_manifest.json
🔍 Scanning userscripts directory for standalone scripts: ./userscripts/
📋 Parsing standalone userscript: livebench-frontier.user.js
✅ Parsed: "LiveBench Efficient Frontier Highlight" -> matches [https://livebench.ai/*]
📋 Parsing standalone userscript: perplexity.js
✅ Parsed: "Perplexity Thread Saver" -> matches [https://www.perplexity.ai/*]
📊 Final manifest has 24 script entries
✅ Generated manifest with 24 script entries
🧩 Prepending compatibility layer (compat.js)...
📦 Processing script 1/24: control-center.js
✅ Wrapped control-center.js as script_func_0 (run-at: document-idle)
📦 Processing script group 2/24: Gemini Enhancements (11 files)
✅ Wrapped group Gemini Enhancements (11 files) as script_func_1 (run-at: document-start)
📦 Processing script 3/24: Perplexity.ai Improvements.user.js
✅ Wrapped Perplexity.ai Improvements.user.js as script_func_2 (run-at: document-start)
📦 Processing script 4/24: d2l-content-tools.user.js
✅ Wrapped d2l-content-tools.user.js as script_func_3 (run-at: document-idle)
📦 Processing script 5/24: youtube-master.user.js
✅ Wrapped youtube-master.user.js as script_func_4 (run-at: document-start)
📦 Processing script 6/24: contentconnections.js
✅ Wrapped contentconnections.js as script_func_5 (run-at: document-idle)
📦 Processing script 7/24: studyforge-frame-downloader.user.js
✅ Wrapped studyforge-frame-downloader.user.js as script_func_6 (run-at: document-idle)
📦 Processing script 8/24: m3u8-capture.user.js
✅ Wrapped m3u8-capture.user.js as script_func_7 (run-at: document-idle)
📦 Processing script 9/24: amazon filter.js
✅ Wrapped amazon filter.js as script_func_8 (run-at: document-idle)
📦 Processing script 10/24: custom-youtub
<truncated 1261 bytes>
 script_func_18 (run-at: document-idle)
📦 Processing script 20/24: openrouter-credit-reminder.user.js
✅ Wrapped openrouter-credit-reminder.user.js as script_func_19 (run-at: document-idle)
📦 Processing script 21/24: auto-redirect-paywalls.user.js
✅ Wrapped auto-redirect-paywalls.user.js as script_func_20 (run-at: document-idle)
📦 Processing script 22/24: xkcd-explain.user.js
✅ Wrapped xkcd-explain.user.js as script_func_21 (run-at: document-idle)
📦 Processing script 23/24: livebench-frontier.user.js
✅ Wrapped livebench-frontier.user.js as script_func_22 (run-at: document-idle)
📦 Processing script 24/24: perplexity.js
✅ Wrapped perplexity.js as script_func_23 (run-at: document-start)
🔧 Adding execution dispatcher...
🗺️  Generating Source Map...
💾 Writing bundle to: userscript_bundle.js
🎉 Bundling completed successfully!
📊 Stats: 1705.22 KB, 24 scripts

📦 Compiling 1 multi-module userscript(s) into standalone files in: /Users/matt/projects/userscript-bundler/compiled
  ✅ Compiled: gemini-enhancements.user.js (144.92 KB, read-only)

📖 Master Userscript Configuration:
---------------------------------------
// ==UserScript==
// @name         Local Userscript Bundle Loader
// @match        *://*/*
// @run-at       document-start
// @grant        GM.getValue
// @grant        GM.setValue
// @grant        GM.xmlHttpRequest
// @grant        GM_addElement
// @grant        GM_addStyle
// @grant        GM_getResourceText
// @grant        GM_getValue
// @grant        GM_registerMenuCommand
// @grant        GM_setClipboard
// @grant        GM_setValue
// @grant        GM_unregisterMenuCommand
// @grant        GM_xmlhttpRequest
// @grant        unsafeWindow
// @require      file:///Users/matt/projects/userscript-bundler/userscript_bundle.js
// ==/UserScript==
---------------------------------------
⚠️ Make sure to update your loader script in Tampermonkey with the grants above!
3. The bundle will automatically detect the current page URL and execute the appropriate scripts

I have added a **Raw Payload Mode** feature to `gemini-enhancements`.

### Key Enhancements:
1. **Raw Payload Preservation**:
   - Original raw inner text (including system directives, timestamp, and token context headers) is saved on `dataset.rawContent`.
   - Cleaned text is stored on `dataset.cleanContent`.
2. **Global & UI Toggle**:
   - Added `window.toggleRawPayloadMode(enable)` function to switch between displaying clean text vs. exact raw injected payload across all message queries.
   - Added a **"Raw Payload Mode"** option under the **⚡ Quick Actions** dropdown in the Gemini prompt interface.

3. **Bundle Build**:
   - Rebuilt the bundle via `bun run build`.

---
