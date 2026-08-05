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
from datetime import datetime
from pathlib import Path

def clean_agent_content(text: str) -> str:
    """Strip out thread.md / conversation_response.md artifact links and associated clutter lines from agent response text."""
    if not text:
        return text

    link_pattern = re.compile(
        r'\[`?(?:thread|conversation_response)\.md`?\]\([^\)]*\)|'
        r'\[[^\]]*\]\([^\)]*?/(?:thread|conversation_response)\.md(?:#[^\)]*)?\)',
        flags=re.IGNORECASE
    )

    text = link_pattern.sub('', text)

    prefix_pattern = re.compile(
        r'^\s*(?:[-*+]\s*|\d+\.\s*)?'
        r'(?:reference\s+link(?:\s+to(?:\s+the)?\s+thread\s+artifact)?|thread(?:\s+artifact)?(?:\s+link)?|thread\.md|conversation_response\.md)?'
        r'\s*:?\s*$',
        flags=re.IGNORECASE
    )

    cleaned_lines = []
    for line in text.splitlines():
        if prefix_pattern.match(line):
            continue
        cleaned_lines.append(line.rstrip())

    result = '\n'.join(cleaned_lines)
    result = re.sub(r'\n{3,}', '\n\n', result).strip()
    return result


APP_DATA_DIR = Path.home() / '.gemini/antigravity'


# ─── Forking ──────────────────────────────────────────────────────────────────

def render_fork_file(items: list, output_path: Path):
    """Render a forked thread.md for undone exchanges."""
    exchange_blocks = []
    for item in items:
        if item['type'] == 'exchange':
            exchange_blocks.append(make_exchange_block(item['users'], item['agent_content'], item['agent_time']))
    
    separator = '\n\n---\n\n'
    doc = separator.join(exchange_blocks) + '\n'
    output_path.write_text(doc)


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
    """Decode common HTML entities back to their characters.
    Only decodes entities that appear in Antigravity artifact selections.
    """
    import html as html_mod
    return html_mod.unescape(text)


