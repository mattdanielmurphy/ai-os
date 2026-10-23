#!/usr/bin/env python3
"""Reel 03 slides, written as SVG by hand (theme role classes, not hexes). Run: python3 slides.py
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

S[1] = svg(
    g(1, chip("REEL 03 — HOW YOUR MAC STAYS CALM")),
    g(2, title(["AIR TRAFFIC", "CONTROL"], y=200, size=104)),
    g(3, para(["Several Claude agents work on your Mac",
               "at once. One queue decides who may",
               "touch the keyboard, mouse and screen,",
               "so nobody types over anybody. Including you."], y=360, size=25, lh=38)),
    g(4, radar(950, 330, 210, [])),
    g(5, '<circle cx="1028" cy="214" r="9" class="f-accent pulse"/>', label(1044, 219, "FIGMA TEST", 14, "f-ink"),
         '<circle cx="852" cy="430" r="9" class="f-sky pulse" style="animation-delay:.6s"/>', label(868, 435, "MUSIC", 14, "f-ink"),
         '<circle cx="1062" cy="440" r="9" class="f-sky pulse" style="animation-delay:1.2s"/>', label(1078, 445, "CHECK-IN", 14, "f-ink")),
    g(6, '<line x1="104" y1="560" x2="1176" y2="560" class="s-line" stroke-width="2"/>',
         stat(104, 630, 1, "", "HOLDS CONTROL AT A TIME"), stat(420, 630, 3, " MIN", "LONGEST WAIT IN LINE"),
         stat(736, 630, 2, "", "KINDS OF ASK"), stat(990, 630, 0, "", "SURPRISE KEYSTROKES")),
)

chips = [("KEYS &amp; CLICKS", 104, 200), ("OPENING FILES &amp; APPS", 320, 286), ("FOCUSING WINDOWS", 622, 236), ("PLAY · PAUSE · VOLUME", 874, 302)]
S[2] = svg(
    g(1, chip("CH 01 — THE RULE")),
    g(2, title(["ASK FIRST. ALWAYS."])),
    g(3, para(["Before an agent touches anything you can see or hear, it runs one",
               "command, says what it wants and why, then waits for a yes."], y=236)),
    g(4, box(104, 316, 1072, 132, "f-ink", "s-ink", 6),
         '<circle cx="132" cy="340" r="6" class="f-muted"/><circle cx="152" cy="340" r="6" class="f-muted"/><circle cx="172" cy="340" r="6" class="f-muted"/>',
         '<text x="132" y="392" class="tm f-bg" font-size="21" data-type="$ claude-control ask &quot;Click Export in Figma&quot; 3 --thread cmsg_…">'
         '$ claude-control ask "Click Export in Figma" 3 --thread cmsg_…</text>'),
    g(5, '<text x="132" y="428" class="tm f-accent" font-size="21">granted 7f3a</text>',
         '<rect x="320" y="410" width="12" height="22" class="f-accent blink"/>'),
    g(6, label(104, 512, "ALL OF THESE COUNT AS INPUT", 15),
         "".join(f'<rect x="{x}" y="532" width="{w}" height="56" rx="28" class="f-surface s-accent" stroke-width="2"/>'
                 f'<text x="{x + w / 2}" y="566" class="tm f-ink" font-size="16" text-anchor="middle">{t}</text>'
                 for t, x, w in chips)),
    g(7, para(["Even a file opening in Finder, or music pausing, is a change on your screen or speakers."],
              y=640, size=21, cls="f-muted")),
)

dot = '<circle r="8" class="f-accent"><animateMotion dur="2.4s" repeatCount="indefinite" path="M334 470 H700"/></circle>'
S[3] = svg(
    g(1, chip("CH 02 — THE QUEUE")),
    g(2, title(["ONE QUEUE. ONE PILOT."])),
    g(3, para(["Asks line up in the order they arrive. Only one agent holds control;",
               "the rest wait their turn, up to three minutes, then give up politely."], y=236)),
    g(4, box(104, 330, 230, 140), label(124, 366, "WAITING #2", 15), '<text x="124" y="414" class="td f-ink" font-size="36">CHECK-IN</text>',
         label(124, 446, "queued:2", 14, "f-muted")),
    g(5, box(364, 330, 230, 140), label(384, 366, "WAITING #1", 15), '<text x="384" y="414" class="td f-ink" font-size="36">MUSIC</text>',
         label(384, 446, "queued:1", 14, "f-muted"),
         '<line x1="334" y1="400" x2="364" y2="400" class="s-accent flow" stroke-width="3"/>',
         '<line x1="594" y1="400" x2="700" y2="400" class="s-accent flow" stroke-width="3"/>'),
    g(6, '<rect x="700" y="318" width="330" height="164" rx="6" fill="none" class="s-accent glow" stroke-width="8"/>',
         box(700, 318, 330, 164, "f-accent", "s-accent", 6), label(724, 356, "HAS CONTROL", 15, "f-accent-ink"),
         '<text x="724" y="412" class="td f-accent-ink" font-size="44">FIGMA TEST</text>',
         label(724, 452, "granted · banner showing", 14, "f-accent-ink")),
    g(7, '<path d="M1030 400 H1100 V530 H220 V470" pathLength="1" fill="none" class="s-muted draw" stroke-width="2" stroke-dasharray="1"/>',
         label(1112, 405, "DONE", 15, "f-ink"), label(640, 556, "done hands control to the next in line", 14, "f-muted", "middle")),
    g(8, stat(104, 640, 1, "", "HOLDS CONTROL"), stat(420, 640, 2, "", "WAITING THEIR TURN"), stat(736, 640, 180, " S", "THEN THEY GIVE UP")),
)

S[4] = svg(
    g(1, chip("CH 03 — BANNER OR PILL")),
    g(2, title(["TWO KINDS OF ASK"])),
    g(3, para(["The bigger the intrusion, the louder the ask."], y=236)),
    g(4, box(104, 290, 520, 290, "f-surface", "s-line", 8),
         '<rect x="112" y="298" width="504" height="274" rx="6" fill="none" class="s-accent glow" stroke-width="10"/>',
         box(194, 396, 340, 84, "f-ink", "s-ink", 6),
         label(214, 428, "CLAUDE WANTS CONTROL", 14, "f-bg"),
         '<text x="214" y="460" class="tb f-bg" font-size="20">Click Export in Figma</text>',
         label(104, 620, "FULL BANNER + GLOW", 16, "f-ink"),
         para(["Typing, clicking, moving the mouse.", "Hands off until it's done."], y=652, size=21, lh=30)),
    g(5, box(656, 290, 520, 290, "f-surface", "s-line", 8),
         '<rect x="990" y="306" width="170" height="34" rx="17" class="f-ink pulse"/>',
         label(1075, 328, "OPENING A FILE", 12, "f-bg", "middle"),
         '<line x1="700" y1="420" x2="940" y2="420" class="s-line" stroke-width="10" stroke-linecap="round"/>'
         '<line x1="700" y1="450" x2="1010" y2="450" class="s-line" stroke-width="10" stroke-linecap="round"/>'
         '<line x1="700" y1="480" x2="880" y2="480" class="s-line" stroke-width="10" stroke-linecap="round"/>'
         '<rect x="886" y="468" width="4" height="24" class="f-ink blink"/>',
         label(656, 620, "LIGHT PILL", 16, "f-ink"),
         para(["Open a file or app, focus, play, volume.", "Keep typing; it's small."], x=656, y=652, size=21, lh=30)),
)


def key(x, y, t, w=96):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="72" rx="8" class="f-surface s-ink" stroke-width="2"/>'
            f'<rect x="{x}" y="{y + 66}" width="{w}" height="8" rx="3" class="f-ink"/>'
            f'<text x="{x + w / 2}" y="{y + 45}" class="tm f-ink" font-size="20" text-anchor="middle">{t}</text>')


S[5] = svg(
    g(1, chip("CH 04 — YOU'RE IN CHARGE")),
    g(2, title(["ONE KEY TO SAY NOT NOW"])),
    g(3, para(["Every ask can be answered from the keyboard, without finding a window."], y=236)),
    g(4, key(104, 300, "ESC"), '<text x="104" y="440" class="td f-ink" font-size="40">NOT NOW</text>',
         para(["The agent backs off and", "waits for your go. It", "won't re-ask on its own."], y=480, size=22, lh=32),
         label(104, 600, "exit 1 · cancelled", 14)),
    g(5, key(464, 300, "ESC"), key(572, 300, "ESC"), '<text x="464" y="440" class="td f-bad" font-size="40">STOP</text>',
         para(["Ends that agent's whole", "task, and blocks it from", "asking again for"], x=464, y=480, size=22, lh=32),
         '<text x="660" y="544" class="td f-bad" font-size="34" data-count="2" data-unit=" HOURS">2 HOURS</text>',
         label(464, 600, "exit 3 · stopped", 14)),
    g(6, "".join(f'<rect x="{824 + k * 112}" y="300" width="96" height="72" rx="36" class="f-surface s-sky" stroke-width="2"/>'
                 f'<text x="{872 + k * 112}" y="345" class="tm f-ink" font-size="20" text-anchor="middle">{t}</text>'
                 for k, t in enumerate(["30S", "1M", "5M"])),
         '<text x="824" y="440" class="td f-ink" font-size="40">SNOOZE</text>',
         para(["Not yet? It waits that", "long and keeps its place", "in the line."], x=824, y=480, size=22, lh=32),
         label(824, 600, "still queued", 14)),
)

S[6] = svg(
    g(1, chip("CH 05 — WHO'S ASKING?")),
    g(2, title(["CLICK THE BANNER, FIND THE THREAD"])),
    g(3, para(["Every ask carries a link to the thread behind it, so you can see why."], y=236)),
    g(4, box(104, 300, 360, 100, "f-ink", "s-ink", 6), label(124, 336, "CLAUDE WANTS CONTROL", 14, "f-bg"),
         '<text x="124" y="372" class="tb f-bg" font-size="21">Click Export in Figma</text>',
         '<path d="M420 360 l0 34 l9 -8 l7 15 l7 -3 l-7 -15 l12 -1 z" class="f-bg s-ink" stroke-width="2"/>'),
    g(5, '<path d="M464 350 C560 350 560 350 640 350" pathLength="1" fill="none" class="s-accent draw" stroke-width="3"/>',
         '<line x1="464" y1="350" x2="640" y2="350" class="s-accent flow" stroke-width="3" opacity=".6"/>',
         box(640, 290, 536, 130, "f-surface", "s-accent", 6), label(664, 326, "PROJECT THREAD", 14),
         '<text x="664" y="372" class="td f-ink" font-size="38">EXPLAINER REELS</text>',
         '<text x="664" y="404" class="tb f-muted" font-size="20">“Testing the export, muted. Back in a sec.”</text>'),
    g(6, box(104, 470, 1072, 150, "f-bad-bg", "s-bad", 6), label(132, 510, "--URGENT", 18, "f-bad"),
         '<text x="132" y="560" class="td f-ink" font-size="40">SKIPS THE LINE. RUNAWAYS ONLY.</text>',
         '<text x="132" y="596" class="tb f-ink" font-size="21">For stopping something hammering your Mac right now. Never for routine tests.</text>'),
)

S[7] = svg(
    g(1, chip("CH 06 — ROBOTS TAKE A NUMBER")),
    g(2, title(["YOUR AUTOMATIONS QUEUE TOO"])),
    g(3, para(["Hammerspoon, Keyboard Maestro and scripts use the same queue, silently:",
               "claude-control lock. No banner, but no collisions either."], y=236)),
    g(4, box(104, 340, 300, 96), label(124, 374, "YOU PRESS A KEY", 15), '<text x="124" y="416" class="td f-ink" font-size="32">A HOTKEY, A PAD</text>',
         '<line x1="404" y1="388" x2="860" y2="388" class="s-good flow" stroke-width="4"/>',
         '<circle r="8" class="f-good"><animateMotion dur="1.1s" repeatCount="indefinite" path="M404 388 H860"/></circle>',
         box(860, 340, 316, 96, "f-good-bg", "s-good"), label(880, 374, "RUNS NOW", 15, "f-good"),
         '<text x="880" y="416" class="td f-ink" font-size="32">NEVER QUEUED</text>'),
    g(5, box(104, 486, 300, 96), label(124, 520, "RUNS ON ITS OWN", 15), '<text x="124" y="562" class="td f-ink" font-size="32">TIMERS · AGENTS</text>',
         '<line x1="404" y1="534" x2="520" y2="534" class="s-accent flow" stroke-width="4"/>',
         box(520, 496, 230, 76, "f-surface", "s-accent"), label(635, 541, "lock · wait turn", 15, "f-ink", "middle"),
         '<line x1="750" y1="534" x2="860" y2="534" class="s-accent flow" stroke-width="4"/>',
         '<circle r="8" class="f-accent"><animateMotion dur="3.2s" repeatCount="indefinite" keyPoints="0;0.27;0.27;1" keyTimes="0;0.25;0.65;1" calcMode="linear" path="M404 534 H860"/></circle>',
         box(860, 486, 316, 96, "f-surface", "s-line"), label(880, 520, "RUNS IN TURN", 15),
         '<text x="880" y="562" class="td f-ink" font-size="32">NO BANNER</text>'),
    g(6, para(["Rule of thumb: quick things you trigger run instantly; anything that holds input for more than a second or two waits."],
              y=640, size=20, cls="f-muted")),
)

S[8] = svg(
    g(1, chip("THAT'S IT")),
    g(2, title(["NOBODY FIGHTS", "FOR THE KEYBOARD"], y=190, size=80)),
    g(3, check(110, 360, "Agents ask before touching anything", .0),
         check(110, 420, "One holds control; the rest wait in line", .25),
         check(110, 480, "Esc means not now. Esc Esc means stop", .5),
         check(110, 540, "Click a banner to see who's flying", .75)),
    g(4, radar(1000, 400, 170, [(1060, 330, "LANDED"), (930, 470, "WAITING")])),
    g(5, label(104, 640, "MADE WITH A DEEPGRAM VOICE · MUSIC UNDER, DUCKED SO SHE STAYS CLEAR", 14)),
)

for n, body in S.items():
    (HERE / f"{n}.svg").write_text(body)
print(f"wrote {len(S)} slides")
