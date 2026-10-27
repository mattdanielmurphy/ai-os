#!/usr/bin/env python3
"""Tab Tidy native helper. Chrome starts it for each tidy run.

Gets every tab from the extension, decides which stale tabs to close (rules
below plus a Haiku check), archives those tabs to disk BEFORE answering, and
returns day/topic groups for the rest. Knobs live in the Tweaks file
(~/.hammerspoon/tweaks/tab_tidy.json, ⌃⌥⌘T panel) and are read on every run.
"""
import json, os, re, struct, subprocess, sys, time
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

TWEAKS = Path(os.environ.get("TAB_TIDY_TWEAKS", Path.home() / ".hammerspoon/tweaks/tab_tidy.json"))
ARCHIVE = Path(os.environ.get("TAB_TIDY_DIR", Path.home() / "projects/ai-os/private/tab-tidy"))
CLAUDE = os.environ.get("TAB_TIDY_CLAUDE", "/opt/homebrew/bin/claude")

DEFAULTS = {
    "dry_run": (1, 0, 1, 1, "1 = only write what would be closed to dry-run.md; 0 = really close tabs"),
    "every_minutes": (120, 15, 720, 15, "How often the tidy runs while Chrome is open"),
    "idle_hours": (24, 2, 336, 1, "Hours unused before a normal tab may be closed"),
    "youtube_hours": (6, 1, 168, 1, "Hours unused before a YouTube tab is closed (no Haiku check)"),
    "heavy_factor": (0.5, 0.1, 1, 0.05, "Heavy sites still loaded in memory close this much sooner (0.5 = half the time)"),
    "rare_visits": (3, 0, 50, 1, "A site you've visited this many times or fewer counts as new to you"),
    "rare_factor": (3, 1, 10, 0.5, "Tabs on sites new to you wait this many times longer"),
    "blank_hours": (1, 0.25, 24, 0.25, "Hours before an empty New Tab page is closed"),
    "duplicate_hours": (1, 0.25, 48, 0.25, "Hours before an unused duplicate of another open tab is closed"),
    "group_min_tabs": (12, 0, 100, 1, "Only group when at least this many loose tabs are open"),
    "topic_min_tabs": (2, 1, 10, 1, "Tabs a topic needs in one day to get its own group (others go to Misc)"),
    "collapse_older": (1, 0, 1, 1, "1 = collapse groups older than yesterday"),
    "use_haiku": (1, 0, 1, 1, "1 = ask Haiku for topics and to rescue tabs worth keeping"),
}
HEAVY = ("youtube.com", "figma.com", "docs.google.com", "sheets.google.com", "maps.google.com",
         "google.com/maps", "twitch.tv", "netflix.com", "open.spotify.com", "music.apple.com",
         "canva.com", "miro.com", "notion.so", "claude.ai", "chatgpt.com", "gemini.google.com",
         "x.com", "facebook.com", "instagram.com", "reddit.com", "linear.app")
COLORS = {"Today": "blue", "Yesterday": "cyan", "Older": "grey"}  # weekdays: green


def tweaks():
    data = {"app": "Tab Tidy", "tweaks": {}}
    try:
        data = json.loads(TWEAKS.read_text())
    except FileNotFoundError:
        pass
    except Exception:
        return {k: v[0] for k, v in DEFAULTS.items()}  # bad JSON: fall back, leave file alone
    changed = False
    for k, (d, lo, hi, step, note) in DEFAULTS.items():
        if k not in data["tweaks"]:
            data["tweaks"][k] = {"value": d, "default": d, "min": lo, "max": hi, "step": step, "note": note}
            changed = True
    if changed:
        TWEAKS.parent.mkdir(parents=True, exist_ok=True)
        TWEAKS.write_text(json.dumps(data, indent=2) + "\n")
    return {k: data["tweaks"][k]["value"] for k in DEFAULTS}


def host_of(url):
    try:
        return urlparse(url).hostname or ""
    except Exception:
        return ""


