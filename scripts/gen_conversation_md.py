#!/usr/bin/env python3
"""
gen_conversation_md.py — Generate thread.md from transcript + agent response files.

ARCHITECTURE:
  Each turn, the agent:
    1. Writes its response (plain markdown) to:
         brain/<conv-id>/history/turn_<N>.md
    2. Runs:
         python3 gen_conversation_md.py <conv-id> --title "Thread Title"

  This script reads:
    - transcript.jsonl  -> all user messages + timestamps (auto-extracted)
    - history/turn_N.md -> agent response content per turn (agent writes this)

  And generates a pure-markdown thread.md (no HTML tables).

USAGE:
  python3 gen_conversation_md.py <conversation-id> [--title "Thread Title"] [--app-data-dir PATH]
"""

import argparse
import json
import re
import sys
import subprocess
from datetime import datetime
from pathlib import Path

APP_DATA_DIR = Path.home() / '.gemini/antigravity'

def iso_to_epoch(iso_str: str) -> float:
    if not iso_str:
        return 0.0
    try:
        dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        return dt.timestamp()
    except Exception:
        return 0.0

def balance_code_fences(text: str) -> str:
    """Ensure all open markdown fenced code blocks (backticks or tildes >= 3) are properly closed."""
    if not text:
        return text

    fence_char = None
    fence_len = 0
    in_fence = False
    fence_start_re = re.compile(r'^[ ]{0,3}(`{3,}|~{3,})')

    for line in text.splitlines():
        if not in_fence:
            m = fence_start_re.match(line)
            if m:
                fence = m.group(1)
                fence_char = fence[0]
                fence_len = len(fence)
                in_fence = True
        else:
            close_re = re.compile(rf'^[ ]{{0,3}}{re.escape(fence_char)}{{{fence_len},}}\s*$')
            if close_re.match(line):
                in_fence = False
                fence_char = None
                fence_len = 0

    if in_fence and fence_char and fence_len:
        closing = fence_char * fence_len
        return text + f"\n{closing}\n"

    return text


def escape_currency_dollar_signs(text: str) -> str:
    """
    Escape currency dollar signs (e.g. $500, $3,877.14, **$500**) so that
    Markdown / KaTeX does not misinterpret pairs of currency values as LaTeX math delimiters.
    Preserves fenced code blocks and inline code spans.
    """
    if not text:
        return text

    parts = re.split(r'(```[\s\S]*?```|`[^`\n]+`)', text)
    for idx in range(0, len(parts), 2):
        parts[idx] = re.sub(r'(?<!\\)\$(?=\d)', r'\\$', parts[idx])

    return ''.join(parts)


def is_transient_status_line(s: str) -> bool:
    """Return True if s is a short intermediate status update emitted while tools/subagents are running."""
    if not s:
        return False
    if '\n' in s or s.startswith('#') or s.startswith('-') or s.startswith('*') or s.startswith('|'):
        return False
    s_clean = s.strip()
    if len(s_clean) > 160:
        return False
    if re.match(r'^(?:updating|running|checking|waiting|wait|verifying|restarting|generating|modifying|fetching|reading|analyzing|inspecting|cleaning|completed\s+task|subagent\s+updating|subagent\s+active|planner\s+is\s+still|plan\s+generation|generation\s+is\s+progressing|still\s+awaiting|streaming|gemini\s+\d.*streaming)[^\n]*$', s_clean, re.IGNORECASE):
        return True
    if re.match(r'^\s*(?:[-*+]\s*)?(?:📄\s*)?(?:Reference(?:\s+link)?(?:\s+to\s+(?:the\s+)?thread\s+artifact)?:\s*|Current\s+Thread:\s*)?\[`?(?:thread|conversation_response)\.md`?\]\([^\)]*\)\s*$', s_clean, re.IGNORECASE):
        return True
    return False


