#!/usr/bin/env python3
"""
discussions_html.py — Generate a standalone Discussions.html from a conversation transcript.

GLOBAL RULE (per Matt, 2026-08-09):
  - Keep every user prompt verbatim.
  - Fold large pasted CODE blocks by default (<details>/<summary>).
  - Summarize verbose AGENT replies (concise default; full text behind a <details> toggle).
  - Produce a self-contained, browser-openable Discussions.html per project.

Reads the same transcript.jsonl format as gen_conversation_md.py (Antigravity brain dirs),
but is path-agnostic so it works for any project.

USAGE:
  python3 discussions_html.py <transcript.jsonl> --output Discussions.html [--title "Thread Title"]
  python3 discussions_html.py --conv-id <UUID> [--app-data-dir ~/.gemini/antigravity] [--output ...]

If --conv-id is given, the transcript is resolved to:
  <app-data-dir>/brain/<conv-id>/.system_generated/logs/transcript.jsonl
"""

import argparse
import json
import re
import html as html_mod
from datetime import datetime
from pathlib import Path

# ─── Constants and Path Helpers ───────────────────────────────────────────

def get_project_root() -> Path:
    """Auto-detect project root by looking for common markers."""
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        if (parent / '.git').exists() or (parent / 'package.json').exists() or (parent / 'AG_CONTEXT.md').exists():
            return parent
    return cwd


# ─── Token/verbosity helpers ──────────────────────────────────────────────

def estimate_words(text: str) -> int:
    return len(text.split()) if text else 0


# ─── Transcript parsing (mirrors gen_conversation_md.py) ──────────────────

def is_transient_status_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    # Filter out single-word prompts, status noise, and transient traces
    if re.match(r'^(?:continue|status|ok|yes|no|done|thanks|please\s+proceed)$', s, re.IGNORECASE):
        return True
    if re.match(r'^(?:completed\s+task-\d+|waiting\s+for|wait\s+for|subagent\s+(?:launched|execution)|i\s+have\s+(?:launched|requested|dispatched)|gemini\s+3\.1\s+pro|streaming\s+its\s+reasoning|actively\s+processing|completing\s+its\s+reasoning|finishing\s+its\s+detailed\s+architectural|will\s+agy|delegated\s+the\s+task\s+to|i\'ll\s+fetch\s+the\s+full\s+output|i\'ll\s+present\s+its\s+complete|i\s+will\s+retrieve\s+and\s+display|traceback|error|exception|stack\s+trace)', s, re.IGNORECASE):
        return True
    if re.match(r'^\s*\[`?(?:thread|conversation_response)\.md`?\]\([^\)]*\)\s*$', s, re.IGNORECASE):
        return True
    return False


def escape_html(text: str) -> str:
    """Safely escape text, avoiding double-escaping."""
    return html_mod.escape(text, quote=True)


def parse_inline_markdown(text: str) -> str:
    """Parse basic markdown inline formatting to HTML."""
    # Escape everything first
    text = escape_html(text)
    # **bold**
    text = re.sub(r'&amp;&amp;(.+?)&amp;&amp;', r'<b>\1</b>', text)
    # *italic*
    text = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<i>\1</i>', text)
    # `code`
    text = re.sub(r'&grave;([^&]+)&grave;', r'<code>\1</code>', text)
    # links [text](url)
    text = re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+|file://[^)\s]+)\)', r'<a href="\2">\1</a>', text)
    return text


def strip_html_tags(text: str) -> str:
    return re.sub(r'<[^>]+>', '', text)


def decode_html_entities(text: str) -> str:
    import html as html_mod
    return html_mod.unescape(text)


def fmt_time(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str.strip())
        return dt.strftime("%I:%M%p").lstrip("0").lower()
    except Exception:
        return ''


