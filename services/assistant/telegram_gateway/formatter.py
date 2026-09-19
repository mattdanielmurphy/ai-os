"""Markdown to Telegram HTML converter and text formatting utilities."""

import html
import re
import textwrap
from typing import List

# Telegram supported HTML tags per official Bot API specification:
# <b>, <i>, <u>, <s>, <tg-spoiler>, <a>, <code>, <pre>, <blockquote>
TELEGRAM_ALLOWED_TAG_PATTERN = re.compile(
    r"</?(?:b|strong|i|em|u|ins|s|strike|del|span\s+class=\"tg-spoiler\"|tg-spoiler|a(?:\s+href=\"[^\"]*\")?|code(?:\s+class=\"language-[^\"]*\")?|pre|blockquote(?:\s+expandable)?)>",
    re.IGNORECASE,
)

PAT_DOUBLE_BOLD = re.compile(
    r"(^|[\s\(\[\{<\"])\*\*(?!\s)([^\*\n]+?)(?<!\s)\*\*(?=$|[\s\)\]\}>\":;,\.\!\?])"
)
PAT_SINGLE_BOLD = re.compile(
    r"(^|[\s\(\[\{<\"])\*(?!\s)([^\*\n]+?)(?<!\s)\*(?=$|[\s\)\]\}>\":;,\.\!\?])"
)
PAT_ITALIC = re.compile(
    r"(^|[\s\(\[\{<\"])_(?!\s)([^_\n]+?)(?<!\s)_(?=$|[\s\)\]\}>\":;,\.\!\?])"
)
PAT_STRIKE = re.compile(
    r"(^|[\s\(\[\{<\"])~~(?!\s)([^~\n]+?)(?<!\s)~~(?=$|[\s\)\]\}>\":;,\.\!\?])"
)
PAT_SPOILER = re.compile(r"\|\|([^|\n]+?)\|\|")
PAT_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^\s\)]+)\)")
PAT_HEADER = re.compile(r"^(?:#{1,6})\s+(.+)$", re.MULTILINE)
PAT_BULLET = re.compile(r"^(\s*)[*\-]\s+", re.MULTILINE)


def clean_cell_text(cell: str) -> str:
    """Strips outermost markdown bold/italic/code wrappers for clean monospace table alignment."""
    c = cell.strip()
    if c.startswith("**") and c.endswith("**") and len(c) >= 4:
        c = c[2:-2]
    elif c.startswith("*") and c.endswith("*") and len(c) >= 2:
        c = c[1:-1]
    elif c.startswith("_") and c.endswith("_") and len(c) >= 2:
        c = c[1:-1]
    elif c.startswith("`") and c.endswith("`") and len(c) >= 2:
        c = c[1:-1]
    return c.strip()


def is_markdown_table_separator(line: str) -> bool:
    """Checks if a line is a markdown table separator like | :--- | :---: | ---: |"""
    cleaned = line.strip()
    if not cleaned:
        return False
    if cleaned.startswith("|"):
        cleaned = cleaned[1:]
    if cleaned.endswith("|"):
        cleaned = cleaned[:-1]
    parts = [p.strip() for p in cleaned.split("|")]
    if not parts or not any(parts):
        return False
    return all(re.match(r"^:?-+:?$", p) for p in parts)


def parse_markdown_table_row(line: str) -> List[str]:
    """Splits a markdown table row by pipe delimiter into cleaned cell values."""
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [clean_cell_text(c) for c in stripped.split("|")]


