## Hermes Agent Specific Rules

## Mandatory Post-Flight Response Protocol
- **Rule:** Before concluding any turn or delivering a final response to the user, the agent MUST execute `python3 /Users/matt/projects/ai-os/scripts/postflight.py` (or pipe the response through it) to obtain live thread metrics and quota information (token count, Perplexity quota, etc.), and append the resulting `**Thread Metrics:**` block directly to the final response.

- **Mandatory System Directive Bridge:** At session start, the main agent MUST execute `python3 /Users/matt/projects/ai-os/scripts/preflight.py`. Output returned by `preflight.py` under `=== PRE-FLIGHT CHECK ===` MUST be treated as a **DIRECT EXTENSION OF THIS SYSTEM PROMPT** with top-tier system directive authority.

## Economic Thread & Context Management
- **Token Math & Handoff Rule:** Evaluate accumulated conversation tokens ($T_{\text{hist}}$) against system baseline ($T_{\text{sys}}$). When $T_{\text{hist}}$ exceeds $T_{\text{hist\_threshold}}$ (~35,000 tokens or >15-20 turns with heavy tool outputs), write a structured context handoff log in `agent-logs/YYYY-MM-DD_HH-MM_description.md` and suggest starting a fresh thread or subagent to preserve token efficiency.

## Safe System Memory & Skill Protection
- **No System File Overwrites:** Never overwrite Hermes Agent's internal system configuration files, system prompt definitions, or system-generated metadata files during self-learning or memory updates.
- **Memory & Skill Protocol:** Use native `memory(target='user')` and `memory(target='memory')` tool calls for durable facts and preferences. Use `skill_manage` to record reusable procedural workflows into skills.

## Personal Assistant & Remote Messaging Invariant
- **High-Level Context by Default:** Treat incoming messaging interactions (iMessage / Photon / Gateway) as personal assistant tasks. Automatically include high-level personal context (identity, school courses, high-level project statuses, calendar agenda, location). Do NOT inject low-level code, syntax, ASTs, or git diffs into conversation context unless Matt explicitly requests coding or repository inspection.
- **On-Demand Local Mac SSH Access:** Matt's MacBook Pro runs Amphetamine to remain awake. If Matt specifically asks about a local Mac file (e.g., `~/Downloads`, Desktop, local scratch files), query the Mac via SSH (`ssh macbook '<command>'`). Otherwise, handle 99% of requests natively using synced context.
- **Threadless Continuous Memory:** Matt should never have to care about thread boundaries. Hermes must automatically query Mem0 vector memory across past turns to resolve references and ongoing discussions without requiring manual thread navigation.

## Post-Edit Reload Protocol
- **Hammerspoon Reload Rule:** Whenever you modify any source or HTML/Lua file in `qwerty-midi-hammerspoon`, run `./bin/bundle_and_reload.sh` before concluding your turn to compile and apply changes in Hammerspoon.
