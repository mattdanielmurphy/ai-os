---
id: "hermes-triage-routing-blueprint"
status: "review"
priority: "medium"
assignee: null
epic: null
dueDate: null
created: "2026-07-19T22:18:00.000Z"
modified: "2026-07-19T22:18:00.000Z"
completedAt: null
labels: []
order: "a6"
---
# Hermes Agent Triage Routing Blueprint

Implement the updated Hermes Agent Triage Routing Blueprint under ~/projects/ai-os/.
Create a Multi-Tiered Triage and Routing architecture with:
1. Tier 1 Triage Gateway (Gemini 3.1 Flash-Lite) to classify initial query strings.
2. Tier 2 Executive Investigation & Escalation to handle terminal crashes/impasses and select the minimum intelligence tier.
3. Credit/usage tracking with conservation logic (quota < 20% -> throttle to Gemini 3.1 Pro Low).
4. Escalation paths including paid endpoints (GLM 5.2, Google Premium) and a hard block on Claude Fable 5.
5. Fire-and-forget Web UI valve mechanism.
