#!/usr/bin/env python3
"""Copy the mailbox login from ai-os .env to the VPS relay, then restart it.

Reads these keys from ~/projects/ai-os/.env (never printed):
  MAIL_USER        iCloud login (the @icloud.com / Apple Account email)
  MAIL_PASSWORD    Apple app-specific password (account.apple.com > Sign-In and Security)
  MAIL_FROM        the address mail is sent as (the custom-domain address)
  MAIL_FROM_NAME   optional display name
  SMTP_USER        optional, defaults to MAIL_USER

Usage: python3 configure.py [--check]   (--check: only report which keys are set)
"""

import subprocess
import sys
from pathlib import Path

ENV = Path.home() / "projects/ai-os/.env"
KEYS = ["MAIL_USER", "MAIL_PASSWORD", "MAIL_FROM", "MAIL_FROM_NAME", "SMTP_USER"]
REQUIRED = ["MAIL_USER", "MAIL_PASSWORD", "MAIL_FROM"]
HOST = "oracle-vps"
REMOTE = "~/apps/mail-relay/env"


def read_env():
    vals = {}
    for line in ENV.read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            k = k.strip()
            if k in KEYS:
                vals[k] = v.strip().strip('"').strip("'")
    return vals


def main():
    vals = read_env()
    missing = [k for k in REQUIRED if not vals.get(k)]
    for k in KEYS:
        print(f"{k}: {'set' if vals.get(k) else 'missing'}")
    if "--check" in sys.argv:
        return
    if missing:
        sys.exit(f"add {', '.join(missing)} to {ENV} first")
    # rewrite the remote env: keep its token/port lines, replace mailbox lines
    script = (
        "set -e; f=" + REMOTE + "; umask 077; "
        "grep -v -E '^(" + "|".join(KEYS) + ")=|^# filled in' $f > $f.new; "
        "cat >> $f.new; mv $f.new $f; chmod 600 $f; "
        "sudo systemctl restart mail-relay; sleep 2; curl -s 127.0.0.1:8790/health"
    )
    payload = "".join(f"{k}={vals[k]}\n" for k in KEYS if vals.get(k))
    r = subprocess.run(["ssh", "-o", "BatchMode=yes", HOST, script], input=payload, text=True,
                       capture_output=True, timeout=60)
    print(r.stdout.strip() or r.stderr.strip())
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