def format_vertical_card_table(rows: List[List[str]]) -> str:
    """
    Renders a 2D array of table rows into clean, mobile-native Telegram vertical cards/blocks
    with bold labels, preventing wrapped/scrambled ASCII tables on narrow screens.
    """
    if not rows:
        return ""

    headers = rows[0]
    data_rows = rows[1:]
    if not data_rows:
        return "\n".join(f"• <b>{html.escape(c, quote=False)}</b>" for c in headers if c)

    cards = []
    num_cols = len(headers)

    if num_cols == 2:
        # 2-column key-value pairs: • <b>Key:</b> Value
        lines = []
        for r in data_rows:
            k = r[0] if len(r) > 0 else ""
            v = r[1] if len(r) > 1 else ""
            if k or v:
                k_esc = html.escape(k, quote=False)
                v_esc = html.escape(v, quote=False)
                if k and v:
                    lines.append(f"• <b>{k_esc}:</b> {v_esc}")
                elif k:
                    lines.append(f"• <b>{k_esc}</b>")
                else:
                    lines.append(f"• {v_esc}")
        return "\n".join(lines)

    # 3 or more columns: Vertical Entity Cards
    for r in data_rows:
        card_title = r[0] if len(r) > 0 else ""
        card_lines = []
        if card_title:
            card_lines.append(f"<b>{html.escape(card_title, quote=False)}</b>")

        for c_idx in range(1, num_cols):
            h_name = headers[c_idx] if c_idx < len(headers) else f"Field {c_idx}"
            val = r[c_idx] if c_idx < len(r) else ""
            if val:
                card_lines.append(
                    f"• <b>{html.escape(h_name, quote=False)}:</b> {html.escape(val, quote=False)}"
                )

        if card_lines:
            cards.append("\n".join(card_lines))

    return "\n\n".join(cards)


def format_ascii_box_table(rows: List[List[str]], max_col_width: int = 32) -> str:
    """
    Alias redirecting to format_vertical_card_table to enforce the Telegram
    presentation rule: format data as vertical cards/blocks, never ASCII tables.
    """
    return format_vertical_card_table(rows)


