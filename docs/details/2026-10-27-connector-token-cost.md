# Connector token cost (2026-10-27)

## 17:35 Do connectors cost tokens in every thread?

Asked: make threads not pay connector cost by default, but get a connector instantly when needed.

### Already deferred today
Checked a live Code-tab thread: every connector tool (Linear, Calendar, Docs, Chrome, computer-use, scheduled tasks, ccd_*) is already deferred via ToolSearch. A thread pays only one line per tool *name* (~170 names, roughly 3-5k tokens) plus each server's instructions. Full schemas load only when a thread calls ToolSearch. So connectors are already "off until needed"; disabling them per session saves little.

### Where the real waste is
- **browser-use plugin**: injects a very long instructions block into every thread, and duplicates Claude in Chrome + the built-in browser. Biggest single cost.
- **productivity + design plugins**: 9 MCP servers that are not even signed in (Asana, Atlassian, ClickUp, Monday, Notion, Slack, Intercom, Figma, Linear-plugin) add an "needs authentication" notice every thread. Linear already works through the claude.ai connector.
- No `.mcp.json` servers; only `qmd` in `~/.claude.json` (useful, keep).

### Recommendation (not applied)
Turn off the browser-use, productivity and design plugins in the desktop app's plugin settings (Figma: keep design if he uses its Figma). These are app-managed, so I didn't toggle them from a side thread. No hook/coordinator system needed: ToolSearch already gives instant per-task loading.

Rejected: per-session `set_session_connector_enabled` toggling by coordinator (saves only names, adds friction); converting connectors to CLIs (big work, tiny gain).

Undo: re-enable the plugins.

## 17:50 Recheck: the ~16k "MCP tools (loaded)"

Matt's panel shows MCP tools loaded 32.9k (now ~16k), server instructions 6.3k. I was wrong: the Linear/Calendar/Figma connectors are not that cost; they sit in the "deferred" bucket (330k, not in context).

### What actually loads up front
Checked which MCP tools arrive with full schemas in a fresh Code-tab thread (this one): only the desktop app's built-ins.
- **Built-in browser pane** (`Claude_Browser`, 19 tools with long descriptions): the bulk, roughly 8-10k.
- **iOS Simulator** control tool: one big schema, ~1.5-2k. Only needed for iOS work.
- **Docs connector** (batch/guide/update): ~1k.
- ccd_session, terminal reader, visualize: ~2-3k, part of the app; keep.

### Server instructions (6.3k)
browser-use plugin is the largest block, then Claude in Chrome, computer-use, qmd.

### Recommendation
1. Turn off the **iOS Simulator** and **Docs** connectors in the app; switch on in the threads that need them.
2. Pick one browser: the built-in pane OR Claude in Chrome + browser-use. Dropping browser-use saves most of the 6.3k; disabling the pane saves most of the 16k but Chrome then becomes the only browser (deferred, so cheap).
3. Remove the unsigned productivity/design plugins (noise).
Estimates are from schema sizes, not a per-tool meter; confirm with the context panel after toggling.
