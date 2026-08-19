---
title: "Karabiner Passwords App Shortcut"
date: "2026-08-19"
conversation_id: "cfb3beac-26f0-47ab-8172-11ddab34e967"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 19, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 48px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">create a karabiner elemnts script that maps right-command + `P` to open Passwords app<span style="display: block; margin: 8px 0; border: none; border-top: 1px solid rgba(130, 115, 220, 0.35);"></span>and just those two keys, any other modifiers, and it shouldn't work.</span>



<span title="Responded at 9:52pm" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

I have created and activated the Karabiner-Elements rule mapping strictly **Right Command + `P`** to launch the macOS Passwords app (`/System/Applications/Passwords.app`).

### Strict Modifier Matching
By only declaring `mandatory: ["right_command"]` and omitting any `optional` modifiers (such as `caps_lock`, `shift`, `control`, or `option`), Karabiner-Elements strictly enforces that **only** `Right Command` + `P` triggers the shortcut. If any other modifier key is held down simultaneously, it will not match or trigger.

---

### Files Updated & Installed

1. **Complex Modification Asset File**:
   - [open_passwords.json](file:///Users/matt/.config/karabiner/assets/complex_modifications/open_passwords.json) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.config/karabiner/assets/complex_modifications/open_passwords.json) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.config/karabiner/assets/complex_modifications/open_passwords.json)
   ```json
   {
     "title": "Open Passwords App Shortcut",
     "rules": [
       {
         "description": "Right Command + P to Open Passwords app (Strict: No other modifiers allowed)",
         "manipulators": [
           {
             "type": "basic",
             "from": {
               "key_code": "p",
               "modifiers": {
                 "mandatory": [
                   "right_command"
                 ]
               }
             },
             "to": [
               {
                 "shell_command": "open -a '/System/Applications/Passwords.app'"
               }
             ]
           }
         ]
       }
     ]
   }
   ```

2. **Active Profile Configuration**:
   - Injected directly into the active profile within [karabiner.json](file:///Users/matt/.config/karabiner/karabiner.json) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.config/karabiner/karabiner.json) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.config/karabiner/karabiner.json) so the mapping is live immediately without requiring a restart.

---

*Conversation log reference: [thread.md](file:///Users/matt/.gemini/antigravity/brain/cfb3beac-26f0-47ab-8172-11ddab34e967/thread.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/cfb3beac-26f0-47ab-8172-11ddab34e967/thread.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/cfb3beac-26f0-47ab-8172-11ddab34e967/thread.md)*

</span>



</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">

| Tokens | Expiry | Committed | PPLX Quota |
| :--- | :--- | :--- | :--- |
| ~40k / ~450k 🟢 (optimal) | 4:50pm | 🟢 Clean | 104 ❓, 41 📤 |

<span style="position: absolute; right: 2rem; bottom: 0.5rem; display: inline-block; font-size: 11px; font-weight: 600; opacity: 0.7; padding: 3px 10px; border: 1px solid rgba(113,100,175,0.4); border-radius: 20px; white-space: nowrap; letter-spacing: 0.3px;"><a href="file:///Users/matt/.gemini/antigravity/brain/cfb3beac-26f0-47ab-8172-11ddab34e967/kanban.md" style="text-decoration:none;">📋 Kanban</a></span>

</span>

</span>