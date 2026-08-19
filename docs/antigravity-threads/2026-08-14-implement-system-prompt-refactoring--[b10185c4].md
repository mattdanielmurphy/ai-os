---
title: "Implement System Prompt Refactoring"
date: "2026-08-14"
conversation_id: "b10185c4-f55b-4628-9af5-16f18f5ce489"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw + 2px); bottom: 0; padding: 2.5rem 2rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 14, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Implement the changes specified in `/Users/matt/.gemini/antigravity/brain/aefd4046-878c-48cc-b7d0-c1dae37a8be3/implementation_plan.md`:

Files to modify:
1. `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js`
   - In `hasAlreadyPrepended`, check for `<context>` or `[context to this point is` instead of `[SYSTEM CONTEXT & DIRECTIVES:`.
   - Update the systemPrefix template:
     Change `[SYSTEM CONTEXT & DIRECTIVES: ... ]` to:
     `<context>\n# Reference Context & Directives:\n1. Core Identity & Role: ...\n2. Tone & Conciseness: ...\n3. Code Output Standards: ...\n4. Search & Exploration Behavior: ...\n5. Fact-Checking Directive: ...\n</context>\n\n`
   - In `KEYWORD_CONTEXT_DEFINITIONS`:
     Update each `output` template to use `<context>\n# Title\n...\n</context>` instead of square bracket headers like `[Mac Environment & Installed Applications Context]`.

2. `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js`
   - Update `SYSTEM_DIRECTIVE_RE` to match `/<context>[\s\S]*?<\/context>\s*/g` or any remaining square brackets as needed.
   - Update multi-paragraph detection logic (`insideSysDirective`) to start when encountering `<context>` and end when encountering `</context>` (and also handle `[SYSTEM CONTEXT` for backwards compatibility).

3. Re-bundle:
   - Run `bun run bundler.cjs` from `/Users/matt/projects/userscript-bundler` to update `compiled/gemini-enhancements.user.js` and `userscript_bundle.user.js`.
   - Report git diff summary when done.

</span>



<span title="Responded at 6:50pm" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The requested changes have been implemented and the project has been re-bundled.

### Summary of Changes
1.  **Modified `05-prompt-tools.js`**:
    *   Updated `hasAlreadyPrepended` to check for `<context>` or `[context to this point is`.
    *   Replaced the hardcoded bracketed system instructions with the new `<context>`-tagged format.
    *   Updated `KEYWORD_CONTEXT_DEFINITIONS` to use the new `<context>`-tagged format.
2.  **Modified `03-timestamps.js`**:
    *   Updated `SYSTEM_DIRECTIVE_RE` to correctly target `<context>` tag blocks.
    *   Refined `insideSysDirective` parsing logic to handle both `<context>` and legacy `[SYSTEM CONTEXT` markers.
3.  **Bundling**:
    *   Executed `bun run bundler.cjs` to update `compiled/gemini-enhancements.user.js` and `userscript_bundle.user.js`.

### Git Diff Summary
```diff
 bundler.cjs                                        |  141 --
 compiled/gemini-enhancements.user.js               |  242 ++-
 userscript_bundle.user.js                          | 2037 +++++++++++---------
 userscripts/Perplexity.ai Improvements.user.js     | 1467 +++++++-------
 userscripts/gemini-enhancements/03-timestamps.js   |   14 +-
 userscripts/gemini-enhancements/05-prompt-tools.js |   80 +-
 .../gemini-enhancements/09-page-observer.js        |   38 +
 userscripts/openrouter-credit-reminder.user.js     |   17 +-
 userscripts/perplexity.js                          |  499 -----
 9 files changed, 2159 insertions(+), 2376 deletions(-)
```

</span>



</span>

</span>