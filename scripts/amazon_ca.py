#!/usr/bin/env python3
"""Amazon.ca lookups from Matt's Mac (home IP; Amazon blocks cloud IPs).

Uses curl with a desktop Chrome UA + en-CA, every call capped at 30s.
Delivery quotes follow the IP's default location (Edmonton T6G).
Raw HTML is kept in ./tmp/amazon/ for debugging.

  python3 scripts/amazon_ca.py search "lenovo m720q tiny" [--pages 1]
  python3 scripts/amazon_ca.py product B07XFH6YXZ [B0...] [--seller-rating]

Prints JSON to stdout. Cloud threads: send_task the command to the Mac.
"""
import argparse
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse

BASE = "https://www.amazon.ca"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "tmp", "amazon")
COOKIES = os.path.join(CACHE, "cookies.txt")


def fetch(url, name=None):
    os.makedirs(CACHE, exist_ok=True)
    name = name or hashlib.md5(url.encode()).hexdigest()[:12]
    out = os.path.join(CACHE, name + ".html")
    cmd = ["curl", "-s", "-L", "--compressed", "--max-time", "30", "-A", UA,
           "-H", "Accept-Language: en-CA,en;q=0.9",
           "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
           "-c", COOKIES, "-b", COOKIES, "-o", out, "-w", "%{http_code}", url]
    code = subprocess.run(cmd, capture_output=True, text=True, timeout=35).stdout.strip()
    with open(out, encoding="utf-8", errors="ignore") as f:
        page = f.read()
    if "captcha" in page.lower() and "validateCaptcha" in page:
        raise RuntimeError(f"captcha on {url} (saved {out})")
    if code != "200":
        raise RuntimeError(f"HTTP {code} on {url}")
    return page


def text(fragment):
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", fragment, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def money(s):
    m = re.search(r"\$\s?([\d,]+\.\d{2})", s or "")
    return float(m.group(1).replace(",", "")) if m else None


def search(query, pages=1):
    results, seen = [], set()
    for p in range(1, pages + 1):
        url = f"{BASE}/s?k={urllib.parse.quote_plus(query)}&page={p}"
        page = fetch(url, "search-" + re.sub(r"\W+", "-", query) + f"-p{p}")
        blocks = re.split(r'(?=<div[^>]+data-component-type="s-search-result")', page)[1:]
        for b in blocks:
            asin = re.search(r'data-asin="(\w{10})"', b)
            if not asin or asin.group(1) in seen:
                continue
            seen.add(asin.group(1))
            title = re.search(r"<h2[^>]*aria-label=\"([^\"]+)\"", b) or \
                re.search(r"<h2[^>]*>(.*?)</h2>", b, re.S)
            price = re.search(r'class="a-price"[^>]*>.*?<span class="a-offscreen">([^<]+)<', b, re.S)
            ship = re.search(r'<div[^>]*data-cy="delivery-recipe".*?</div>\s*</div>', b, re.S)
            results.append({
                "asin": asin.group(1),
                "title": text(title.group(1)).removeprefix("Sponsored Ad – ") if title else None,
                "price": money(price.group(1)) if price else None,
                "delivery": text(ship.group(0)) if ship else None,
                "sponsored": "puis-sponsored-label" in b or "AdHolder" in b[:600],
                "url": f"{BASE}/dp/{asin.group(1)}",
            })
        time.sleep(1)
    return results


def table_rows(page, anchor, span=40000):
    i = page.find(anchor)
    if i < 0:
        return {}
    rows = {}
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", page[i:i + span], re.S):
        cells = re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, re.S)
        if len(cells) >= 2:
            k, v = text(cells[0]), text(cells[1])
            if k and v and len(k) < 60:
                rows.setdefault(k, v.lstrip("‎ "))
    return rows


def seller_rating(seller_id):
    page = fetch(f"{BASE}/sp?seller={seller_id}", "seller-" + seller_id)
    t = text(page)
    pos = re.search(r"(\d{1,3})% positive in the last 12 months \(([\d,]+) ratings?\)", t) \
        or re.search(r"(\d{1,3})% positive lifetime \(([\d,]+) total ratings?\)", t) \
        or re.search(r"(\d{1,3})% positive[^(]{0,40}\(([\d,]+) ratings?\)", t)
    stars = re.search(r"([\d.]+) out of 5 stars", t)
    return {"positive_pct": int(pos.group(1)) if pos else None,
            "ratings": int(pos.group(2).replace(",", "")) if pos else None,
            "stars": float(stars.group(1)) if stars else None}


def product(asin, with_seller=False):
    url = f"{BASE}/dp/{asin}"
    page = fetch(url, "dp-" + asin)
    title = re.search(r'id="productTitle"[^>]*>(.*?)</span>', page, re.S)
    core = page.find('id="corePrice_feature_div"')
    if core < 0:
        core = page.find('id="corePriceDisplay_desktop_feature_div"')
    price = re.search(r'class="a-offscreen">([^<]+)<', page[core:core + 5000]) if core >= 0 else None
    deliv = re.search(r'data-csa-c-delivery-price="([^"]*)"[^>]*data-csa-c-delivery-time="([^"]*)"', page)
    seller = re.search(r"seller=(\w+)[^>]*id='sellerProfileTriggerId'[^>]*>([^<]+)<", page)
    ships = re.search(r'offer-display-feature-name="desktop-fulfiller-info".*?offer-display-feature-text-message">([^<]+)<', page, re.S)
    merchant = re.search(r'offer-display-feature-name="desktop-merchant-info".*?offer-display-feature-text-message[^>]*>([^<]+)<', page, re.S)
    bullets = page.find('id="feature-bullets"')
    specs = {**table_rows(page, 'id="productOverview_feature_div"'), **table_rows(page, 'id="prodDetails"')}
    unavailable = 'id="outOfStock"' in page or "Currently unavailable" in text(page[core:core + 20000] if core >= 0 else "")
    out = {
        "asin": asin, "url": url,
        "title": text(title.group(1)) if title else None,
        "price": money(price.group(1)) if price else None,
        "available": not unavailable,
        "shipping": deliv.group(1) if deliv else None,
        "delivery_date": deliv.group(2) if deliv else None,
        "deliver_to": (re.search(r"Delivering to ([^<]+?)\s*<", page) or [None, None])[1],
        "seller": text(seller.group(2)) if seller else (text(merchant.group(1)) if merchant else None),
        "seller_id": seller.group(1) if seller else None,
        "ships_from": text(ships.group(1)) if ships else None,
        "specs": specs,
        "bullets": text(page[page.find('>', bullets) + 1:bullets + 8000]).split(" Show more")[0][:1500] if bullets >= 0 else None,
    }
    if with_seller and out["seller_id"]:
        out["seller_rating"] = seller_rating(out["seller_id"])
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search")
    s.add_argument("query")
    s.add_argument("--pages", type=int, default=1)
    p = sub.add_parser("product")
    p.add_argument("asins", nargs="+")
    p.add_argument("--seller-rating", action="store_true")
    a = ap.parse_args()
    try:
        if a.cmd == "search":
            data = search(a.query, a.pages)
        else:
            data = []
            for x in a.asins:
                try:
                    data.append(product(x, a.seller_rating))
                except Exception as e:  # keep going on one bad ASIN
                    data.append({"asin": x, "error": str(e)})
                time.sleep(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)
    json.dump(data, sys.stdout, indent=1, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
