#!/usr/bin/env python3
"""Build an explainer reel: Figma slides + a narrated voice, as one self-contained player page.

Usage: build.py REEL_DIR [--voice maeve]

REEL_DIR holds reel.json ({title, eyebrow, voice, theme, pace, figma, music, beats: [{svg, say}]}) and one SVG
per beat, exported from Figma (exportAsync SVG_STRING, svgOutlineText false, svgIdAttribute true).
Layers named a1, a2, … reveal in that order while the beat plays.

Look: themes/<theme>.json gives fonts and colour roles ([light, dark] per role). Design the Figma slides
with the roles' LIGHT hexes; the build swaps them for role classes so slides follow light/dark. Other
colours (e.g. swatches shown as content) are left alone. Every reel should get its own theme or a
deliberate one; never the stock kit (No Claude-default look rule).

Voice: the whole script is read in one Deepgram take at `pace` (default: tweak voice.pace), then cut per
beat by word timings (see one_take), cached in REEL_DIR/audio/.
Music: optional `music` (path to a loop) plays under the voice, side-chain ducked in the player. The build
trims it to what the reel can use (Gentle pace included), evens its loudness and fades its ends.
Output: REEL_DIR/reel.html (publish it with the Artifact tool).
"""
import argparse, base64, difflib, hashlib, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
from tts import speak, words  # noqa: E402


def theme_css(theme: dict) -> str:
    roles, f = theme["roles"], theme["fonts"]
    light = "".join(f"--{r}:{v[0]};" for r, v in roles.items())
    dark = "".join(f"--{r}:{v[1]};" for r, v in roles.items()) + "color-scheme:dark;"
    fonts = f'--display:"{f["display"]}",system-ui,sans-serif;--body:"{f["body"]}",system-ui,sans-serif;' \
            f'--mono:"{f["mono"]}",ui-monospace,monospace;'
    classes = "".join(f".f-{r}{{fill:var(--{r})}}.s-{r}{{stroke:var(--{r})}}" for r in roles)
    return (f":root{{{light}{fonts}}}"
            f"@media (prefers-color-scheme: dark){{:root:not([data-theme=\"light\"]){{{dark}}}}}"
            f":root[data-theme=\"dark\"]{{{dark}}}{classes}{theme.get('css', '')}")


def themed(svg: str, theme: dict) -> str:
    """fill="#hex" / stroke="#hex" matching a role's light value → classes f-<role> / s-<role>."""
    lookup = {v[0].upper(): r for r, v in theme["roles"].items()}
    lookup.update({k.upper(): r for k, r in theme.get("aliases", {}).items()})

    def tag(m):
        t, classes = m.group(0), []
        for attr, pre in (("fill", "f"), ("stroke", "s")):
            a = re.search(rf'\s{attr}="([^"]+)"', t)
            role = a and lookup.get(a.group(1).upper())
            if role:
                t = t.replace(a.group(0), "", 1)
                classes.append(f"{pre}-{role}")
        return t if not classes else re.sub(r"^<(\w+)", rf'<\1 class="{" ".join(classes)}"', t)
    svg = re.sub(r"<(?:rect|text|path|circle|ellipse|line|polygon)\b[^>]*>", tag, svg)
    svg = re.sub(r'\sclip-path="url\(#[^)]*\)"', "", svg)  # Figma clips groups; they'd crop the rise-in animation
    return re.sub(r'^<svg width="\d+" height="\d+"', "<svg", svg.strip())  # scale to its container


def duration(mp3: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp3)],
                         capture_output=True, text=True, check=True).stdout
    return round(float(out), 2)


def norm(w: str) -> str:
    return re.sub(r"[^a-z0-9']", "", w.lower())


