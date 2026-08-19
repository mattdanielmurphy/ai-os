---
title: "Update Economics Calculation Logic"
date: "2026-08-14"
conversation_id: "8d106f18-ea65-4c7c-ad66-85c14cb14e26"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

In /Users/matt/projects/ai-os/scripts/postflight.py, update the economics calculation in main() to get t_sys dynamically from check_thread_bloat.get_sys_prompt_tokens(Path(os.getcwd())) if possible, falling back to 25000 (or token_count // 2 if smaller) instead of 5000.
Also, ensure the financial rotation line shows a clean status indicator (e.g. if OK, show 'OK'; if warning or hard cap, show the warning icon and action).

</span>



<span title="Responded at 12:50am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The requested updates to `/Users/matt/projects/ai-os/scripts/postflight.py` have been completed. 
- The `t_sys` calculation now attempts to retrieve values dynamically from `check_thread_bloat.get_sys_prompt_tokens()`. If that fails, it falls back to `min(25000, token_count // 2)` or 25,000 if the token count is

</span>



</span>

</span>