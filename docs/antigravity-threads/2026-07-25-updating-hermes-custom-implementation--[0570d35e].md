---
title: "Updating Hermes Custom Implementation"
date: "2026-07-25"
conversation_id: "0570d35e-811b-495e-99e9-6c5460408411"
source: "antigravity"
---

# Updating Hermes Custom Implementation

## User

SYSTEM: Generate a short session title from this conversation start.
Use BOTH the user's question and the assistant's visible answer.
Match the language of the user question.
Return only the title text, 3-8 words, as a topic label.
Do not use markdown, bullets, labels, or prefixes like Session Title:.
Do not output a full sentence.
Do not output acknowledgements or completion phrases like OK, done, or all set.
Do not describe internal reasoning.
Bad: The user is asking..., OK, all set.
Good: Title Generation Test, Clarify Dialog Layout, GitHub Issue Triage

USER: User question:
so there's a massive amount of updates to Hermes... But I believe we've customized it or built on top of it or something? Am I free to just hit an "Update" button in the desktop? I think it just does git pull anyway?

Assistant answer:
Yes, you are free to click the **Update** button (or do a `git pull`). Here is the situation: - **How we customize/build on top of it:** Our integrations (like the Thread Sync Daemon, `agy-proxy` service, and prompt handoffs) are built as separate helper scripts, services (`/Users/matt/projects/ai-os/services/agy-proxy/`), wrappers, or configuration files, rather than directly modifying the core Hermes/Antigravity source code. - **Your active project repository (`~/projects/ai-os`):** Your git r

---

## Assistant

Hermes Updates and Customization Compatibility

---
