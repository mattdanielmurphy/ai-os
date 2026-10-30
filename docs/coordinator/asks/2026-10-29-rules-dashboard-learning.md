# Matt's dictated message, 2026-10-29 (verbatim intent, lightly trimmed)

Context: replying to the rules→hooks plan (ai-os docs/rules-hooks/PLAN.md, PLAN-summary.md; A/B/C reports beside them).

1. **Self-editing rules.** Not certain he doesn't want agents to change rules. Self-learning needs the ability to edit its own rules (Hermes idea is good; for an end user like his mom, asking her to approve rules is useless). For now, keep Matt (and Tyler) in the loop while the system is being designed.
2. **Rules dashboard** ("a really fucking good idea"): see every rule, switch on/off, what's enabled, telemetry (how often each hook-based rule fires), self-audit stats (how often a rule is troublesome or misinterpreted; self-audit can run automatically since it has no side effects), background/why for each rule, overlaps, dependencies (relies on / relied on by), visual clashes, maybe gaps where rules are missing.
3. **Beta rules**: a lower tier of dynamic, experimental, agent-authored rules. They can never override official rules. Agents follow them; a UI dot shows "running beta rules" so Matt/Tyler always know. With telemetry, an agent can recommend promoting one ("2 weeks in beta, dozens of threads, no issues") to official. He's fine with agent-authored rules as long as there are checks and balances. "Correct me if I'm wrong."
4. **Dictation must be sacred.** Claude dictation stopped mid-speech with "Dictation stopped because it heard no words for 1 minute. Your words so far are in the message box." while he was talking. Possibly a bug (maybe from our own read-aloud/dictation mod). New project idea: a new version of TypeWhisper as good as Claude's dictation, for Slub Utils; not now, add it to the eventual projects list.
5. **Stay educated without wasting time** (do now):
   - Weekly scheduled "what's new and what do I specifically need to know" brief on agent tools/frameworks.
   - A personal syllabus so he becomes near-expert at agentic systems and stops making amateur mistakes.
   - A Hacker News digest that filters noise.
   - Constant research for off-the-shelf tools/frameworks so Slub wraps existing tools with its taste instead of building backends; relevance changes over time (switching cost grows as the project matures, users grow, decisions pile up).
6. **Coordinator model**: coordinator stays Opus low by default, but big dumps like this should go to a higher-thinking sub-coordinator that advises: "if you were the coordinator, tell me what to do", and the main coordinator carries out its actions.
