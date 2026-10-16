#!/usr/bin/env python3
"""Pytest process wrapper that exits cleanly once pytest prints its session summary.

Prevents hanging on background asyncio task runtimes or lingering event loops.
"""

import os
import re
import signal
import subprocess
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/run_pytest.py <pytest args...>")
        sys.exit(1)

    cmd = sys.argv[1:]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    summary_pattern = re.compile(r"^=+.*(?:passed|failed|skipped|deselected|warnings).*in\s+[\d\.]+s\s*=+", re.MULTILINE)
    exit_code = 0

    try:
        for line in iter(proc.stdout.readline, ""):
            sys.stdout.write(line)
            sys.stdout.flush()
            if summary_pattern.search(line):
                if "failed" in line or "error" in line.lower():
                    exit_code = 1
                # Exit cleanly as soon as pytest summary is output
                try:
                    proc.terminate()
                    proc.wait(timeout=1.5)
                except Exception:
                    proc.kill()
                sys.exit(exit_code)
    except KeyboardInterrupt:
        proc.kill()
        sys.exit(130)

    proc.stdout.close()
    ret = proc.wait()
    sys.exit(ret)


if __name__ == "__main__":
    main()
