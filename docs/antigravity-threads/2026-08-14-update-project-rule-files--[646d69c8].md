---
title: "Update Project Rule Files"
date: "2026-08-14"
conversation_id: "646d69c8-3bbb-4aef-ae75-266fabae5dac"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Please apply the approved learning proposal updates to the rule files:

1. In `/Users/matt/projects/ai-os/.rules/core_safety.md`:
Under `## Project Detection`, add:
```markdown

4. **Subdirectory Git Detection:** Scripts and agents must ALWAYS detect git repository roots using `git rev-parse --is-inside-work-tree` and `git rev-parse --show-toplevel` instead of checking `os.path.exists(".git")` in the current working directory.
```

2. In `/Users/matt/projects/ai-os/.rules/gemini_only.md`:
Add a section:
```markdown

## Proxima & Perplexity Integration Guardrails
- **Strict File Upload Ban**: NEVER pass the `files` argument/array to `proxima:ask_perplexity`. Perplexity file upload quota is strictly limited (8/day). All repository context must be referenced via the authenticated GitHub connector or embedded text in the prompt.
- **Disabled Proxima Providers**: NEVER call `proxima:ask_claude` or `proxima:ask_chatgpt`.
- **Async Recovery on Timeout**: If `proxima:ask_perplexity` times out after 3 minutes, do NOT switch providers or abandon the query. Immediately run `node ~/projects/ai-os/scripts/query_proxima.js --provider perplexity --recover --output ./tmp/planner_output.txt --timeout 300` to retrieve the finished output.
```

Make these modifications now.

</span>



<span title="Responded at 3:23am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The requested updates have been successfully applied to the specified rule files.
1.  Modified [`/Users/matt/projects/ai-os/.rules/core_safety.md`](file:///Users/matt/projects/ai-os/.rules/core_safety.md) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/.rules/core_safety.md) to include the "Subdirectory Git Detection" rule under the `## Project Detection` section.
2.  Modified [`/Users/matt/projects/ai-os/.rules/gemini_only.md`](file:///Users/matt/projects/ai-os/.rules/gemini_only.md) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/.rules/gemini_only.md) to include the `## Proxima & Perplexity Integration Guardrails` section at the end of the file.

</span>



</span>

</span>