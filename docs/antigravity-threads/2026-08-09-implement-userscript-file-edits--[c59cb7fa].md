---
title: "Implement Userscript File Edits"
date: "2026-08-09"
conversation_id: "c59cb7fa-f734-4f59-9ff5-3e4c671ec324"
source: "antigravity"
---

# Implement Userscript File Edits

## User

You are a leaf file editor. Make the following TWO precise edits to the userscript source files, then report done.

## EDIT 1: Add `window.injectAndSendPrompt` to 05-prompt-tools.js

File: `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js`

Insert the following block AFTER the closing brace of `replaceEditorContent` (which ends at line 69 with a lone `}`).
Insert it at line 70, after that closing brace. The content to insert is:

```

// ─── External Prompt Injection API ────────────────────────────────────────
// Called by Tauri Axum server (/api/prompt) and main.rs pending_prompt.txt
window.injectAndSendPrompt = function(text, opts) {
	opts = opts || {}
	const autoSend = opts.autoSend !== false // default: true

	// Find Gemini's contenteditable editor — try selectors in priority order
	const EDITOR_SELECTORS = [
		'.ql-editor[contenteditable="true"]',
		'rich-textarea [contenteditable="true"]',
		'[contenteditable="true"]',
		'textarea',
	]
	let editor = null
	for (const sel of EDITOR_SELECTORS) {
		editor = document.querySelector(sel)
		if (editor) break
	}

	if (!editor) {
		console.warn('[GMT] injectAndSendPrompt: No input editor found. Storing as __pendingPrompt.')
		window.__pendingPrompt = text
		return false
	}

	replaceEditorContent(editor, text)
	console.log('[GMT] injectAndSendPrompt: Injected', text.length, 'chars into editor.')

	if (!autoSend) return true

	// Click the Send button after a short delay for React/Angular state to update
	setTimeout(function() {
		const sendBtn = document.querySelector(
			'button[aria-label*="Send" i], button[aria-label*="Submit" i], button.send-button, button[data-test-id*="send" i]'
		)
		if (sendBtn) {
			sendBtn.click()
			console.log('[GMT] injectAndSendPrompt: Send button clicked.')
		} else {
			console.warn('[GMT] injectAndSendPrompt: Send button not found — text injected but not sent.')
		}
	}, 150)

	return true
}
```

The target TargetContent to insert AFTER is exactly:
```
function replaceEditorContent(editor, newText) {
	editor.focus()
	document.execCommand("selectAll", false, null)
	document.execCommand("insertText", false, newText)
}
```

So the ReplacementContent should be that same block followed by the new `window.injectAndSendPrompt` block.

---

## EDIT 2: Add `__pendingPrompt` polling to 09-page-observer.js

File: `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/09-page-observer.js`

Insert the following block BEFORE the line `console.log("[GMT] observers started")` (line 190):

```
	// Consume any prompt that was set before the userscript was ready
	setTimeout(function() {
		if (window.__pendingPrompt && typeof window.injectAndSendPrompt === 'function') {
			const pending = window.__pendingPrompt
			delete window.__pendingPrompt
			console.log('[GMT] Consuming __pendingPrompt:', pending.length, 'chars')
			window.injectAndSendPrompt(pending)
		}
	}, 800)

```

The TargetContent to replace is:
```
	console.log("[GMT] observers started")
}
```

The ReplacementContent should be:
```
	// Consume any prompt that was set before the userscript was ready
	setTimeout(function() {
		if (window.__pendingPrompt && typeof window.injectAndSendPrompt === 'function') {
			const pending = window.__pendingPrompt
			delete window.__pendingPrompt
			console.log('[GMT] Consuming __pendingPrompt:', pending.length, 'chars')
			window.injectAndSendPrompt(pending)
		}
	}, 800)

	console.log("[GMT] observers started")
}
```

Make both edits now and report done.

---

## Assistant

Created At: 2026-08-08T19:29:35-06:00
Completed At: 2026-08-08T19:29:35-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -68,6 +68,52 @@
 	document.execCommand("insertText", false, newText)
 }
 
+// ─── External Prompt Injection API ────────────────────────────────────────
+// Called by Tauri Axum server (/api/prompt) and main.rs pending_prompt.txt
+window.injectAndSendPrompt = function(text, opts) {
+	opts = opts || {}
+	const autoSend = opts.autoSend !== false // default: true
+
+	// Find Gemini's contenteditable editor — try selectors in priority order
+	const EDITOR_SELECTORS = [
+		'.ql-editor[contenteditable="true"]',
+		'rich-textarea [contenteditable="true"]',
+		'[contenteditable="true"]',
+		'textarea',
+	]
+	let editor = null
+	for (const sel of EDITOR_SELECTORS) {
+		editor = document.querySelector(sel)
+		if (editor) break
+	}
+
+	if (!editor) {
+		console.warn('[GMT] injectAndSendPrompt: No input editor found. Storing as __pendingPrompt.')
+		window.__pendingPrompt = text
+		return false
+	}
+
+	replaceEditorContent(editor, text)
+	console.log('[GMT] injectAndSendPrompt: Injected', text.length, 'chars into editor.')
+
+	if (!autoSend) return true
+
+	// Click the Send button after a short delay for React/Angular state to update
+	setTimeout(function() {
+		const sendBtn = document.querySelector(
+			'button[aria-label*="Send" i], button[aria-label*="Submit" i], button.send-button, button[data-test-id*="send" i]'
+		)
+		if (sendBtn) {
+			sendBtn.click()
+			console.log('[GMT] injectAndSendPrompt: Send button clicked.')
+		} else {
+			console.warn('[GMT] injectAndSendPrompt: Send button not found — text injected but not sent.')
+		}
+	}, 150)
+
+	return true
+}
+
 function processCommandReplacement(editor) {
 	const currentText = editor.innerText || ""
 	let newText = currentText.trim()
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-08T19:29:36-06:00
Completed At: 2026-08-08T19:29:36-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/09-page-observer.js. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -187,6 +187,16 @@
 		}
 	}, 1500)
 
+	// Consume any prompt that was set before the userscript was ready
+	setTimeout(function() {
+		if (window.__pendingPrompt && typeof window.injectAndSendPrompt === 'function') {
+			const pending = window.__pendingPrompt
+			delete window.__pendingPrompt
+			console.log('[GMT] Consuming __pendingPrompt:', pending.length, 'chars')
+			window.injectAndSendPrompt(pending)
+		}
+	}, 800)
+
 	console.log("[GMT] observers started")
 }
 
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-08T19:29:37-06:00
Completed At: 2026-08-08T19:29:37-06:00
Message sent to "b6512175-77fe-4fd7-89c9-c1c5375f45f1".

Done.

---
