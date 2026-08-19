---
title: "Create a new log file at `/Users/matt/projects/userscript-bundler/agent-logs/2026-08-06_19-56_fix_system_directives_stripping.md` with:"
date: "2026-08-07"
conversation_id: "3740fdce-c3fd-4a32-95e2-6c67428643dd"
source: "antigravity"
---

# Create a new log file at `/Users/matt/projects/userscript-bundler/agent-logs/2026-08-06_19-56_fix_system_directives_stripping.md` with:

## User

Create a new log file at `/Users/matt/projects/userscript-bundler/agent-logs/2026-08-06_19-56_fix_system_directives_stripping.md` with:
```markdown
# Fix Multi-Line System Directive Stripping in Gemini Web UI

## Problem
In Gemini Web UI, injected system directives (`[SYSTEM CONTEXT & DIRECTIVES: ... ]`) were remaining visible in the rendered user prompt box.

## Root Cause
Gemini Web UI splits multi-line user queries into individual `<p class="query-text-line">` elements inside `<user-query>`. The previous regex matching was running on single `<p>` nodes independently. Since the opening `[SYSTEM CONTEXT & DIRECTIVES:` and closing `]` were on different `<p>` lines, single-line regex matching failed for every line in the block.

## Solution
1. Updated `03-timestamps.js` to iterate over query containers (`user-query`) and track `insideSysDirective` state across paragraph elements (`pNodes`).
2. Cleared clean content and set `display: none` for paragraph elements containing system directive lines so they are visually hidden without leaving empty DOM gaps.
3. Updated `toggleRawPayloadMode` to support toggling display between raw payload mode and clean mode.
4. Rebuilt userscript bundle (`userscript_bundle.js` and `compiled/gemini-enhancements.user.js`).
```

Also, append the following entry to `/Users/matt/projects/userscript-bundler/DEVELOPMENT_JOURNAL.md`:
```markdown
## 2026-08-06
- **Fix Multi-Line System Directive Stripping:** Updated `03-timestamps.js` to track multi-line `[SYSTEM CONTEXT & DIRECTIVES:]` state across paragraph nodes in `user-query` containers and hide system directive lines from prompt display. See [agent-logs/2026-08-06_19-56_fix_system_directives_stripping.md](file:///Users/matt/projects/userscript-bundler/agent-logs/2026-08-06_19-56_fix_system_directives_stripping.md).
```

---