def clean_agent_content(text: str) -> str:
    """Strip out thread.md / conversation_response.md artifact links, transient status lines, and clutter."""
    if not text:
        return text

    # Strip system banners and background execution wrappers
    text = re.sub(r'All background operations have completed\.[\s\S]*?</ADDITIONAL_METADATA>', '', text)
    text = re.sub(r'<USER_REQUEST>[\s\S]*?</USER_REQUEST>', '', text)
    text = re.sub(r'<ADDITIONAL_METADATA>[\s\S]*?</ADDITIONAL_METADATA>', '', text)
    text = re.sub(r'<SYSTEM_MESSAGE>[\s\S]*?</SYSTEM_MESSAGE>', '', text)
    text = re.sub(r'<USER_SETTINGS_CHANGE>[\s\S]*?</USER_SETTINGS_CHANGE>', '', text)
    text = re.sub(r'\[Message\] timestamp=[^\n]*', '', text)

    footer_link_re = re.compile(
        r'^\s*(?:[-*+]\s*)?(?:📄\s*)?(?:Reference(?:\s+link)?(?:\s+to\s+(?:the\s+)?thread\s+artifact)?:\s*|Current\s+Thread:\s*)?\[`?(?:thread|conversation_response)\.md`?\]\([^\)]*\)(?:\s*\[[^\]]*\]\([^\)]*\))*\s*$',
        re.IGNORECASE
    )
    divider_re = re.compile(r'^\s*(?:-{3,}|\*{3,}|_{3,})\s*$')

    lines = text.splitlines()
    drop = [False] * len(lines)

    for i, line in enumerate(lines):
        if footer_link_re.match(line):
            drop[i] = True
            if i > 0 and divider_re.match(lines[i - 1]):
                drop[i - 1] = True
            continue

        if is_transient_status_line(line):
            drop[i] = True
            continue

    filtered_lines = []
    for i, line in enumerate(lines):
        if drop[i]:
            continue
        if line.strip() in ('-', '*', '+'):
            continue
        filtered_lines.append(line)

    result = '\n'.join(filtered_lines)
    result = re.sub(r'\n{3,}', '\n\n', result).strip()
    return result


def filter_transient_lines(text: str) -> str:
    """If text contains non-transient content, strip ALL transient lines while preserving paragraph spacing.
    If text contains ONLY transient content, retain ONLY the latest.
    """
    lines = text.splitlines()
    has_substantive = any(l.strip() and not is_transient_status_line(l) for l in lines)
    if has_substantive:
        filtered = [l for l in lines if not l.strip() or not is_transient_status_line(l)]
        res = '\n'.join(filtered)
        return re.sub(r'\n{3,}', '\n\n', res).strip()

    transient = [l for l in lines if is_transient_status_line(l)]
    if transient:
        return transient[-1]
    return text


def normalize_blockquotes(text: str) -> str:
    """Ensure clean blockquote formatting without splitting internal lines.
    Self-heals fragmented blockquotes where empty blank lines separated quote lines.
    """
    if not text:
        return text

    lines = text.splitlines()
    new_lines = []
    in_quote = False

    for line in lines:
        stripped = line.strip()
        is_quote = stripped.startswith('>')

        if not stripped and in_quote:
            # Retain quote block continuation on empty lines
            new_lines.append('>')
            continue

        if is_quote:
            if not in_quote:
                if new_lines and new_lines[-1].strip():
                    new_lines.append('')
                in_quote = True
        else:
            if in_quote and stripped:
                if new_lines and new_lines[-1].strip():
                    new_lines.append('')
                in_quote = False

        new_lines.append(line)

    return '\n'.join(new_lines)


def normalize_tables(text: str) -> str:
    """Ensure clean markdown table boundaries without splitting rows."""
    if not text:
        return text

    lines = text.splitlines()
    new_lines = []
    in_table = False

    for line in lines:
        stripped = line.strip()
        is_table = stripped.startswith('|') and stripped.endswith('|')

        if is_table:
            if not in_table:
                if new_lines and new_lines[-1].strip():
                    new_lines.append('')
                in_table = True
        else:
            if in_table and stripped:
                if new_lines and new_lines[-1].strip():
                    new_lines.append('')
                in_table = False

        new_lines.append(line)

    return '\n'.join(new_lines)


