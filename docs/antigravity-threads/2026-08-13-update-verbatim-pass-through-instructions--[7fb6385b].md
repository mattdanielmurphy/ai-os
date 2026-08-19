---
title: "Update Verbatim Pass-Through Instructions"
date: "2026-08-13"
conversation_id: "7fb6385b-8faf-4fb9-a1c7-25fcaea79207"
source: "antigravity"
---

# Update Verbatim Pass-Through Instructions

## User

Please make the following edits to clarify verbatim pass-through:

1. In `/Users/matt/.gemini/config/global_workflows/proxima-planner.md`:
Replace line 11:
4. **Invoke Perplexity**: Call `proxima:ask_perplexity` with the content of `./tmp/planner_prompt.txt`. Instruct Perplexity to query the GitHub connector for repository source code and documentation.

With:
4. **Invoke Perplexity**: Read the EXACT verbatim text from `./tmp/planner_prompt.txt`. Pass the entire string directly into the `query` parameter of `proxima:ask_perplexity` without summarizing, trimming, or extracting just the user request portion. Instruct Perplexity to query the GitHub connector for repository source code and documentation if needed.

2. In `/Users/matt/projects/ai-os/scripts/generate_planner_prompt.py`:
Replace line 74:
print("2. Call `proxima:ask_perplexity` with the prompt content.")

With:
print("2. Read the entire text of ./tmp/planner_prompt.txt and pass it VERBATIM as the `query` parameter to `proxima:ask_perplexity`. Do NOT extract or pass only the user request.")

Use replace_file_content for both edits.

---

## Assistant

The files have been updated as requested to clarify that the prompt content from `./tmp/planner_prompt.txt` must be passed verbatim to `proxima:ask_perplexity`.

*   [proxima-planner.md](file:///Users/matt/.gemini/config/global_workflows/proxima-planner.md)
*   [generate_planner_prompt.py](file:///Users/matt/projects/ai-os/scripts/generate_planner_prompt.py)

---
