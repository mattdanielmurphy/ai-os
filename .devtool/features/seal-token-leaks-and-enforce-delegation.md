---
id: "seal-token-leaks-and-enforce-delegation"
status: "review"
priority: "high"
assignee: null
epic: null
dueDate: null
created: "2026-07-10T03:28:00Z"
modified: "2026-07-10T03:28:00Z"
completedAt: null
labels: []
order: 100
---

# Seal Token Leaks and Enforce Delegation

Implement three architectural updates to seal token leaks and enforce strict delegation:
1. Update CLAUDE.md to add rules: Research Delegation (use delegate_research), and Strict File Reading (use read_lines).
2. Update mcp_server.py to add read_lines tool.
3. Update audit_transcripts.py to fix false-positive shell redirect detection.