def normalize_headings(text: str) -> str:
    """Ensure blank line before headings and proper heading levels."""
    if not text:
        return text

    lines = text.splitlines()
    new_lines = []

    for line in lines:
        m = re.match(r'^(#{1,6})\s+(.*)', line)
        if m:
            level = len(m.group(1))
            demoted_level = max(level, 3)
            heading_prefix = '#' * demoted_level
            line = f"{heading_prefix} {m.group(2)}"
            if new_lines and new_lines[-1].strip():
                new_lines.append('')
        new_lines.append(line)

    return '\n'.join(new_lines)


def heal_markup_spans(text: str) -> str:
    """Self-healing: balance open and closed span tags to prevent DOM corruption."""
    if not text:
        return text

    open_spans = len(re.findall(r'<span\b[^>]*>', text, re.IGNORECASE))
    close_spans = len(re.findall(r'</span>', text, re.IGNORECASE))

    if open_spans > close_spans:
        text = text + ('\n</span>' * (open_spans - close_spans))
    elif close_spans > open_spans:
        diff = close_spans - open_spans
        for _ in range(diff):
            text = re.sub(r'</span>\s*$', '', text, count=1, flags=re.IGNORECASE)

    return text


def clean_agent_response(text: str) -> str:
    """
    1. Clean agent content (links/status lines).
    2. Normalize headings (idempotent spacing & demotion).
    3. Normalize tables (idempotent spacing).
    4. Normalize blockquotes (self-healing unbroken quote blocks).
    5. Strip orphan status/context lines.
    6. Balance code fences and escape currency dollar signs.
    """
    text = clean_agent_content(text)
    if not text:
        return ''

    text = normalize_headings(text)
    text = normalize_tables(text)
    text = normalize_blockquotes(text)

    # Ensure blank lines before and after **Thread Metrics:**
    text = re.sub(r'([^\n])\n(\*\*Thread Metrics:\*\*)', r'\1\n\n\2', text)
    text = re.sub(r'(\*\*Thread Metrics:\*\*)\n([^\n])', r'\1\n\n\2', text)

    # Strip orphan status/context lines
    lines = []
    orphan_pattern = re.compile(
        r'^(?:Thread\s+context\s+logged\s+at:|Thread\s+artifact:|Thread\s+logged\s+at:|Reference\s+link:)',
        flags=re.IGNORECASE
    )
    for line in text.splitlines():
        if orphan_pattern.match(line.strip()):
            continue
        lines.append(line)

    result = '\n'.join(lines).strip()
    result = re.sub(r'\n{3,}', '\n\n', result)
    result = balance_code_fences(result)
    result = escape_currency_dollar_signs(result)
    return result


def resolve_app_data_dir(conv_id: str, default_app_data_dir: Path) -> Path:
    if (default_app_data_dir / 'brain' / conv_id).exists():
        return default_app_data_dir
    cli_app_data_dir = Path.home() / '.gemini/antigravity-cli'
    if (cli_app_data_dir / 'brain' / conv_id).exists():
        return cli_app_data_dir
    return default_app_data_dir


# ─── Forking ──────────────────────────────────────────────────────────────────

def render_fork_file(items: list, output_path: Path):
    """Render a forked thread.md for undone exchanges."""
    exchange_blocks = []
    for item in items:
        if item['type'] == 'exchange':
            exchange_blocks.append(make_exchange_block(item['users'], clean_agent_response(item['agent_content']), item['agent_time']))

    separator = '\n\n---\n\n'
    doc = separator.join(exchange_blocks) + '\n'
    output_path.write_text(doc, encoding='utf-8')


def make_fork_notice_block(fork_path: Path, undone_count: int) -> str:
    """Render a fork notice block."""
    return (
        f"> [!NOTE]\n"
        f"> 🔀 **Undone Branch**: {undone_count} turn(s) were undone at this point. "
        f"View the [forked thread](file://{fork_path})."
    )


