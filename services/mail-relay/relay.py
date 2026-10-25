#!/usr/bin/env python3
"""Mail relay: lets agents read, draft and send Matt's email over HTTPS.

Talks IMAP/SMTP to the mailbox (iCloud Mail by default) and exposes the same
tools two ways:
  - REST:  GET/POST /api/<tool> with `Authorization: Bearer <MAIL_RELAY_TOKEN>`
  - MCP:   POST /mcp/<MAIL_RELAY_TOKEN> (streamable HTTP, JSON responses), so
           claude.ai and Claude Code can add it as a custom connector.

Python stdlib only. Config comes from the environment (see env.example).
"""

import email
import email.header
import email.policy
import email.utils
import hmac
import imaplib
import json
import os
import re
import smtplib
import ssl
import sys
import time
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from email.utils import formataddr, getaddresses, make_msgid, parsedate_to_datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

VERSION = "0.1.0"


def env(name, default=None):
    v = os.environ.get(name)
    return v if v not in (None, "") else default


def load_config():
    return {
        "token": env("MAIL_RELAY_TOKEN"),
        "port": int(env("MAIL_RELAY_PORT", "8790")),
        "imap_host": env("IMAP_HOST", "imap.mail.me.com"),
        "imap_port": int(env("IMAP_PORT", "993")),
        "imap_ssl": env("IMAP_SSL", "1") == "1",
        "smtp_host": env("SMTP_HOST", "smtp.mail.me.com"),
        "smtp_port": int(env("SMTP_PORT", "587")),
        "smtp_starttls": env("SMTP_STARTTLS", "1") == "1",
        "user": env("MAIL_USER"),
        "password": env("MAIL_PASSWORD"),
        "smtp_user": env("SMTP_USER") or env("MAIL_USER"),
        "from_addr": env("MAIL_FROM") or env("MAIL_USER"),
        "from_name": env("MAIL_FROM_NAME", ""),
        "drafts": env("DRAFTS_FOLDER", "Drafts"),
        "sent": env("SENT_FOLDER", "Sent Messages"),
        "save_sent": env("SAVE_SENT", "1") == "1",
        "allow_send": env("ALLOW_SEND", "1") == "1",
        "send_log": env("SEND_LOG", os.path.join(os.path.dirname(os.path.abspath(__file__)), "sent.jsonl")),
    }


CFG = load_config()
MAX_BODY = 20000  # chars of body returned per message


# ---------- IMAP helpers ----------

def imap():
    if CFG["imap_ssl"]:
        c = imaplib.IMAP4_SSL(CFG["imap_host"], CFG["imap_port"], ssl_context=ssl.create_default_context())
    else:
        c = imaplib.IMAP4(CFG["imap_host"], CFG["imap_port"])
    c.login(CFG["user"], CFG["password"])
    return c