def extract_user_input(content: str):
    """Extract (prompt_text, local_timestamp_str) from a USER_INPUT step content.
    
    Returns the user's prompt as clean plain text (no HTML escaping, no HTML tags).
    Artifact comments are formatted as markdown blockquotes + comment text.
    """
    # Find timestamp if present
    ts = re.search(r'current local time is:\s*([^\n<]+)', content)
    time = fmt_time(ts.group(1)) if ts else ''

    # Clean out internal IDE system tags
    for tag in ['USER_SETTINGS_CHANGE', 'user_rules', 'context', 'system', 'workflows', 'skills', 'ADDITIONAL_METADATA']:
        cleaned = re.sub(fr'<{tag}>.*?</{tag}>', '', content, flags=re.DOTALL)
    cleaned = content if 'cleaned' not in locals() else cleaned

    # Extract artifact comments if present
    # The IDE sends: "Comments on artifact URI: ...\n\nSelection:\n>...\n\nComment: \"...\""
    comment_blocks = []
    comment_match = re.search(
        r'Selection:\s*\n(.*?)\n\nComment:\s*(.+?)(?=\n<USER_REQUEST>|\Z)',
        cleaned, re.DOTALL
    )
    if comment_match:
        sel_raw = comment_match.group(1).strip()
        cmt_raw = comment_match.group(2).strip()
        # Strip surrounding quotes from comment
        if cmt_raw.startswith('"') and cmt_raw.endswith('"'):
            cmt_raw = cmt_raw[1:-1].strip()
        comment_blocks.append((sel_raw, cmt_raw))

    # Extract user request prompts
    user_requests = re.findall(r'<USER_REQUEST>(.*?)</USER_REQUEST>', cleaned, flags=re.DOTALL)
    if user_requests:
        req_prompt = '\n\n---\n\n'.join(r.strip() for r in user_requests)
    else:
        # Fallback: strip comment/artifact URI prefix and tags
        req_prompt = re.sub(r'Comments on artifact URI:.*', '', cleaned, flags=re.DOTALL)
        req_prompt = re.sub(r'</?USER_REQUEST>', '', req_prompt).strip()

    # Build formatted parts
    formatted_parts = []

    for sel_raw, cmt_raw in comment_blocks:
        # Clean selection text:
        # 1. Strip HTML tags (captures <td>, </td>, etc. from artifact selections)
        # 2. Decode HTML entities (captures &lt; -> <, &#x27; -> ', &amp; -> &, etc.)
        # 3. Strip leading > characters (markdown quote prefixes from the IDE)
        quote_lines = []
        for line in sel_raw.split('\n'):
            line_clean = strip_html_tags(line)
            line_clean = decode_html_entities(line_clean)
            line_clean = line_clean.lstrip('>').strip()
            if line_clean:
                quote_lines.append(line_clean)

        # Decode entities in comment text too
        cmt_clean = strip_html_tags(cmt_raw)
        cmt_clean = decode_html_entities(cmt_clean)

        # Format as markdown blockquote
        if quote_lines:
            quote_body = '\n'.join(f'> {line}' for line in quote_lines)
            if cmt_clean:
                formatted_parts.append(f"{quote_body}\n>\n> 💬 **Comment**: {cmt_clean}")
            else:
                formatted_parts.append(quote_body)
        elif cmt_clean:
            formatted_parts.append(f"💬 **Comment**: {cmt_clean}")

    if req_prompt:
        # Clean any stray HTML tags from the prompt itself
        req_prompt_clean = strip_html_tags(req_prompt).strip()
        # Decode any HTML entities that leaked in
        req_prompt_clean = decode_html_entities(req_prompt_clean).strip()
        if req_prompt_clean:
            formatted_parts.append(req_prompt_clean)

    # Join comment blocks and user prompt with spacing
    if len(formatted_parts) > 1:
        prompt = '\n\n---\n\n'.join(formatted_parts).strip()
    else:
        prompt = '\n\n'.join(formatted_parts).strip()
    return prompt, time


def parse_exchanges(transcript_path: Path, conv_id: str = '', app_data_dir: Path = None) -> list:
    """
    Parse transcript.jsonl into a list of exchanges, handling undos.
    """
    exchanges = []
    active_items = []
    pending_users = []
    current_agent_time = ''
    current_agent_content = []

    if not transcript_path.exists():
        return []

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
                # Check for Undo/Rewind
                undone = [
                    item for item in active_items
                    if item.get('min_step', 0) >= idx or item.get('max_step', 0) >= idx
                ]
                if undone:
                    # Sort by step, filter and move to fork
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

                prompt, ts = extract_user_input(obj.get('content', ''))
                if prompt:
                    pending_users.append({'prompt': prompt, 'time': ts, 'step': idx})

            elif t == 'PLANNER_RESPONSE':
                if not pending_users and not current_agent_content:
                    continue
                
                created = obj.get('created_at') or obj.get('timestamp') or ''
                if created and not current_agent_time:
                    current_agent_time = fmt_time(created)

                content = obj.get('content', '') or obj.get('text', '')
                if content and isinstance(content, str) and content.strip():
                    cleaned = clean_agent_content(content.strip())
                    if not cleaned:
                        continue
                    if not current_agent_content or current_agent_content[-1] != cleaned:
                        current_agent_content.append(cleaned)

                # If we have content and it ends a turn, flush to active
                if pending_users:
                    agent_text = '\n\n'.join(c for c in current_agent_content if c.strip()).strip()
                    min_step = pending_users[0]['step']
                    max_step = pending_users[-1]['step']
                    active_items.append({
                        'type': 'exchange',
                        'users': pending_users[:],
                        'agent_turn': len([i for i in active_items if i['type'] == 'exchange']) + 1,
                        'agent_content': agent_text,
                        'agent_time': current_agent_time,
                        'min_step': min_step,
                        'max_step': max_step
                    })
                    pending_users = []
                    current_agent_time = ''
                    current_agent_content = []

    return active_items