def fmt_time(iso_str: str) -> str:
    """Convert ISO8601 timestamp string to '2:05pm' format."""
    try:
        dt = datetime.fromisoformat(iso_str.strip())
        hour = dt.hour % 12 or 12
        ampm = 'am' if dt.hour < 12 else 'pm'
        return f"{hour}:{dt.minute:02d}{ampm}"
    except Exception:
        return ''


# ─── Transcript Parsing ───────────────────────────────────────────────────────

def strip_html_tags(text: str) -> str:
    """Remove all HTML tags from text, preserving the text content between them."""
    return re.sub(r'<[^>]+>', '', text)


def decode_html_entities(text: str) -> str:
    """Decode common HTML entities back to their characters."""
    import html as html_mod
    return html_mod.unescape(text)


def extract_user_input(content: str):
    """Extract (prompt_text, local_timestamp_str) from a USER_INPUT step content.

    Returns formatted user input with styled selection cards and comment text.
    """
    # Find timestamp if present
    ts = re.search(r'current local time is:\s*([^\n<]+)', content)
    time = fmt_time(ts.group(1)) if ts else ''

    # Clean out internal IDE system tags
    cleaned = content
    for tag in ['USER_SETTINGS_CHANGE', 'user_rules', 'context', 'system', 'workflows', 'skills', 'ADDITIONAL_METADATA']:
        cleaned = re.sub(fr'<{tag}>.*?</{tag}>', '', cleaned, flags=re.DOTALL)

    # Extract all artifact comment blocks: Selection + Comment pairs
    comment_blocks = []
    sel_cmt_pattern = re.compile(
        r'Selection:\s*\n(.*?)\n+Comment:\s*(".*?"|[^\n]+(?:\n(?!\n*(?:Selection:|<USER_REQUEST>))[^\n]+)*)',
        re.DOTALL
    )
    for m in sel_cmt_pattern.finditer(cleaned):
        sel_raw = m.group(1).strip()
        cmt_raw = m.group(2).strip()
        if cmt_raw.startswith('"') and cmt_raw.endswith('"'):
            cmt_raw = cmt_raw[1:-1].strip()
        comment_blocks.append((sel_raw, cmt_raw))

    # Extract user request prompts
    user_requests = re.findall(r'<USER_REQUEST>(.*?)</USER_REQUEST>', cleaned, flags=re.DOTALL)
    if user_requests:
        req_prompt = '\n\n'.join(r.strip() for r in user_requests if r.strip())
    else:
        # Fallback: strip comments header and tags
        req_prompt = re.sub(r'Comments on artifact URI:.*', '', cleaned, flags=re.DOTALL)
        req_prompt = re.sub(r'</?USER_REQUEST>', '', req_prompt).strip()

    # If there were comment blocks, strip them from req_prompt to prevent duplication
    if comment_blocks:
        req_prompt = re.sub(r'Comments on artifact URI:[^\n]*', '', req_prompt)
        req_prompt = sel_cmt_pattern.sub('', req_prompt).strip()

    formatted_parts = []

    for sel_raw, cmt_raw in comment_blocks:
        quote_lines = []
        for line in sel_raw.split('\n'):
            line_clean = strip_html_tags(line)
            line_clean = decode_html_entities(line_clean)
            line_clean = line_clean.lstrip('>').strip()
            quote_lines.append(line_clean)

        cmt_clean = strip_html_tags(cmt_raw)
        cmt_clean = decode_html_entities(cmt_clean).strip()

        if quote_lines:
            quote_text = '<br>'.join(quote_lines).strip()
            quote_html = f'<span style="display: block; background: rgba(0, 0, 0, 0.25); border-left: 3px solid rgba(130, 115, 220, 0.7); padding: 6px 10px; margin-bottom: 8px; border-radius: 4px; font-size: 13px; opacity: 0.9; white-space: pre-wrap;">{quote_text}</span>'
            if cmt_clean:
                formatted_parts.append(f"{quote_html}<br>💬 **Comment**: {cmt_clean}")
            else:
                formatted_parts.append(quote_html)
        elif cmt_clean:
            formatted_parts.append(f"💬 **Comment**: {cmt_clean}")

    if req_prompt:
        req_prompt_clean = decode_html_entities(req_prompt).strip()
        if req_prompt_clean:
            formatted_parts.append(req_prompt_clean)

    # Detect artifact approvals
    if "The user has approved this document." in cleaned:
        uri_match = re.search(r'Comments on artifact URI:\s*(file://[^\s\n]+)', cleaned)
        if uri_match:
            uri = uri_match.group(1)
            artifact_approval = f"✅ **Approved Plan/Artifact**: [{uri.split('/')[-1]}]({uri})"
            formatted_parts.append(artifact_approval)
        else:
            formatted_parts.append("✅ **Approved Plan/Artifact**")

    if len(formatted_parts) > 1:
        divider = '<span style="display: block; margin: 8px 0; border: none; border-top: 1px solid rgba(130, 115, 220, 0.35);"></span>'
        prompt = divider.join(formatted_parts).strip()
    elif len(formatted_parts) == 1:
        prompt = formatted_parts[0].strip()
    elif cleaned.strip():
        prompt = cleaned.strip()
    else:
        prompt = ''
    return prompt, time


