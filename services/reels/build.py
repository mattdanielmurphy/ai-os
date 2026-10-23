#!/usr/bin/env python3
"""Build an explainer reel: Figma slides + a narrated voice, as one self-contained player page.

Usage: build.py REEL_DIR [--voice maeve]

REEL_DIR holds reel.json ({title, eyebrow, voice, figma, beats: [{svg, say}]}) and one SVG per beat,
exported from Figma (exportAsync SVG_STRING, svgOutlineText false, svgIdAttribute true). Layers named
a1, a2, … reveal in that order while the beat plays. Colours are the page kit's light hexes; the build
swaps them for kit roles so the slides follow light/dark. Voice lines go through Deepgram (tts.py) and
are cached by text+voice in REEL_DIR/audio/, so re-builds only pay for changed lines.
Output: REEL_DIR/reel.html (publish it with the Artifact tool).
"""
import argparse, base64, hashlib, json, re, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
from tts import speak  # noqa: E402

# Kit light-mode hex → role (services/pages/kit.css). Anything else is left alone.
ROLES = {"#EEF2F6": "bg", "#FFFFFF": "surface", "WHITE": "surface", "#1D2A3A": "ink", "#5D6B7C": "muted",
         "#D6DEE8": "line", "#D9822B": "accent", "#9FB8D4": "sky", "#2F7D5B": "good", "#B3443C": "bad",
         "#E3F2EA": "good-bg", "#F8E4E2": "bad-bg"}


def themed(svg: str) -> str:
    """fill="#hex" / stroke="#hex" → classes f-<role> / s-<role>, so CSS vars pick light or dark."""
    def tag(m):
        t, classes = m.group(0), []
        for attr, pre in (("fill", "f"), ("stroke", "s")):
            a = re.search(rf'\s{attr}="([^"]+)"', t)
            role = a and ROLES.get(a.group(1).upper())
            if role:
                t = t.replace(a.group(0), "", 1)
                classes.append(f"{pre}-{role}")
        return t if not classes else re.sub(r"^<(\w+)", rf'<\1 class="{" ".join(classes)}"', t)
    svg = re.sub(r"<(?:rect|text|path|circle|ellipse|line|polygon)\b[^>]*>", tag, svg)
    svg = re.sub(r'^<svg width="\d+" height="\d+"', "<svg", svg.strip())  # scale to its container
    return svg


def duration(mp3: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp3)],
                         capture_output=True, text=True, check=True).stdout
    return round(float(out), 2)


def build(reel_dir: Path, voice: str | None = None) -> Path:
    reel = json.loads((reel_dir / "reel.json").read_text())
    voice = voice or reel.get("voice", "maeve")
    audio = reel_dir / "audio"
    audio.mkdir(exist_ok=True)
    beats = []
    for b in reel["beats"]:
        mp3 = audio / (hashlib.sha1(f"{voice}|{b['say']}".encode()).hexdigest()[:12] + ".mp3")
        if not mp3.exists():
            speak(voice, b["say"], mp3)
        beats.append({"svg": themed((reel_dir / b["svg"]).read_text()), "say": b["say"], "dur": duration(mp3),
                      "audio": "data:audio/mpeg;base64," + base64.b64encode(mp3.read_bytes()).decode()})
    tweaks = {k: v["value"] for k, v in json.loads((HERE / "tweaks.json").read_text())["tweaks"].items()}
    data = {"title": reel["title"], "eyebrow": reel.get("eyebrow", ""), "voice": voice.title(),
            "figma": reel.get("figma", ""), "beats": beats, "tweaks": tweaks}
    html = (HERE / "template.html").read_text()
    html = html.replace("/*__KIT_CSS__*/", (HERE.parent / "pages" / "kit.css").read_text())
    html = html.replace("__TITLE__", reel["title"].replace("<", "&lt;"))
    html = html.replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    out = reel_dir / "reel.html"
    out.write_text(html)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("reel_dir", type=Path)
    ap.add_argument("--voice")
    a = ap.parse_args()
    out = build(a.reel_dir.resolve(), a.voice)
    print(f"{out} ({out.stat().st_size // 1024} KB)")
