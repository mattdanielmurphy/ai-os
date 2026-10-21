#!/usr/bin/env python3
"""Catch what the Claude desktop app is doing when dictation freezes it.

Follows ~/Library/Logs/Claude/main.log. When Claude asks for the microphone
("Media permission probe ... captureKind: 'audio'") or reports "Main webview is
unresponsive", it samples Claude's main process, its busiest renderer, its
audio service and coreaudiod for a few seconds (macOS `sample`, read-only).
Output goes to ~/projects/ai-os/tmp/claude-hang/<time>/. Stop with Ctrl-C.

Usage: python3 scripts/claude_hang_capture.py [--seconds 8]
"""
import argparse
import os
import subprocess
import time
from datetime import datetime

LOG = os.path.expanduser("~/Library/Logs/Claude/main.log")
OUT = os.path.expanduser("~/projects/ai-os/tmp/claude-hang")
COOLDOWN = 30  # seconds between captures


def claude_pids():
    ps = subprocess.run(["ps", "-Ao", "pid=,rss=,command="], capture_output=True, text=True).stdout
    main, renderers, audio = None, [], None
    for line in ps.splitlines():
        parts = line.split(None, 2)
        if len(parts) < 3:
            continue
        pid, rss, cmd = int(parts[0]), int(parts[1]), parts[2]
        if cmd.startswith("/Applications/Claude.app/Contents/MacOS/Claude"):
            main = pid
        elif "Claude Helper (Renderer)" in cmd:
            renderers.append((rss, pid))
        elif "Claude Helper" in cmd and "audio.mojom.AudioService" in cmd:
            audio = pid
    targets = {"main": main, "audio": audio}
    if renderers:
        targets["renderer"] = max(renderers)[1]
    found = subprocess.run(["pgrep", "-x", "coreaudiod"], capture_output=True, text=True).stdout.split()
    if found:
        targets["coreaudiod"] = int(found[0])
    return {k: v for k, v in targets.items() if v}


def capture(reason, seconds):
    d = os.path.join(OUT, datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "reason.txt"), "w") as f:
        f.write(reason + "\n")
    procs = [subprocess.Popen(["sample", str(pid), str(seconds), "10", "-mayDie", "-file", os.path.join(d, f"{name}-{pid}.txt")],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
             for name, pid in claude_pids().items()]
    with open(os.path.join(d, "audio-devices.txt"), "w") as f:
        subprocess.run(["/usr/local/bin/SwitchAudioSource", "-a"], stdout=f, stderr=subprocess.DEVNULL)
    for p in procs:
        p.wait()
    print(f"{datetime.now():%H:%M:%S} captured ({reason}) -> {d}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=int, default=8)
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    print(f"watching {LOG}", flush=True)
    f = open(LOG)
    f.seek(0, os.SEEK_END)
    last, probe = 0.0, False
    while True:
        line = f.readline()
        if not line:
            if os.path.getsize(LOG) < f.tell():  # log rotated
                f = open(LOG)
            time.sleep(0.2)
            continue
        reason = None
        if "Media permission probe" in line:
            probe = True
        elif probe and "captureKind: 'audio'" in line:
            reason, probe = "microphone requested (dictation start)", False
        elif "Main webview is unresponsive" in line:
            reason = "main webview unresponsive"
        elif line.startswith("}"):
            probe = False
        if reason and time.time() - last > COOLDOWN:
            last = time.time()
            capture(reason, args.seconds)


if __name__ == "__main__":
    main()
