---
title: "Troubleshooting Planner Skill Availability"
date: "2026-07-31"
conversation_id: "b40ca0e2-d950-4d40-abcc-28fccab07bc4"
source: "antigravity"
---

# Troubleshooting Planner Skill Availability

## User

Write target file /Users/matt/.gemini/antigravity/brain/26a75289-bec3-4737-b152-c0ccc4fb0fc7/conversation_response.md with the following exact content:

---

> **User:** "I'm still missing `/planner` in Antigravity. fucking fix it"

# `/planner` Diagnostic & Availability Status

| Item | Path / Resource | Status |
|---|---|---|
| **Skill Definition** | `/Users/matt/.gemini/config/skills/planner/SKILL.md` | Present & Active |
| **Antigravity Skill Mirror** | `/Users/matt/.gemini/antigravity/skills/planner/SKILL.md` | Present |
| **Global Workflow** | `/Users/matt/.gemini/config/global_workflows/planner.md` | Present |

## Findings & Summary

- The `planner` skill (`/Users/matt/.gemini/config/skills/planner/SKILL.md`) and workflow (`/Users/matt/.gemini/config/global_workflows/planner.md`) are active in your configuration.
- Built-in UI slash commands (like `/goal`, `/schedule`, `/browser`) are native client features. Custom additions like `/planner` function as **skills & workflows**.
- You can invoke `/planner` (or `/planner 3.1 pro high`) at any time directly in your prompt text; the agent recognizes the skill definition and delegates high-reasoning planning via `agymcp`.

---

## Assistant

Created At: 2026-07-31T15:29:04-06:00
Completed At: 2026-07-31T15:29:04-06:00
Created file file:///Users/matt/.gemini/antigravity/brain/b40ca0e2-d950-4d40-abcc-28fccab07bc4/conversation_response.md with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-07-31T15:29:05-06:00
Completed At: 2026-07-31T15:29:05-06:00
Message sent to "26a75289-bec3-4737-b152-c0ccc4fb0fc7".

The diagnostic report has been created at [/Users/matt/.gemini/antigravity/brain/b40ca0e2-d950-4d40-abcc-28fccab07bc4/conversation_response.md](file:///Users/matt/.gemini/antigravity/brain/b40ca0e2-d950-4d40-abcc-28fccab07bc4/conversation_response.md) and the caller agent has been notified.

---