def extract_user_input(content: str):
    """Extract (prompt_text, local_timestamp_str) from a USER_INPUT step content."""
    ts = re.search(r'current local time is:\s*([^\n<]+)', content)
    time = fmt_time(ts.group(1)) if ts else ''

    cleaned = content
    for tag in ['USER_SETTINGS_CHANGE', 'user_rules', 'context', 'system', 'workflows', 'skills', 'ADDITIONAL_METADATA']:
        cleaned = re.sub(fr'<{tag}>.*?</{tag}>', '', cleaned, flags=re.DOTALL)

    # Artifact comments
    comment_blocks = []
    comment_match = re.search(
        r'Selection:\s*\n(.*?)\n\nComment:\s*(.+?)(?=\n<USER_REQUEST>|\Z)',
        cleaned, re.DOTALL
    )
    if comment_match:
        sel_raw = comment_match.group(1).strip()
        cmt_raw = comment_match.group(2).strip()
        if cmt_raw.startswith('"') and cmt_raw.endswith('"'):
            cmt_raw = cmt_raw[1:-1].strip()
        comment_blocks.append((sel_raw, cmt_raw))

    user_requests = re.findall(r'<USER_REQUEST>(.*?)</USER_REQUEST>', cleaned, flags=re.DOTALL)
    if user_requests:
        req_prompt = '\n\n---\n\n'.join(r.strip() for r in user_requests)
    else:
        req_prompt = re.sub(r'Comments on artifact URI:.*', '', cleaned, flags=re.DOTALL)
        req_prompt = re.sub(r'</?USER_REQUEST>', '', req_prompt).strip()

    formatted_parts = []
    for sel_raw, cmt_raw in comment_blocks:
        quote_lines = []
        for line in sel_raw.split('\n'):
            quote_lines.append(decode_html_entities(strip_html_tags(line)).lstrip('>').strip())
        cmt_clean = decode_html_entities(strip_html_tags(cmt_raw))
        if quote_lines:
            quote_body = '\n'.join(f'> {l}' if l else '>' for l in quote_lines)
            formatted_parts.append(f"{quote_body}\n>\n> 💬 **Comment**: {cmt_clean}" if cmt_clean else quote_body)
        elif cmt_clean:
            formatted_parts.append(f"💬 **Comment**: {cmt_clean}")

    if req_prompt:
        req_prompt_clean = decode_html_entities(req_prompt.strip())
        if req_prompt_clean:
            formatted_parts.append(req_prompt_clean)

    if len(formatted_parts) > 1:
        prompt = '\n\n---\n\n'.join(formatted_parts).strip()
    else:
        prompt = '\n\n'.join(formatted_parts).strip()
    # Simple title extraction: first 60 chars of prompt, remove markdown/directives
    title = ""
    if req_prompt:
        first_line = req_prompt.split('\n')[0].strip()
        title = re.sub(r'[\[\]\(\)\*`#]', '', first_line)[:60].strip()
    return prompt, time, title


def parse_exchanges(transcript_path: Path) -> list:
    """Parse transcript.jsonl into a list of {user, time, agent, agent_time, date_iso} exchanges."""
    exchanges = []
    pending_user = None
    pending_time = ''
    agent_content = []
    agent_time = ''
    pending_date = datetime.now().strftime("%Y-%m-%d")

    if not transcript_path.exists():
        return exchanges

    def flush():
        nonlocal pending_user, pending_time, agent_content, agent_time, pending_date
        if pending_user is not None:
            text = '\n\n'.join(c for c in agent_content if c.strip()).strip()
            lines = text.splitlines()
            non_trans = [l for l in lines if not is_transient_status_line(l)]
            if non_trans:
                text = '\n'.join(non_trans).strip()
            elif lines:
                text = lines[-1].strip()
            exchanges.append({
                'user': pending_user,
                'time': pending_time,
                'agent': text,
                'agent_time': agent_time,
                'date_iso': pending_date
            })
        pending_user = None
        pending_time = ''
        agent_content = []
        agent_time = ''

    with open(transcript_path) as f:
        for raw in f:
            raw = raw.strip()
            if not raw: continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError: continue
            t = obj.get('type', '')
            created = obj.get('created_at') or obj.get('timestamp') or ''

            if t == 'USER_INPUT':
                if pending_user is not None: flush()
                prompt, ts, title = extract_user_input(obj.get('content', ''))
                if prompt:
                    pending_user = prompt
                    pending_time = ts
                    pending_title = title
                    if created:
                        try: pending_date = datetime.fromisoformat(created.strip()).strftime("%Y-%m-%d")
                        except: pass
            elif t == 'PLANNER_RESPONSE':
                if created and not agent_time:
                    agent_time = fmt_time(created)
                content = obj.get('content', '') or obj.get('text', '')
                if content and isinstance(content, str):
                    c = content.strip()
                    if c: agent_content.append(c)

    flush()
    return exchanges