# ─── Response Files ───────────────────────────────────────────────────────────

def load_agent_response(history_dir: Path, turn_n: int, fallback_text: str = '') -> str:
    """Load agent response markdown for turn N (history/turn_N.md)."""
    path = history_dir / f'turn_{turn_n}.md'
    if path.exists():
        content = path.read_text().strip()
        if content:
            return clean_agent_content(content)

    if fallback_text and fallback_text.strip():
        return clean_agent_content(fallback_text.strip())

    return '*(response in progress or not recorded)*'


def next_turn_number(history_dir: Path) -> int:
    """Return the next available turn number (max existing + 1, or 1)."""
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
    """Format a user prompt for display in pure markdown.
    
    No HTML escaping — the content is plain text rendered as markdown.
    Long prompts get wrapped in a <details> collapsible.
    """
    text = raw_prompt.strip()
    
    # Ensure code blocks are on their own lines to prevent markdown bleed
    # Pad fenced backticks with a leading newline if preceded by text
    text = re.sub(r'([^\n])```', r'\1\n```', text)
    # Pad ending backticks with a trailing newline if followed by text
    text = re.sub(r'```([^\n]*)\n([^\n])', r'```\1\n\n\2', text)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    
    lines = text.split('\n')

    # Only collapse into <details> if truly massive (> 800 chars or > 12 lines)
    if len(text) > 800 or len(lines) > 12:
        summary_lines = lines[:5]
        summary_text = '\n'.join(summary_lines)
        if len(summary_text) > 350:
            summary_text = summary_text[:350]
        remainder = text[len(summary_text):].strip()
        return f"<details>\n<summary>\n\n{summary_text.strip()}...\n\n</summary>\n\n{remainder}\n\n</details>"

    return text


def make_exchange_block(users: list, agent_content: str, agent_time: str) -> str:
    """Build a single exchange block using pure markdown (no HTML tables)."""
    user_blocks = []
    for u in users:
        p = format_prompt(u['prompt'])
        t = f" — *{u['time']}*" if u['time'] else ''
        user_blocks.append(f"#### 🧔 You{t}\n\n{p}")

    user_md = '\n\n'.join(user_blocks)
    a_time = f" — *{agent_time}*" if agent_time else ''
    agent_text = clean_agent_content(agent_content)
    if not agent_text:
        agent_text = '*(response in progress or not recorded)*'
    agent_md = f"#### 🤖 Agent{a_time}\n\n{agent_text}"

    return f"{user_md}\n\n{agent_md}"


# ─── Main ─────────────────────────────────────────────────────────────────────

def generate(conv_id: str, title: str, app_data_dir: Path, output_path_override: Path = None):
    base            = app_data_dir / 'brain' / conv_id
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

    # No longer needed to load here
    # agent_content = load_agent_response(...)
    # The loading moved into the generation loop

    # Reverse chronological order: newest exchange at top
    reversed_items = list(reversed(exchanges))

    content_blocks = []
    for item in reversed_items:
        if item['type'] == 'exchange':
            # Need to reload response in case of updates
            agent_content = load_agent_response(history_dir, item.get('agent_turn', 0), item.get('agent_content', ''))
            content_blocks.append(make_exchange_block(item['users'], agent_content, item['agent_time']))
        elif item['type'] == 'fork_notice':
            content_blocks.append(make_fork_notice_block(item['fork_path'], item['undone_count']))

    separator = '\n\n---\n\n'
    doc = separator.join(content_blocks) + '\n'

    output_path.write_text(doc)
    print(f"Written: {output_path}")
    print(f"  {len(exchanges)} total exchanges rendered in reverse chronological order")
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
