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
from datetime import datetime
from pathlib import Path

# ─── Token/verbosity helpers ──────────────────────────────────────────────

def estimate_words(text: str) -> int:
    return len(text.split()) if text else 0


# ─── Transcript parsing (mirrors gen_conversation_md.py) ──────────────────

def is_transient_status_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    if re.match(r'^(?:completed\s+task-\d+|waiting\s+for|wait\s+for|subagent\s+(?:launched|execution)|i\s+have\s+(?:launched|requested|dispatched)|gemini\s+3\.1\s+pro|streaming\s+its\s+reasoning|actively\s+processing|completing\s+its\s+reasoning|finishing\s+its\s+detailed\s+architectural|will\s+agy|delegated\s+the\s+task\s+to|i\'ll\s+fetch\s+the\s+full\s+output|i\'ll\s+present\s+its\s+complete|i\s+will\s+retrieve\s+and\s+display)', s, re.IGNORECASE):
        return True
    if re.match(r'^\s*\[`?(?:thread|conversation_response)\.md`?\]\([^\)]*\)\s*$', s, re.IGNORECASE):
        return True
    return False


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
    return prompt, time


def parse_exchanges(transcript_path: Path) -> list:
    """Parse transcript.jsonl into a list of {user, time, agent, agent_time} exchanges.

    Agent content comes from PLANNER_RESPONSE content (no dependency on history/turn_N.md).
    """
    exchanges = []
    pending_user = None
    pending_time = ''
    agent_content = []
    agent_time = ''

    if not transcript_path.exists():
        return exchanges

    def flush():
        nonlocal pending_user, pending_time, agent_content, agent_time
        if pending_user is not None:
            text = '\n\n'.join(c for c in agent_content if c.strip()).strip()
            # Filter transient lines: keep last transient if nothing else, else drop transients
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
            })
        pending_user = None
        pending_time = ''
        agent_content = []
        agent_time = ''

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

            if t == 'USER_INPUT':
                if pending_user is not None:
                    flush()
                prompt, ts = extract_user_input(obj.get('content', ''))
                if prompt:
                    pending_user = prompt
                    pending_time = ts
            elif t == 'PLANNER_RESPONSE':
                created = obj.get('created_at') or obj.get('timestamp') or ''
                if created and not agent_time:
                    agent_time = fmt_time(created)
                content = obj.get('content', '') or obj.get('text', '')
                if content and isinstance(content, str) and content.strip():
                    c = content.strip()
                    if not agent_content or agent_content[-1] != c:
                        agent_content.append(c)

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
    """Render markdown-ish text as HTML with folding of big <pre>/fenced code blocks.

    Fenced ``` blocks are extracted and folded. Non-code text is escaped and rendered
    as paragraphs (best-effort, no full markdown parser to keep it dependency-free).
    """
    # Split into fenced code and normal text segments
    parts = []
    pos = 0
    pattern = re.compile(r'```([\w+-]*)\n(.*?)```', re.DOTALL)
    for m in pattern.finditer(text):
        if m.start() > pos:
            parts.append(('text', text[pos:m.start()]))
        parts.append(('code', m.group(2), m.group(1)))
        pos = m.end()
    if pos < len(text):
        parts.append(('text', text[pos:]))

    out = []
    for part in parts:
        if part[0] == 'code':
            out.append(render_code_folded(part[1], part[2]))
        else:
            txt = escape_html(part[1]).strip()
            if not txt:
                continue
            # basic bold/italic/code inline
            txt = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', txt)
            txt = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<i>\1</i>', txt)
            txt = re.sub(r'`([^`\n]+)`', r'<code>\1</code>', txt)
            # links
            txt = re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+|file://[^)\s]+)\)',
                         r'<a href="\2">\1</a>', txt)
            for para in txt.split('\n\n'):
                para = para.strip()
                if not para:
                    continue
                out.append(f'<p>{para}</p>')
    return '\n'.join(out)


