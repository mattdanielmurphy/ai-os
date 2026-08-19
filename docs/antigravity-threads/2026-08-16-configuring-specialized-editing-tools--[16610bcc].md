---
title: "Configuring Specialized Editing Tools"
date: "2026-08-16"
conversation_id: "16610bcc-a2d5-4aed-aea3-b71cbf95efd6"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 48px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">✅ **Approved Plan/Artifact**: [learning_proposal.md](file:///Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/learning_proposal.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/learning_proposal.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/learning_proposal.md)</span>



<span title="Responded at 10:39pm" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The learning proposal has been executed and persisted across the entire system:

---

### Applied Changes

1. **System Rule Added in [`.rules/core_safety.md`](file:///Users/matt/projects/ai-os/.rules/core_safety.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/.rules/core_safety.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/.rules/core_safety.md)**:
   ```markdown
   # Custom Skills Naming & Authoring Invariant
   - **Rule**: When creating, authoring, or refactoring personal/custom skills for Matt in `~/projects/ai-os/skills/` or environment skill directories:
     - **Leading Underscore Namespace (`_`)**: ALL user-authored/custom skills MUST begin with a leading underscore (`_`) prefix so they sort to the very top of alphabetical listings, IDE pickers, and autocomplete popovers.
     - **Action-First Semantic Naming (`_<action>-<constraint>`)**: Skill names MUST start with the primary action verb, followed by the defining behavioral constraint or modifier (e.g., `_critique-without-ghostwriting`, `_prune-subtractively`).
     - **Auto-Sync Invariant**: After creating or updating any skill under `~/projects/ai-os/skills/`, agents MUST immediately execute `python3 /Users/matt/projects/ai-os/scripts/sync_skills.py` to propagate changes across all local agent runtimes (`~/.hermes`, `~/.gemini`, `~/.claude`, `~/.agents`).
   ```

2. **Compiled Across Agent Ecosystem**:
   - `build_rules.py` was executed, compiling the directive into [`GEMINI.md`](file:///Users/matt/.gemini/GEMINI.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/GEMINI.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/GEMINI.md), [`CLAUDE.md`](file:///Users/matt/projects/ai-os/CLAUDE.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/CLAUDE.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/CLAUDE.md), and [`HERMES.md`](file:///Users/matt/.hermes/HERMES.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.hermes/HERMES.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.hermes/HERMES.md).

3. **Active Skills Ready**:
   - [`_critique-without-ghostwriting`](file:///Users/matt/projects/ai-os/skills/_critique-without-ghostwriting/SKILL.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/skills/_critique-without-ghostwriting/SKILL.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/skills/_critique-without-ghostwriting/SKILL.md)
   - [`_prune-subtractively`](file:///Users/matt/projects/ai-os/skills/_prune-subtractively/SKILL.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/skills/_prune-subtractively/SKILL.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/skills/_prune-subtractively/SKILL.md)

---

- **Learning Proposal:** [learning_proposal.md](file:///Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/learning_proposal.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/learning_proposal.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/learning_proposal.md)
- **Project Board:** [PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md)
- **Thread Artifact:** [thread.md](file:///Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/thread.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/thread.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/thread.md)

</span>



</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">You know, I propose names that are slightly more descriptive but using the main action as the first word.<br>_critique-without-ghostwriting<br>_prune-subtractively<span style="display: block; margin: 8px 0; border: none; border-top: 1px solid rgba(130, 115, 220, 0.35);"></span>I feel like that's a good default way to go about naming skills, right? /learn</span>



<span title="Responded at 10:39pm" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

I have prepared the `/learn` proposal to persist this as a permanent system directive across your entire environment.

Please review the proposed rule in [learning_proposal.md](file:///Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/learning_proposal.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/learning_proposal.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/learning_proposal.md). Once approved, I will add it to [`.rules/core_safety.md`](file:///Users/matt/projects/ai-os/.rules/core_safety.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/.rules/core_safety.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/.rules/core_safety.md) and recompile `GEMINI.md`, `CLAUDE.md`, and `HERMES.md`.

---

- **Learning Proposal:** [learning_proposal.md](file:///Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/learning_proposal.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/learning_proposal.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/learning_proposal.md)
- **Project Board:** [PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md)
- **Thread Artifact:** [thread.md](file:///Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/thread.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/thread.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/thread.md)

</span>



</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">Why is it called meta-critique? Why not just critique?</span>



<span title="Responded at 10:37pm" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The name **"meta-critique"** was used because it operates strictly at the **meta-level** (feedback *about* the structure, logic, and arguments) rather than the **object-level** (the actual words/sentences). 

When an LLM is asked to "critique", its default tendency is to be helpful by offering example rewrites: *"Here is a revised version: ..."* or *"You could write it like this: ..."* Calling it a *meta*-critique was a way of emphasizing that it discusses the architecture of the piece while withholding draft prose.

### That Said: `_critique` is Much Better

In practice, **`_critique`** is shorter, punchier, and far more natural to call. The strict "never draft sentences / conceptual feedback only" rule is enforced inside the `SKILL.md` definition anyway, so the skill name doesn't need to over-explain itself.

We can also shorten **`_subtractive-prune`** $\rightarrow$ **`_prune`** for the exact same reason:

| Current | Proposed | Purpose |
| :--- | :--- | :--- |
| `_meta-critique` | **`_critique`** | Evaluative feedback & structural issues without ghostwriting |
| `_subtractive-prune` | **`_prune`** | Pure deletion of fluff with zero synonym replacement |

Would you like me to rename them to **`_critique`** and **`_prune`**?

---

- **Project Board:** [PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md)
- **Thread Artifact:** [thread.md](file:///Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/thread.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/thread.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/thread.md)

</span>



</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);"><span style="display: block; background: rgba(0, 0, 0, 0.25); border-left: 3px solid rgba(130, 115, 220, 0.7); padding: 6px 10px; margin-bottom: 8px; border-radius: 4px; font-size: 13px; opacity: 0.9; white-space: pre-wrap;">Pushes all your custom skills to the very top of alphabetical listings.</span><br>💬 **Comment**: I want this. Technically when I first see a leading underscore I think of: internal variable. But who cares, we can repurpose it. Not a huge clash there honestly. proceed with this.</span>



<span title="Responded at 10:37pm" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The leading underscore (`_`) prefix convention has been applied and synced across the system:

---

### Configured Skills (Top of Alphabetical Order)

1. **[`_subtractive-prune`](file:///Users/matt/.gemini/config/skills/_subtractive-prune/SKILL.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/config/skills/_subtractive-prune/SKILL.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/config/skills/_subtractive-prune/SKILL.md)**
   - **File:** [`skills/_subtractive-prune/SKILL.md`](file:///Users/matt/projects/ai-os/skills/_subtractive-prune/SKILL.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/skills/_subtractive-prune/SKILL.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/skills/_subtractive-prune/SKILL.md)
   - **Behavior:** Pure destructive deletion. Trims fluff and bloat while preserving original human phrasing verbatim.

2. **[`_meta-critique`](file:///Users/matt/.gemini/config/skills/_meta-critique/SKILL.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/config/skills/_meta-critique/SKILL.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/config/skills/_meta-critique/SKILL.md)**
   - **File:** [`skills/_meta-critique/SKILL.md`](file:///Users/matt/projects/ai-os/skills/_meta-critique/SKILL.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/skills/_meta-critique/SKILL.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/skills/_meta-critique/SKILL.md)
   - **Behavior:** Bulleted structural critique and conceptual suggestions without generating draft prose.

Both skills now float directly to the **top** of any skill listing or search dialog (typing `_` surfaces all your personal tools instantly).

---

### Other Potential Custom Skills for `_` Prefixing

Whenever you're ready, we can also migrate your other custom/workflow skills to use the `_` prefix so your entire personal suite stays unified at the top:

- `apple-reminders` $\rightarrow$ `_apple-reminders`
- `apple-notes` $\rightarrow$ `_apple-notes`
- `ai-os-quiet-run` $\rightarrow$ `_ai-os-quiet-run`
- `ai-os-auto-commit` $\rightarrow$ `_ai-os-auto-commit`
- `hammerspoon-webview` $\rightarrow$ `_hammerspoon-webview`
- `la-launch-agent-manager` $\rightarrow$ `_la-launch-agent-manager`

---

- **Project Board:** [PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md)
- **Thread Artifact:** [thread.md](file:///Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/thread.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/thread.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/thread.md)

</span>



</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">you know what? Here's an issue that comes to mind: there's a shitload of skills that I basically will never call because I didn't make them and idk what they even do. But I don't want to get rid of them.<br>What I DO want to do is to identify MY skills by name.<br>with a prefix or suffix</span>



<span title="Responded at 10:35pm" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

Naming conventions make a huge difference here—especially with **prefixes**, because they instantly cluster all your personal tools together alphabetically and in autocomplete menus.

---

### Why a Prefix is Better Than a Suffix

1. **Alphabetical Clustering:** All your skills stay tightly grouped together in directory listings (`ls skills`), IDE sidebars, and skill tables.
2. **Fuzzy Search / Autocomplete Filter:** In any skill picker or CLI prompt, typing `m-` (or your chosen prefix) instantly filters out all the third-party/upstream noise and surfaces *only* your tools.
3. **Collision Immunity:** If Hermes Hub or community packages add new skills upstream, they will never collide with or overwrite yours.

---

### Prefix Candidates

| Style | Example Name | Autocomplete / Listing Behavior |
| :--- | :--- | :--- |
| **`m-`** *(Recommended)* | `m-subtractive-prune`<br>`m-meta-critique`<br>`m-reminders` | Ultra-short (2 keystrokes). Clean, minimalist, and groups everything under **`m`**. |
| **`my-`** | `my-subtractive-prune`<br>`my-meta-critique` | Explicitly self-descriptive across all agent prompts and docs. |
| **`matt-`** | `matt-subtractive-prune`<br>`matt-meta-critique` | Unambiguous personal namespace. |
| **`_` (Leading underscore)** | `_subtractive-prune`<br>`_meta-critique` | Pushes all your custom skills to the **very top** of alphabetical listings. |

---

### How We Can Apply This Across Your Setup

Once you pick a prefix (e.g., **`m-`**), we can:
1. Rename and update **`subtractive-prune`** $\rightarrow$ **`m-subtractive-prune`** and **`meta-critique`** $\rightarrow$ **`m-meta-critique`**.
2. Audit your other custom-built tools in `ai-os/skills/` (like `apple-reminders`, `apple-notes`, `la-launch-agent-manager`, `ai-os-quiet-run`, `hammerspoon-webview`, etc.) and apply the same prefix so your entire personal toolbox is unified.
3. Run [`sync_skills.py`](file:///Users/matt/projects/ai-os/scripts/sync_skills.py) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/sync_skills.py) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/scripts/sync_skills.py) to propagate the clean namespace across Antigravity, Claude, and Hermes.

Which prefix style feels best to you?

---

- **Project Board:** [PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md)
- **Thread Artifact:** [thread.md](file:///Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/thread.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/thread.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/thread.md)

</span>



</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">ok, so the trouble now is... how do I remember these exist? lol<br>Propose a list of suggestions</span>



<span title="Responded at 10:33pm" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

Here are several ways to make these skills frictionless to discover and trigger across your daily workflow:

---

### 1. Antigravity Slash Commands (`/prune` & `/critique`)
* **How it works:** Create two workflow files in `~/.gemini/config/global_workflows/prune.md` and `critique.md`.
* **Benefit:** Typing `/` in the Antigravity chat prompt will immediately surface `/prune` and `/critique` in the autocomplete popover with inline descriptions, so you don't have to remember exact skill names.

---

### 2. Natural Language Auto-Routing (Zero Recall)
* **How it works:** Add an instruction in system directives (`.rules/` / `GEMINI.md`) mapping natural editing intentions to these skills.
* **Benefit:** Whenever you casually say:
  - *"cut the fat"* / *"strip the fluff"* / *"make this concise without rewriting it"* $\rightarrow$ auto-invokes **`subtractive-prune`**.
  - *"give me editorial feedback"* / *"critique this without drafting"* / *"tell me what to fix"* $\rightarrow$ auto-invokes **`meta-critique`**.
* You don't need to remember the skill name at all; just state your goal naturally.

---

### 3. macOS Global Hotkeys / Hammerspoon Quick Menu
* **How it works:** Wire a Hammerspoon hotkey (e.g., `Hyper + P` or `Hyper + C`) or a Raycast script:
  1. Grabs selected text in any macOS app via clipboard.
  2. Runs a fast local call (e.g. `pbpaste | agy -s subtractive-prune | pbcopy` or displays a HUD modal for `meta-critique`).
* **Benefit:** Instant, system-wide access across Google Docs, Obsidian, Mail, Slack, or web forms without switching to the IDE.

---

### 4. Terminal CLI Pipes (`pbpaste | prune | pbcopy`)
* **How it works:** Add two quick zsh functions in `~/.zshrc_aios`:
  ```zsh
  alias prune="agy -s subtractive-prune"
  alias critique="agy -s meta-critique"
  ```
* **Benefit:** In terminal or quick scripts, you can run `pbpaste | prune | pbcopy` to destructive-prune your clipboard in under 2 seconds.

---

### 5. Obsidian / Project Board Quick Reference Badge
* **How it works:** Add an **Editing Tools** quick-link ribbon to [`PROJECT_BOARD.md`](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) or your Obsidian Daily Notes template.
* **Benefit:** Visible in the sidebar whenever starting new tasks or reviewing written drafts.

---

### Recommended Next Steps

We can implement:
1. **Slash commands (`/prune` and `/critique`)** for immediate chat autocomplete.
2. **Natural language trigger rules** in `.rules/` so Antigravity and Hermes auto-route to them transparently.
3. **Zsh shell helpers** in `.zshrc_aios`.

Let me know which of these you'd like wired up!

---

- **Project Board:** [PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md)
- **Thread Artifact:** [thread.md](file:///Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/thread.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/thread.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/thread.md)

</span>



</span>

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 16, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">## Mission Overview<br><br>**Objective:** Configure two dedicated editing skills in Antigravity to streamline document polishing while strictly preserving original human entropy and preventing AI-generated phrasing, syntax smoothing, or detection markers (e.g., Pangram).<br><br>### The Two-Pillar Workflow<br><br>1. **Subtractive Pruning:** Purely destructive pruning. Removes bloat, redundancy, and fluff without substituting vocabulary or inserting generative transitional phrases.<br>2. **Meta-Review / Structural Critique:** Evaluative feedback. Explains *what* and *why* to adjust conceptually, explicitly withholding draft sentences to prevent cognitive anchoring or ghostwriting.<br><br>---<br><br>## Skill Definitions & Prompts<br><br>### Skill 1: `subtractive-prune`<br><br>* **Purpose:** Trims selected text down to its essential points without altering the author's original phrasing or vocabulary.<br><br>```markdown<br>Act exclusively as a deletion tool. Prune the user's text to make it concise and direct. <br><br>RULES:<br>1. Under no circumstances may you substitute synonyms, add transitional markers (e.g., 'furthermore', 'additionally', 'in summary'), or rephrase clauses.<br>2. Only remove tokens and adjust residual punctuation/capitalization caused by deletions.<br>3. Preserve all remaining original human phrasing verbatim.<br>4. Output ONLY the pruned text with no preamble or commentary.<br><br>```<br><br>---<br><br>### Skill 2: `meta-critique`<br><br>* **Purpose:** Delivers high-level editorial feedback and structural analysis without generating any copy.<br><br>```markdown<br>Review the provided text for clarity, conciseness, pacing, and tone.<br><br>RULES:<br>1. Identify structural fluff, weak arguments, logical gaps, or repetitive points.<br>2. Point out these issues using concise, bulleted descriptions.<br>3. NEVER provide example sentences, draft paragraphs, or rewritten prose. <br>4. The author must write all text themselves; only describe the suggested structural changes conceptually.<br><br>```</span>



<span title="Responded at 10:32pm" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The two editing skills have been configured and synced across Antigravity and the environment:

---

### Configured Skills

1. **[`subtractive-prune`](file:///Users/matt/.gemini/config/skills/subtractive-prune/SKILL.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/config/skills/subtractive-prune/SKILL.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/config/skills/subtractive-prune/SKILL.md)**
   - **File:** [`skills/subtractive-prune/SKILL.md`](file:///Users/matt/projects/ai-os/skills/subtractive-prune/SKILL.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/skills/subtractive-prune/SKILL.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/skills/subtractive-prune/SKILL.md)
   - **Behavior:** Purely destructive pruning. Removes bloat, redundancy, and fluff without substituting vocabulary, rephrasing clauses, or inserting generative transitions. Retains the author's original entropy and phrasing verbatim, outputting only the pruned text.

2. **[`meta-critique`](file:///Users/matt/.gemini/config/skills/meta-critique/SKILL.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/config/skills/meta-critique/SKILL.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/config/skills/meta-critique/SKILL.md)**
   - **File:** [`skills/meta-critique/SKILL.md`](file:///Users/matt/projects/ai-os/skills/meta-critique/SKILL.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/skills/meta-critique/SKILL.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/skills/meta-critique/SKILL.md)
   - **Behavior:** Delivers concise, conceptual, bulleted editorial feedback on structural fluff, pacing, weak logic, or repetition. Strictly forbids drafting example sentences, paragraphs, or rewritten prose to prevent cognitive anchoring.

Both skills were registered under [`ai-os/skills/`](file:///Users/matt/projects/ai-os/skills/) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/skills/) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/skills/) and synced to `~/.gemini/config/skills/` and related agent skill paths via [`sync_skills.py`](file:///Users/matt/projects/ai-os/scripts/sync_skills.py) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/sync_skills.py) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/scripts/sync_skills.py).

---

- **Project Board:** [PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md)
- **Thread Artifact:** [thread.md](file:///Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/thread.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/thread.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/thread.md)

</span>



</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">

| Tokens | Expiry | Committed | PPLX Quota |
| :--- | :--- | :--- | :--- |
| ~65k / ~430k 🟢 (optimal) | 5:40pm | 🟢 Clean | 114 ❓, 27 📤 |

<span style="position: absolute; right: 2rem; bottom: 0.5rem; display: inline-block; font-size: 11px; font-weight: 600; opacity: 0.7; padding: 3px 10px; border: 1px solid rgba(113,100,175,0.4); border-radius: 20px; white-space: nowrap; letter-spacing: 0.3px;"><a href="file:///Users/matt/.gemini/antigravity/brain/16610bcc-a2d5-4aed-aea3-b71cbf95efd6/kanban.md" style="text-decoration:none;">📋 Kanban</a></span>

</span>

</span>