---
id: "improve-transcript-token-auditing"
status: "review"
priority: "medium"
assignee: null
epic: null
dueDate: null
created: "2026-07-10T00:30:00Z"
modified: "2026-07-10T00:31:00Z"
completedAt: null
labels: []
order: "a7"
---
# Improve Transcript Token Auditing

The audit transcripts script should count and estimate the actual tokens used by Gemini itself in a thread. It should analyze the full transcript, stripping away JSON wrapper overhead, and sum up the character/token counts of commands (inputs and outputs), thoughts/thinking, file contents read, etc. to give a realistic count of the tokens Gemini consumed in the thread.