def quoted(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def select(c, folder):
    typ, data = c.select(quoted(folder), readonly=True)
    if typ != "OK":
        raise ValueError(f"no folder {folder!r}")


def summarize(uid, raw_headers, flags=""):
    m = email.message_from_bytes(raw_headers, policy=email.policy.default)
    date = m.get("Date")
    try:
        iso = parsedate_to_datetime(date).isoformat() if date else None
    except Exception:
        iso = date
    return {
        "uid": uid,
        "from": str(m.get("From", "")),
        "to": str(m.get("To", "")),
        "subject": str(m.get("Subject", "")),
        "date": iso,
        "unread": "\\Seen" not in flags,
    }


def fetch_summaries(c, uids):
    out = []
    if not uids:
        return out
    typ, data = c.uid("FETCH", ",".join(uids), "(FLAGS BODY.PEEK[HEADER.FIELDS (FROM TO SUBJECT DATE)])")
    for part in data:
        if not isinstance(part, tuple):
            continue
        meta = part[0].decode(errors="replace")
        uid = re.search(r"UID (\d+)", meta)
        flags = re.search(r"FLAGS \(([^)]*)\)", meta)
        if uid:
            out.append(summarize(uid.group(1), part[1], flags.group(1) if flags else ""))
    out.sort(key=lambda x: int(x["uid"]), reverse=True)
    return out


def search_uids(c, *criteria):
    typ, data = c.uid("SEARCH", None, *criteria)
    return [u.decode() for u in data[0].split()] if data and data[0] else []


def body_text(m):
    """Best plain-text body of a parsed message."""
    part = m.get_body(preferencelist=("plain", "html"))
    if part is None:
        return ""
    text = part.get_content()
    if part.get_content_type() == "text/html":
        text = re.sub(r"(?is)<(script|style).*?</\1>", "", text)
        text = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</tr>", "\n", text)
        text = re.sub(r"<[^>]+>", "", text)
        text = text.replace("&nbsp;", " ").replace("&amp;", "&")
        text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    return text.strip()


def load_message(c, folder, uid):
    select(c, folder)
    typ, data = c.uid("FETCH", str(uid), "(BODY.PEEK[])")
    for part in data or []:
        if isinstance(part, tuple):
            return email.message_from_bytes(part[1], policy=email.policy.default)
    raise ValueError(f"no message with uid {uid} in {folder}")


# ---------- tools ----------

def t_list_folders(_):
    c = imap()
    try:
        typ, data = c.list()
        names = []
        for line in data:
            s = line.decode(errors="replace")
            mm = re.search(r'\((?:[^)]*)\) (?:"[^"]*"|NIL) (.+)$', s)
            if mm:
                names.append(mm.group(1).strip().strip('"'))
        return {"folders": names}
    finally:
        c.logout()


def t_list_messages(a):
    folder = a.get("folder") or "INBOX"
    limit = min(int(a.get("limit") or 20), 100)
    unread = str(a.get("unread_only", "")).lower() in ("1", "true", "yes")
    c = imap()
    try:
        select(c, folder)
        uids = search_uids(c, "UNSEEN" if unread else "ALL")[-limit:]
        return {"folder": folder, "messages": fetch_summaries(c, uids)}
    finally:
        c.logout()


def t_search(a):
    q = (a.get("query") or "").strip()
    if not q:
        raise ValueError("query is required")
    if not q.isascii():
        raise ValueError("query must be plain ASCII (IMAP search limit)")
    folder = a.get("folder") or "INBOX"
    limit = min(int(a.get("limit") or 20), 100)
    field = (a.get("field") or "TEXT").upper()
    if field not in ("TEXT", "FROM", "SUBJECT", "TO", "BODY"):
        raise ValueError("field must be TEXT, FROM, SUBJECT, TO or BODY")
    c = imap()
    try:
        select(c, folder)
        uids = search_uids(c, field, quoted(q))[-limit:]
        return {"folder": folder, "query": q, "messages": fetch_summaries(c, uids)}
    finally:
        c.logout()


def t_read_message(a):
    folder = a.get("folder") or "INBOX"
    uid = a.get("uid")
    if not uid:
        raise ValueError("uid is required")
    c = imap()
    try:
        m = load_message(c, folder, uid)
        atts = [p.get_filename() for p in m.iter_attachments() if p.get_filename()]
        body = body_text(m)
        return {
            "uid": str(uid),
            "folder": folder,
            "from": str(m.get("From", "")),
            "to": str(m.get("To", "")),
            "cc": str(m.get("Cc", "")),
            "subject": str(m.get("Subject", "")),
            "date": str(m.get("Date", "")),
            "message_id": str(m.get("Message-ID", "")),
            "attachments": atts,
            "body": body[:MAX_BODY],
            "truncated": len(body) > MAX_BODY,
        }
    finally:
        c.logout()


CODE_RE = re.compile(r"(?<![\w-])(\d{4,8}|[A-Z0-9]{3}-[A-Z0-9]{3})(?![\w-])")
CODE_HINT = re.compile(r"(?i)code|verif|one[- ]time|otp|sign[- ]?in|log[- ]?in|2fa|passcode|\bpin\b")


def t_find_codes(a):
    """Recent sign-in / verification codes (the 'switch apps to refresh' pain point)."""
    minutes = min(int(a.get("minutes") or 15), 24 * 60)
    since = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    c = imap()
    try:
        select(c, "INBOX")
        # IMAP SINCE is date-only, so look back a day and filter by the Date header
        day = (since - timedelta(days=1)).strftime("%d-%b-%Y")
        uids = search_uids(c, "SINCE", day)[-30:]
        found = []
        for uid in reversed(uids):
            m = load_message(c, "INBOX", uid)
            try:
                when = parsedate_to_datetime(m.get("Date"))
                if when.tzinfo is None:
                    when = when.replace(tzinfo=timezone.utc)
            except Exception:
                when = None
            if when and when < since:
                continue
            subject = str(m.get("Subject", ""))
            text = subject + "\n" + body_text(m)
            if not CODE_HINT.search(text):
                continue
            codes = [x for x in CODE_RE.findall(text) if not re.fullmatch(r"(19|20)\d\d", x)]
            if codes:
                found.append({"uid": uid, "from": str(m.get("From", "")), "subject": subject,
                              "date": when.isoformat() if when else None,
                              "codes": list(dict.fromkeys(codes))[:3]})
        return {"minutes": minutes, "codes": found}
    finally:
        c.logout()


def as_list(v):
    if not v:
        return ""
    return v if isinstance(v, str) else ", ".join(v)


def build_message(a, c):
    to = as_list(a.get("to"))
    if not to:
        raise ValueError("to is required")
    msg = EmailMessage()
    msg["From"] = formataddr((CFG["from_name"], CFG["from_addr"])) if CFG["from_name"] else CFG["from_addr"]
    msg["To"] = to
    if a.get("cc"):
        msg["Cc"] = as_list(a["cc"])
    subject = a.get("subject") or ""
    if a.get("in_reply_to_uid"):
        orig = load_message(c, a.get("folder") or "INBOX", a["in_reply_to_uid"])
        mid = orig.get("Message-ID")
        if mid:
            msg["In-Reply-To"] = mid
            msg["References"] = ((orig.get("References") or "") + " " + mid).strip()
        if not subject:
            s = str(orig.get("Subject", ""))
            subject = s if s.lower().startswith("re:") else "Re: " + s
    msg["Subject"] = subject
    msg["Date"] = email.utils.formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=(CFG["from_addr"] or "localhost").split("@")[-1])
    msg.set_content(a.get("body") or "")
    return msg