def parse_exchanges(transcript_path: Path, conv_id: str = '', app_data_dir: Path = None) -> list:
    """
    Parse transcript.jsonl into a list of exchanges, handling undos.
    """
    if transcript_path.name == 'transcript.jsonl':
        full_path = transcript_path.with_name('transcript_full.jsonl')
        if full_path.exists() and full_path.stat().st_size > 0:
            transcript_path = full_path
    active_items = []
    pending_users = []
    current_agent_time = ''
    accumulated_text = []
    latest_tool_action = None
    latest_transient_status = None
    current_agent_epoch = 0.0
    history_dir = app_data_dir / 'brain' / conv_id / 'history' if (app_data_dir and conv_id) else None

    if not transcript_path.exists():
        return []

    def flush_current_turn():
        nonlocal pending_users, accumulated_text, latest_tool_action, latest_transient_status, current_agent_time, active_items, current_agent_epoch
        if pending_users:
            history_turn_text = load_agent_response(history_dir, len([i for i in active_items if i['type'] == 'exchange']) + 1) if history_dir else ''
            if accumulated_text:
                agent_text = '\n\n'.join(t for t in accumulated_text if t.strip()).strip()
            elif history_turn_text:
                agent_text = history_turn_text
            elif latest_tool_action:
                agent_text = f"✅ *Action completed: {latest_tool_action}*"
            else:
                agent_text = latest_transient_status or ''

            min_step = pending_users[0]['step']
            max_step = pending_users[-1]['step']
            start_epoch = pending_users[0].get('epoch', 0.0) if pending_users else 0.0
            active_items.append({
                'type': 'exchange',
                'users': pending_users[:],
                'agent_turn': len([i for i in active_items if i['type'] == 'exchange']) + 1,
                'agent_content': agent_text,
                'agent_time': current_agent_time,
                'is_in_progress': (not accumulated_text and not history_turn_text),
                'tool_action': latest_tool_action,
                'transient_status': latest_transient_status,
                'start_epoch': start_epoch,
                'end_epoch': current_agent_epoch,
                'min_step': min_step,
                'max_step': max_step
            })
            pending_users = []
            current_agent_time = ''
            accumulated_text = []
            latest_tool_action = None
            latest_transient_status = None

    with open(transcript_path) as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                continue

            t = obj.get('type', '')
            idx = obj.get('step_index', 0)

            if t == 'USER_INPUT':
                if pending_users and (accumulated_text or (history_dir and load_agent_response(history_dir, len([i for i in active_items if i['type'] == 'exchange']) + 1))):
                    flush_current_turn()

                # Check for Undo/Rewind
                undone = [
                    item for item in active_items
                    if item.get('min_step', 0) >= idx or item.get('max_step', 0) >= idx
                ]
                if undone:
                    undone.sort(key=lambda x: x.get('min_step', 0))
                    if conv_id and app_data_dir:
                        fork_dir = app_data_dir / 'brain' / conv_id / 'forks'
                        fork_dir.mkdir(parents=True, exist_ok=True)
                        fork_path = fork_dir / f'fork_step_{idx}.md'
                        count = 1
                        while fork_path.exists():
                            fork_path = fork_dir / f'fork_step_{idx}_{count}.md'
                            count += 1

                        render_fork_file(undone, fork_path)
                        active_items = [i for i in active_items if i not in undone]
                        active_items.append({
                            'type': 'fork_notice',
                            'fork_step': idx,
                            'fork_path': fork_path,
                            'undone_count': len(undone)
                        })

                created_iso = obj.get('created_at') or obj.get('timestamp') or ''
                user_epoch = iso_to_epoch(created_iso)
                prompt, ts = extract_user_input(obj.get('content', ''))
                if prompt:
                    pending_users.append({'prompt': prompt, 'time': ts, 'step': idx, 'epoch': user_epoch})

            elif t == 'PLANNER_RESPONSE':
                created_iso = obj.get('created_at') or obj.get('timestamp') or ''
                if created_iso:
                    current_agent_epoch = iso_to_epoch(created_iso)
                    current_agent_time = fmt_time(created_iso)

                tool_calls = obj.get('tool_calls')
                has_tool_calls = bool(tool_calls and isinstance(tool_calls, list) and len(tool_calls) > 0)
                if has_tool_calls:
                    first = tool_calls[0]
                    args = first.get('args', {})
                    latest_tool_action = args.get('toolAction') or args.get('toolSummary') or first.get('name')

                content = obj.get('content', '') or obj.get('text', '')
                if content and isinstance(content, str) and content.strip():
                    cleaned = clean_agent_content(content.strip())
                    if cleaned:
                        if is_transient_status_line(cleaned):
                            latest_transient_status = cleaned
                        elif has_tool_calls:
                            pass
                        else:
                            accumulated_text = [cleaned]

    # Flush final turn at EOF
    flush_current_turn()

    return active_items


