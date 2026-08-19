---
title: "Check the status of task dispatches, sessions, and bounty earnings in `/Volumes/127.0.0.1/projects/jules-burner`."
date: "2026-08-09"
conversation_id: "e7e5fdb4-5678-4384-80ae-e5e98450888c"
source: "antigravity"
---

# Check the status of task dispatches, sessions, and bounty earnings in `/Volumes/127.0.0.1/projects/jules-burner`.

## User

Check the status of task dispatches, sessions, and bounty earnings in `/Volumes/127.0.0.1/projects/jules-burner`.
Inspect SQLite database (`data/audit.sqlite` or `src/audit/db.ts` paths) or logs using `bun sqlite3` / `sqlite3` or reading log files.
Return:
1. Total sessions run.
2. Status breakdown (COMPLETED, FAILED, IN_PROGRESS).
3. Total bounties claimed ($ amount or sats).
4. Any active errors or blockers in daemon logs (`agent-logs/` or PM2 logs).

---
