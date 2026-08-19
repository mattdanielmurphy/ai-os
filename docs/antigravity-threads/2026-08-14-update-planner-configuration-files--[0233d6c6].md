---
title: "Update Planner Configuration Files"
date: "2026-08-14"
conversation_id: "0233d6c6-fecc-402d-9a67-2e27def9c898"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Update /Users/matt/.gemini/config/global_workflows/proxima-planner.md and /Users/matt/projects/ai-os/scripts/generate_planner_prompt.py:

1. /Users/matt/.gemini/config/global_workflows/proxima-planner.md:
Add the Vision Provider Protocol:
"**Vision Provider & Image Attachment Protocol**: If the user attaches an image or screenshot, do NOT pass the raw image to Perplexity by default (preserving Perplexity file upload quota). The main orchestrator acts as the vision provider, inspecting and describing the visual elements, UI layout, diagrams, or error details in rich textual descriptions, and embeds that description into the prompt passed to Perplexity."

2. /Users/matt/projects/ai-os/scripts/generate_planner_prompt.py:
Add an optional argument `--image-desc` to `argparse`. If provided, append:
`\n--- Visual Context & Image Description ---\n{image_desc}\n`
into the generated prompt.

Ensure both files are updated cleanly.

</span>



<span title="Responded at 12:54am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The requested updates have been successfully applied to both the workflow documentation and the prompt generation script.
*   Updated [`proxima-planner.md`](file:///Users/matt/.gemini/config/global_workflows/proxima-planner.md) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/config/global_workflows/proxima-planner.md) to include the **Vision Provider & Image Attachment Protocol**.
*   Updated [`generate_planner_prompt.py`](file:///Users/matt/projects/ai-os/scripts/generate_planner_prompt.py) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/generate_planner_prompt.py) to support the new `--image-desc` argument and inject visual context into the generated prompt.

</span>



</span>

</span>