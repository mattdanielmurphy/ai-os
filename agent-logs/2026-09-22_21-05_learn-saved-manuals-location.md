# Saved Manuals Location and Opening Files

- Recorded the saved manuals directory as `~/Documents/Books & Reference Documents/Manuals/` in AG_CONTEXT and added the `_find-saved-manuals` custom skill.
- The skill directs agents to match the exact product/model before giving instructions and to use Codex `open_in_codex` when Matt asks to pull up a local file.
- Ran `scripts/sync_skills.py`; verified the skill propagated to `~/.agents/skills/custom-skills/` and `~/.gemini/config/skills/custom-skills/`.