def append(c, folder, msg, flags):
    typ, data = c.append(quoted(folder), flags, imaplib.Time2Internaldate(time.time()), msg.as_bytes())
    if typ != "OK":
        raise RuntimeError(f"could not save to {folder}: {data}")


def t_create_draft(a):
    c = imap()
    try:
        msg = build_message(a, c)
        append(c, CFG["drafts"], msg, "(\\Draft \\Seen)")
        return {"saved_to": CFG["drafts"], "subject": msg["Subject"], "to": msg["To"]}
    finally:
        c.logout()


def t_send(a):
    if not CFG["allow_send"]:
        raise PermissionError("sending is turned off on this relay (ALLOW_SEND=0)")
    c = imap()
    try:
        msg = build_message(a, c)
        # skip empty fields: some Python builds' getaddresses() drop everything when given ""
        fields = [f for f in (str(msg.get("To", "")), str(msg.get("Cc", "")), as_list(a.get("bcc"))) if f]
        rcpts = [addr for _, addr in getaddresses(fields) if addr]
        s = smtplib.SMTP(CFG["smtp_host"], CFG["smtp_port"], timeout=30)
        try:
            if CFG["smtp_starttls"]:
                s.starttls(context=ssl.create_default_context())
            if CFG["password"] and CFG["smtp_starttls"]:
                s.login(CFG["smtp_user"], CFG["password"])
            s.send_message(msg, from_addr=CFG["from_addr"], to_addrs=rcpts)
        finally:
            s.quit()
        if CFG["save_sent"]:
            try:
                append(c, CFG["sent"], msg, "(\\Seen)")
            except Exception as e:  # the send worked; the Sent copy is best-effort
                print(f"sent-copy failed: {e}", file=sys.stderr)
        with open(CFG["send_log"], "a") as f:
            f.write(json.dumps({"at": datetime.now(timezone.utc).isoformat(), "to": rcpts,
                                "subject": msg["Subject"], "agent": a.get("agent", "")}) + "\n")
        return {"sent": True, "to": rcpts, "subject": msg["Subject"], "message_id": msg["Message-ID"]}
    finally:
        c.logout()


S = {"type": "string"}
TOOLS = {
    "list_folders": (t_list_folders, "List mail folders.", {}, []),
    "list_messages": (t_list_messages, "Newest messages in a folder (default INBOX), newest first.",
                      {"folder": S, "limit": {"type": "integer"}, "unread_only": {"type": "boolean"}}, []),
    "search": (t_search, "Search a folder. field: TEXT (default), FROM, SUBJECT, TO or BODY.",
               {"query": S, "folder": S, "field": S, "limit": {"type": "integer"}}, ["query"]),
    "read_message": (t_read_message, "Read one message (headers, plain-text body, attachment names) by uid.",
                     {"uid": S, "folder": S}, ["uid"]),
    "find_codes": (t_find_codes, "Verification / sign-in codes from the last N minutes (default 15).",
                   {"minutes": {"type": "integer"}}, []),
    "create_draft": (t_create_draft, "Save a draft in Drafts for Matt to review. in_reply_to_uid threads a reply.",
                     {"to": S, "cc": S, "subject": S, "body": S, "in_reply_to_uid": S, "folder": S}, ["to", "body"]),
    "send": (t_send, "Send an email as Matt. Only after Matt approved this exact message in chat.",
             {"to": S, "cc": S, "bcc": S, "subject": S, "body": S, "in_reply_to_uid": S, "folder": S, "agent": S},
             ["to", "body"]),
}


