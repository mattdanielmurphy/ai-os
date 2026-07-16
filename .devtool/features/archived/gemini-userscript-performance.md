---
id: "gemini-userscript-performance"
status: "done"
priority: "medium"
assignee: null
epic: null
dueDate: null
created: "2026-07-10T00:14:07.293258Z"
modified: "2026-07-12T05:32:25.894Z"
completedAt: "2026-07-12T05:32:25.894Z"
labels: []
order: "a9"
---
# Optimize Gemini Userscript Performance

The browser userscript for gemini.google.com sync has performance lag issues on long threads. We need to:
1. Optimize MutationObserver and DOM queries to prevent layout thrashing and high CPU usage.
2. Ensure that other AI-OS agents are aware of these userscripts and how to edit/interact with them by updating the global context.