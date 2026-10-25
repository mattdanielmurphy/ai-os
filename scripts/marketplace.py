#!/usr/bin/env python3
"""Facebook Marketplace search from Matt's Mac, no login.

Renders the public search page in headless Chrome (fresh throwaway profile,
nothing on screen, every render capped at 60s) and reads the listing JSON
Facebook embeds in the page. Cloud IPs and plain curl get a 400; this works
from the home IP.

  python3 scripts/marketplace.py search "m720q" ["lenovo tiny" ...] [--city edmonton]
        [--near "Edmonton,Sherwood Park,St. Albert"] [--max-price 200] [--details 5]

--near keeps only listings whose city matches (default: Edmonton area).
--details N opens the N cheapest listings to read their descriptions.
Don't add &sortBy=price_ascend: logged out, it returns almost nothing.
Prints JSON to stdout. Raw HTML stays in ./tmp/marketplace/ for debugging.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "tmp", "marketplace")
EDMONTON_AREA = ["Edmonton", "Sherwood Park", "St. Albert", "Spruce Grove", "Stony Plain",
                 "Leduc", "Beaumont", "Fort Saskatchewan", "Devon", "Nisku", "Morinville",
                 "Gibbons", "Ardrossan", "Calmar", "Parkland County", "Strathcona County"]


def render(url, name=None):
    os.makedirs(CACHE, exist_ok=True)
    name = name or hashlib.md5(url.encode()).hexdigest()[:12]
    out = os.path.join(CACHE, name + ".html")
    cmd = ["perl", "-e", "alarm 60; exec @ARGV", "--", CHROME, "--headless=new",
           "--disable-gpu", "--no-first-run", "--mute-audio",
           f"--user-data-dir={os.path.join(CACHE, 'profile')}",
           "--virtual-time-budget=15000", "--window-size=1280,3000", "--dump-dom", url]
    with open(out, "w") as f:
        subprocess.run(cmd, stdout=f, stderr=subprocess.DEVNULL, timeout=70)
    return open(out, encoding="utf-8", errors="replace").read()


def unjson(s):
    try:
        return json.loads('"' + s + '"')
    except ValueError:
        return s


LISTING = re.compile(
    r'"listing":\{"__typename":"GroupCommerceProductItem","id":"(\d+)".*?'
    r'"creation_time":(\d+).*?"listing_price":\{"formatted_amount":"([^"]*)"[^}]*"amount":"([\d.]+)"\}.*?'
    r'"location":\{"reverse_geocode":\{"city":"([^"]*)","state":"([^"]*)".*?'
    r'"is_pending":(true|false),"is_sold":(true|false).*?'
    r'"marketplace_listing_title":"((?:[^"\\]|\\.)*)"', re.S)


def search(query, city):
    q = urllib.parse.quote(query)
    url = f"https://www.facebook.com/marketplace/{city}/search?query={q}"
    s = render(url, f"search_{city}_{re.sub(r'\W+', '_', query)}")
    out = []
    for m in LISTING.finditer(s):
        lid, ctime, fmt, amount, lcity, state, pending, sold, title = m.groups()
        out.append({"id": lid, "title": unjson(title), "price": float(amount), "price_text": fmt,
                    "city": unjson(lcity), "state": state,
                    "listed": time.strftime("%Y-%m-%d", time.localtime(int(ctime))),
                    "pending": pending == "true", "sold": sold == "true",
                    "url": f"https://www.facebook.com/marketplace/item/{lid}/", "query": query})
    return out


def details(lid):
    s = render(f"https://www.facebook.com/marketplace/item/{lid}/", f"item_{lid}")
    m = re.search(r'"redacted_description":\{"text":"((?:[^"\\]|\\.)*)"', s)
    return unjson(m.group(1)) if m else None


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("search")
    sp.add_argument("queries", nargs="+")
    sp.add_argument("--city", default="edmonton", help="Marketplace city slug")
    sp.add_argument("--near", default=",".join(EDMONTON_AREA),
                    help="comma list of allowed cities, or 'any'")
    sp.add_argument("--max-price", type=float)
    sp.add_argument("--details", type=int, default=0)
    a = ap.parse_args()

    seen = {}
    for q in a.queries:
        for item in search(q, a.city):
            seen.setdefault(item["id"], item)
    items = [i for i in seen.values() if not i["sold"] and not i["pending"]]
    if a.near != "any":
        near = {c.strip().lower() for c in a.near.split(",")}
        items = [i for i in items if i["city"].lower() in near]
    if a.max_price is not None:
        items = [i for i in items if i["price"] <= a.max_price]
    items.sort(key=lambda i: i["price"])
    for i in items[:a.details]:
        i["description"] = details(i["id"])
    json.dump(items, sys.stdout, indent=1, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
