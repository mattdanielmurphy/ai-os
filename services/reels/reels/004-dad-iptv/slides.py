#!/usr/bin/env python3
"""Reel 04 slides, written as SVG by hand (theme role classes, not hexes). Run: python3 slides.py
Groups a1, a2, … reveal in order; inside them: draw, grow, flow, pulse, glow, spin, blink, data-count, data-type."""
from pathlib import Path
from html import escape as e

HERE = Path(__file__).parent


def svg(*parts):
    return ('<svg viewBox="0 0 1280 720" xmlns="http://www.w3.org/2000/svg">'
            '<rect width="1280" height="720" class="f-bg"/>' + "".join(parts) + "</svg>\n")


def g(n, *parts):
    return f'<g id="a{n}">' + "".join(parts) + "</g>"


def chip(text, y=92):
    return (f'<circle cx="111" cy="{y - 6}" r="7" class="f-accent pulse"/>'
            f'<text x="132" y="{y}" class="tm f-muted" font-size="17">{e(text)}</text>')


def title(lines, y=168, size=62):
    return "".join(f'<text x="104" y="{y + k * size * .95:.0f}" class="td f-ink" font-size="{size}">{e(l)}</text>'
                   for k, l in enumerate(lines))


def para(lines, x=104, y=250, size=24, lh=36, cls="f-muted"):
    return "".join(f'<text x="{x}" y="{y + k * lh}" class="tb {cls}" font-size="{size}">{e(l)}</text>'
                   for k, l in enumerate(lines))


def box(x, y, w, h, fill="f-surface", stroke="s-line", rx=4, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{fill} {stroke}" stroke-width="2" {extra}/>'


def label(x, y, text, size=15, cls="f-muted", anchor="start"):
    return f'<text x="{x}" y="{y}" class="tm {cls}" font-size="{size}" text-anchor="{anchor}">{e(text)}</text>'


def stat(x, y, n, unit, text):
    return (f'<text x="{x}" y="{y}" class="td f-ink" font-size="54" data-count="{n}" data-unit="{unit}">{n}{unit}</text>'
            + label(x, y + 30, text, 14))


def radar(cx, cy, r, blips):
    rings = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r * f:.0f}" fill="none" class="s-line" stroke-width="2"/>'
                    for f in (1, .68, .36))
    out = (f'<circle cx="{cx}" cy="{cy}" r="{r}" class="f-surface s-line" stroke-width="2"/>' + rings +
           f'<line x1="{cx - r}" y1="{cy}" x2="{cx + r}" y2="{cy}" class="s-line" stroke-width="2"/>'
           f'<line x1="{cx}" y1="{cy - r}" x2="{cx}" y2="{cy + r}" class="s-line" stroke-width="2"/>'
           f'<g class="spin" style="transform-origin:{cx}px {cy}px">'
           f'<path d="M{cx} {cy} L{cx} {cy - r} A{r} {r} 0 0 1 {cx + r * .71:.1f} {cy - r * .71:.1f} Z" class="f-accent" opacity=".22"/>'
           f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy - r}" class="s-accent" stroke-width="3"/></g>')
    for k, (x, y, name) in enumerate(blips):
        out += (f'<circle cx="{x}" cy="{y}" r="9" class="f-accent pulse" style="animation-delay:{k * .5}s"/>'
                + label(x + 16, y + 5, name, 14, "f-ink"))
    return out


def check(x, y, text, delay):
    return (f'<path d="M{x} {y - 8} l9 9 l17 -19" pathLength="1" fill="none" class="s-good draw" stroke-width="4" '
            f'stroke-linecap="round" stroke-linejoin="round" style="transition-delay:{delay}s"/>'
            f'<text x="{x + 44}" y="{y}" class="tb f-ink" font-size="27">{e(text)}</text>')


S = {}


def bar(y, name, amt, w, cls, note, delay=0):
    return (label(104, y - 14, name, 15, "f-ink")
            + f'<rect x="104" y="{y}" width="{w}" height="40" rx="4" class="{cls} grow" style="transition-delay:{delay}s"/>'
            + f'<text x="{116 + w}" y="{y + 29}" class="td f-ink" font-size="30">{e(amt)}</text>'
            + label(116 + w + 6 + len(amt) * 17, y + 28, note, 14))


def pill(x, y, w, text, cls="s-accent"):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="48" rx="24" class="f-surface {cls}" stroke-width="2"/>'
            f'<text x="{x + w / 2}" y="{y + 31}" class="tm f-ink" font-size="17" text-anchor="middle">{e(text)}</text>')


