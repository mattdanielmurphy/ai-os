---
title: "Implementing AIOS Agent Learning"
date: "2026-08-14"
conversation_id: "7122ea40-3369-4dad-9d10-7e2082d82d3a"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

cool

</span>



<span title="Responded at 3:17am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

I will verify the changes as soon as the subagent finishes.
**Thread Metrics:**
| Total Tokens | Cache Expiry | Financial Rotation | Perplexity Quota |
| :--- | :--- | :--- | :--- |
| ~39k | 10:15pm | ~39k / ~377k 🟢 | 93, 20 🔬, 7 📤 |
The subagent is currently writing the files. Waiting for completion...
**Thread Metrics:**
| Total Tokens | Cache Expiry | Financial Rotation | Perplexity Quota |
| :--- | :--- | :--- | :--- |
| ~40k | 10:15pm | ~40k / ~377k 🟢 | 93, 20 🔬, 7 📤 |
The Universal Learning Protocol and Global AI-OS Context are now active across all workspaces.

### Summary of What Was Implemented
1. **Global Standing Directives ([`~/.gemini/GEMINI.md`](file:///Users/matt/.gemini/GEMINI.md) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/GEMINI.md))**:
   - Added the **AI-OS Knowledge & Universal Learning Protocol** section.
   - Mandated cross-workspace awareness for AI-OS tools (`/Users/matt/projects/ai-os/scripts/`).
   - Added strict guardrails prohibiting direct edits to built-in/plugin Gemini skills in `~/.gemini/antigravity/builtin/` and `~/.gemini/config/plugins/`.
   - Defined the 4-tier knowledge hierarchy:
     - **Domain Rules**: [`AG_CONTEXT.md`](file:///Users/matt/projects/ai-os/AG_CONTEXT.md) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/AG_CONTEXT.md)
     - **Narrative Timeline**: [`DEVELOPMENT_JOURNAL.md`](file:///Users/matt/projects/ai-os/DEVELOPMENT_JOURNAL.md) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/DEVELOPMENT_JOURNAL.md)
     - **Conceptual & Entity Knowledge**: Quartz Wiki Engine
     - **Custom Skills / Reusable Workflows**: `skills/custom-skills/<skill>/SKILL.md` (auto-synced via `watch_skills.sh`).
2. **Universal Learning Script ([`scripts/learn_from_moment.py`](file:///Users/matt/projects/ai-os/scripts/learn_from_moment.py) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/learn_from_moment.py))**:
   - Resolves target repo root from any arbitrary working directory.
   - Guards against modifying built-in skills with `guard_skill_path()`.
   - Classifies learning into domain rules, narrative decisions, conceptual entities, or reusable procedures.
   - Appends events to `agent-logs/learning-events.jsonl`.
3. **Custom Skill Definition ([`skills/custom-skills/learn-from-this-moment/SKILL.md`](file:///Users/matt/projects/ai-os/skills/custom-skills/learn-from-this-moment/SKILL.md) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/skills/custom-skills/learn-from-this-moment/SKILL.md))**:
   - Automatically activates on triggers like `"learn from this moment"`, `"remember this"`, or `"learn from this"`.
4. **Test Suite ([`tests/test_learn_from_moment.py`](file:///Users/matt/projects/ai-os/tests/test_learn_from_moment.py) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/tests/test_learn_from_moment.py))**:
   - All tests passing for repository resolution, skill path safety, and event classification.
**Thread Metrics:**
| Total Tokens | Cache Expiry | Financial Rotation | Perplexity Quota |
| :--- | :--- | :--- | :--- |
| ~41k | 10:20pm | ~41k / ~378k 🟢 | 93, 20 🔬, 7 📤 |

</span>



</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

/proxima-planner

</span>



<span title="Responded at 3:14am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

I have created the implementation plan using Proxima / Perplexity architecture planning.
Please review the plan in [`implementation_plan.md`](file:///Users/matt/.gemini/antigravity/brain/7122ea40-3369-4dad-9d10-7e2082d82d3a/implementation_plan.md) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/7122ea40-3369-4dad-9d10-7e2082d82d3a/implementation_plan.md) and let me know if you would like to proceed with execution or make adjustments.
**Thread Metrics:**
| Total Tokens | Cache Expiry | Financial Rotation | Perplexity Quota |
| :--- | :--- | :--- | :--- |
| ~38k | 10:15pm | ~38k / ~377k 🟢 | 93, 20 🔬, 7 📤 |

</span>



</span>

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Okay, we actually need all agents in any directory to know how things work in AIOS because I could be in any thread and tell the agent, "I want you to learn from this moment" and it needs to know how to learn. So it needs to know that it's not supposed to just edit Gemini skills, for instance. And yeah, it basically needs a lot of AIOS specific context, I think.

</span>



<span title="Responded at 3:13am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

You're spot on. Right now, global rules in `~/.gemini/GEMINI.md` handle base environment safety, pre-flight checks, and subagent delegation, but they don't explicitly codify how **learning, skill authoring, and cross-repo context** function within AI-OS.

### Recommended Core Rules to Add to Global Context (`~/.gemini/GEMINI.md`)
1. **Explicit Learning & Skill Modification Guardrails:**
   - **Do Not Edit Native/Default Skills Directly:** When instructed to "learn" or persist a pattern, agents must **never** mutate built-in or plugin Gemini skills directly in `~/.gemini/antigravity/builtin/` or `~/.gemini/config/plugins/` unless explicitly instructed to develop that skill plugin.
   - **Target Learning Destinations:**
     - **Project-Specific Knowledge:** Write durable bullets to `./AG_CONTEXT.md` or append to `./DEVELOPMENT_JOURNAL.md`.
     - **Global Architectural / System Directives:** Record into `~/projects/ai-os/wiki/` (or invoke the local `wiki-engine` / update `~/.gemini/GEMINI.md` for environmental rules).
     - **Custom Skills:** Custom persistent skills belong in `~/.gemini/config/skills/<skill-name>/SKILL.md` or the dedicated repo's skill folder, following the standard frontmatter format.
2. **AI-OS Context Awareness Across Any Workspace:**
   - When in any arbitrary repository, agents must recognize that AI-OS scripts reside in `/Users/matt/projects/ai-os/scripts/` (e.g., `preflight.py`, `postflight.py`, `auto_commit.py`).
   - Knowledge of the global ecosystem: `ai-os` is the central operational core, `qwerty-midi-hammerspoon` manages UI/Hammerspoon integration, and global workflows live in `~/.gemini/config/global_workflows/`.
Would you like me to update `~/.gemini/GEMINI.md` to add a dedicated **"AI-OS Knowledge & Learning Protocol"** section covering these rules?
**Thread Metrics:**
| Total Tokens | Cache Expiry | Financial Rotation | Perplexity Quota |
| :--- | :--- | :--- | :--- |
| ~30k | 10:15pm | ~30k / ~377k 🟢 | 95, 20 🔬, 7 📤 |

</span>



</span>

</span>