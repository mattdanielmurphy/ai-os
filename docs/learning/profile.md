# Learning profile (read by the weekly agent brief)

What Matt builds right now, how mature each thing is, and what he wants to learn. The weekly brief job (`~/.claude/scheduled-tasks/weekly-agent-brief`) reads this every Sunday and updates the **Stages** and **Feedback** sections from evidence. Design: `docs/coordinator/asks/2026-10-29-advisor-answer.md` §4.

Last updated: 2026-10-29 (initial, by the learning-brief setup session).

## Goal
Become near-expert at agentic systems so he stops making amateur mistakes; stay current on agent tools in ~15 min a week; keep scouting off-the-shelf tools so Slub wraps existing tools with its own taste instead of building backends.

## Stage bar: when to recommend replacing something he built
| Stage | Recommend replacing a component when… |
|---|---|
| Idea | Any off-the-shelf tool does it reasonably well: use it. |
| Prototype | It's clearly better and the swap is under a day. |
| Committed | It removes a whole piece of backend he'd otherwise maintain. |
| Has users | Only for security, deprecation, or a cost/quality jump users would notice. |

## Stages (the job updates these from commits, slub-hq `NOW.md`, users)
| Project | What it is | Stage | Components worth watching for replacements |
|---|---|---|---|
| ai-os | His Claude Code setup: rules, hooks, coordinator, scripts, QMD recall | Committed | Rules→hooks compiler and dispatcher, rule dashboard, QMD memory/recall, coordinator inbox + custodian, details/Readthrough pages |
| Rules → hooks plan | `docs/rules-hooks/PLAN.md`: rules as files, hooks, beta rules, weekly tuner | Idea (designed, not built) | Rule sync tools (rulesync/agentsync), hook frameworks, OTel observability for Claude Code |
| Hammerspoon suite / Slub Utils | HUDs, take-control queue, Tweaks panel, read-aloud mod, installer for Tyler | Prototype (Tyler about to use it) | Window/HUD managers, dictation apps (TypeWhisper, VoiceInk, Superwhisper), TTS |
| Slub (with Tyler) | Audio software co.; generative synth; "coordinator that gives each task only the rules it needs" | Idea | Plugin frameworks (JUCE etc.), sample analysis, agent rule routing |
| Slub Telegram bot | Shared bot with Mac failover | Prototype | Hosted bot runners, agent-to-chat bridges |
| Glass TV | Android TV app / streaming catalog | Prototype | Off-the-shelf players, catalog APIs |
| pages | Vercel page publishing (`pages md`, reels, Readthroughs) | Committed | Static hosting, markdown publishers |
| Daily mini crossword | mattmurphy.ca crossword | Has users | Only security/deprecation |
| qwerty MIDI plugin | Keyboard-as-MIDI | Prototype | MIDI/plugin frameworks |

## Topics he already knows (skip the basics)
Claude Code hooks (PreToolUse/Stop/UserPromptSubmit), skills, subagents and side sessions, MCP connectors, launchd agents, Hammerspoon, Vercel deploys, QMD/BM25+vector search, prompt-caching basics, model families (Opus/Sonnet/Haiku).

## Topics to learn (weight 1–3; the job raises/lowers from ratings)
- 3 · Evals: measuring whether a rule, prompt or agent change helped
- 3 · Deterministic guards vs. model judges; when an LLM layer is worth it
- 3 · Multi-agent orchestration cost and failure modes
- 2 · Context engineering and token budgets
- 2 · Agent observability (OpenTelemetry, traces of tool calls)
- 2 · Memory/recall systems for agents
- 2 · Voice/dictation/TTS pipelines (practical, for his tools)
- 1 · New model releases (only when they change what he should use)

## Skip
Funding/startup drama, AI policy debates, benchmark leaderboards without practical change, crypto, generic "10 prompts" listicles, AI-generated music tools (banned except jokes), anything needing orange/terracotta UIs.

## Feedback (Matt's ratings and comments; newest first; the job reads and acts on these)
- (none yet: rate items in the brief, or tell the Coordinator "brief: …")