def row(x, y, w, head, sub, cls="s-line", fill="f-surface", h=96):
    return (box(x, y, w, h, fill, cls, 6)
            + f'<text x="{x + 22}" y="{y + 42}" class="td f-ink" font-size="30">{e(head)}</text>'
            + "".join(f'<text x="{x + 22}" y="{y + 72 + k * 26}" class="tb f-muted" font-size="19">{e(t)}</text>'
                     for k, t in enumerate(sub.split("|"))))



def col(x, k, head, lines, total, tcls="f-ink", cls="s-line"):
    out = box(x, 250, 260, 360, "f-surface", cls, 6) + label(x + 20, 286, k, 14)
    out += f'<text x="{x + 20}" y="324" class="td f-ink" font-size="26">{e(head)}</text>'
    for n, (a, b) in enumerate(lines):
        yy = 372 + n * 52
        out += (f'<text x="{x + 20}" y="{yy}" class="tb f-muted" font-size="17">{e(a)}</text>'
                f'<text x="{x + 240}" y="{yy}" class="tm f-ink" font-size="17" text-anchor="end">{e(b)}</text>'
                f'<line x1="{x + 20}" y1="{yy + 14}" x2="{x + 240}" y2="{yy + 14}" class="s-line" stroke-width="1"/>')
    out += f'<text x="{x + 20}" y="568" class="td {tcls}" font-size="36">{e(total)}</text>'
    return out


S[1] = svg(
    g(1, chip("THE CHEAP TV BOX")),
    g(2, title(["WILL IT JUST", "WORK LIKE", "TELUS TV?"], y=190, size=88)),
    g(3, para(["A Firestick sold with a year of live TV for about $150–400.",
               "The savings are real. So are the catches."], y=480, size=26, lh=40)),
    g(4, box(104, 570, 1072, 80, "f-surface", "s-line", 6),
         '<text x="132" y="622" class="td f-ink" font-size="30">Short answer: cheaper, but not hands-off.</text>'),
)

S[2] = svg(
    g(1, chip("CH 01 — WHAT TV COSTS A YEAR NOW")),
    g(2, title(["BEFORE: ABOUT $2,000"])),
    g(3, bar(290, "TELUS TV  (CANCELLED)", "$900", 630, "f-line", "$75 a month", 0)),
    g(4, bar(380, "SPORTSNET+ ALONE", "$350", 245, "f-sky", "per year", .2)),
    g(5, bar(470, "EVERYTHING ELSE: APPLE ONE, NETFLIX, PRIME…", "~$750", 525, "f-sky", "estimate", .4)),
    g(6, box(104, 560, 1072, 90, "f-ink", "s-ink", 6),
         '<text x="132" y="618" class="td f-bg" font-size="34">With Telus gone: about $1,100 a year.</text>'),
)

S[3] = svg(
    g(1, chip("CH 02 — FOUR WAYS FORWARD")),
    g(2, title(["WHAT EACH ONE COSTS"], size=54)),
    g(3, col(104, "A", "KEEP AS IS", [("Sportsnet+", "$350"), ("Everything else", "~$750")], "~$1,100")),
    g(4, col(380, "B", "BOX + KEEP APPS", [("The box", "$150–400"), ("Sportsnet+", "dropped"), ("Everything else", "~$750")], "$900–1,150", "f-bad", "s-bad")),
    g(5, col(656, "C", "BOX ONLY", [("The box", "$150–400"), ("Everything else", "dropped")], "$150–400", "f-bad", "s-bad")),
    g(6, col(932, "D", "TRIM + PLEX", [("Sportsnet+, 7 mo", "~$245"), ("Plex", "free"), ("Others, trimmed", "~$375")], "~$620", "f-good", "s-good")),
    g(7, label(104, 650, "Everything else ~$750 is an estimate from the ~$2,000 total; trimmed assumes half of it is dropped.", 14)),
)

S[4] = svg(
    g(1, chip("CH 03 — THE UPSIDE")),
    g(2, title(["WHY IT'S TEMPTING"])),
    g(3, row(104, 260, 520, "BIG SAVING", "Often well under cable or Telus TV.", "s-good", "f-good-bg"),
         row(656, 260, 520, "LOTS OF CHANNELS", "Live sports, news, movies. Count unverified.", "s-good", "f-good-bg")),
    g(4, row(104, 380, 520, "EASY TO START", "Arrives as a plug-in Firestick.", "s-good", "f-good-bg"),
         row(656, 380, 520, "LOW-RISK TRIAL", "Trials and monthly plans cap the cost.", "s-good", "f-good-bg")),
    g(5, box(104, 520, 1072, 100, "f-surface", "s-line", 6),
         '<text x="132" y="580" class="tb f-ink" font-size="25">A coworker uses it and vouches for it. That counts, but it is one user.</text>'),
)

