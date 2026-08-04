#!/usr/bin/env python3
"""
gen_conversation_md.py — Generate conversation_response.md from transcript + agent response files.

ARCHITECTURE:
  Each turn, the agent:
    1. Writes its response (plain markdown) to:
         brain/<conv-id>/history/turn_<N>.md
    2. Runs:
         python3 gen_conversation_md.py <conv-id> --title "Thread Title"

  This script reads:
    - transcript.jsonl  -> all user messages + timestamps (auto-extracted)
    - history/turn_N.md -> agent response content per turn (agent writes this)

  And generates the full HTML-table conversation_response.md.

USAGE:
  python3 gen_conversation_md.py <conversation-id> [--title "Thread Title"] [--app-data-dir PATH]
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
import html

APP_DATA_DIR = Path.home() / '.gemini/antigravity'
STRUT = '&nbsp;' * 28


# ─── Timestamp ────────────────────────────────────────────────────────────────

def fmt_time(iso_str: str) -> str:
    """Convert ISO8601 local timestamp string to '2:05pm' format."""
    try:
        dt = datetime.fromisoformat(iso_str.strip())
        hour = dt.hour % 12 or 12
        ampm = 'am' if dt.hour < 12 else 'pm'
        return f"{hour}:{dt.minute:02d}{ampm}"
    except Exception:
        return ''


# ─── Transcript Parsing ───────────────────────────────────────────────────────

def extract_user_input(content: str):
    """Extract (prompt_text, local_timestamp_str) from a USER_INPUT step content."""
    # Find timestamp if present
    ts = re.search(r'current local time is:\s*([^\n<]+)', content)
    time = fmt_time(ts.group(1)) if ts else ''

    # Clean out metadata block
    cleaned = re.sub(r'<ADDITIONAL_METADATA>.*?</ADDITIONAL_METADATA>', '', content, flags=re.DOTALL)
    
    # Extract artifact comments if present
    # Pattern matching "Comments on artifact URI: ... Selection:\n>...\n\nComment: ..."
    comment_blocks = []
    # Match from Selection:\n up to Comment:
    comment_match = re.search(r'Selection:\s*\n(.*?)(?=\n\nComment:|\n<USER_REQUEST>|\Z)\s*(?:\n\nComment:\s*(.*?))?(?=\n<USER_REQUEST>|\Z)', cleaned, re.DOTALL)
    if comment_match:
        sel = comment_match.group(1).strip()
        cmt = comment_match.group(2).strip() if comment_match.group(2) else ''
        if cmt.startswith('"') and cmt.endswith('"'):
            cmt = cmt[1:-1].strip()
        comment_blocks.append((sel, cmt))

    # Extract user request prompt inside <USER_REQUEST>
    req = re.search(r'<USER_REQUEST>(.*?)</USER_REQUEST>', cleaned, re.DOTALL)
    if req:
        req_prompt = req.group(1).strip()
    else:
        req_prompt = re.sub(r'Comments on artifact URI:.*', '', cleaned, flags=re.DOTALL)
        req_prompt = re.sub(r'</?USER_REQUEST>', '', req_prompt).strip()

    # Format elegant comment quotes safely using html.escape so selections like `</td>` render cleanly in blockquotes without breaking table cells
    formatted_parts = []
    for sel, cmt in comment_blocks:
        quote_lines = []
        for line in sel.split('\n'):
            line_clean = line.lstrip('>').strip()
            if line_clean:
                # Escape HTML special chars so raw HTML/tag text in selections (like `</td>`) renders cleanly as text inside the blockquote
                quote_lines.append(html.escape(line_clean))
        
        quote_body = "\n".join([f"> {line}" for line in quote_lines])
        
        if cmt:
            cmt_escaped = html.escape(cmt)
            if quote_body:
                formatted_parts.append(f"{quote_body}\n>\n> 💬 **Comment**: {cmt_escaped}")
            else:
                formatted_parts.append(f"💬 **Comment**: {cmt_escaped}")
        elif quote_body:
            formatted_parts.append(quote_body)

    if req_prompt:
        # Also clean any raw <td> / </td> remnants if present in prompt text
        req_prompt_clean = re.sub(r'</?(?:td|tr|table)[^>]*>', '', req_prompt, flags=re.IGNORECASE).strip()
        if req_prompt_clean:
            formatted_parts.append(req_prompt_clean)

    # Join comment blocks and user prompt with clear newline spacing
    prompt = "\n\n---\n\n".join(formatted_parts).strip() if len(formatted_parts) > 1 else "\n\n".join(formatted_parts).strip()
    return prompt, time


def parse_exchanges(transcript_path: Path) -> list:
    """
    Parse transcript.jsonl into a list of exchanges.
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
                if pending_users:
                    agent_text = "\n\n".join([c for c in current_agent_content if c.strip()]).strip()
                    exchanges.append({
                        'users': pending_users[:],
                        'agent_turn': len(exchanges) + 1,
                        'agent_time': current_agent_time,
                        'agent_text': agent_text
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
                    if not (stripped.startswith('[conversation_response.md](') and stripped.endswith(')')):
                        if not current_agent_content or current_agent_content[-1] != stripped:
                            current_agent_content.append(stripped)

    if pending_users:
        agent_text = "\n\n".join([c for c in current_agent_content if c.strip()]).strip()
        exchanges.append({
            'users': pending_users[:],
            'agent_turn': len(exchanges) + 1,
            'agent_time': current_agent_time,
            'agent_text': agent_text
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


# ─── HTML Generation ──────────────────────────────────────────────────────────

def format_prompt(raw_prompt: str) -> str:
    # Safely escape HTML characters
    escaped = html.escape(raw_prompt.strip())
    lines = escaped.split('\n')
    
    # Only collapse into <details><summary> if truly massive (> 800 chars or > 12 lines)
    if len(escaped) > 800 or len(lines) > 12:
        summary_text = escaped[:350]
        if '\n' in summary_text:
            summary_text = '\n'.join(summary_text.split('\n')[:5])
        
        remainder = escaped[len(summary_text):]
        return f"<details><summary>{summary_text.strip()}...</summary>\n\n{remainder.strip()}\n</details>"
    
    return escaped


def make_exchange_block(users: list, agent_content: str, agent_time: str) -> str:
    user_blocks = []
    for u in users:
        p = format_prompt(u['prompt'])
        t = f" — *{u['time']}*" if u['time'] else ""
        user_blocks.append(f"""<table width="100%" border="0" frame="void" rules="none">
  <tr>
    <td>

### 🧔 **You**{t}

{p}

    </td>
  </tr>
</table>""")

    user_html = "\n\n".join(user_blocks) if user_blocks else ""
    a_time = f" — *{agent_time}*" if agent_time else ""
    
    agent_html = f"""<table width="100%" border="0" frame="void" rules="none">
<tr>
<td>

### 🤖 **Agent**{a_time}

{agent_content}

<br> <!-- Trailing <br> for bottom padding -->
</td>
</tr>
</table>"""

    return f"{user_html}\n\n{agent_html}"


# ─── Main ─────────────────────────────────────────────────────────────────────

def generate(conv_id: str, title: str, app_data_dir: Path):
    base            = app_data_dir / 'brain' / conv_id
    transcript_path = base / '.system_generated/logs/transcript.jsonl'
    history_dir     = base / 'history'
    output_path     = base / 'conversation_response.md'

    history_dir.mkdir(exist_ok=True)

    if not transcript_path.exists():
        print(f"ERROR: Transcript not found: {transcript_path}", file=sys.stderr)
        sys.exit(1)

    exchanges = parse_exchanges(transcript_path)
    if not exchanges:
        print("ERROR: No exchanges found in transcript.", file=sys.stderr)
        sys.exit(1)

    for ex in exchanges:
        ex['agent_content'] = load_agent_response(history_dir, ex['agent_turn'], ex.get('agent_text', ''))

    # Reverse chronological order: newest exchange at top, older below
    reversed_exchanges = list(reversed(exchanges))

    exchange_blocks = [
        make_exchange_block(ex['users'], ex['agent_content'], ex['agent_time'])
        for ex in reversed_exchanges
    ]

    separator = "\n\n\n<br>\n<br>\n<br>\n<br>\n\n---\n<br>\n<br>\n<br>\n<br>\n<br>\n\n"
    doc = separator.join(exchange_blocks) + "\n"

    output_path.write_text(doc)
    print(f"Written: {output_path}")
    print(f"  {len(exchanges)} total exchanges rendered in reverse chronological order")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate conversation_response.md from transcript + turn response files.'
    )
    parser.add_argument('conv_id',        help='Conversation ID (UUID)')
    parser.add_argument('--title',        default='Conversation', help='Thread title')
    parser.add_argument('--app-data-dir', default=str(APP_DATA_DIR))
    parser.add_argument('--save-turn',    action='store_true', help='Read markdown from stdin and save as next turn_N.md before generating')
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