def summarize_agent(text: str, max_chars: int = 500) -> tuple:
    """Return (summary_text, is_truncated). Heuristic: first non-empty sentence(s)."""
    if not text:
        return '', False
    stripped = text.strip()
    # Try to grab a lead sentence, dropping code fences
    plain = re.sub(r'```.*?```', ' ', stripped, flags=re.DOTALL)
    plain = re.sub(r'\s+', ' ', plain).strip()
    # Take first meaningful sentence up to max_chars
    if len(plain) <= max_chars:
        return stripped, False
    # Find a sentence boundary near the cap
    cut = plain[max_chars // 2:max_chars]
    boundary = cut.rfind('. ')
    if boundary == -1:
        boundary = cut.rfind(' ')
    idx = max_chars // 2 + (boundary + 1 if boundary != -1 else max_chars // 2)
    summary = plain[:idx].strip()
    # keep at sentence boundary
    if '.' not in summary[-3:]:
        last = summary.rfind('. ')
        if last != -1:
            summary = summary[:last + 1]
    return summary, True


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
        '<details class="full-reply" open>'
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
<title>{title}</title>
<style>
  :root {{
    --bg:#0f1115; --panel:#161a22; --panel2:#1b202b;
    --text:#e6e8ee; --muted:#9aa3b5;
    --user:#2b2350; --user-border:#6d56d9;
    --agent:#1c2130; --agent-border:#4a4a5e;
    --accent:#8b7cf6; --code-bg:#0a0c12;
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--text);
         font:14px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; }}
  header {{ padding:28px 32px 16px; border-bottom:1px solid #262b38; }}
  header h1 {{ margin:0 0 4px; font-size:20px; }}
  header .meta {{ color:var(--muted); font-size:12px; }}
  .toolbar {{ padding:10px 32px; display:flex; gap:14px; align-items:center;
              border-bottom:1px solid #262b38; background:var(--panel); position:sticky; top:0;
              font-size:12px; color:var(--muted); }}
  .toolbar label {{ display:flex; align-items:center; gap:6px; cursor:pointer; }}
  main {{ max-width:860px; margin:0 auto; padding:24px 32px 80px; }}
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
  /* "Summary mode" — hide full replies and code bodies when the toolbar toggle is on */
  body.folded details.full-reply summary {{ display:block; }}
  body.folded details.full-reply .full {{ display:none; }}
  body.folded details.code-fold .code {{ display:none; }}
  a {{ color:#a99bff; text-decoration:none; }}
  a:hover {{ text-decoration:underline; }}
</style>
</head>
<body>
<header>
  <h1>{title}</h1>
  <div class="meta">{exchange_count} exchanges · generated {generated}</div>
</header>
<div class="toolbar">
  <label><input type="checkbox" id="foldToggle" checked> Fold long replies &amp; code</label>
</div>
<main>
{body}
</main>
<script>
  const t = document.getElementById('foldToggle');
  const B = document.body;
  function apply(v) {{ B.classList.toggle('folded', v); }}
  t.addEventListener('change', () => apply(t.checked));
  apply(true);
</script>
</body>
</html>
"""


def build_document(title: str, exchanges: list) -> str:
    body = '\n'.join(exchange_html(ex) for ex in exchanges)
    now = datetime.now().strftime("%B %d, %Y %I:%M%p").replace(" 0", " ").lower()
    return PAGE_TEMPLATE.format(
        title=title,
        exchange_count=len(exchanges),
        generated=now,
        body=body,
    )


# ─── Main ─────────────────────────────────────────────────────────────────

def resolve_transcript(args) -> Path:
    if args.transcript:
        return Path(args.transcript).expanduser()
    if args.conv_id:
        base = Path(args.app_data_dir).expanduser() / 'brain' / args.conv_id
        return base / '.system_generated/logs/transcript.jsonl'
    raise SystemExit("Error: provide --transcript or --conv-id")


def main():
    parser = argparse.ArgumentParser(description="Generate a self-contained Discussions.html from a transcript.")
    parser.add_argument('transcript', nargs='?', help='Path to transcript.jsonl')
    parser.add_argument('--conv-id', help='Antigravity conversation UUID (resolves via --app-data-dir)')
    parser.add_argument('--app-data-dir', default='~/.gemini/antigravity')
    parser.add_argument('--output', '-o', default='Discussions.html', help='Output file path')
    parser.add_argument('--title', default=None, help='Thread title (defaults to transcript dir name)')
    args = parser.parse_args()

    transcript_path = resolve_transcript(args)
    if not transcript_path.exists():
        raise SystemExit(f"Error: transcript not found: {transcript_path}")

    exchanges = parse_exchanges(transcript_path)
    if not exchanges:
        raise SystemExit("No exchanges parsed from transcript.")

    title = args.title or transcript_path.parent.parent.name
    html = build_document(title, exchanges)

    out = Path(args.output).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    print(f"Written: {out}")
    print(f"  {len(exchanges)} exchanges · {len(html):,} bytes")


if __name__ == '__main__':
    main()
