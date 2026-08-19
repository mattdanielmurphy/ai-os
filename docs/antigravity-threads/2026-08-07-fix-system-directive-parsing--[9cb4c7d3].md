---
title: "Fix System Directive Parsing"
date: "2026-08-07"
conversation_id: "9cb4c7d3-2084-4d9a-b2e0-e0396d918417"
source: "antigravity"
---

# Fix System Directive Parsing

## User

Please update `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js` to fix the multi-line system directive stripping issue.

Use `replace_file_content` on `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js`.

Target content lines 184 to 259:
```javascript
const SYSTEM_DIRECTIVE_RE = /\[SYSTEM CONTEXT & DIRECTIVES:[\s\S]*?\]\s*/
let isRawPayloadMode = false

window.toggleRawPayloadMode = function(enable) {
	isRawPayloadMode = enable !== undefined ? enable : !isRawPayloadMode
	console.log(`[GMT] Raw payload mode set to: ${isRawPayloadMode}`)
	document.querySelectorAll("p.query-text-line").forEach((p) => {
		if (!p.dataset.rawContent) return
		if (isRawPayloadMode) {
			p.innerText = p.dataset.rawContent
		} else if (p.dataset.cleanContent !== undefined) {
			p.innerText = p.dataset.cleanContent
		}
	})
	return isRawPayloadMode
}

function processEmbeddedTimestamps() {
	const nodes = document.querySelectorAll("p.query-text-line")
	if (nodes.length === 0) return
	nodes.forEach((p, i) => {
		const raw = p.dataset.rawContent || p.innerText || p.textContent || ""
		if (!p.dataset.rawContent) {
			p.dataset.rawContent = raw
		}
		const sysMatch = raw.match(SYSTEM_DIRECTIVE_RE)
		const match = raw.match(EMBED_RE)

		const userQuery = p.closest("user-query")
		if (!userQuery) {
			if (!match && !sysMatch) return
			console.warn(`[GMT] [${i}] no user-query ancestor`)
			return
		}
		const container = userQuery.parentElement

		let cleanText = raw
		if (sysMatch) {
			cleanText = cleanText.replace(SYSTEM_DIRECTIVE_RE, "")
		}
		if (match) {
			if (
				container &&
				!exactContainers.has(container) &&
				!container.querySelector(".gm-timestamp")
			) {
				const unix = parseEmbeddedUnix(
					match[1],
					match[2],
					parseFloat(match[4]),
				)
				exactContainers.add(container)
				injectTimestamp(container, unix, false)
			}
			const contextMatch = cleanText.match(
				/\[context to this point is (\d+|\*)\]/,
			)
			const qu
<truncated 1691 bytes>
Nodes.forEach((p) => {
			if (p.dataset.rawContent === undefined) {
				p.dataset.rawContent = p.innerText || p.textContent || ""
			}
		})

		let insideSysDirective = false

		pNodes.forEach((p) => {
			const raw = p.dataset.rawContent
			let cleanText = raw

			if (
				!insideSysDirective &&
				cleanText.includes("[SYSTEM CONTEXT & DIRECTIVES:")
			) {
				insideSysDirective = true
			}

			if (insideSysDirective) {
				if (cleanText.includes("]")) {
					const sysEndIdx = cleanText.indexOf("]")
					cleanText = cleanText.substring(sysEndIdx + 1)
					insideSysDirective = false
				} else {
					cleanText = ""
				}
			}

			cleanText = cleanText.replace(SYSTEM_DIRECTIVE_RE, "")
			const match = cleanText.match(EMBED_RE)

			const timeContainer =
				container.closest("user-query")?.parentElement ||
				container.parentElement ||
				container

			if (match) {
				if (
					timeContainer &&
					!exactContainers.has(timeContainer) &&
					!timeContainer.querySelector(".gm-timestamp")
				) {
					const unix = parseEmbeddedUnix(
						match[1],
						match[2],
						parseFloat(match[4]),
					)
					exactContainers.add(timeContainer)
					injectTimestamp(timeContainer, unix, false)
				}
				const contextMatch = cleanText.match(
					/\[context to this point is (\d+|\*)\]/,
				)
				const queryTextEl = p.closest(".query-text")
				if (contextMatch && queryTextEl) {
					queryTextEl.dataset.contextAnchor = contextMatch[1]
				}
				cleanText = cleanText.replace(EMBED_RE, "")
				cleanText = cleanText.replace(
					/\[context to this point is (\d+|\*)\]\s*/,
					"",
				)
			}

			p.dataset.cleanContent = cleanText.trim()
			if (isRawPayloadMode) {
				p.innerText = p.dataset.rawContent
				p.style.display = ""
			} else {
				p.innerText = p.dataset.cleanContent
				if (p.dataset.cleanContent === "") {
					p.style.display = "none"
				} else {
					p.style.display = ""
				}
			}
		})
	})
}
```

