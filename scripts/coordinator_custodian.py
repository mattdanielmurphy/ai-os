#!/usr/bin/env python3
"""Daily custodian nudge: queue the custodian prompt for the Code-tab Coordinator (launchd, 08:41)."""
import subprocess
import sys
from pathlib import Path

AIOS = Path(__file__).resolve().parent.parent
PROMPT = ("🧹 Daily custodian run. Follow docs/coordinator/custodian.md: loose ends, cleanup without asking, "
          "long-thread flags, upcoming due dates; update coordinator/custodian-state.md; stay silent if nothing needs Matt.")

r = subprocess.run([sys.executable, str(AIOS / "scripts" / "coordinator_inbox.py"), "put"], input=PROMPT, text=True)
sys.exit(r.returncode)