def one_take(lines: list[str], voice: str, pace: float, folder: Path) -> list[Path]:
    """Read the whole script in ONE TTS call (one consistent voice, no energy drop at every line end),
    then cut it into per-beat clips. Cut points come from speech-to-text word timings: halfway between
    the last word of one beat and the first word of the next. Cached by voice + pace + full script."""
    tag = hashlib.sha1((f"{voice}|{pace}|" + "\n".join(lines)).encode()).hexdigest()[:12]
    clips = [folder / f"{tag}-{k + 1}.mp3" for k in range(len(lines))]
    if all(c.exists() for c in clips):
        return clips
    full = folder / f"{tag}-full.mp3"
    if not full.exists():
        speak(voice, "\n\n".join(lines), full, speed=pace)
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
        subprocess.run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-i", str(full), "-ss", str(cuts[k]), "-to", str(cuts[k + 1]),
                        "-c:a", "libmp3lame", "-b:a", "64k", str(clip)], check=True)
    return clips


def music_bed(src: Path, seconds: float, folder: Path) -> Path:
    """Trim a loop to `seconds`, even its loudness (so music.level means the same for every loop), fade
    both ends, and encode small. Cached by source + length."""
    seconds = min(seconds, duration(src))
    tag = hashlib.sha1(f"{src.resolve()}|{src.stat().st_mtime}|{seconds:.0f}".encode()).hexdigest()[:12]
    out = folder / f"music-{tag}.m4a"
    if not out.exists():
        fade = f"afade=t=in:d=1.5,afade=t=out:st={seconds - 6:.2f}:d=6"
        subprocess.run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-i", str(src), "-t", f"{seconds:.2f}",
                        "-af", f"loudnorm=I=-20:TP=-2,{fade}", "-ar", "44100", "-c:a", "aac", "-b:a", "96k", str(out)],
                       check=True)
    return out


def build(reel_dir: Path, voice: str | None = None, music: str | None = None) -> Path:
    reel = json.loads((reel_dir / "reel.json").read_text())
    tweaks = {k: v["value"] for k, v in json.loads((HERE / "tweaks.json").read_text())["tweaks"].items()}
    theme = json.loads((HERE / "themes" / f"{reel.get('theme', 'panel')}.json").read_text())
    voice = voice or reel.get("voice", "maeve")
    pace = reel.get("pace", tweaks["voice.pace"])
    audio = reel_dir / "audio"
    audio.mkdir(exist_ok=True)
    clips = one_take([b["say"] for b in reel["beats"]], voice, pace, audio)
    beats = []
    for b, mp3 in zip(reel["beats"], clips):
        beats.append({"svg": themed((reel_dir / b["svg"]).read_text(), theme), "say": b["say"], "dur": duration(mp3),
                      "audio": "data:audio/mpeg;base64," + base64.b64encode(mp3.read_bytes()).decode()})
    data = {"title": reel["title"], "eyebrow": reel.get("eyebrow", ""), "voice": voice.title(),
            "figma": reel.get("figma", ""), "beats": beats, "tweaks": tweaks, "music": None}
    music = music or reel.get("music")
    if music:
        src = (reel_dir / Path(music).expanduser()).resolve()
        talk = sum(b["dur"] for b in beats) + len(beats) * (tweaks["beat.gap"] + tweaks["beat.lead"])
        bed = music_bed(src, talk / tweaks["pace.gentle"] + tweaks["music.intro"] + 20, audio)
        data["music"] = {"name": reel.get("music_name") or src.stem,
                         "audio": "data:audio/mp4;base64," + base64.b64encode(bed.read_bytes()).decode()}
    html = (HERE / "template.html").read_text()
    html = html.replace("/*__KIT_CSS__*/", (HERE.parent / "pages" / "kit.css").read_text())
    html = html.replace("/*__THEME_CSS__*/", theme_css(theme))
    html = html.replace("__FONTS__", theme["google"])
    html = html.replace("__TITLE__", reel["title"].replace("<", "&lt;"))
    html = html.replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    out = reel_dir / "reel.html"
    out.write_text(html)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("reel_dir", type=Path)
    ap.add_argument("--voice")
    ap.add_argument("--music", help="loop to play under the voice (overrides reel.json `music`)")
    a = ap.parse_args()
    out = build(a.reel_dir.resolve(), a.voice, a.music)
    print(f"{out} ({out.stat().st_size // 1024} KB)")
