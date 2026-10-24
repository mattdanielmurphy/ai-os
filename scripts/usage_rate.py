#!/usr/bin/env python3
"""Claude spend per ACTIVE hour, from local Claude Code logs (~/.claude/projects).

Active time = wall-clock union of every event (Matt's messages, assistant replies,
tool results) across all sessions, in Mountain time. Consecutive events <= GAP_MIN
apart count in full; longer gaps count as idle. Parallel sessions never double-count.
Cost = tokens x per-model prices from CodexBar's pricing cache (same source as the
menu-bar widget), deduped by request id, converted USD -> CAD with CodexBar's rate.

Usage: usage_rate.py [--json out.json] [--days N]
"""
import argparse, glob, json, os, subprocess
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

GAP_MIN = 10
TZ = ZoneInfo("America/Edmonton")
SWITCH = datetime(2026, 10, 23, 19, 24, tzinfo=timezone.utc)  # Sonnet became default
LOGS = os.path.expanduser("~/.claude/projects/*/*.jsonl")
PRICES = os.path.expanduser("~/Library/Caches/CodexBar/model-pricing/models-dev-v1.json")


def cad_rate():
    try:
        out = subprocess.run(["defaults", "read", "com.steipete.codexbar", "CodexBar.CurrencyExchangeRates"],
                             capture_output=True, text=True, timeout=5).stdout
        for line in out.splitlines():
            if line.strip().startswith("CAD"):
                return float(line.split("=")[1].strip(' ";'))
    except Exception:
        pass
    return 1.39


def load_prices():
    cat = json.load(open(PRICES))["catalog"]["providers"]["anthropic"]["models"]
    return {k: v["cost"] for k, v in cat.items() if "cost" in v}


def price_for(prices, model):
    if model in prices:
        return prices[model]
    for k in sorted(prices, key=len, reverse=True):
        if model.startswith(k):
            return prices[k]
    return None


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def project_of(cwd):
    if not cwd:
        return "?"
    p = cwd.replace("/Users/matt/", "~/")
    if "/.claude/worktrees/" in p:
        p = p.split("/.claude/worktrees/")[0]
    if "/.hammerspoon/" in p:
        p = "~/.hammerspoon"
    parts = p.split("/")
    return "/".join(parts[:3]) if len(parts) > 2 and parts[0] == "~" and parts[1] == "projects" else p


def collect():
    prices, rate = load_prices(), cad_rate()
    events, seen, rows, unpriced = [], set(), [], set()
    for f in glob.glob(LOGS):
        for line in open(f, errors="replace"):
            if not line.startswith("{"):
                continue
            try:
                d = json.loads(line)
            except ValueError:
                continue
            t = d.get("type")
            if t not in ("user", "assistant") or "timestamp" not in d:
                continue
            when = ts(d["timestamp"])
            events.append(when)
            if t != "assistant":
                continue
            m = d.get("message") or {}
            u, model = m.get("usage"), m.get("model")
            if not u or not model or model == "<synthetic>":
                continue
            key = d.get("requestId") or m.get("id")
            if key in seen:
                continue
            seen.add(key)
            p = price_for(prices, model)
            if not p:
                unpriced.add(model)
                continue
            cc = u.get("cache_creation") or {"ephemeral_5m_input_tokens": u.get("cache_creation_input_tokens", 0)}
            usd = (u.get("input_tokens", 0) * p.get("input", 0)
                   + u.get("output_tokens", 0) * p.get("output", 0)
                   + u.get("cache_read_input_tokens", 0) * p.get("cache_read", 0)
                   + (cc.get("ephemeral_5m_input_tokens", 0) * p.get("cache_write", 0)
                      + cc.get("ephemeral_1h_input_tokens", 0) * p.get("input", 0) * 2)) / 1e6
            tokens = sum(u.get(k, 0) for k in ("input_tokens", "output_tokens",
                         "cache_read_input_tokens", "cache_creation_input_tokens"))
            rows.append((when, model, project_of(d.get("cwd")), usd * rate, tokens))
    return events, rows, unpriced, rate


def active_segments(events):
    ev = sorted(set(events))
    return [(a, b) for a, b in zip(ev, ev[1:]) if (b - a) <= timedelta(minutes=GAP_MIN)]