---

## Assistant

Created At: 2026-08-06T19:56:21-06:00
Completed At: 2026-08-06T19:56:21-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -187,12 +187,18 @@
 window.toggleRawPayloadMode = function(enable) {
 	isRawPayloadMode = enable !== undefined ? enable : !isRawPayloadMode
 	console.log(`[GMT] Raw payload mode set to: ${isRawPayloadMode}`)
-	document.querySelectorAll("p.query-text-line").forEach((p) => {
-		if (!p.dataset.rawContent) return
-		if (isRawPayloadMode) {
-			p.innerText = p.dataset.rawContent
+	document.querySelectorAll("p.query-text-line, user-query p").forEach((p) => {
+		if (p.dataset.rawContent === undefined) return
+		if (isRawPayloadMode) {
+			p.innerText = p.dataset.rawContent
+			p.style.display = ""
 		} else if (p.dataset.cleanContent !== undefined) {
 			p.innerText = p.dataset.cleanContent
+			if (p.dataset.cleanContent === "") {
+				p.style.display = "none"
+			} else {
+				p.style.display = ""
+			}
 		}
 	})
 	return isRawPayloadMode
@@ -199,61 +199,96 @@
 
 function processEmbeddedTimestamps() {
-	const nodes = document.querySelectorAll("p.query-text-line")
-	if (nodes.length === 0) return
-	nodes.forEach((p, i) => {
-		const raw = p.dataset.rawContent || p.innerText || p.textContent || ""
-		if (!p.dataset.rawContent) {
-			p.dataset.rawContent = raw
-		}
-		const sysMatch = raw.match(SYSTEM_DIRECTIVE_RE)
-		const match = raw.match(EMBED_RE)
-
-		const userQuery = p.closest("user-query")
-		if (!userQuery) {
-			if (!match && !sysMatch) return
-			console.warn(`[GMT] [${i}] no user-query ancestor`)
-			return
-		}
-		const container = userQuery.parentElement
-
-		let cleanText = raw
-		if (sysMatch) {
-			cleanText = cleanText.replace(SYSTEM_DIRECTIVE_RE, "")
-		}
-		if (match) {
+	const userQueries = document.querySelectorAll(
+		"user-query, .user-qu
<truncated 1432 bytes>
		p.dataset.cleanContent = cleanText.trim()
-		if (isRawPayloadMode) {
-			p.innerText = p.dataset.rawContent
-		} else {
-			p.innerText = p.dataset.cleanContent
-		}
+				insideSysDirective = true
+			}
+
+			if (insideSysDirective) {
+				if (cleanText.includes("]")) {
+					const sysEndIdx = cleanText.indexOf("]")
+					cleanText = cleanText.substring(sysEndIdx + 1)
+					insideSysDirective = false
+				} else {
+					cleanText = ""
+				}
+			}
+
+			cleanText = cleanText.replace(SYSTEM_DIRECTIVE_RE, "")
+			const match = cleanText.match(EMBED_RE)
+
+			const timeContainer =
+				container.closest("user-query")?.parentElement ||
+				container.parentElement ||
+				container
+
+			if (match) {
+				if (
+					timeContainer &&
+					!exactContainers.has(timeContainer) &&
+					!timeContainer.querySelector(".gm-timestamp")
+				) {
+					const unix = parseEmbeddedUnix(
+						match[1],
+						match[2],
+						parseFloat(match[4]),
+					)
+					exactContainers.add(timeContainer)
+					injectTimestamp(timeContainer, unix, false)
+				}
+				const contextMatch = cleanText.match(
+					/\[context to this point is (\d+|\*)\]/,
+				)
+				const queryTextEl = p.closest(".query-text")
+				if (contextMatch && queryTextEl) {
+					queryTextEl.dataset.contextAnchor = contextMatch[1]
+				}
+				cleanText = cleanText.replace(EMBED_RE, "")
+				cleanText = cleanText.replace(
+					/\[context to this point is (\d+|\*)\]\s*/,
+					"",
+				)
+			}
+
+			p.dataset.cleanContent = cleanText.trim()
+			if (isRawPayloadMode) {
+				p.innerText = p.dataset.rawContent
+				p.style.display = ""
+			} else {
+				p.innerText = p.dataset.cleanContent
+				if (p.dataset.cleanContent === "") {
+					p.style.display = "none"
+				} else {
+					p.style.display = ""
+				}
+			}
+		})
 	})
 }
 
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-06T19:56:23-06:00
Completed At: 2026-08-06T19:56:23-06:00
Message sent to "ee1b915f-4a03-4015-b194-2fda62be71b5".

The file `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js` has already been updated with the requested changes. I have sent the confirmation to the parent agent.

---
