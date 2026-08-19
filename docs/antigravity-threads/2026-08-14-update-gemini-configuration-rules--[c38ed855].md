---
title: "Update Gemini Configuration Rules"
date: "2026-08-14"
conversation_id: "c38ed855-191e-435a-a179-c1b11a29a33d"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Please update `/Users/matt/.gemini/GEMINI.md` and `/Users/matt/projects/ai-os/.gemini/GEMINI.md` to add the Mandatory Post-Flight Response Protocol:

Under `## Gemini / Antigravity Specific Rules`:
Add:
```markdown

## Mandatory Post-Flight Response Protocol
- **Rule:** Before concluding any turn or delivering a final response to the user, the agent MUST execute `python3 /Users/matt/projects/ai-os/scripts/postflight.py` (or pass the response through it) to obtain live thread metrics and quota information (token count, Perplexity quota, etc.), and append the resulting `**Thread Metrics:**` block to the final response.
```

Also run `bash /Users/matt/projects/ai-os/scripts/sync_rules.sh` to synchronize rules across all locations.

</span>



<span title="Responded at 12:38am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The `Mandatory Post-Flight Response Protocol` has been added to `/Users/matt/.gemini/GEMINI.md` and `/Users/matt/projects/ai-os/.gemini/GEMINI.md`, and the rules have been synchronized using `bash /Users/matt/projects/ai-os/scripts/sync_rules.sh`.

</span>



</span>

</span>