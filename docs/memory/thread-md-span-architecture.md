# Thread.md Span-Only Styling Architecture & Invariants

## Invariant
All layout, containers, bubbles, cards, dividers, banners, and footers in `thread.md` and related markdown documents **MUST use `<span>` tags exclusively**.
Using `<div>`, `<p>`, or other block-level HTML tags for styling containers is strictly prohibited.

## Why `<span>` with `display: block`?
1. **Universal Markdown Viewer Compatibility**:
   Many embedded markdown renderers, previewers, and webviews restrict or strip block-level HTML tags (`<div>`, `<section>`, `<article>`) or handle them unpredictably.
2. **Pure-CSS Block Conversion**:
   Adding `display: block;` (or `display: flex;`) to a `<span>` element transforms it into a full block/flex container in the browser/webview rendering engine while retaining valid inline-level markdown semantics.

## Handling Multiline User Prompts & Paragraphs
In standard Markdown parsers (e.g. `markdown-it`, CommonMark), a literal double newline (`\n\n`) is parsed as a paragraph boundary, which causes the parser to wrap inline content in `<p>` and auto-terminate any open inline tags (such as `<span>`).

To support multi-line prompts and paragraph breaks inside a `<span>` container without breaking out of the styled bubble:
- All newline characters (`\n`) must be converted to `<br>` tags.
- Blank lines / paragraph breaks (`\n\n`) must be converted to `<br><br>` tags.
- The `<span>` container must specify `white-space: pre-wrap;`, `overflow-wrap: anywhere;`, `word-break: break-word;`, and `display: block;`.

### Example Container Schema:
```html
<span title="Sent at 2:30pm" style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">Line 1<br><br>Paragraph 2</span>
```