S[5] = svg(
    g(1, chip("CH 04 — WILL IT JUST WORK?")),
    g(2, title(["NOT LIKE TELUS TV"])),
    g(3, para(["Telus is a company with a phone number.", "This is a reseller of streams the channels never licensed."], y=236, size=22, lh=32)),
    g(4, row(104, 290, 520, "IT CAN VANISH", "Mid-term, with no refund (unverified).", "s-bad", "f-bad-bg", 84),
         row(656, 290, 520, "PEAK-HOUR BUFFERING", "Hockey night is when it strains.", "s-bad", "f-bad-bg", 84)),
    g(5, row(104, 394, 520, "SITES GET BLOCKED", "An ISP block may need a VPN.", "s-bad", "f-bad-bg", 84),
         row(656, 394, 520, "NO MONEY BACK", "E-transfer has no chargeback.", "s-bad", "f-bad-bg", 84)),
    g(6, para(["Plus payment details go to a seller no one holds accountable."], y=540, size=21, cls="f-muted")),
)

S[6] = svg(
    g(1, chip("CH 05 — WHO FIXES IT?")),
    g(2, title(["YOU ARE TECH SUPPORT"])),
    g(3, para(["Telus fixed problems. Here the only help is one person on WhatsApp."], y=236, size=23)),
    g(4, row(104, 290, 520, "IT BREAKS AT THE WORST TIME", "Game night, and the call comes to you.", "s-accent", "f-surface", 84),
         row(656, 290, 520, "NO NETFLIX-STYLE APP", "No profiles; 15,000 channels to dig through.", "s-accent", "f-surface", 84)),
    g(5, row(104, 394, 520, "SIDE-LOADED APPS", "Outside the app store; malware risk.", "s-accent", "f-surface", 84),
         row(656, 394, 520, "NOTHING IS CHECKED", "Age, refunds, channel count: unverified.", "s-accent", "f-surface", 84)),
    g(6, box(104, 520, 1072, 100, "f-ink", "s-ink", 6),
         '<text x="132" y="582" class="td f-bg" font-size="32">Expect a few calls a month, and some outages.</text>'),
)

S[7] = svg(
    g(1, chip("CH 06 — THE FREE ONE")),
    g(2, title(["PLEX: FREE, WITH ADS"])),
    g(3, para(["Not cable, but a lot of watching for $0."], y=236, size=24)),
    g(4, row(104, 290, 520, "LIVE CHANNELS", "Hundreds: news, movies, kids, some sports.", "s-good", "f-good-bg", 84),
         row(656, 290, 520, "ON-DEMAND LIBRARY", "Tens of thousands of movies and shows.", "s-good", "f-good-bg", 84)),
    g(5, row(104, 394, 520, "CANADIAN CHANNELS", "Bell Media's CTV News and TSN The Ocho.", "s-good", "f-good-bg", 84),
         row(656, 394, 520, "RUNS ON YOUR TV", "App for Fire TV, Roku and most smart TVs.", "s-good", "f-good-bg", 84)),
    g(6, para(["No NHL or premium cable channels.", "Channel counts vary by source (about 250–600+); check Plex's guide."],
              x=104, y=540, size=20, lh=30, cls="f-muted")),
)

S[8] = svg(
    g(1, chip("THE TAKEAWAY")),
    g(2, title(["TRIM FIRST,", "THEN DECIDE"], y=190, size=76)),
    g(3, check(110, 340, "Add Plex; it's free", .0),
         check(110, 400, "Pay for hockey only in season", .25),
         check(110, 460, "Drop overlapping subscriptions", .5),
         check(110, 520, "That alone gets near $620 a year", .75)),
    g(4, box(104, 566, 1072, 92, "f-bad-bg", "s-bad", 6),
         '<text x="132" y="604" class="tb f-ink" font-size="24">Still tempted by the box? Pay month to month, not for a year.</text>',
         '<text x="132" y="638" class="tb f-ink" font-size="24">Keep another way to watch hockey in case it stops working.</text>'),
)

for n, body in S.items():
    (HERE / f"{n}.svg").write_text(body)
print(f"wrote {len(S)} slides")
