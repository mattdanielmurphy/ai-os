---
title: "Fixing TrustedHTML InnerHTML Error"
date: "2026-08-14"
conversation_id: "9ff88f70-9311-45a5-b465-ad81650df5cb"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

❌ [Bundler] Error in Runtime Error: Failed to set the 'innerHTML' property on 'Element': This document requires 'TrustedHTML' assignment. TypeError: Failed to set the 'innerHTML' property on 'Element': This document requires 'TrustedHTML' assignment.
    at injectImmersiveModalButton (userscript.html?name=Local-Userscript-Dynamic-Loader.user.js&id=f65e81f6-58d8-489e-9958-22e7daba99a5:3537:16)
    at injectUI (userscript.html?name=Local-Userscript-Dynamic-Loader.user.js&id=f65e81f6-58d8-489e-9958-22e7daba99a5:3169:2)

</span>



<span title="Responded at 2:27am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

### Root Cause & Fix
**Problem:** Google domains enforce strict Trusted Types / `TrustedHTML` policies. In [05-prompt-tools.js](file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js#L1331-L1380) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js%3A1331%3A1380), `injectImmersiveModalButton` was directly setting `btn.innerHTML = ...` with raw SVG strings, triggering:
```
TypeError: Failed to set the 'innerHTML' property on 'Element': This document requires 'TrustedHTML' assignment.
```
**Solution:**
1. Replaced all raw `btn.innerHTML = ...` calls in `injectImmersiveModalButton` with standard DOM/SVG construction using `document.createElementNS("http://www.w3.org/2000/svg", ...)` and `btn.replaceChildren(...)`.
2. Rebuilt the bundles with `bun run build` to compile the fix into [gemini-enhancements.user.js](file:///Users/matt/projects/userscript-bundler/compiled/gemini-enhancements.user.js) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/userscript-bundler/compiled/gemini-enhancements.user.js) and [userscript_bundle.js](file:///Users/matt/projects/userscript-bundler/userscript_bundle.js) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/userscript-bundler/userscript_bundle.js).
**Thread Metrics:**
| Total Tokens | Cache Expiry | Financial Rotation | Perplexity Quota |
| :--- | :--- | :--- | :--- |
| ~38k | 9:30pm | ~38k / ~363k 🟢 | 96, 20 🔬, 8 📤 |

</span>



</span>

</span>