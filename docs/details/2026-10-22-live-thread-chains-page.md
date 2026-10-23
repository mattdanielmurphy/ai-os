# Live thread chains page (Everything Shelf)

## 23:45 First live version

Matt asked (via the coordinator) for a live Artifact page to replace the static Custom view: handoff chains, sorted into six topics, two columns of cards with an icon and colour each, the start of each thread's last message, a right-click menu, state tags, resolved threads hidden. Mid-build he added: "really try to get parity with the Threads view", with two screenshots of the app's Threads list.

---

### Page is live

https://claude.ai/artifact/6Ei7CuXHVYeHvsx94yQH4o. Rows copy the Threads view: title, a coloured state word ("Blocked", "Ready", "Working", "Idle") then the last message, time on the right, ⋮ menu, collapsible group headers with counts, "Welcome back, Matt. N threads are waiting on you."

On top of parity: group by Topic (default, his six categories) or State; a filter chip row for the other grouping; 2 columns or List layout (both remembered in this browser); each row has a tinted icon chosen from its title, coloured by topic; a chain badge (link icon + count) when a thread was handed off; Pinned group; a blue unread dot when Claude wrote since you last opened or marked it read (tracked in this browser only; the very first visit shows no dots so it doesn't light up everything).

---

### Right-click menu

Open thread, Copy link, Copy title, Mark as read/unread, Pin/Unpin, Show earlier threads (chains), Resolve (asks for a second click). Also ⋮ button, Enter to open the focused row, double-click to open, Shift+F10 / Menu key opens the menu.

Links use `claude://code/project/<chan>?thread=<cmsg>` (the form found to work in the desktop app, see memory claude-app-thread-links). I couldn't find a claude.ai web URL for a project thread, so "Open" only works in the Claude desktop app; on iPhone it likely does nothing. Untested: whether the artifact frame lets a claude:// link through at all.

Resolve: the page can't call hearthbot, so it writes `requests/<thread id>` into the artifact's database and hides the row at once (Undo in the toast). The refresh job (below) calls set_thread_resolved and deletes the request.

---

### Where the data comes from

Only a Claude session can read project threads, so the page can't fetch them itself. Options rejected: the page's `mcp` capability (no claude.ai connector exposes thread lists; "Claude Code Remote" only offers send_message to viewers here), the My Mac connector reading a file a launchd job writes (transcripts lack resolved state and handoff links), a Claude scheduled task (would not have the hearthbot tools).

Chosen: this thread refreshes the artifact database. A subagent read all 92 open threads (last message, handoff link in the root message, a topic), `scripts/thread_shelf.py` shapes them into one document `shelf/current` (one doc so a refresh is a single pinned write; per-chain docs would each need their version pinned), and the page subscribes to it live.

---

### Refresh is session-bound

A cron job in this thread runs at :13 and :43 each hour: lists threads changed since the last run (since_ts), fetches the newest message only for those, applies resolve requests, rewrites `shelf/current`. Limits: it only runs while this thread's session is alive on the Mac, and session crons expire after 7 days (Oct 29). A durable version needs either a thread-list connector or a long-lived session; not built.

---

### Design choices

Palette: the "Apothecary glass" candidate from design/candidates/directions.json (the MDMA/Appothecary direction), since no palette is picked yet; swap by changing the tokens. Topic colours: cobalt (Claude), verdigris (MDMA), lavender oil (music), iodine (school), camphor (life), absinthe (ideas). Oxblood for "Blocked". No orange. Fonts: Recursive (casual axis) for the heading, Atkinson Hyperlegible for rows, Martian Mono for labels. Light and dark tokens defined; dark only checked by reading the tokens (the local preview pane can't emulate dark for local files). Phone width checked: rows stay one column and titles truncate.

Categories were assigned by the subagent from titles and messages; Claude setup is the big bucket (43). Fix a wrong one by telling the thread.

---

### Leftovers and undo

Undo: delete the artifact from the gallery; cancel the cron (it dies with the session anyway). Orphaned docs: an earlier seed wrote 90 `chains/*` docs and `meta/state` that the page no longer reads; harmless, left in place.

Queued next (from the coordinator, Matt's idea): real icons per row, an editable note per chain, a Resolved tab with notes, coordinator notes in a sparing orange accent.
