---
title: "You need to edit `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js` using `replace_file_content`."
date: "2026-08-05"
conversation_id: "c7111f01-96a8-4400-bc39-e352018192e2"
source: "antigravity"
---

# You need to edit `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js` using `replace_file_content`.

## User

You need to edit `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js` using `replace_file_content`.

Replace the `processEmbeddedTimestamps` function (lines 184-224) with:
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

		p.innerText = cleanText.trim()
	})
}
```

Make the change in `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js` immediately.

---
