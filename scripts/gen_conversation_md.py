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

def is_transient_status_line(line: str) -> bool:
    """Check if a line is a transient progress/status update from tool execution."""
    s = line.strip()
    if not s:
        return False
    if re.match(r'^(?:completed\s+task-\d+|waiting\s+for|wait\s+for|subagent\s+(?:launched|execution)|i\s+have\s+(?:launched|requested|dispatched)|gemini\s+3\.1\s+pro|streaming\s+its\s+reasoning|actively\s+processing|completing\s+its\s+reasoning|finishing\s+its\s+detailed\s+architectural|will\tagy|delegated\s+the\s+task\s+to|i\'ll\s+fetch\s+the\s+full\s+output|i\'ll\s+present\s+its\s+complete|i\s+will\s+retrieve\s+and\s+display)[^\n]*$', s, re.IGNORECASE):
        return True
    if re.match(r'^\s*\[`?(?:thread|conversation_response)\.md`?\]\([^\)]*\)\s*$', s, re.IGNORECASE):
        return True
    return False


def clean_agent_content(text: str) -> str:
    """Strip out thread.md / conversation_response.md artifact links, transient status lines, and clutter."""
    if not text:
        return text

    link_re = re.compile(r'\[`?(?:thread|conversation_response)\.md`?\]\([^\)]*\)', re.IGNORECASE)
    divider_re = re.compile(r'^\s*(?:-{3,}|\*{3,}|_{3,})\s*$')

    lines = text.splitlines()
    drop = [False] * len(lines)

    for i, line in enumerate(lines):
        # Any line containing a thread.md / conversation_response.md link is removed entirely.
        if link_re.search(line):
            drop[i] = True
            # If the line directly above is a divider (---, ***, ___), remove that too.
            if i > 0 and divider_re.match(lines[i - 1]):
                drop[i - 1] = True
            continue

        if is_transient_status_line(line):
            drop[i] = True
            continue

        cleaned_str = line.strip()
        if re.match(r'^(?:(?:[-*+]\s*|\d+\.\s*)?reference\s+link(?:\s+to(?:\s+the)?\s+thread\s+artifact)?|thread(?:\s+artifact)?(?:\s+logged\s+at)?|conversation_response\.md)\s*:?\s*$', cleaned_str, re.IGNORECASE):
            drop[i] = True
            continue

        if not line.strip() or line.strip() in ('-', '*', '+'):
            drop[i] = True

    result = '\n'.join(line for i, line in enumerate(lines) if not drop[i])
    result = re.sub(r'\n{3,}', '\n\n', result).strip()
    return result

def filter_transient_lines(text: str) -> str:
    """If text contains non-transient content, strip ALL transient lines.
    If text contains ONLY transient content, retain ONLY the latest.
    """
    lines = text.splitlines()
    non_transient = [l for l in lines if not is_transient_status_line(l)]

    if non_transient:
        return '\n'.join(non_transient)

    transient = [l for l in lines if is_transient_status_line(l)]
    if transient:
        return transient[-1]
    return text


def clean_agent_response(text: str) -> str:
    """
    1. Clean agent content (links/status lines).
    2. Demote headings # -> #####, ## -> ######, ### -> ######.
    3. Strip orphan status/context lines.
    """
    text = clean_agent_content(text)
    if not text:
        return ''

    # Demote headings
    text = re.sub(r'^#{1,6}\s+', '### ', text, flags=re.MULTILINE)

    # Ensure blank lines before headings
    text = re.sub(r'([^\n])\n(#{1,6}\s+)', r'\1\n\n\2', text)

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

    return '\n'.join(lines).strip()


APP_DATA_DIR = Path.home() / '.gemini/antigravity'


# ─── Forking ──────────────────────────────────────────────────────────────────