def call_tool(name, args):
    if name not in TOOLS:
        raise KeyError(f"unknown tool {name}")
    if not (CFG["user"] and CFG["password"]):
        raise RuntimeError("mailbox not configured yet (MAIL_USER / MAIL_PASSWORD)")
    return TOOLS[name][0](args or {})


# ---------- MCP (JSON-RPC over streamable HTTP, JSON responses only) ----------

def mcp_handle(req):
    method, rid = req.get("method"), req.get("id")
    if rid is None:  # notification: nothing to answer
        return None
    if method == "initialize":
        result = {"protocolVersion": (req.get("params") or {}).get("protocolVersion", "2025-03-26"),
                  "capabilities": {"tools": {}},
                  "serverInfo": {"name": "matt-mail", "version": VERSION},
                  "instructions": "Matt's email. Read freely; use create_draft for anything he should review; "
                                  "send only after Matt approved that exact message in chat."}
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": [{"name": n, "description": d,
                             "inputSchema": {"type": "object", "properties": p, "required": r}}
                            for n, (_, d, p, r) in TOOLS.items()]}
    elif method == "tools/call":
        p = req.get("params") or {}
        try:
            out = call_tool(p.get("name"), p.get("arguments"))
            result = {"content": [{"type": "text", "text": json.dumps(out, indent=1, ensure_ascii=False)}]}
        except Exception as e:
            result = {"content": [{"type": "text", "text": f"error: {e}"}], "isError": True}
    else:
        return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": f"unknown method {method}"}}
    return {"jsonrpc": "2.0", "id": rid, "result": result}


# ---------- HTTP ----------

class Handler(BaseHTTPRequestHandler):
    server_version = "mail-relay/" + VERSION

    def log_message(self, fmt, *args):  # never log full paths: the MCP path carries the token
        first = urlparse(self.path).path.strip("/").split("/")[0]
        sys.stderr.write(f"{self.command} /{first} {args[1] if len(args) > 1 else ''}\n")

    def reply(self, code, obj=None):
        body = json.dumps(obj, ensure_ascii=False).encode() if obj is not None else b""
        self.send_response(code)
        if body:
            self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def authed(self, given=None):
        tok = CFG["token"]
        if given is None:
            given = (self.headers.get("Authorization") or "").removeprefix("Bearer ").strip()
        return bool(tok) and hmac.compare_digest(given.encode(), tok.encode())

    def body_json(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n)) if n else {}

    def route(self):
        u = urlparse(self.path)
        parts = [p for p in u.path.split("/") if p]
        if parts == ["health"]:
            return self.reply(200, {"ok": True, "version": VERSION,
                                    "configured": bool(CFG["user"] and CFG["password"])})
        if len(parts) == 2 and parts[0] == "mcp":
            if not self.authed(parts[1]):
                return self.reply(404, {"error": "not found"})
            if self.command != "POST":  # no server-initiated stream
                return self.reply(405)
            req = self.body_json()
            out = [r for r in map(mcp_handle, req) if r] if isinstance(req, list) else mcp_handle(req)
            return self.reply(200, out) if out else self.reply(202)
        if len(parts) == 2 and parts[0] == "api":
            if not self.authed():
                return self.reply(401, {"error": "unauthorized"})
            args = {k: v[0] for k, v in parse_qs(u.query).items()}
            if self.command == "POST":
                args.update(self.body_json())
            try:
                return self.reply(200, call_tool(parts[1], args))
            except KeyError as e:
                return self.reply(404, {"error": str(e)})
            except (ValueError, PermissionError) as e:
                return self.reply(400, {"error": str(e)})
            except Exception as e:
                return self.reply(502, {"error": f"{type(e).__name__}: {e}"})
        return self.reply(404, {"error": "not found"})

    do_GET = route
    do_POST = route


def main():
    if not CFG["token"] or len(CFG["token"]) < 24:
        sys.exit("MAIL_RELAY_TOKEN missing or too short (24+ chars)")
    srv = ThreadingHTTPServer(("127.0.0.1", CFG["port"]), Handler)
    print(f"mail-relay {VERSION} on 127.0.0.1:{CFG['port']} "
          f"(mailbox configured: {bool(CFG['user'] and CFG['password'])})", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
