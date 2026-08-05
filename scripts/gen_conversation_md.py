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

APP_DATA_DIR = Path.home() / '.gemini/antigravity'


# ─── Timestamp ────────────────────────────────────────────────────────────────

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

    # Clean out metadata block
    cleaned = re.sub(r'<ADDITIONAL_METADATA>.*?</ADDITIONAL_METADATA>', '', content, flags=re.DOTALL)

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

    # Extract user request prompt inside <USER_REQUEST>
    req = re.search(r'<USER_REQUEST>(.*?)</USER_REQUEST>', cleaned, re.DOTALL)
    if req:
        req_prompt = req.group(1).strip()
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


def parse_exchanges(transcript_path: Path) -> list:
    """
    Parse transcript.jsonl into a list of exchanges.
    Each exchange = one or more user messages followed by agent response(s).
    """
    exchanges = []
    pending_users = []
    current_agent_time = ''
    current_agent_content = []

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
                # Flush previous exchange if we have pending users
                if pending_users:
                    agent_text = '\n\n'.join(
                        c for c in current_agent_content if c.strip()
                    ).strip()
                    exchanges.append({
                        'users': pending_users[:],
                        'agent_turn': len(exchanges) + 1,
                        'agent_time': current_agent_time,
                        'agent_text': agent_text,
                    })
                    pending_users = []
                    current_agent_content = []
                    current_agent_time = ''

                prompt, ts = extract_user_input(obj.get('content', ''))
                if prompt:
                    pending_users.append({'prompt': prompt, 'time': ts, 'step': idx})

            elif t == 'PLANNER_RESPONSE':
                created = obj.get('created_at') or obj.get('timestamp') or ''
                if created and not current_agent_time:
                    current_agent_time = fmt_time(created)

                content = obj.get('content', '') or obj.get('text', '')
                if content and isinstance(content, str) and content.strip():
                    stripped = content.strip()
                    # Filter out the artifact pointer link itself
                    if stripped.startswith('[thread.md](') and stripped.endswith(')'):
                        continue
                    # Deduplicate consecutive identical content
                    if not current_agent_content or current_agent_content[-1] != stripped:
                        current_agent_content.append(stripped)

    # Flush final exchange
    if pending_users:
        agent_text = '\n\n'.join(
            c for c in current_agent_content if c.strip()
        ).strip()
        exchanges.append({
            'users': pending_users[:],
            'agent_turn': len(exchanges) + 1,
            'agent_time': current_agent_time,
            'agent_text': agent_text,
        })

    return exchanges


# ─── Response Files ───────────────────────────────────────────────────────────

def load_agent_response(history_dir: Path, turn_n: int, fallback_text: str = '') -> str:
    """Load agent response markdown for turn N (history/turn_N.md)."""
    path = history_dir / f'turn_{turn_n}.md'
    if path.exists():
        content = path.read_text().strip()
        if content:
            return content

    if fallback_text and fallback_text.strip():
        return fallback_text.strip()

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
    text = text.replace('```', '\n```\n')
    import re
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
    agent_md = f"#### 🤖 Agent{a_time}\n\n{agent_content}"

    return f"{user_md}\n\n{agent_md}"


# ─── Main ─────────────────────────────────────────────────────────────────────

def generate(conv_id: str, title: str, app_data_dir: Path):
    base            = app_data_dir / 'brain' / conv_id
    transcript_path = base / '.system_generated/logs/transcript.jsonl'
    history_dir     = base / 'history'
    output_path     = base / 'thread.md'

    history_dir.mkdir(exist_ok=True)

    if not transcript_path.exists():
        print(f"ERROR: Transcript not found: {transcript_path}", file=sys.stderr)
        sys.exit(1)

    exchanges = parse_exchanges(transcript_path)
    if not exchanges:
        print("ERROR: No exchanges found in transcript.", file=sys.stderr)
        sys.exit(1)

    for ex in exchanges:
        ex['agent_content'] = load_agent_response(
            history_dir, ex['agent_turn'], ex.get('agent_text', '')
        )

    # Reverse chronological order: newest exchange at top
    reversed_exchanges = list(reversed(exchanges))

    exchange_blocks = [
        make_exchange_block(ex['users'], ex['agent_content'], ex['agent_time'])
        for ex in reversed_exchanges
    ]

    separator = '\n\n---\n\n'
    doc = separator.join(exchange_blocks) + '\n'

    output_path.write_text(doc)
    print(f"Written: {output_path}")
    print(f"  {len(exchanges)} total exchanges rendered in reverse chronological order")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate thread.md from transcript + turn response files.'
    )
    parser.add_argument('conv_id',        help='Conversation ID (UUID)')
    parser.add_argument('--title',        default='Conversation', help='Thread title')
    parser.add_argument('--app-data-dir', default=str(APP_DATA_DIR))
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

    generate(args.conv_id, args.title, app_dir)
