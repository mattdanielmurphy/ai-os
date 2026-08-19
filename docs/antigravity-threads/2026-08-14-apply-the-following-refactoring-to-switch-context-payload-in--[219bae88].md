---
title: "Apply the following refactoring to switch context payload injection fr"
date: "2026-08-14"
conversation_id: "219bae88-9760-4c60-9233-cc883d467619"
source: "antigravity"
---

# Apply the following refactoring to switch context payload injection fr

## User

Apply the following refactoring to switch context payload injection from adversarial brackets to standard `<context>` XML blocks.

Target File 1: /Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js
Use replace_file_content to make the following edits:

Edit 1 (around line 145):
```javascript
function hasAlreadyPrepended(text) {
	if (!text) return false
	return (
		text.includes("<context>") ||
		text.includes("[context to this point is") ||
		EMBED_RE.test(text)
	)
}
```

Edit 2 (around line 200) AND Edit 3 (around line 270) - Both places where `if (isNewThread)` exists:
Replace the `systemPrefix = \`[SYSTEM CONTEXT & DIRECTIVES:... ]\n\n\`` blocks with:
```javascript
		let systemPrefix = ""
		if (isNewThread) {
			systemPrefix = `<context>
# Background Directives
1. Primary User Vault: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/
2. Strict Media & Story Spoilers Directive: STRICT NO SPOILERS POLICY. You MUST NOT under any circumstances reveal plot twists, endings, key character fates, deaths, betrayals, secret identities, major narrative developments, or unreleased details for movies, TV shows, books, anime, games, or story-driven media. If asked about media, err heavily on the side of caution. Give zero hints or foreshadowing of major events unless the user explicitly requests spoilers with confirmation.
3. Tone, Sycophancy & Banned Buzzwords: No sycophantic praise or routine filler ("that's very insightful", "great question", "I understand..."). NEVER use banned buzzwords: "glitch in the matrix", "nuclear option", "final boss", "game changer", "level up", "cheat code", "you've hit on", "unlocking the potential".
4. Tool Call Directive: You can output JSON tool calls inside a \`\`\`tool_call codeblock. Schema: {"tool":"save_note","run_automatically":true,"args":{"title":"...","content":"..."}}. Set "run_automatically": true ONLY if the tool should execute immediately without user confirmation (e.g. proactive note-taking). Set t
<truncated 1954 bytes>
matter (tags, date), # Title, High-Level Summary, Bulleted Breakdown, Expanded Details, Thread Link.
</context>`
	},
	{
		id: "kw-ai-os",
		title: "AI-OS Protocols Context",
		keywords: ["ai-os", "aios", "agent rules", "ag_context", "preflight", "auto-commit", "bun", "subagent"],
		output: `<context>
# AI-OS Protocols Context
Project Root: /Users/matt/projects/ai-os
Preflight Routine: python3 /Users/matt/projects/ai-os/scripts/preflight.py
Auto-Commit Routine: python3 /Users/matt/projects/ai-os/scripts/auto_commit.py
Rules Summary: Bun is required for JS projects; ./tmp for temporary scripts; mv ~/.Trash/ for deletions; no heredocs; concise token-efficient outputs.
</context>`
	},
	{
		id: "kw-terminal-cli",
		title: "Terminal & CLI Context",
		keywords: ["terminal", "cli", "zsh", "bash", "tmux", "command", "shell"],
		output: `<context>
# Terminal & Local Execution Context
Shell: Zsh on macOS (/bin/zsh)
Local Command Executor Service: http://127.0.0.1:3033/run-command
Headers: x-gemini-thread-saver-key (requires secret configuration)
Inline Terminal Sessions: tmux background sessions monitored via HTTP
</context>`
	}
```


Target File 2: /Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js
Use replace_file_content to make the following edits:

Edit 1 (around line 184):
Change `const SYSTEM_DIRECTIVE_RE = /\[SYSTEM CONTEXT & DIRECTIVES:[\s\S]*?\]\s*/`
To `const SYSTEM_DIRECTIVE_RE = /<context>[\s\S]*?<\/context>\s*/g`

Edit 2 (around line 234):
Replace the `insideSysDirective` block:
```javascript
			if (
				!insideSysDirective &&
				cleanText.includes("<context>")
			) {
				insideSysDirective = true
			}

			if (insideSysDirective) {
				if (cleanText.includes("</context>")) {
					const sysEndIdx = cleanText.indexOf("</context>")
					cleanText = cleanText.substring(sysEndIdx + 10)
					insideSysDirective = false
				} else {
					cleanText = ""
				}
			}
```

---

## Assistant

The requested refactoring from adversarial brackets to `<context>...</context>` XML blocks has been completed for both files.

- Applied updates in [`/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js`](file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js) to switch injection methods and keyword context outputs.
- Applied updates in [`/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js`](file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js) to update the `SYSTEM_DIRECTIVE_RE` regex and internal processing logic.

---