# ─── Response Files ───────────────────────────────────────────────────────────

def load_agent_response(history_dir: Path, turn_n: int) -> str:
    """Load agent response markdown for turn N (history/turn_N.md)."""
    if not history_dir:
        return ''
    path = history_dir / f'turn_{turn_n}.md'
    if path.exists():
        return clean_agent_content(path.read_text().strip())
    return ''


def next_turn_number(history_dir: Path) -> int:
    """Return the next available turn number (max existing + 1, or 1)."""
    if not history_dir:
        return 1
    existing = list(history_dir.glob('turn_*.md'))
    if not existing:
        return 1
    nums = []
    for p in existing:
        m = re.match(r'turn_(\d+)\.md', p.name)
        if m:
            nums.append(int(m.group(1)))
    return max(nums) + 1 if nums else 1


# ─── Pure Markdown Generation ─────────────────────────────────────────────────

def format_prompt(raw_prompt: str) -> str:
    """Format a user prompt for display in pure markdown using span containers.

    Preserves exact newlines, multiline formatting, and code blocks using <br>
    so Markdown parsers do not break inline styled span containers into multiple paragraphs.
    """
    text = raw_prompt.strip()

    # Normalize newlines
    text = text.replace('\r\n', '\n')
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    text = balance_code_fences(text)
    text = escape_currency_dollar_signs(text)

    # Convert newlines to <br> to preserve multiline structure inside <span>
    text = text.replace('\n', '<br>')

    return text


