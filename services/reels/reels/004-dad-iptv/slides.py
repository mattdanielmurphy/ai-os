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


S[1] = svg(
    g(1, chip("REEL 04 — FOR DAD")),
    g(2, title(["IS THE CHEAP", "TV BOX WORTH IT?"], y=200, size=92)),
    g(3, para(["A Firestick that streams 15,000 channels for about",
               "$150–400 a year. A friend vouches for it.",
               "Here is the honest upside, the downside, and the safer options."], y=370, size=25, lh=38)),
    g(4, box(104, 520, 1072, 110, "f-surface", "s-line", 6),
         label(132, 560, "THE SHORT VERSION", 15),
         '<text x="132" y="606" class="td f-ink" font-size="36">Cheap, but legally risky and could vanish any day.</text>'),
)

S[2] = svg(
    g(1, chip("CH 01 — THE MONEY")),
    g(2, title(["WHAT TV COSTS A YEAR"])),
    g(3, para(["Rough yearly costs. The first two are what Dad paid, then what he cut."], y=236)),
    g(4, bar(310, "TELUS TV  (CANCELLED)", "$900", 640, "f-line", "$75 a month", 0)),
    g(5, bar(398, "NOW: SPORTSNET+, APPLE ONE, NETFLIX, PRIME", "$350", 250, "f-sky", "Dad's own count", .2)),
    g(6, bar(486, "THE IPTV BOX", "$150–400", 260, "f-bad", "unverified", .4)),
    g(7, bar(574, "FREE LOCAL TV + FREE APPS", "$0–100", 40, "f-good", "one-off antenna", .6)),
    g(8, para(["Only the box saves real money against what he has now, and only if it keeps working."],
              y=662, size=20, cls="f-muted")),
)

S[3] = svg(
    g(1, chip("CH 02 — THE UPSIDE")),
    g(2, title(["WHY PEOPLE LIKE IT"])),
    g(3, row(104, 260, 520, "BIG SAVING", "Often a fraction of cable or Telus TV.", "s-good", "f-good-bg")),
    g(4, row(656, 260, 520, "LOTS OF CHANNELS", "Live sports, news, movies. Count unverified.", "s-good", "f-good-bg")),
    g(5, row(104, 380, 520, "EASY SETUP", "Arrives as a plug-in Firestick.", "s-good", "f-good-bg")),
    g(6, row(656, 380, 520, "TRY BEFORE YOU COMMIT", "Trials and monthly plans cap the risk.", "s-good", "f-good-bg")),
    g(7, box(104, 520, 1072, 100, "f-surface", "s-line", 6),
         '<text x="132" y="580" class="tb f-ink" font-size="25">A real friend uses it, and Dad does not care about 720p versus 4K.</text>'),
)

S[4] = svg(
    g(1, chip("CH 03 — THE BIG ONE: LEGAL")),
    g(2, title(["IT SELLS STREAMS NOBODY LICENSED"], size=54)),
    g(3, row(104, 250, 340, "SELLING", "Clearly illegal|in Canada.", "s-bad", "f-bad-bg", 130)),
    g(4, row(470, 250, 340, "BLOCKING", "Courts made ISPs|block these sites.", "s-bad", "f-bad-bg", 130)),
    g(5, row(836, 250, 340, "WATCHING", "Grey zone.|Not clearly safe.", "s-accent", "f-surface", 130)),
    g(6, para(["Court blocking began with a 2019 order against GoldTV and was upheld on appeal in 2021."],
              y=440, size=22, cls="f-muted"),
         box(104, 490, 1072, 130, "f-ink", "s-ink", 6),
         '<text x="132" y="545" class="td f-bg" font-size="34">Do not assume nobody will come after you.</text>',
         '<text x="132" y="588" class="tb f-bg" font-size="22">For a firm answer about Dad personally, ask a lawyer.</text>'),
)

