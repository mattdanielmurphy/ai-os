#!/usr/bin/env python3
"""End-to-end test against a throwaway GreenMail server (no real mailbox).

    docker run -d --rm --name mail-relay-test -p 127.0.0.1:3143:3143 -p 127.0.0.1:3025:3025 \
      -e GREENMAIL_OPTS='-Dgreenmail.setup.test.all -Dgreenmail.hostname=0.0.0.0 \
      -Dgreenmail.users=me:pw@example.com -Dgreenmail.users.login=email' greenmail/standalone:2.1.2
    python3 test_relay.py
"""

import json
import os
import smtplib
import sys
import threading
import time
import urllib.error
import urllib.request
from email.message import EmailMessage

TOKEN = "t" * 32
os.environ.update({
    "MAIL_RELAY_TOKEN": TOKEN, "MAIL_RELAY_PORT": "8799",
    "IMAP_HOST": "127.0.0.1", "IMAP_PORT": "3143", "IMAP_SSL": "0",
    "SMTP_HOST": "127.0.0.1", "SMTP_PORT": "3025", "SMTP_STARTTLS": "0",
    "MAIL_USER": "me@example.com", "MAIL_PASSWORD": "pw", "MAIL_FROM": "me@example.com",
    "MAIL_FROM_NAME": "Test Me", "DRAFTS_FOLDER": "Drafts", "SENT_FOLDER": "Sent Messages",
    "SEND_LOG": "/tmp/mail-relay-test-sent.jsonl",
})
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relay  # noqa: E402

BASE = "http://127.0.0.1:8799"
fails = 0


def check(name, cond, detail=""):
    global fails
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  {detail}"))
    fails += 0 if cond else 1


def http(method, path, body=None, token=TOKEN):
    req = urllib.request.Request(BASE + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json",
                                          **({"Authorization": "Bearer " + token} if token else {})})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read()
            return r.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        raw = e.read()
        return e.code, json.loads(raw) if raw else None


def deliver(subject, body):
    m = EmailMessage()
    m["From"] = "Bank <noreply@bank.example>"
    m["To"] = "me@example.com"
    m["Subject"] = subject
    m["Date"] = __import__("email.utils").utils.formatdate(localtime=True)
    m.set_content(body)
    with smtplib.SMTP("127.0.0.1", 3025) as s:
        s.send_message(m)


def main():
    # mailbox folders the relay writes to
    c = relay.imap()
    for f in ("Drafts", '"Sent Messages"'):
        c.create(f)
    c.logout()

    srv = relay.ThreadingHTTPServer(("127.0.0.1", 8799), relay.Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    deliver("Your sign-in code", "Hi,\n\nYour verification code is 482913. It expires in 10 minutes.\n")
    deliver("Lunch Friday?", "Want to grab lunch on Friday?")
    time.sleep(1)

    st, h = http("GET", "/health", token=None)
    check("health", st == 200 and h["configured"], h)
    st, _ = http("GET", "/api/list_messages", token="wrong" * 8)
    check("bad token rejected", st == 401)
    st, _ = http("POST", "/mcp/" + "x" * 32, {"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    check("bad MCP token is 404", st == 404)

    st, r = http("GET", "/api/list_messages?limit=10")
    subs = [m["subject"] for m in r.get("messages", [])] if st == 200 else r
    check("list_messages", st == 200 and "Lunch Friday?" in subs and "Your sign-in code" in subs, subs)
    lunch = next(m for m in r["messages"] if m["subject"] == "Lunch Friday?")
    check("list shows unread", lunch["unread"], lunch)

    st, r = http("GET", "/api/search?query=lunch&field=SUBJECT")
    check("search", st == 200 and [m["subject"] for m in r["messages"]] == ["Lunch Friday?"], r)

    st, r = http("GET", "/api/read_message?uid=" + lunch["uid"])
    check("read_message", st == 200 and "grab lunch" in r["body"], r)
    st, r = http("GET", "/api/list_messages?unread_only=1")
    check("read does not mark seen", st == 200 and any(m["uid"] == lunch["uid"] for m in r["messages"]), r)

    st, r = http("GET", "/api/find_codes?minutes=30")
    codes = [x for m in r.get("codes", []) for x in m["codes"]] if st == 200 else r
    check("find_codes", st == 200 and codes == ["482913"], codes)

    st, r = http("POST", "/api/create_draft", {"to": "friend@example.com", "body": "Sure, noon?",
                                               "in_reply_to_uid": lunch["uid"]})
    check("create_draft", st == 200 and r["subject"] == "Re: Lunch Friday?", r)
    c = relay.imap()
    c.select("Drafts", readonly=True)
    check("draft is in Drafts", c.uid("SEARCH", None, "SUBJECT", '"Re: Lunch Friday?"')[1][0] != b"")
    c.logout()

    st, r = http("POST", "/api/send", {"to": "me@example.com", "subject": "Relay send test", "body": "hello",
                                       "agent": "test"})
    check("send", st == 200 and r.get("sent"), r)
    time.sleep(1)
    st, r = http("GET", "/api/search?query=Relay%20send%20test&field=SUBJECT")
    got = r["messages"][0] if st == 200 and r["messages"] else {}
    check("sent mail arrives with From name", "Test Me" in got.get("from", ""), r)
    st, r = http("GET", "/api/search?query=Relay%20send%20test&field=SUBJECT&folder=Sent%20Messages")
    check("copy saved to Sent", st == 200 and len(r["messages"]) == 1, r)

    st, r = http("POST", "/api/send", {"subject": "x", "body": "no recipient"})
    check("send without to is 400", st == 400, r)
    st, r = http("GET", "/api/read_message?uid=1&folder=Nope")
    check("missing folder is 400", st == 400, r)

    # MCP
    st, r = http("POST", "/mcp/" + TOKEN, {"jsonrpc": "2.0", "id": 1, "method": "initialize",
                                           "params": {"protocolVersion": "2025-06-18"}})
    check("mcp initialize", st == 200 and r["result"]["serverInfo"]["name"] == "matt-mail", r)
    st, r = http("POST", "/mcp/" + TOKEN, {"jsonrpc": "2.0", "method": "notifications/initialized"})
    check("mcp notification is 202", st == 202)
    st, r = http("POST", "/mcp/" + TOKEN, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    names = [t["name"] for t in r["result"]["tools"]] if st == 200 else r
    check("mcp tools/list", st == 200 and "find_codes" in names and "send" in names, names)
    st, r = http("POST", "/mcp/" + TOKEN, {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                                           "params": {"name": "find_codes", "arguments": {"minutes": 30}}})
    check("mcp tools/call", st == 200 and "482913" in r["result"]["content"][0]["text"], r)

    relay.CFG["allow_send"] = False
    st, r = http("POST", "/api/send", {"to": "me@example.com", "body": "x"})
    check("ALLOW_SEND=0 blocks send", st == 400, r)

    srv.shutdown()
    print(f"\n{'ALL PASSED' if not fails else f'{fails} FAILED'}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
