#!/usr/bin/env python3
"""Kill known memory leakers on Matt's Mac before they push it into swap.

Runs every 10 minutes from launchd (com.matt.agent.memory-guard). Only touches
processes that are safe to kill:
- accountsd above LIMIT_MB (it leaks; 7.6 GB and 97% CPU on 2026-10-25). It
  ignores SIGTERM, so SIGKILL; launchd respawns it on demand.
- Antigravity `agy --hub` processes orphaned by a closed app (parent is launchd),
  with their MCP children. Antigravity is shelved; these pile up for days.
Each kill is logged to tmp/memory-guard.log. Usage: memory_guard.py [--dry-run]
"""
import argparse
import datetime
import os
import re
import signal
import subprocess

LOG = os.path.expanduser("~/projects/ai-os/tmp/memory-guard.log")
LIMIT_MB = 1024


def log(msg):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"{datetime.datetime.now():%Y-%m-%d %H:%M} {msg}\n")


def mem_mb(pid):
    # top's MEM includes compressed/swapped pages, which ps RSS misses.
    out = subprocess.run(["top", "-l", "1", "-pid", str(pid), "-stats", "mem"],
                         capture_output=True, text=True).stdout.split()
    m = re.match(r"(\d+)([KMG])", out[-1]) if out else None
    if not m:
        return 0
    return int(m[1]) * {"K": 1 / 1024, "M": 1, "G": 1024}[m[2]]


def rows():
    out = subprocess.run(["ps", "-axo", "pid=,ppid=,comm=,command="], capture_output=True, text=True).stdout
    for l in out.splitlines():
        m = re.match(r"\s*(\d+)\s+(\d+)\s+(\S+)\s+(.*)", l)
        if m:
            yield int(m[1]), int(m[2]), m[3], m[4]


def kill(pid, sig, why, dry):
    log(f"{'would kill' if dry else 'killed'} {pid}: {why}")
    if not dry:
        try:
            os.kill(pid, sig)
        except ProcessLookupError:
            pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    procs = list(rows())
    for pid, _, comm, _ in procs:
        if comm.endswith("/accountsd"):
            mb = mem_mb(pid)
            if mb > LIMIT_MB:
                kill(pid, signal.SIGKILL, f"accountsd using {mb:.0f} MB", a.dry_run)
    hubs = [pid for pid, ppid, _, cmd in procs if ppid == 1 and "/.gemini/bin/agy --hub" in cmd]
    for hub in hubs:
        kids = [p for p, pp, _, _ in procs if pp == hub]
        grand = [p for p, pp, _, _ in procs if pp in kids]
        for p in grand + kids:
            kill(p, signal.SIGTERM, f"child of orphaned agy hub {hub}", a.dry_run)
        kill(hub, signal.SIGTERM, "orphaned agy hub", a.dry_run)


if __name__ == "__main__":
    main()