S[5] = svg(
    g(1, chip("CH 04 — WHAT CAN GO WRONG")),
    g(2, title(["THE EVERYDAY RISKS"])),
    g(3, row(104, 230, 520, "IT CAN VANISH", "Mid-term, no refund (unverified).", "s-bad", "f-bad-bg", 84)),
    g(4, row(656, 230, 520, "HOCKEY NIGHT BUFFERING", "Peak hours strain these services.", "s-bad", "f-bad-bg", 84)),
    g(5, row(104, 334, 520, "SITES GET BLOCKED", "Your ISP may block it; a VPN may be needed.", "s-bad", "f-bad-bg", 84)),
    g(6, row(656, 334, 520, "NO WAY TO GET MONEY BACK", "E-transfer has no chargeback.", "s-bad", "f-bad-bg", 84)),
    g(7, row(104, 438, 520, "ONE PERSON FOR HELP", "Support is a single WhatsApp contact.", "s-line", "f-surface", 84)),
    g(8, row(656, 438, 520, "SAFETY OF THE APP", "Side-loaded apps can carry malware.", "s-line", "f-surface", 84)),
    g(9, para(["Also: payment details go to a seller no one holds accountable,",
               "and it is nothing like Netflix: no profiles, 15,000 channels to dig through."],
              x=104, y=584, size=20, lh=30)),
)

S[6] = svg(
    g(1, chip("CH 05 — THINGS WE COULD NOT CHECK")),
    g(2, title(["UNVERIFIED"])),
    g(3, para(["Nothing here was independently confirmed. Ask the seller before paying:"], y=236)),
    g(4, "".join(pill(104 + (k % 2) * 560, 290 + (k // 2) * 76, 512, t, "s-line")
                 for k, t in enumerate(["How old is the business?", "Is there any refund policy?",
                                        "Do the 15,000 channels really work?", "Does it hold up on game night?"]))),
    g(5, box(104, 470, 1072, 120, "f-surface", "s-accent", 6),
         label(132, 508, "WHAT HELPS", 15),
         '<text x="132" y="556" class="td f-ink" font-size="32">Ask the friend: how long, how many outages, how hockey runs.</text>'),
)

S[7] = svg(
    g(1, chip("CH 06 — LEGAL OPTIONS")),
    g(2, title(["SAFER WAYS TO SAVE"])),
    g(3, row(104, 230, 520, "FREE LOCAL TV", "Antenna: one-off, about $0–100.", "s-good", "f-good-bg", 84),
         row(656, 230, 520, "FREE APPS", "CBC Gem and others. Check which games.", "s-good", "f-good-bg", 84)),
    g(4, row(104, 334, 520, "SPORTSNET+", "$34.99 a month, $269.99 a year.", "s-line", "f-surface", 84),
         row(656, 334, 520, "CRAVE", "$11.99 a month with ads, $22 without.", "s-line", "f-surface", 84)),
    g(5, row(104, 438, 520, "ONLY IN SEASON", "Pay by the month for hockey, then stop.", "s-sky", "f-surface", 84),
         row(656, 438, 520, "TRIM OVERLAPS", "Keep only what you actually watch.", "s-sky", "f-surface", 84)),
    g(6, para(["List prices from this month; check each site before signing up.",
               "Netflix with ads $7.99, Prime $99 a year, Apple One from $22.95 a month."],
              x=104, y=584, size=19, lh=28)),
)

S[8] = svg(
    g(1, chip("SO WHAT SHOULD DAD DO?")),
    g(2, title(["START WITH THE", "SAFE SAVINGS"], y=190, size=76)),
    g(3, check(110, 340, "Add an antenna and free apps first", .0),
         check(110, 400, "Pay for hockey only while it's in season", .25),
         check(110, 460, "Drop overlapping subscriptions", .5),
         check(110, 520, "Tempted by the box? Ask a lawyer first", .75)),
    g(4, box(104, 570, 1072, 80, "f-bad-bg", "s-bad", 6),
         '<text x="132" y="622" class="tb f-ink" font-size="24">If he still goes ahead: month-to-month only, and expect it to stop working.</text>'),
)

for n, body in S.items():
    (HERE / f"{n}.svg").write_text(body)
print(f"wrote {len(S)} slides")
