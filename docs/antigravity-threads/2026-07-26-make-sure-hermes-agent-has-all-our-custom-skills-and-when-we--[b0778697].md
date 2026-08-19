---
title: "make sure Hermes agent has all our custom skills, and when we make a n"
date: "2026-07-26"
conversation_id: "b0778697a5a7"
source: "antigravity"
---

# make sure Hermes agent has all our custom skills, and when we make a n

## User

make sure Hermes agent has all our custom skills, and when we make a new skill, just like when we add a new rule, it's done in a way so Antigravity/claude/Hermes can all access them.

---

## Assistant

I will check our skills directories across Hermes, Claude, Antigravity, and ai-os to see what custom skills exist and how they are currently synchronized across platform locations.

I will check the existing skill installer/sync tools in agy-mcp and `ai-os` scripts to see how skill synchronization and multi-agent sharing are currently handled.

I will check agy-mcp's `agy_install_skill` implementation and search the codebase/repo for existing skill sync scripts or tools.

I will inspect `build_rules.py` in `~/projects/ai-os/scripts/` to see how rules are compiled and managed across platforms.

I will check the skills directories across all platforms (`~/.hermes/skills`, `~/.claude/skills`, `~/.gemini/config/skills`, `~/.agents/skills`, `~/.agy/skills`, and `~/.antigravity/skills`) to map all existing custom skills and see where skills are currently stored or missing.

I will check what `agy_install_skill` does or how agy-mcp installs skill bundles.

I will search for `agy_install_skill` or skill synchronization logic across the ai-os repository and python environment.

I will check all the skill locations and rules files in `ai-os` to see how skills are stored and how rules are managed across Claude, Antigravity, and Hermes.

I will test running `sync_skills.py` or creating a unified sync script to verify how skill syncing works across Hermes (`~/.hermes/skills`), Antigravity/Gemini (`~/.gemini/config/skills`), Claude (`~/.claude/skills`), and Codex (`~/.agents/skills`). Let's inspect `build_rules.py` and see where a `build_skills.py` or `sync_skills.py` script can fit into `ai-os/scripts/`.

I will search for `agymcp` or `agy-mcp` on disk to see where its source code or script lives.

I will write a python script in `~/projects/ai-os/scripts/sync_skills.py` that synchronizes skills across all targets (`~/.hermes/skills`, `~/.claude/skills`, `~/.agents/skills`, `~/.gemini/config/skills`, `~/.agy/skills`, `~/.antigravity/skills`). Let's design `sync_skills.py` cleanly.

Let's check how skill files are formatted in Hermes vs Claude/Gemini.
In Hermes, skills are organized in subdirectories like `software-development/plan/SKILL.md` or directly like `hyperframes/SKILL.md`.
In Claude / Gemini / Codex, skills are usually expected in top-level skill folders like `~/.claude/skills/<skill-name>/SKILL.md` or `~/.gemini/config/skills/<skill-name>/SKILL.md` or `~/.agents/skills/<skill-name>/SKILL.md`.

Let's test this layout by inspecting how Gemini (`~/.gemini/config/skills`) stores skills right now.
In `~/.gemini/config/skills`, we have:
- `plan/SKILL.md`
- `macos-background-gui/SKILL.md`
- `resume/SKILL.md`
- `build/SKILL.md`

And in `~/.gemini/antigravity-cli/skills`:
- `audit/SKILL.md`
- `fast/SKILL.md`
- `start/SKILL.md`
- `strict-delegation/SKILL.md`

Let's write a python script `sync_skills.py` that finds all skills across Hermes (`~/.hermes/skills`) and synchronizes them to:
1. `~/.claude/skills/`
2. `~/.agents/skills/`
3. `~/.gemini/config/skills/`
4. `~/.gemini/antigravity-cli/skills/`
5. `~/.agy/skills/`
6. `~/.antigravity/skills/`

Let's also update `build_rules.py` or create a wrapper so that running `python3 /Users/matt/projects/ai-os/scripts/sync_skills.py` (or as part of `preflight.py` or rule updates) keeps everything synced across platforms automatically!

Let's check `preflight.py` first to see what it currently executes.

I will create `sync_skills.py` in `~/projects/ai-os/scripts/sync_skills.py` to synchronize skills bidirectionally / cross-platform between:
- `~/.hermes/skills/`
- `~/.claude/skills/`
- `~/.agents/skills/`
- `~/.gemini/config/skills/`
- `~/.gemini/antigravity-cli/skills/`
- `~/.agy/skills/`
- `~/.antigravity/skills/`

Let's test writing the script and verifying skill discovery across all target platforms.

I will make `sync_skills.py` executable and run it to test syncing across all targets.

I will check the item counts across all skill target directories after running `sync_skills.py`.

I will integrate `sync_skills.py` into `build_rules.py` and `preflight.py` so that skill synchronization runs automatically whenever rules are built or pre-flight checks are run, ensuring skills are seamlessly available across Hermes, Claude, Antigravity, agy, and Codex.

Let's check `build_rules.py` and add a call to `sync_skills.py`.

I will update `common.md` in `~/.rules/common.md` to establish the rule for creating and synchronizing skills across Antigravity, Claude, and Hermes, similar to rule management. Let's inspect `common.md`.

I will patch `common.md` to add a rule section for skill creation and synchronization across Antigravity, Claude, Codex, and Hermes.

I will run `build_rules.py` to rebuild `HERMES.md`, `CLAUDE.md`, and `GEMINI.md` and verify that all rules and skills are fully synchronized across targets.

I will check git status to see what changes were made.

I will save a durable memory about skill synchronization so future sessions automatically run `sync_skills.py` or `build_rules.py` whenever skills are created or edited.

I will consolidate memory entries in a single batch to fit the 2200 char limit.

I will consolidate memory by shortening several entries in one atomic batch.

All changes are in place and verified. I will now summarize the setup for the user.

---

## User

you will now? Go ahead

---

## Assistant

I have set up and verified the universal skill synchronization system across all platform environments:

### 1. Unified Skill Synchronizer (`sync_skills.py`)
Created `/Users/matt/projects/ai-os/scripts/sync_skills.py`. It scans and synchronizes all custom skills (104 unique skills found) bidirectionally across:
- **Hermes**: `~/.hermes/skills/`
- **Claude Code**: `~/.claude/skills/`
- **Codex / Agents**: `~/.agents/skills/`
- **Antigravity / Gemini**: `~/.gemini/config/skills/` & `~/.gemini/antigravity-cli/skills/`
- **agy / Antigravity CLI**: `~/.agy/skills/` & `~/.antigravity/skills/`

### 2. Automatic Rule & Skill Bundling
Integrated `sync_skills.py` into `/Users/matt/projects/ai-os/scripts/build_rules.py`. 
Whenever you or any agent edit system rules or run `build_rules.py`, `preflight.py`, or `auto_commit.py`, skills are automatically synchronized across all agent targets.

### 3. Updated Global Rules (`.rules/common.md`)
Added Rule 21 to `~/projects/ai-os/.rules/common.md`:
> **Cross-Platform Skill Synchronization:** All custom skills created or updated by any agent (Hermes, Antigravity/Gemini, Claude Code, Codex, agy) must be synchronized across all platforms. When creating or editing a skill, place/update the skill under `~/.hermes/skills/<skill-name>/` or `~/.gemini/config/skills/<skill-name>/` and run `python3 /Users/matt/projects/ai-os/scripts/sync_skills.py` (or `build_rules.py`).

All 104 custom skills are now synchronized across Hermes, Antigravity, Claude, Codex, and agy.

---