def is_youtube(url):
    h = host_of(url)
    return h == "youtu.be" or h.endswith("youtube.com")


def is_heavy(url):
    return any(k in url for k in HEAVY)


def bucket(ms, now_ms):
    d = datetime.fromtimestamp(ms / 1000).date()
    today = datetime.fromtimestamp(now_ms / 1000).date()
    if d >= today:
        return "Today", 0
    if d == today - timedelta(days=1):
        return "Yesterday", 1
    if d > today - timedelta(days=7):
        return d.strftime("%a"), (today - d).days
    return "Older", 99


def ask_haiku(items, max_wait=90):
    """items: [{i, title, site, idle_h, candidate}] → (topics{i: str}, keep{i: reason})."""
    prompt = (
        "You tidy a person's browser tabs. For EVERY tab give a short topic (1-2 words, Title Case), "
        "reusing the same few topics across tabs (at most 8 topics overall). For tabs marked "
        "candidate=true, decide if the person would regret losing it: KEEP it if it is specific and "
        "hard to find again (a particular article, doc, forum thread, order or booking page, product "
        "they were comparing, something half-done like a form or draft). Let it close if it is generic "
        "or easy to get back (search results, home pages, feeds, logins, videos, already-finished pages).\n"
        "Reply with only JSON: {\"topics\": {\"<i>\": \"Topic\"}, \"keep\": {\"<i>\": \"short reason\"}}\n\n"
        + json.dumps(items, ensure_ascii=False)
    )
    env = dict(os.environ, PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin")
    out = subprocess.run(
        [CLAUDE, "-p", "--model", "haiku", "--no-session-persistence", "--setting-sources", "",
         "--strict-mcp-config", "--tools", ""],
        input=prompt, capture_output=True, text=True, timeout=max_wait, env=env, cwd=str(Path.home()),
    ).stdout
    m = re.search(r"\{.*\}", out, re.S)
    data = json.loads(m.group(0))
    topics = {int(k): str(v)[:24] for k, v in data.get("topics", {}).items()}
    keep = {int(k): str(v)[:80] for k, v in data.get("keep", {}).items()}
    return topics, keep


def plan(msg, t=None, haiku=ask_haiku):
    t = t or tweaks()
    now = msg["now"]
    visits = msg.get("visits", {})
    tabs = [x for x in msg["tabs"] if not x.get("pinned") and not (x.get("group") and not x.get("ourGroup"))]
    idle = {x["id"]: (now - x["lastAccessed"]) / 3.6e6 for x in tabs}

    # Rules: which tabs are old enough to close, and does Haiku get a say?
    close, ask = {}, {}
    seen = {}
    for x in sorted(tabs, key=lambda x: -x["lastAccessed"]):  # newest first, so older dupes lose
        url, h, why = x["url"], idle[x["id"]], None
        if x.get("active") or x.get("audible"):
            seen.setdefault(url, x["id"])
            continue
        if url.startswith(("chrome://newtab", "about:blank")) or url == "":
            why = "empty tab" if h >= t["blank_hours"] else None
        elif not url.startswith(("http://", "https://")):
            continue
        elif url in seen and h >= t["duplicate_hours"]:
            why = "duplicate of an open tab"
        elif is_youtube(url):
            why = "YouTube, unused %dh" % h if h >= t["youtube_hours"] else None
        else:
            limit = t["idle_hours"]
            if is_heavy(url) and not x.get("discarded"):
                limit *= t["heavy_factor"]
            if visits.get(host_of(url), 99) <= t["rare_visits"]:
                limit *= t["rare_factor"]
            if h >= limit:
                ask[x["id"]] = "unused %dh" % h
        seen.setdefault(url, x["id"])
        if why:
            close[x["id"]] = why

    # Haiku: topics for grouping + a veto on rule-based closes.
    topics, keep, haiku_ok = {}, {}, False
    if t["use_haiku"] and tabs:
        items = [{"i": x["id"], "title": x["title"][:90], "site": host_of(x["url"]) or x["url"][:30],
                  "idle_h": int(idle[x["id"]]), "candidate": x["id"] in ask} for x in tabs]
        try:
            topics, keep = haiku(items)
            haiku_ok = True
        except Exception as e:
            sys.stderr.write("haiku failed: %s\n" % e)
    if haiku_ok:  # without Haiku's check, only the obvious rules close tabs
        for i, why in ask.items():
            if i not in keep:
                close[i] = why + ", Haiku agreed"

    by_id = {x["id"]: x for x in tabs}
    closing = [by_id[i] for i in close]
    archive(closing, close, keep, ask, t["dry_run"], now)

    # Groups: per window, by day of last use, then topic. Oldest first.
    groups = []
    loose = [x for x in tabs if x["id"] not in close]
    if len(loose) >= t["group_min_tabs"]:
        cells = {}
        for x in loose:
            day, age = bucket(x["lastAccessed"], now)
            cells.setdefault((x["windowId"], age, day), []).append(x)
        for (win, age, day), xs in sorted(cells.items(), key=lambda c: (c[0][0], -c[0][1])):
            by_topic = {}
            for x in xs:
                by_topic.setdefault(topics.get(x["id"], "Misc"), []).append(x)
            misc = [x for tp, ys in by_topic.items() if tp == "Misc" or len(ys) < t["topic_min_tabs"] for x in ys]
            named = sorted((tp, ys) for tp, ys in by_topic.items() if tp != "Misc" and len(ys) >= t["topic_min_tabs"])
            if misc:
                named.append(("Misc" if named else "Tabs", misc))
            for tp, ys in named:
                groups.append({
                    "windowId": win, "title": "%s · %s" % (day, tp),
                    "color": COLORS.get(day, "green"),
                    "collapsed": bool(t["collapse_older"]) and age > 1 and not any(y.get("active") for y in ys),
                    "tabIds": [y["id"] for y in sorted(ys, key=lambda y: y["lastAccessed"])],
                })

    verb = "would close" if t["dry_run"] else "closed"
    summary = "%s %d, %d groups%s" % (verb, len(close), len(groups), "" if haiku_ok or not t["use_haiku"] else ", Haiku unavailable")
    return {"close": list(close), "groups": groups, "dry_run": bool(t["dry_run"]),
            "every_minutes": int(t["every_minutes"]), "summary": summary}


def archive(closing, close, keep, ask, dry_run, now):
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    stamp = datetime.fromtimestamp(now / 1000).strftime("%Y-%m-%d %H:%M")
    lines = ["- [%s](%s) · %s" % ((x["title"] or x["url"]).replace("]", ")"), x["url"], close[x["id"]]) for x in closing]
    kept = ["- kept %s: %s" % (i, r) for i, r in keep.items() if i in ask]
    if dry_run:
        (ARCHIVE / "dry-run.md").write_text("# Would close (%s)\n\n%s\n\n## Haiku kept\n\n%s\n" % (
            stamp, "\n".join(lines) or "(nothing)", "\n".join(kept) or "(nothing)"))
        return
    if lines:
        with open(ARCHIVE / "closed.md", "a") as f:
            f.write("\n## %s\n\n%s\n" % (stamp, "\n".join(lines)))
        with open(ARCHIVE / "closed.jsonl", "a") as f:
            for x in closing:
                f.write(json.dumps({"t": now, "url": x["url"], "title": x["title"], "why": close[x["id"]]}) + "\n")


def main():
    raw = sys.stdin.buffer.read(4)
    if len(raw) < 4:
        return
    msg = json.loads(sys.stdin.buffer.read(struct.unpack("<I", raw)[0]))
    try:
        reply = plan(msg)
    except Exception as e:
        reply = {"error": "%s: %s" % (type(e).__name__, e)}
    body = json.dumps(reply).encode()
    sys.stdout.buffer.write(struct.pack("<I", len(body)) + body)
    sys.stdout.buffer.flush()


if __name__ == "__main__":
    main()