def split_by_day(segs):
    per_day = defaultdict(float)
    for a, b in segs:
        a, b = a.astimezone(TZ), b.astimezone(TZ)
        while a.date() != b.date():
            end = datetime.combine(a.date() + timedelta(days=1), datetime.min.time(), TZ)
            per_day[a.date().isoformat()] += (end - a).total_seconds()
            a = end
        per_day[a.date().isoformat()] += (b - a).total_seconds()
    return per_day


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    ap.add_argument("--days", type=int, default=21)
    a = ap.parse_args()
    events, rows, unpriced, rate = collect()
    segs = active_segments(events)
    act = split_by_day(segs)

    day = lambda w: w.astimezone(TZ).date().isoformat()
    cost, tok = defaultdict(float), defaultdict(int)
    by_model, by_proj = defaultdict(lambda: defaultdict(float)), defaultdict(lambda: defaultdict(float))
    for when, model, proj, cad, tokens in rows:
        d = day(when)
        cost[d] += cad
        tok[d] += tokens
        by_model[d][model] += cad
        by_proj[d][proj] += cad

    days = sorted(set(act) | set(cost))[-a.days:]
    out_days = []
    for d in days:
        h = act.get(d, 0) / 3600
        out_days.append({
            "day": d, "active_h": round(h, 2), "cad": round(cost[d], 2), "tokens": tok[d],
            "cad_per_h": round(cost[d] / h, 2) if h >= 0.25 else None,
            "mtok_per_h": round(tok[d] / 1e6 / h, 1) if h >= 0.25 else None,
            "by_model": {k: round(v, 2) for k, v in sorted(by_model[d].items(), key=lambda x: -x[1])},
            "by_project": {k: round(v, 2) for k, v in sorted(by_proj[d].items(), key=lambda x: -x[1])[:8]},
        })

    def span(lo, hi):
        s = sum((b - a_).total_seconds() for a_, b in segs if lo <= a_ < hi) / 3600
        c = sum(r[3] for r in rows if lo <= r[0] < hi)
        t = sum(r[4] for r in rows if lo <= r[0] < hi)
        return s, c, t
    far = datetime(2100, 1, 1, tzinfo=timezone.utc)
    sb, cb, tb = span(SWITCH - timedelta(days=7), SWITCH)
    sa, ca, ta = span(SWITCH, far)
    mix = defaultdict(float)
    for r in rows:
        if r[0] >= SWITCH:
            mix[r[1]] += r[3]
    r1 = lambda x: round(x, 1)
    switch = {
        "before_7d": {"active_h": r1(sb), "cad": round(cb, 2), "cad_per_h": round(cb / sb, 2) if sb else None,
                      "mtok_per_h": r1(tb / 1e6 / sb) if sb else None},
        "after": {"active_h": r1(sa), "cad": round(ca, 2), "cad_per_h": round(ca / sa, 2) if sa else None,
                  "mtok_per_h": r1(ta / 1e6 / sa) if sa else None},
        "after_model_mix_cad": {k: round(v, 2) for k, v in sorted(mix.items(), key=lambda x: -x[1])},
    }

    today = datetime.now(TZ).date().isoformat()
    last7 = [x for x in out_days if x["day"] < today][-7:]
    h7 = sum(x["active_h"] for x in last7)
    summary = {
        "generated": datetime.now(TZ).isoformat(timespec="minutes"),
        "definition": f"active = merged event timeline across sessions; gaps > {GAP_MIN} min not counted",
        "usd_to_cad": rate, "unpriced_models": sorted(unpriced),
        "today": next((x for x in out_days if x["day"] == today), None),
        "avg7_cad_per_h": round(sum(x["cad"] for x in last7) / h7, 2) if h7 else None,
        "avg7_mtok_per_h": r1(sum(x["tokens"] for x in last7) / 1e6 / h7) if h7 else None,
        "switch": switch, "days": out_days,
    }
    if a.json:
        json.dump(summary, open(a.json, "w"), indent=1)
    t = summary["today"] or {}
    print(f"today  CA${t.get('cad_per_h')}/h  {t.get('mtok_per_h')} Mtok/h  ({t.get('active_h')} h active)")
    print(f"7-day avg  CA${summary['avg7_cad_per_h']}/h  {summary['avg7_mtok_per_h']} Mtok/h")
    print("switch", json.dumps(switch))
    for x in out_days:
        print(x["day"], x["active_h"], "h", "CA$", x["cad"], "->", x["cad_per_h"], "/h", list(x["by_model"].items())[:3])


if __name__ == "__main__":
    main()
