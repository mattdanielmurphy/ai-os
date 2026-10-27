"""Guided audio: a script of spoken lines and pauses -> one m4a, voice over a music bed.

  build.py scripts/<name>.txt [out.m4a]     default out: out/<name>.m4a

Script format: `# voice: <speechify id>`, `# speed: 0.88`, `# music: <audio file>` headers, then one spoken
segment per line and `[pause N]` for N seconds of music only. Each line is voiced once by Speechify
(services/reels/tts.py) and cached in tmp/ by its text, so editing one line re-records only that line.
The music is one of the code-rendered real-instrument loops in ~/projects/claude-ambient (no AI music).
"""
import hashlib, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "reels"))
import tts  # noqa: E402

# Feel knobs
GAP = 1.2          # s of quiet after every spoken line, on top of any [pause]
MUSIC_DB = -13     # music level under the voice (dB) before ducking
DUCK = 4           # extra dB the music dips while the voice speaks
FADE_IN, FADE_OUT = 6, 12
LUFS = -18         # final loudness: quiet, for headphones in bed


def parse(path):
    head, items = {}, []
    for raw in Path(path).read_text().splitlines():
        line = raw.strip()
        if m := re.match(r"#\s*(\w+):\s*(.+)", line):
            head[m[1]] = m[2].strip()
        elif not line or line.startswith("#"):
            continue
        elif m := re.match(r"\[pause\s+([\d.]+)\]", line):
            items.append(("pause", float(m[1])))
        else:
            items.append(("say", line))
    return head, items


def dur(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", str(f)]).decode())


def build(script, out=None):
    head, items = parse(script)
    voice, speed = head.get("voice", "douglas"), float(head.get("speed", 0.9))
    music = Path(head["music"]).expanduser()
    name = Path(script).stem
    out = Path(out or HERE / "out" / f"{name}.m4a")
    cache = HERE / "tmp" / "lines"
    cache.mkdir(parents=True, exist_ok=True)
    out.parent.mkdir(parents=True, exist_ok=True)

    t, placed, lines = 0.0, [], []
    for kind, val in items:
        if kind == "pause":
            t += val
            continue
        key = hashlib.sha1(f"{voice}|{speed}|{val}".encode()).hexdigest()[:12]
        mp3 = cache / f"{key}.mp3"
        if not mp3.exists() or mp3.stat().st_size < 1000:
            tts.speak(voice, val, mp3, speed)
        d = dur(mp3)
        placed.append((mp3, t))
        lines.append({"t": round(t, 2), "text": val})
        t += d + GAP
    total = t + FADE_OUT

    # Voice track: each line delayed to its start; music: loop trimmed, faded, ducked under the voice.
    args = ["ffmpeg", "-y", "-v", "error"]
    for mp3, _ in placed:
        args += ["-i", str(mp3)]
    args += ["-stream_loop", "-1", "-i", str(music)]
    fc = [f"[{i}]aresample=48000,aformat=channel_layouts=stereo,adelay={int(s * 1000)}:all=1[v{i}]"
          for i, (_, s) in enumerate(placed)]
    n = len(placed)
    fc.append("".join(f"[v{i}]" for i in range(n)) + f"amix=inputs={n}:normalize=0,apad=whole_dur={total}[vo]")
    fc.append("[vo]asplit[voice][key]")
    fc.append(f"[{n}]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{total},volume={MUSIC_DB}dB,"
              f"afade=t=in:d={FADE_IN},afade=t=out:st={total - FADE_OUT}:d={FADE_OUT}[m]")
    fc.append(f"[m][key]sidechaincompress=threshold=0.02:ratio={1 + DUCK}:attack=200:release=1500[md]")
    fc.append(f"[voice][md]amix=inputs=2:normalize=0,loudnorm=I={LUFS}:TP=-2:LRA=11[out]")
    args += ["-filter_complex", ";".join(fc), "-map", "[out]", "-t", str(total),
             "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(out)]
    subprocess.run(args, check=True)
    (out.with_suffix(".json")).write_text(json.dumps({"title": name, "voice": voice, "music": music.name,
                                                      "seconds": round(total), "lines": lines}, indent=1))
    print(json.dumps({"out": str(out), "seconds": round(total), "lines": len(lines)}))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__.strip())
    build(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
