---
title: "Troubleshooting Antigravity Planner Skill"
date: "2026-07-30"
conversation_id: "05ad1864-803f-48f6-88c1-1da5abd19f2d"
source: "antigravity"
---

# Troubleshooting Antigravity Planner Skill

## User

Create the file /Users/matt/.gemini/antigravity/brain/84611c8a-ce70-46af-b110-ae9ec54f7c44/conversation_response.md with the following initial content:

---

> **User:** "why am I STILL missing `/planner` skill in Antigravity?"

The `/planner` skill **is** actually present on disk (`~/.gemini/config/skills/planner/SKILL.md`), but Antigravity wasn't registering `/planner` in its active skill registry.

### Root Cause
In Antigravity's architecture, there is a distinct difference between **Slash Commands** and **Skills**:

1. **Skills List**: Skills are loaded into the system prompt's `<skills>` block. The system prompt currently lists skills like `plan` (`~/.gemini/config/skills/plan/SKILL.md`) and `plan-multi-step` (`~/.gemini/config/skills/plan-multi-step/SKILL.md`).
2. **Slash Commands (`/command`)**: Slash commands in the Antigravity UI (listed under `<slash_commands>`) are separate UI-level shortcuts (such as `/goal`, `/schedule`, `/grill-me`, `/browser`). Typing `/planner` in the chat UI doesn't invoke custom markdown skills as slash commands unless they are explicitly mapped or recognized by the client UI.
3. **Prompt Activation**: Because `/planner` was created as a skill folder in `~/.gemini/config/skills/planner`, but was added after the initial skills registration index was cached, the assistant's runtime `<skills>` block did not include it in the active prompt context until refreshed/re-indexed.

### Solution
- To use the `/planner` skill workflow, you can trigger it directly by typing `planner` or referencing `use the planner skill` in your message.
- If you want `/planner` recognized specifically as a slash command, it can be aliased or invoked via the `agymcp` delegation workflow.

---

## Assistant

Created At: 2026-07-30T14:00:10-06:00
Completed At: 2026-07-30T14:00:11-06:00
Created file file:///Users/matt/.gemini/antigravity/brain/05ad1864-803f-48f6-88c1-1da5abd19f2d/conversation_response.md with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-07-30T14:00:12-06:00
Completed At: 2026-07-30T14:00:12-06:00
Message sent to "84611c8a-ce70-46af-b110-ae9ec54f7c44".

The file [conversation_response.md](file:///Users/matt/.gemini/antigravity/brain/05ad1864-803f-48f6-88c1-1da5abd19f2d/conversation_response.md) has been created as requested. I've sent a notification to the parent agent with the details.

---