def make_exchange_block(users: list, agent_content: str, agent_time: str, is_newest: bool = False, tool_action: str = None, transient_status: str = None) -> str:
    """Build a single exchange block using styled span containers."""
    user_blocks = []
    for u in users:
        p = format_prompt(u['prompt']).strip()
        if p:
            user_blocks.append(p)

    divider = '<span style="display: block; margin: 8px 0; border: none; border-top: 1px solid rgba(130, 115, 220, 0.35);"></span>'
    user_md = divider.join(user_blocks) if len(user_blocks) > 1 else (user_blocks[0] if user_blocks else '')
    a_time = agent_time if agent_time else ''
    agent_text = clean_agent_response(agent_content)
    if not agent_text:
        if is_newest:
            if tool_action:
                agent_text = f"⏳ *Executing: {tool_action}...*"
            elif transient_status:
                agent_text = f"⏳ *{transient_status}*"
            else:
                agent_text = "*Thinking...*"
        else:
            agent_text = "✅ *Turn completed.*"

    user_time_str = f"Sent at {users[0]['time']}" if users and users[0].get('time') else "Sent at "
    user_span = (
        f'<span title="{user_time_str}" style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">{user_md}</span>'
    )

    agent_span = (
        f'\n\n<span title="Responded at {a_time}" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">\n\n'
        f'{agent_text}\n\n'
        f'</span>\n\n'
    )

    style = 'style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;"'
    if is_newest:
        style = 'style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 48px; overflow-wrap: anywhere; word-break: break-word;"'

    return f'<span {style}>\n\n{user_span}\n\n{agent_span}\n\n</span>'


