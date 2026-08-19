---
title: "Troubleshooting Livebench Userscript Injection"
date: "2026-07-27"
conversation_id: "ed958975-cb30-42ad-adfe-3223bbf94c01"
source: "antigravity"
---

# Troubleshooting Livebench Userscript Injection

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
livebench userscript doesn't work. probably trying to inject too early before everything is loaded fully

Assistant answer:
I will inspect the workspace files in `/Users/matt/projects/userscript-bundler` to locate the `livebench` userscript. I will search for occurrences of "livebench" in the workspace to locate the source code or metadata for the userscript. I will list the contents of the `userscripts` directory to find the userscript files. I will list the contents of `userscripts/gemini-enhancements` to see if the livebench userscript resides there. I will search case-insensitively for "livebench" across the enti

---

## Assistant

Fix Livebench Userscript Load Timing

---
