#!/usr/bin/env python3
"""Build an explainer reel: Figma slides + a narrated voice, as one self-contained player page.

Usage: build.py REEL_DIR [--voice maeve]

REEL_DIR holds reel.json ({title, eyebrow, voice, figma, beats: [{svg, say}]}) and one SVG per beat,
exported from Figma (exportAsync SVG_STRING, svgOutlineText false, svgIdAttribute true). Layers named
a1, a2, … reveal in that order while the beat plays. Colours are the page kit's light hexes; the build
swaps them for kit roles so the slides follow light/dark. Voice lines go through Deepgram (tts.py) and
are read in one take and cut per beat (see one_take), cached in REEL_DIR/audio/.
Output: REEL_DIR/reel.html (publish it with the Artifact tool).
"""
import argparse, base64, difflib, hashlib, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
from tts import speak, words  # noqa: E402

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


def norm(w: str) -> str:
    return re.sub(r"[^a-z0-9']", "", w.lower())


def one_take(lines: list[str], voice: str, folder: Path) -> list[Path]:
    """Read the whole script in ONE TTS call (one consistent voice, no energy drop at every line end),
    then cut it into per-beat clips. Cut points come from speech-to-text word timings: halfway between
    the last word of one beat and the first word of the next. Cached by voice + full script."""
    tag = hashlib.sha1((f"{voice}|" + "\n".join(lines)).encode()).hexdigest()[:12]
    clips = [folder / f"{tag}-{k + 1}.mp3" for k in range(len(lines))]
    if all(c.exists() for c in clips):
        return clips
    full = folder / f"{tag}-full.mp3"
    if not full.exists():
        speak(voice, "\n\n".join(lines), full)
    heard = [w for w in words(full) if norm(w["word"])]
    said, owner = [], []
    for k, line in enumerate(lines):
        for w in line.split():
            if norm(w):
                said.append(norm(w)); owner.append(k)
    # map each heard word to the beat that owns the matching scripted word
    beat_of = [None] * len(heard)
    sm = difflib.SequenceMatcher(None, said, [norm(w["word"]) for w in heard], autojunk=False)
    for a, b, n in sm.get_matching_blocks():
        for j in range(n):
            beat_of[b + j] = owner[a + j]
    cuts, end = [0.0], duration(full)
    for k in range(1, len(lines)):
        last = max((w["end"] for w, o in zip(heard, beat_of) if o is not None and o < k), default=None)
        first = min((w["start"] for w, o in zip(heard, beat_of) if o is not None and o >= k), default=None)
        if last is None or first is None:
            sys.exit(f"couldn't place the cut before beat {k + 1}; check the script against the audio")
        cuts.append(round((last + first) / 2, 3))
    cuts.append(end)
    for k, clip in enumerate(clips):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(full), "-ss", str(cuts[k]), "-to", str(cuts[k + 1]),
                        "-c:a", "libmp3lame", "-b:a", "64k", str(clip)], check=True)
    return clips


def build(reel_dir: Path, voice: str | None = None) -> Path:
    reel = json.loads((reel_dir / "reel.json").read_text())
    voice = voice or reel.get("voice", "maeve")
    audio = reel_dir / "audio"
    audio.mkdir(exist_ok=True)
    clips = one_take([b["say"] for b in reel["beats"]], voice, audio)
    beats = []
    for b, mp3 in zip(reel["beats"], clips):
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
