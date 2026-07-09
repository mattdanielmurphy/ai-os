---
id: "audit-transcripts-token-waste"
status: "done"
priority: "medium"
assignee: null
epic: null
dueDate: null
created: "2026-07-09T15:26:00.000Z"
modified: "2026-07-09T15:26:00.000Z"
completedAt: null
labels: []
order: "a17"
---
# Audit Transcripts for Token Waste

Audit past conversation transcripts to analyze token waste, specifically checking if the orchestrator (Gemini 3.5 Flash) is reading/editing files directly instead of delegating to specialized scripts/cheaper models. Create a tool/script to parse `transcript_full.jsonl` files and calculate estimated token waste.
