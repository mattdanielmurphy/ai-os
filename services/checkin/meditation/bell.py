"""The guiding bell: a tingsha (two small Tibetan cymbals), rendered from code to bell-tingsha.flac.

Bright, high and metallic with a slow shimmer, so it can't be mistaken for the soft low mallet notes in the music.
"""
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent / "bell-tingsha.flac"
LENGTH = 6
PARTIALS = [(2093, 1, 1.5), (2099, .8, 1.4), (3517, .45, 1.0), (5240, .25, .6), (7310, .12, .35)]  # Hz, level, decay s


def expr(delay):
    return "+".join(f"{a}*exp(-(t-{delay})/{d})*sin(2*PI*{f}*(t-{delay}))*gte(t,{delay})" for f, a, d in PARTIALS)


if __name__ == "__main__":
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
                    f"aevalsrc='0.22*({expr(0)})+0.16*({expr(0.16)})':s=48000:d={LENGTH}",
                    "-af", f"afade=t=out:st={LENGTH - 1}:d=1", "-ac", "2", str(OUT)], check=True)
    print(OUT)