def markdown_to_telegram_html(text: str) -> str:
    """
    Safely converts standard Markdown and Telegram-legacy formatting into Telegram-compliant HTML.
    
    Guarantees:
    - Special HTML chars (&, <, >) outside formatting are strictly escaped.
    - Code blocks (```lang ... ``` and `code`) preserve literal content inside <pre><code>.
    - Headers (# Header) become bold <b>Header</b>.
    - Bulleted lists (- or *) become clean Unicode bullets (•).
    - Blockquotes (> quote) become <blockquote>quote</blockquote>.
    - Bold (**text** or *text*) become <b>text</b>.
    - Italic (_text_) becomes <i>text</i> without breaking snake_case_identifiers.
    - Spoilers (||text||) become <tg-spoiler>text</tg-spoiler>.
    - Strikethrough (~~text~~) becomes <s>text</s>.
    - Markdown links [label](url) become <a href="url">label</a>.
    - Existing valid Telegram HTML tags are safely preserved.
    """
    if not text:
        return ""

    placeholders: List[str] = []

    def save_placeholder(val: str) -> str:
        idx = len(placeholders)
        key = f"\x00TGHX{idx}X\x00"
        placeholders.append(val)
        return key

    # 1. Extract fenced code blocks: ```lang\ncode\n```
    def replace_code_block(match):
        lang = (match.group(1) or "").strip()
        code_content = match.group(2)
        # Escape code content for HTML
        escaped_code = html.escape(code_content, quote=False)
        if lang:
            tag = f'<pre><code class="language-{html.escape(lang, quote=True)}">{escaped_code}</code></pre>'
        else:
            tag = f"<pre>{escaped_code}</pre>"
        return save_placeholder(tag)

    text = re.sub(
        r"```([a-zA-Z0-9_\-\+]*)\n?(.*?)```", replace_code_block, text, flags=re.DOTALL
    )

    # 2. Extract inline code: `code`
    def replace_inline_code(match):
        code_content = match.group(1)
        escaped_code = html.escape(code_content, quote=False)
        return save_placeholder(f"<code>{escaped_code}</code>")

    text = re.sub(r"`([^`\n]+)`", replace_inline_code, text)

    # 2.5. Extract and format Markdown Tables: | col1 | col2 | ...
    table_lines = text.split("\n")
    processed_table_lines = []
    i = 0
    num_l = len(table_lines)
    while i < num_l:
        line = table_lines[i]
        if "|" in line and i + 1 < num_l and is_markdown_table_separator(table_lines[i + 1]):
            t_rows = [parse_markdown_table_row(line)]
            i += 2
            while i < num_l and "|" in table_lines[i] and not table_lines[i].strip().startswith("#"):
                if not table_lines[i].strip():
                    break
                t_rows.append(parse_markdown_table_row(table_lines[i]))
                i += 1
            box_html = format_ascii_box_table(t_rows)
            processed_table_lines.append(save_placeholder(box_html))
        else:
            processed_table_lines.append(line)
            i += 1
    text = "\n".join(processed_table_lines)

    # 3. Preserve any pre-existing valid Telegram HTML tags
    def preserve_html_tags(match):
        return save_placeholder(match.group(0))

    text = TELEGRAM_ALLOWED_TAG_PATTERN.sub(preserve_html_tags, text)

    # 4. Escape all remaining raw &, <, > so plain text does not break HTML parsing
    text = html.escape(text, quote=False)

    # 5. Convert Blockquotes: lines starting with > (which is now &gt;)
    lines = text.split("\n")
    processed_lines = []
    quote_buf: List[str] = []
    in_quote = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("&gt; ") or stripped == "&gt;":
            in_quote = True
            content = line.replace("&gt; ", "", 1) if "&gt; " in line else ""
            quote_buf.append(content)
        else:
            if in_quote:
                quote_html = "<blockquote>" + "\n".join(quote_buf) + "</blockquote>"
                processed_lines.append(save_placeholder(quote_html))
                quote_buf = []
                in_quote = False
            processed_lines.append(line)

    if in_quote:
        quote_html = "<blockquote>" + "\n".join(quote_buf) + "</blockquote>"
        processed_lines.append(save_placeholder(quote_html))

    text = "\n".join(processed_lines)

    # 6. Convert Markdown Headers: # Title -> <b>Title</b>
    text = PAT_HEADER.sub(r"<b>\1</b>", text)

    # 7. Convert Markdown Links: [text](url) -> <a href="url">text</a>
    text = PAT_LINK.sub(r'<a href="\2">\1</a>', text)

    # 8. Convert Strikethrough: ~~text~~ -> <s>text</s>
    text = PAT_STRIKE.sub(r"\1<s>\2</s>", text)

    # 9. Convert Telegram Spoiler: ||text|| -> <tg-spoiler>text</tg-spoiler>
    text = PAT_SPOILER.sub(r"<tg-spoiler>\1</tg-spoiler>", text)

    # 10. Convert Double Bold: **text** -> <b>text</b>
    text = PAT_DOUBLE_BOLD.sub(r"\1<b>\2</b>", text)

    # 11. Convert Single Bold: *text* -> <b>text</b>
    text = PAT_SINGLE_BOLD.sub(r"\1<b>\2</b>", text)

    # 12. Convert Italic: _text_ -> <i>text</i> (safe against snake_case_identifiers)
    text = PAT_ITALIC.sub(r"\1<i>\2</i>", text)

    # 13. Convert bullet lists: - item or * item at line start -> • item
    text = PAT_BULLET.sub(r"\1• ", text)

    # 14. Restore placeholders in reverse order
    for idx in range(len(placeholders) - 1, -1, -1):
        key = f"\x00TGHX{idx}X\x00"
        text = text.replace(key, placeholders[idx])

    return text


def split_message_chunks(text: str, max_chars: int = 4000) -> List[str]:
    """
    Splits long messages into Telegram-safe chunks (<4096 chars),
    prioritizing splits at double newlines (paragraphs), single newlines, or spaces.
    """
    if len(text) <= max_chars:
        return [text]

    chunks = []
    remaining = text
    while remaining:
        if len(remaining) <= max_chars:
            chunks.append(remaining)
            break

        # Look for clean split point
        split_idx = remaining.rfind("\n\n", 0, max_chars)
        if split_idx == -1 or split_idx < max_chars // 3:
            split_idx = remaining.rfind("\n", 0, max_chars)
        if split_idx == -1 or split_idx < max_chars // 3:
            split_idx = remaining.rfind(" ", 0, max_chars)
        if split_idx == -1:
            split_idx = max_chars

        chunk = remaining[:split_idx].strip()
        if chunk:
            chunks.append(chunk)
        remaining = remaining[split_idx:].strip()

    return chunks