# ─── Markdown → HTML rendering ────────────────────────────────────────────

def escape_html(text: str) -> str:
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def render_code_folded(code_text: str, lang: str = '') -> str:
    """Render a code block inside a <details> that is closed by default (folded)."""
    inner = escape_html(code_text.rstrip('\n'))
    summary = f"<b>Code</b> · {estimate_words(inner):,} words" if inner else "<b>Code</b>"
    return (
        '<details class="code-fold"><summary>' + summary + '</summary>\n'
        f'<pre class="code"><code class="lang-{escape_html(lang or "text")}">{inner}</code></pre>\n'
        '</details>'
    )


def render_paragraphs(text: str) -> str:
    """Render markdown-ish text as HTML with folding of big <pre>/fenced code blocks."""
    # Pre-process: temporary placeholders for markdown syntax to survive HTML escaping
    text = text.replace('**', '&&')
    text = text.replace('`', '`') # Using &grave; would be better in escaping
    # Actually, the simplest is just handling it after escaping.
    # Modified: escape_html is done in parse_inline_markdown, let's rethink.
    
    # 1. Extract and fold code
    segments = []
    pos = 0
    pattern = re.compile(r'```([\w+-]*)\n(.*?)```', re.DOTALL)
    for m in pattern.finditer(text):
        if m.start() > pos:
            segments.append(('text', text[pos:m.start()]))
        segments.append(('code', m.group(2), m.group(1)))
        pos = m.end()
    if pos < len(text):
        segments.append(('text', text[pos:]))

    out = []
    for seg in segments:
        if seg[0] == 'code':
            out.append(render_code_folded(seg[1], seg[2]))
        else:
            # text segment: process paragraphs and headings
            lines = seg[1].splitlines()
            current_p = []
            def flush_p():
                if current_p:
                    out.append(f'<p>{parse_inline_markdown(" ".join(current_p))}</p>')
                    current_p.clear()

            for line in lines:
                stripped = line.strip()
                if not stripped:
                    flush_p()
                    continue
                # Heading detection
                if stripped.startswith('#'):
                    flush_p()
                    level = min(len(re.match(r'#+', stripped).group(0)), 6)
                    heading_text = stripped[level:].strip()
                    out.append(f'<h{level}>{parse_inline_markdown(heading_text)}</h{level}>')
                else:
                    current_p.append(stripped)
            flush_p()
    return '\n'.join(out)


def summarize_agent(text: str, max_chars: int = 500) -> tuple:
    """Return (summary_text, is_truncated). Distillation engine: clean text only."""
    if not text:
        return '', False
    # Distillation: Strip code blocks, raw attachments, and CLI output
    clean = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    clean = re.sub(r'\[.*?\]\(.*?\)', '', clean) # Links
    clean = re.sub(r'\n+', ' ', clean).strip()
    
    if len(clean) <= max_chars:
        return clean, False
    return (clean[:max_chars] + "..."), True