def render_fork_file(items: list, output_path: Path):
    """Render a forked thread.md for undone exchanges."""
    exchange_blocks = []
    for item in items:
        if item['type'] == 'exchange':
            exchange_blocks.append(make_exchange_block(item['users'], clean_agent_response(item['agent_content']), item['agent_time']))

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
    # We escape spans in content_spans, but here we strip them.
    # Note: this is only used for formatting user input quotes, where we strip tags anyway.
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
            quote_lines.append(line_clean)

        # Decode entities in comment text too
        cmt_clean = strip_html_tags(cmt_raw)
        cmt_clean = decode_html_entities(cmt_clean)

        # Format as markdown blockquote
        if quote_lines:
            quote_body = '\n'.join(f'> {line}' if line else '>' for line in quote_lines)
            if cmt_clean:
                formatted_parts.append(f"{quote_body}\n>\n> 💬 **Comment**: {cmt_clean}")
            else:
                formatted_parts.append(quote_body)
        elif cmt_clean:
            formatted_parts.append(f"💬 **Comment**: {cmt_clean}")

    if req_prompt:
        # User prompt can contain arbitrary HTML and Markdown, so we DO NOT strip HTML tags.
        # Just clean up the prompt extraction and decode entities.
        req_prompt_clean = req_prompt.strip()
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

    def flush_current_turn():
        nonlocal pending_users, current_agent_content, current_agent_time, active_items
        if pending_users:
            # Joined with \n\n to maintain paragraph separation
            agent_text = '\n\n'.join(c for c in current_agent_content if c.strip()).strip()
            agent_text = filter_transient_lines(agent_text)

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
                # Flush prior turn ONLY if agent activity (response text or timestamp) occurred for it
                if pending_users and (current_agent_content or current_agent_time):
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

                prompt, ts = extract_user_input(obj.get('content', ''))
                if prompt:
                    pending_users.append({'prompt': prompt, 'time': ts, 'step': idx})

            elif t == 'PLANNER_RESPONSE':
                created = obj.get('created_at') or obj.get('timestamp') or ''
                if created and not current_agent_time:
                    current_agent_time = fmt_time(created)

                content = obj.get('content', '') or obj.get('text', '')
                if content and isinstance(content, str) and content.strip():
                    cleaned = clean_agent_content(content.strip())
                    if cleaned:
                        if not current_agent_content or current_agent_content[-1] != cleaned:
                            current_agent_content.append(cleaned)

    # Flush final turn at EOF
    flush_current_turn()

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

    Preserves exact newlines, multiline formatting, and code blocks.
    No HTML escaping, no <details> wrapping.
    """
    text = raw_prompt.strip()

    # Ensure code blocks are on their own lines to prevent markdown bleed
    # Pad fenced backticks with a leading newline if preceded by text
    text = re.sub(r'([^\n])```', r'\1\n```', text)
    # Pad ending backticks with a trailing newline if followed by text
    text = re.sub(r'```([^\n]*)\n([^\n])', r'```\1\n\n\2', text)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()

    return text


def make_exchange_block(users: list, agent_content: str, agent_time: str) -> str:
    """Build a single exchange block using pure markdown (no HTML tables)."""
    user_blocks = []
    for u in users:
        p = format_prompt(u['prompt'])
        user_blocks.append(p)

    user_md = '\n\n'.join(user_blocks)
    a_time = agent_time if agent_time else ''
    agent_text = clean_agent_response(agent_content)
    if not agent_text:
        agent_text = '*(response in progress or not recorded)*'

    user_span = (
        f'<span title="Sent at {users[0]["time"] if users else ""}" style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">\n\n'
        f'{user_md}\n\n'
        f'</span>'
    )

    agent_span = (
        f'\n\n<span title="Responded at {a_time}" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">\n\n'
        f'{agent_text}\n\n'
        f'</span>\n\n'
    )

    return f'<span style="display: block; width: 100%; margin-top: 8px;">\n\n{user_span}\n\n{agent_span}\n\n</span>'


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
                    # Detect common subagent start patterns
                    if re.search(r'(?:invoke_subagent|agy_start|agy)\b', content):
                        # Simple heuristic to extract UUID-like IDs
                        matches = re.findall(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', content)
                        for m in matches:
                            if m != conv_id:
                                subagent_ids.add(m)
                except: continue
    except: return None

    # Check for active subagent activity
    for sub_id in subagent_ids:
        sub_transcript = app_data_dir / 'brain' / sub_id / '.system_generated/logs/transcript.jsonl'
        if not sub_transcript.exists():
            continue

        # Read last few lines to check for activity
        try:
            # Using tail command to get latest lines
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


def make_exchange_block_with_progress(users: list, agent_content: str, agent_time: str, subagent_progress: str | None) -> str:
    """Build a single exchange block with potential subagent progress."""
    base_block = make_exchange_block(users, agent_content, agent_time)
    if subagent_progress:
        return f"{base_block}\n\n> [!NOTE]\n> 🔄 **Subagent Active**: {subagent_progress}"
    return base_block


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

    doc_content = []
    # Requirement 2: Thread Started Banner
    # Placed INSIDE the first (oldest) exchange block
    banner = f'<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — {datetime.now().strftime("%B %d, %Y")}</span>'

    doc_content.append(f'<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">')

    reversed_exchanges = list(reversed(exchanges))
    for i, item in enumerate(reversed_exchanges):
        if item['type'] == 'exchange':
            # Need to reload response in case of updates
            agent_content = load_agent_response(history_dir, item.get('agent_turn', 0), item.get('agent_content', ''))

            # Check for subagent progress
            progress = None
            # Requirement: pass progress to the NEWEST exchange (first in reversed list)
            if i == 0:
                progress = get_subagent_progress(conv_id, app_data_dir)

            block = make_exchange_block_with_progress(item['users'], agent_content, item['agent_time'], progress)

            # Prepend banner to the first exchange block
            # Requirement: Thread Started banner to the OLDEST exchange (which is the last in the reversed list)
            if i == len(reversed_exchanges) - 1:
                block = f"{banner}\n\n{block}"

            doc_content.append(block)
        elif item['type'] == 'fork_notice':
            doc_content.append(make_fork_notice_block(item['fork_path'], item['undone_count']))

    doc_content.append('</span>')

    rendered_doc = '\n\n'.join(doc_content)
    try:
        from link_formatter import enrich_file_links
        rendered_doc = enrich_file_links(rendered_doc)
    except Exception:
        pass

    output_path.write_text(rendered_doc)
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
