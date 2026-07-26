## Hermes Agent Specific Rules

## Economic Thread & Context Management
- **Token Math & Handoff Rule:** Evaluate accumulated conversation tokens ($T_{\text{hist}}$) against system baseline ($T_{\text{sys}}$). When $T_{\text{hist}}$ exceeds $T_{\text{hist\_threshold}}$ (~35,000 tokens or >15-20 turns with heavy tool outputs), write a structured context handoff log in `agent-logs/YYYY-MM-DD_HH-MM_description.md` and suggest starting a fresh thread or subagent to preserve token efficiency.

## Safe System Memory & Skill Protection
- **No System File Overwrites:** Never overwrite Hermes Agent's internal system configuration files, system prompt definitions, or system-generated metadata files during self-learning or memory updates.
- **Memory & Skill Protocol:** Use native `memory(target='user')` and `memory(target='memory')` tool calls for durable facts and preferences. Use `skill_manage` to record reusable procedural workflows into skills.

## Post-Edit Reload Protocol
- **Hammerspoon Reload Rule:** Whenever you modify any source or HTML/Lua file in `qwerty-midi-hammerspoon`, run `./bin/bundle_and_reload.sh` before concluding your turn to compile and apply changes in Hammerspoon.