def agent_to_html(text: str) -> str:
    """Render an agent reply: folded code + verbose reply, with a concise lead + full toggle."""
    full_body = render_paragraphs(text)

    words = estimate_words(text)
    lead, truncated = summarize_agent(text)

    # Determines whether we fold the whole verbose reply.
    # Code-heavy replies: always show the lead, fold the code/'everything' inside a details.
    lead_html = render_paragraphs(lead)

    if not truncated and words <= 400:
        # Short reply: render inline, full text.
        return (
            f'<div class="agent-body">'
            f'<div class="lead">{lead_html}</div>'
            f'</div>'
        )
    # Verbose: show summarized lead, then a details to expand the full reply.
    detail = (
        '<details class="full-reply">'
        f'<summary>Full reply from agent ({"{:,}".format(words)} words)</summary>'
        f'<div class="full">{full_body}</div>'
        '</details>'
    )
    return (
        f'<div class="agent-body">'
        f'<div class="lead">{lead_html}</div>'
        f'{detail}'
        f'</div>'
    )


def user_to_html(text: str) -> str:
    """Keep the user prompt verbatim; fold only large pasted code blocks."""
    return render_paragraphs(text)


# ─── Document assembly ────────────────────────────────────────────────────

def exchange_html(ex) -> str:
    user_html = user_to_html(ex['user'])
    agent_html = agent_to_html(ex['agent'])
    u_ts = f'<span class="ts">at {ex["time"]}</span>' if ex['time'] else ''
    a_ts = f'<span class="ts">at {ex["agent_time"]}</span>' if ex['agent_time'] else ''
    return f"""
<div class="exchange">
  <div class="msg user">{u_ts}
    <div class="body">{user_html}</div>
  </div>
  <div class="msg agent">{a_ts}
    {agent_html}
  </div>
</div>"""

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{project_name} Discussions</title>
<style>
  :root {{
    --bg:#0f1115; --panel:#161a22; --panel2:#1b202b;
    --text:#e6e8ee; --muted:#9aa3b5;
    --user:#2b2350; --user-border:#6d56d9;
    --agent:#1c2130; --agent-border:#4a4a5e;
    --accent: {accent}; --code-bg:#0a0c12;
    --sidebar-w: 320px;
  }}
  /* Custom Scrollbar */
  ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
  ::-webkit-scrollbar-track {{ background: transparent; }}
  ::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,0.2); border-radius: 4px; }}
  ::-webkit-scrollbar-thumb:hover {{ background: var(--accent); }}

  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--text);
         font:14px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
         display: flex; height: 100vh; overflow: hidden; }}
  
  #sidebar {{ width: var(--sidebar-w); background: var(--panel); border-right: 1px solid #262b38;
             display: flex; flex-direction: column; }}
  .toolbar {{ padding: 10px 32px; display:flex; gap:14px; align-items:center;
              border-bottom:1px solid #262b38; background:var(--panel); position:sticky; top:0; z-index: 100;
              font-size:12px; color:var(--muted); }}
  #sidebar-header {{ padding: 20px; font-weight: bold; border-bottom: 1px solid #262b38; 
                     display: flex; justify-content: space-between; align-items: center;
                     position: sticky; top: 0; background: var(--panel); z-index: 100; }}
  
  main {{ flex: 1; overflow-y: auto; max-width:860px; margin:0 auto; padding:24px 32px 80px; width: 100%; }}
  
  .exchange {{ margin-bottom:20px; }}
  .msg {{ border-radius:14px; padding:14px 18px; position:relative; }}
  .msg.user {{ background:var(--user); border:1.5px solid var(--user-border);
               max-width:82%; margin-left:auto; }}
  .msg.agent {{ background:var(--agent); border:1.5px solid var(--agent-border);
                max-width:92%; margin-top:10px; }}
  .ts {{ display:block; font-size:10.5px; color:var(--muted); margin-bottom:6px;
         text-transform:uppercase; letter-spacing:.5px; }}
  .msg p {{ margin:0 0 8px; }}
  .msg p:last-child {{ margin-bottom:0; }}
  .msg code {{ background:rgba(255,255,255,.07); padding:1px 5px; border-radius:4px;
               font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:12.5px; }}
  pre.code {{ background:var(--code-bg); border:1px solid #262b38; border-radius:8px;
              padding:12px 14px; overflow-x:auto; font-size:12.5px; line-height:1.5;
              font-family:ui-monospace,SFMono-Regular,Menlo,monospace; }}
  details.code-fold {{ margin:6px 0; }}
  details.code-fold summary {{ cursor:pointer; color:var(--accent); font-size:12px;
                                user-select:none; }}
  details.full-reply summary {{ cursor:pointer; color:var(--accent); font-size:12px;
                                margin:10px 0 4px; user-select:none; }}
  .lead b {{ color:#cfc7ff; }}

  a {{ color:var(--accent); text-decoration:none; }}
  a:hover {{ text-decoration:underline; }}
  .date-header {{ text-align:center; margin:40px 0 20px; font-weight:600; color:var(--muted);
                  font-size:13px; letter-spacing:0.05em; text-transform:uppercase;
                  border-top:1px solid #262b38; padding-top:20px; }}
</style>
</head>
<body>
<aside id="sidebar">
  <div id="sidebar-header">
    {project_name}
    <div class="links">
        <a href="{zed_url}">Zed</a> · <a href="{finder_url}">Finder</a>
    </div>
  </div>
  <div id="thread-list" style="overflow-y:auto; flex: 1;"></div>
</aside>
<section id="detail-pane">
  <div class="toolbar">
    <label><input type="checkbox" id="foldToggle" checked> Fold long replies &amp; code</label>
  </div>
  <main id="thread-content"></main>
</section>
<script id="threads-data" type="application/json">
{threads_json}
</script>
<script>
  const threads = JSON.parse(document.getElementById('threads-data').textContent);
  const list = document.getElementById('thread-list');
  const content = document.getElementById('thread-content');
  
  function renderThread(id) {{
    const thread = threads[id];
    document.querySelectorAll('.thread-item').forEach(el => el.classList.remove('active'));
    document.getElementById('item-' + id).classList.add('active');
    content.innerHTML = thread.html;
  }}

  Object.keys(threads).sort((a,b) => threads[b].timestamp - threads[a].timestamp).forEach(id => {{
    const t = threads[id];
    const div = document.createElement('div');
    div.className = 'thread-item';
    div.id = 'item-' + id;
    div.innerHTML = `<div class=\"title\">${{t.title}}</div><div class=\"meta\">${{t.date}} · ${{t.count}} exchanges · ${{t.source}}</div>`;
    div.onclick = () => renderThread(id);
    list.appendChild(div);
  }});

  const t = document.getElementById('foldToggle');
  t.addEventListener('change', () => document.body.classList.toggle('folded', t.checked));
  document.body.classList.add('folded');

  if (Object.keys(threads).length > 0) {{
      renderThread(Object.keys(threads).sort((a,b) => threads[b].timestamp - threads[a].timestamp)[0]);
  }}
</script>
</body>
</html>
  document.body.classList.add('folded');

  if (Object.keys(threads).length > 0) {{
      renderThread(Object.keys(threads).sort((a,b) => threads[b].timestamp - threads[a].timestamp)[0]);
  }}
</script>
</body>
</html>
"""


# ─── Main ─────────────────────────────────────────────────────────────────

def resolve_transcript(args) -> Path:
    if args.hermes_session_id:
        return None
    if args.transcript:
        return Path(args.transcript).expanduser()
    if args.conv_id:
        base = Path(args.app_data_dir).expanduser() / 'brain' / args.conv_id
        return base / '.system_generated/logs/transcript.jsonl'
    raise SystemExit("Error: provide --transcript, --conv-id, or --hermes-session-id")


def format_hermes_timestamp(ts):
    if isinstance(ts, (int, float)):
        dt = datetime.fromtimestamp(ts)
        return dt.strftime("%Y-%m-%d"), dt.strftime("%I:%M%p").lstrip("0").lower()
    else:
        dt = datetime.fromisoformat(ts.strip())
        return dt.strftime("%Y-%m-%d"), dt.strftime("%I:%M%p").lstrip("0").lower()

def parse_hermes_session(session_id: str) -> list:
    import sqlite3
    import os
    db_path = os.path.expanduser("~/.hermes/state.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT role, content, timestamp FROM messages WHERE session_id=? AND role IN ('user','assistant') ORDER BY id", (session_id,))
    hermes_msgs = cursor.fetchall()
    conn.close()

    exchanges = []
    pending_user = None
    for role, content, ts in hermes_msgs:
        if role == 'user':
            pending_user = {'text': content, 'time': ts}
        elif role == 'assistant' and pending_user:
            user_date, user_time = format_hermes_timestamp(pending_user['time'])
            agent_date, agent_time = format_hermes_timestamp(ts)
            exchanges.append({
                'user': pending_user['text'],
                'time': user_time,
                'agent': content,
                'agent_time': agent_time,
                'date_iso': agent_date
            })
            pending_user = None
    return exchanges


def build_document(threads: dict, project_name: str, project_root: Path) -> str:
    import hashlib
    themes = ['#a855f7', '#06b6d4', '#10b981', '#f59e0b', '#f43f5e', '#6366f1']
    color_idx = int(hashlib.md5(str(project_root).encode()).hexdigest(), 16) % len(themes)
    accent_color = themes[color_idx]

    return PAGE_TEMPLATE.format(
        threads_json=json.dumps(threads),
        project_name=project_name,
        accent=accent_color,
        zed_url=f"zed://file/{project_root}",
        finder_url=f"file://{project_root}"
    )


def main():
    parser = argparse.ArgumentParser(description="Generate a self-contained Discussions.html from a transcript.")
    parser.add_argument('transcript', nargs='?', help='Path to transcript.jsonl')
    parser.add_argument('--conv-id', help='Antigravity conversation UUID (resolves via --app-data-dir)')
    parser.add_argument('--app-data-dir', default='~/.gemini/antigravity')
    parser.add_argument('--output', '-o', default=None, help='Output file path')
    parser.add_argument('--project-dir', help='Project root directory')
    parser.add_argument('--title', default=None, help='Thread title')
    parser.add_argument('--hermes-session-id', help='Optional Hermes session ID to ingest')
    args = parser.parse_args()

    transcript_path = resolve_transcript(args)
    
    if args.hermes_session_id:
        exchanges = parse_hermes_session(args.hermes_session_id)
    elif transcript_path and transcript_path.exists():
        exchanges = parse_exchanges(transcript_path)
    else:
        raise SystemExit(f"Error: transcript not found: {transcript_path}")

    if not exchanges:
        raise SystemExit("No exchanges parsed.")

    # Extract main title from first exchange
    first_title = exchanges[0].get('title') if exchanges else None
    title = args.title or first_title or (transcript_path.parent.parent.name if transcript_path and transcript_path.parent.parent.name != 'logs' else 'Conversation')
    
    threads = {
        'default': {
            'title': title,
            'date': datetime.now().strftime("%Y-%m-%d"),
            'timestamp': datetime.now().timestamp(),
            'count': len(exchanges),
            'source': 'Antigravity',
            'html': build_thread_html(exchanges)
        }
    }
    
    project_dir = Path(args.project_dir).expanduser() if args.project_dir else get_project_root()
    html = build_document(threads, project_dir.name, project_dir)

    if args.output:
        out = Path(args.output).expanduser()
    else:
        out = project_dir / 'Discussions.html'
        
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    print(f"Written: {out}")
    print(f"  {len(threads)} threads generated.")

def build_thread_html(exchanges: list) -> str:
    body = []
    last_date = None
    for ex in exchanges:
        if ex['date_iso'] != last_date:
            last_date = ex['date_iso']
            dt = datetime.strptime(last_date, "%Y-%m-%d")
            header_date = dt.strftime("%B %d, %Y")
            body.append(f'<div class="date-header">{header_date}</div>')
        body.append(exchange_html(ex))
    return '\n'.join(body)


if __name__ == '__main__':
    main()
