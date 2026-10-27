"""Fake-tab tests for the Tab Tidy rules. Run: python3 host/test_tab_tidy.py"""
import os, sys, tempfile, json, struct, subprocess
from pathlib import Path
tmp = Path(tempfile.mkdtemp(dir=Path(__file__).resolve().parents[1] / "tmp"))
os.environ["TAB_TIDY_DIR"] = str(tmp / "archive")
os.environ["TAB_TIDY_TWEAKS"] = str(tmp / "tweaks.json")
sys.path.insert(0, str(Path(__file__).parent))
import tab_tidy_host as h

H = 3.6e6
NOW = 1_800_000_000_000
def tab(i, url, hours, **kw):
    d = dict(id=i, windowId=1, index=i, url=url, title="Tab %d" % i, lastAccessed=NOW - hours * H,
             pinned=False, audible=False, discarded=False, active=False, group=None, ourGroup=False)
    return {**d, **kw}

tabs = [
    tab(1, "https://www.youtube.com/watch?v=a", 7),          # YouTube past 6h → close
    tab(2, "https://www.youtube.com/watch?v=b", 2),          # YouTube fresh → keep
    tab(3, "https://example.com/article", 30),               # normal 30h, Haiku says close
    tab(4, "https://example.com/order/123", 30),             # normal 30h, Haiku keeps
    tab(5, "https://rare-site.org/page", 30),                # new-to-you site: needs 72h → keep
    tab(6, "https://saved.com/x", 500, group="Read later"),  # Matt's group → never touched
    tab(7, "https://pinned.com", 500, pinned=True),          # pinned → never touched
    tab(8, "chrome://newtab/", 2),                           # empty tab → close
    tab(9, "https://example.com/article", 3),                # newer copy of tab 3 → tab 3 is a duplicate
    tab(10, "https://figma.com/file/x", 13),                 # heavy + loaded: 12h → candidate
    tab(11, "https://figma.com/file/y", 13, discarded=True), # heavy but discarded: 24h → keep
    tab(12, "https://www.youtube.com/watch?v=c", 50, audible=True),  # playing → keep
    tab(13, "https://news.com/a", 1, active=True),
]
visits = {"example.com": 40, "rare-site.org": 1, "figma.com": 30, "news.com": 50, "www.youtube.com": 500}
calls = []
def fake_haiku(items):
    calls.append(items)
    return {x["i"]: ("Video" if "youtube" in x["site"] else "Reading") for x in items}, {4: "order page"}

t = h.tweaks(); t["dry_run"] = 0; t["group_min_tabs"] = 3
p = h.plan({"now": NOW, "tabs": tabs, "visits": visits}, t, fake_haiku)
closed = set(p["close"])
assert closed == {1, 3, 8, 10}, closed
assert not {6, 7} & {i for x in calls[0] for i in [x["i"]]}, "Matt's group / pinned sent to Haiku"
archived = (tmp / "archive/closed.md").read_text()
assert "watch?v=a" in archived and "Tab 3" in archived and "order/123" not in archived
assert all(g["title"].split(" · ")[0] in ("Today", "Yesterday", "Older") or len(g["title"]) for g in p["groups"])
grouped = {i for g in p["groups"] for i in g["tabIds"]}
assert not grouped & (closed | {6, 7}), grouped
# Haiku down: only rule closes (YouTube, empty, duplicate), no Haiku-dependent closes
def broken(items): raise RuntimeError("offline")
p2 = h.plan({"now": NOW, "tabs": tabs, "visits": visits}, t, broken)
assert set(p2["close"]) == {1, 3, 8}, p2["close"]
# Dry run: nothing closes for real, list written to dry-run.md
t["dry_run"] = 1
p3 = h.plan({"now": NOW, "tabs": tabs, "visits": visits}, t, fake_haiku)
assert p3["dry_run"] and "Tab 3" in (tmp / "archive/dry-run.md").read_text()
# Native messaging framing end to end (Haiku off so it's fast)
tw = json.loads((tmp / "tweaks.json").read_text()); tw["tweaks"]["use_haiku"]["value"] = 0
(tmp / "tweaks.json").write_text(json.dumps(tw))
body = json.dumps({"now": NOW, "tabs": tabs, "visits": visits}).encode()
out = subprocess.run([sys.executable, str(Path(__file__).parent / "tab_tidy_host.py")],
                     input=struct.pack("<I", len(body)) + body, capture_output=True).stdout
reply = json.loads(out[4:])
assert "close" in reply and reply["dry_run"], reply
print("all tab tidy tests passed;", p["summary"], "| groups:", [g["title"] for g in p["groups"]])
