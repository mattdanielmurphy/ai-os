---
title: "System Configuration File Organization"
date: "2026-07-20"
conversation_id: "df655566-eb07-429d-a964-67c29455c446"
source: "antigravity"
---

# System Configuration File Organization

## User

SYSTEM: Generate a short, descriptive title (3-7 words) for a conversation that starts with the following exchange. The title should capture the main topic or intent. Write the title in the same language the user is writing in. Return ONLY the title text, nothing else. No quotes, no punctuation at the end, no prefixes.

USER: User: Something I need you to clear up: We have a local files: GEMINI.md, CLAUDE.md, AGENTS.md.
First of all, why all three?
Secondly, these are supposed to be GLOBALLY accessible... meaning, GEMINI.md should be at ~/.gemini/GEMINI.md and nowhere else.
Unless it's just like rsycned here so it can be part of the repo (which it should be).
I believe we set up an rsync system.
Make this whole thing clear and organized and robust for me please.

Assistant: Here is the clarification on how our system rules files (`GEMINI.md`, `CLAUDE.md`, and `AGENTS.md`) are structured, why all three exist, and how the global sync system ties them together.

---

### 1. Why do we have all three files?

Each file serves a specific agent runtime or client environment. When an LLM client initializes, it scans the repository for a matching configuration/system instruction file and loads it automatically:

*   **`GEMINI.md`**: Historically used by the **Gemini agent**

---

## Assistant

Organizing global and local agent rules

---
