# Context Handoff: `conversation_response.md` Rendering Bugs

> Thread abandoned on 2026-08-03 due to accumulated corruption in the conversation_response.md artifact itself (each fix attempt compounded rendering issues). This doc captures the outstanding problems for a fresh thread.

## System Overview

The "Mandatory Response Artifact Protocol" requires every agent turn to update a persistent artifact at `~/.gemini/antigravity/brain/<conversation-id>/conversation_response.md`. The pipeline is:

1. **Agent writes response** → piped via stdin to `gen_conversation_md.py`
2. **`gen_conversation_md.py`** parses `transcript.jsonl`, extracts user prompts + timestamps, loads agent responses from `history/turn_N.md` files, and renders the full HTML-table conversation document.
3. **`watch_transcripts.py`** (daemon) polls `transcript.jsonl` mtime every 2s and re-runs `gen_conversation_md.py` when changes are detected.

### Key Files

- **Generator script**: `/Users/matt/projects/ai-os/scripts/gen_conversation_md.py`
- **Watcher daemon**: `/Users/matt/projects/ai-os/scripts/watch_transcripts.py`
- **User rules reference**: The protocol is defined in the user's global rules under "Mandatory Response Artifact Protocol"

---

## Outstanding Bugs (Unfixed)

### 1. Trailing `</td>` Rendered as Visible Text

**Severity**: High — visible in every user prompt block.

**What happens**: A literal `</td>` string appears at the end of the user prompt inside the rendered markdown. It's the closing tag of the HTML table cell leaking into the visible content.

**Root cause**: The user prompt content is placed inside a `<td>` cell in `make_exchange_block()`. The closing `</td>` tag on a separate line sometimes gets treated as content rather than markup by the Markdown renderer. Multiple fix attempts (regex stripping, html.escape) were tried but each introduced new problems.

**What was tried**:
- Regex stripping `</?(?:td|tr|table)>` from prompt text → stripped legitimate content
- `html.escape()` on prompt text → caused double/triple escaping (see bug #3)
- Moving `</td>` placement → didn't resolve because the watcher re-renders and the selection text from artifact comments contains `</td>` literally

---

### 2. Newlines Stripped from User Prompts

**Severity**: High — all user prompt formatting is lost.

**What happens**: User prompts that span multiple lines render as a single continuous line. The markdown within the `<td>` cell collapses all newlines.

**Root cause**: When content is placed inside HTML `<table><tr><td>` blocks in a Markdown document, the Markdown renderer may not preserve newlines within the HTML context. The script places raw markdown text inside `<td>` elements, but the HTML table context suppresses normal markdown line break behavior.

**Implication**: The entire approach of using HTML tables for layout may be fundamentally incompatible with preserving markdown formatting of the content within those tables. Need either:
- Use `<br>` tags or `<pre>` for line breaks inside HTML
- Or abandon HTML tables entirely and use pure markdown formatting
- Or ensure blank lines around the markdown content inside `<td>` (partially attempted)

---

### 3. Double/Triple HTML Entity Escaping

**Severity**: High — makes prompts unreadable.

**What happens**: Characters like `<` become `&lt;` on first pass, then `&amp;lt;` on second pass, then `&amp;amp;lt;` on third pass. Each time the watcher re-renders, escaping compounds.

**Root cause**: `html.escape()` is called on prompt text in `format_prompt()`. But when the watcher daemon re-renders (triggered by transcript changes), the *already-escaped* text from artifact comment selections gets fed back through `html.escape()` again. The artifact comment "Selection" text captured by the IDE already contains HTML entities from the rendered artifact, creating an escaping feedback loop.

**The feedback loop**:
1. User comments on artifact → IDE captures rendered text (which may already have `&lt;` entities)
2. That selection text goes into `transcript.jsonl` as the user's prompt
3. `gen_conversation_md.py` runs `html.escape()` on it → `&lt;` becomes `&amp;lt;`
4. Watcher re-renders → the now-double-escaped text gets escaped again → `&amp;amp;lt;`

---

### 4. Artifact Comment Block Quotes Not Rendering Properly

**Severity**: Medium — comments lose their quoted context.

**What happens**: When a user highlights text in the artifact and leaves a comment, the comment should show:
- A blockquote of the highlighted text
- The comment text below it

Instead, either:
- The blockquote `>` prefix is treated as part of the text (not rendered as a quote)
- The selection text is stripped entirely when `</td>` cleanup removes it
- The blockquote and comment appear on the same line

**Root cause**: The selection text from artifact comments often contains HTML table fragments (`<td>`, `</td>`, `<tr>`, etc.) because the user is selecting rendered HTML. The regex extraction and cleanup of these fragments is fragile — it either leaves too much (visible tags) or strips too much (loses the quote content).

---

### 5. Watcher Daemon Occasionally Misses Updates

**Severity**: Medium — intermittent.

**What happens**: The `watch_transcripts.py` daemon sometimes doesn't catch the latest agent response, leaving `conversation_response.md` stale with "(response in progress or not recorded)".

**Root cause**: Race condition. The watcher polls mtime every 2s. If the transcript is written and the watcher checks mtime in between writes, it may process a partial state. Also, on first launch `last_mtimes` was initialized empty (fixed during the thread to pre-populate), but there may still be edge cases.

---

## Architectural Concerns

### HTML Tables in Markdown — Fundamental Tension

The core design uses HTML `<table>` elements inside a `.md` file to create a chat-like layout. This creates several inherent problems:

1. **Markdown inside HTML is fragile**: Most renderers require blank lines before/after markdown content inside HTML blocks. Even with blank lines, behavior varies across renderers.
2. **Escaping feedback loops**: Content that gets rendered as HTML entities and then re-ingested (via artifact comments) creates compounding escaping.
3. **Tag leakage**: Closing tags like `</td>` appearing as visible text is a symptom of the renderer not properly parsing the table structure — possibly because the markdown content inside breaks the HTML parser.

### Possible Alternative Approaches

1. **Pure Markdown**: Use headers, blockquotes, and horizontal rules instead of HTML tables. Simpler, no escaping issues, universal renderer support.
2. **Fully escaped HTML**: If tables are needed, ensure ALL content is properly HTML-escaped and use `<br>` for line breaks instead of relying on markdown rendering inside HTML.
3. **Separate rendering**: Generate a standalone `.html` file instead of `.md`, avoiding the markdown-inside-HTML problem entirely.

---

## What Was Successfully Fixed (Keep These)

- ✅ Watcher daemon created and running (`watch_transcripts.py --daemon`)
- ✅ Watcher pre-populates `last_mtimes` on startup to avoid re-processing old conversations
- ✅ Agent response link-only lines (`[conversation_response.md](file://...)`) filtered from agent content
- ✅ Duplicate agent content deduplication in `parse_exchanges()`
- ✅ `<ADDITIONAL_METADATA>` blocks stripped from user prompts
- ✅ `<USER_REQUEST>` wrapper tags stripped from user prompts
- ✅ Artifact comment extraction regex (partially working — extracts Selection + Comment)
- ✅ Collapsible `<details><summary>` for very long prompts (>800 chars or >12 lines)