def get_subagent_progress(conv_id: str, app_data_dir: Path) -> str | None:
    """Check if this conversation has active subagents and return their status."""
    transcript_path = app_data_dir / 'brain' / conv_id / '.system_generated/logs/transcript.jsonl'
    if not transcript_path.exists():
        return None

    subagent_ids = set()
    try:
        with open(transcript_path) as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    content = obj.get('content', '')
                    if re.search(r'(?:invoke_subagent|agy_start|agy)\b', content):
                        matches = re.findall(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', content)
                        for m in matches:
                            if m != conv_id:
                                subagent_ids.add(m)
                except: continue
    except: return None

    for sub_id in subagent_ids:
        sub_transcript = app_data_dir / 'brain' / sub_id / '.system_generated/logs/transcript.jsonl'
        if not sub_transcript.exists():
            continue

        try:
            lines = subprocess.check_output(['tail', '-n', '20', str(sub_transcript)], text=True).splitlines()

            latest_thought = None
            for line in reversed(lines):
                if 'PLANNER_RESPONSE' in line or 'toolAction' in line:
                    try:
                        obj = json.loads(line)
                        if 'toolAction' in obj:
                            latest_thought = f"🔄 **Subagent Activity**: {obj['toolAction']}"
                            break
                        elif 'PLANNER_RESPONSE' in obj:
                            content = obj['PLANNER_RESPONSE'].get('content', '') or obj.get('content', '')
                            if content and not is_transient_status_line(content):
                                latest_thought = f"💭 **Subagent Thought**: {content[:100]}..."
                                break
                    except: continue
            if latest_thought:
                return latest_thought
        except: continue

    return None


def make_exchange_block_with_progress(users: list, agent_content: str, agent_time: str, subagent_progress: str | None, is_newest: bool = False, tool_action: str = None, transient_status: str = None) -> str:
    """Build a single exchange block with potential subagent progress."""
    base_block = make_exchange_block(users, agent_content, agent_time, is_newest, tool_action, transient_status)
    if subagent_progress:
        return f"{base_block}\n\n> [!NOTE]\n> 🔄 **Subagent Active**: {subagent_progress}"
    return base_block


# ─── Main ─────────────────────────────────────────────────────────────────────

def generate(conv_id: str, title: str, app_data_dir: Path, output_path_override: Path = None):
    app_data_dir = resolve_app_data_dir(conv_id, app_data_dir)
    base            = app_data_dir / 'brain' / conv_id
    transcript_path = base / '.system_generated/logs/transcript_full.jsonl'
    if not transcript_path.exists() or transcript_path.stat().st_size == 0:
        transcript_path = base / '.system_generated/logs/transcript.jsonl'
    history_dir     = base / 'history'

    if output_path_override:
        output_path = output_path_override
    else:
        output_path = base / 'thread.md'

    history_dir.mkdir(parents=True, exist_ok=True)
    if output_path.parent:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    if not transcript_path.exists():
        return []

    exchanges = parse_exchanges(transcript_path, conv_id, app_data_dir)
    if not exchanges:
        return output_path

    from postflight_lib import compute_thread_metrics, format_metrics_table, format_nav_toggle

    doc_content = []
    
    # Thread Started Banner (placed at the top of the oldest exchange block)
    banner = f'<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — {datetime.now().strftime("%B %d, %Y")}</span>'

    # Outer container with custom styles
    doc_content.append('<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">')

    reversed_exchanges = list(reversed(exchanges))
    for i, item in enumerate(reversed_exchanges):
        if item['type'] == 'exchange':
            agent_content = item.get('agent_content', '').strip()
            # Drop empty historical exchanges (only newest exchange i==0 can be in-progress)
            if not agent_content and i > 0:
                continue

            agent_content = clean_agent_content(agent_content)

            # Check for subagent progress
            progress = None
            if i == 0:
                progress = get_subagent_progress(conv_id, app_data_dir)

            block = make_exchange_block_with_progress(
                item['users'],
                agent_content,
                item['agent_time'],
                progress,
                i == 0,
                item.get('tool_action'),
                item.get('transient_status')
            )

            # Prepend banner to the oldest exchange (which is the last in the reversed list)
            if i == len(reversed_exchanges) - 1:
                block = f"{banner}\n\n{block}"

            doc_content.append(block)
        elif item['type'] == 'fork_notice':
            doc_content.append(make_fork_notice_block(item['fork_path'], item['undone_count']))

    # Metrics table at bottom (pinned) + nav toggle pill
    metrics = compute_thread_metrics(conv_id)
    metrics_table = format_metrics_table(metrics, conv_id)
    kanban_path = str(Path(app_data_dir) / "brain" / conv_id / "kanban.md") if conv_id and app_data_dir else None
    nav_toggle = format_nav_toggle(kanban_path=kanban_path) if kanban_path else ""
    # metrics_table is raw markdown (blank lines preserved) — nav_toggle is pure HTML positioned
    # within the footer span so it never wraps the table markup.
    pinned_metrics = f'<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">\n\n{metrics_table.strip()}\n\n{nav_toggle}\n\n</span>'
    doc_content.append(pinned_metrics)

    doc_content.append('</span>')

    rendered_doc = '\n\n'.join(doc_content)
    try:
        from link_formatter import enrich_file_links
        rendered_doc = enrich_file_links(rendered_doc)
    except Exception:
        pass

    # Self-healing markup pass on rendered document
    rendered_doc = heal_markup_spans(rendered_doc)
    rendered_doc = balance_code_fences(rendered_doc)

    tmp_path = output_path.with_name(f"{output_path.name}.tmp")
    tmp_path.write_text(rendered_doc, encoding='utf-8')
    tmp_path.replace(output_path)
    print(f"Written: {output_path}")
    print(f"  {len(exchanges)} total exchanges rendered in chronological order")
    return output_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate thread.md from transcript + turn response files.'
    )
    parser.add_argument('conv_id',        help='Conversation ID (UUID)')
    parser.add_argument('--title',        default='Conversation', help='Thread title')
    parser.add_argument('--app-data-dir', default=str(APP_DATA_DIR))
    parser.add_argument('--output',       type=Path, help='Custom output path')
    parser.add_argument('--save-turn',    action='store_true',
                        help='Read markdown from stdin and save as next turn_N.md before generating')
    args = parser.parse_args()

    app_dir = Path(args.app_data_dir)
    history_dir = app_dir / 'brain' / args.conv_id / 'history'

    if args.save_turn:
        history_dir.mkdir(parents=True, exist_ok=True)
        n = next_turn_number(history_dir)
        content = sys.stdin.read().strip()
        if content:
            (history_dir / f'turn_{n}.md').write_text(content)
            print(f"Saved turn_{n}.md")

    generate(args.conv_id, args.title, app_dir, args.output)
