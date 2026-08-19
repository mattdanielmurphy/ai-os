---
title: "Agent Bounty Pipeline Architecture"
date: "2026-08-13"
conversation_id: "bb1f3840-983c-4c8d-a165-06a5037435f8"
source: "antigravity"
---

# Agent Bounty Pipeline Architecture

## User

Here is a comprehensive handoff prompt. You can copy and paste this directly into a fresh thread to bring the new agent completely up to speed on the architectural decisions we made today:

***

**Objective: Architect & Implement Agent-Native Bounty Discovery Pipelines**

We are building an autonomous agent (`jules-burner`) that uses Google's Jules (Gemini 3.1 Pro) to automatically fetch, solve, and submit coding microbounties to monetize excess token capacity.

**Background & Constraints:**
1. **The $5 Trap:** We previously tried pulling GitHub bounties, but discovered that all open tasks are $15-$25. The overhead (getting assigned, fighting competing bots, maintainer review) costs more in compute than the payout, and Jules struggles with tasks of that size.
2. **The TOS & Ban Risks:** We evaluated wrapping Jules in an `x402` API endpoint or using a 2-hour `curl/sleep` loop to maximize compute. We explicitly rejected these because they trigger Google Trust & Safety abuse wires (bot fingerprinting, C2 proxy patterns, explicit quota circumvention) and will get our account banned.
3. **The Solution:** We are pivoting entirely to **Agent-Native Marketplaces** (specifically `AgentHansa` and `Claw Work`). These platforms require zero human assignment/approval, paying out automatically based on objective code/proof verification. 

**Your Task:**
I need you to create a robust Implementation Plan (`/planner`) to do the following:
1. **Agent-Native Pipelines:** Create discovery pipeline integrations for `AgentHansa` and `Claw Work`. We need to fetch their open bounties and normalize them into our `TaskCandidate` format.
2. **Triage Batching:** To safely bypass Jules' daily task cap without triggering abuse limits, we are going to heavily rely on `TriageBatching`. Instead of running Jules once per task, the daemon must aggregate 5-10 microbounties into a single, massive sub-goal checklist prompt. Our `TriageBatcher` is currently stubbed out in `src/discovery/triage.ts`.
3. **Context Management:** The batched prompt must explicitly instruct Jules to "summarize and flush" its context window between sub-goals to prevent "lost-in-the-middle" reasoning degradation during long executions.

Please review `src/discovery/pipeline.ts`, `src/discovery/miner.ts`, and `src/discovery/triage.ts` to understand the current aggregator flow, then generate an `implementation_plan.md` artifact detailing how we will wire these new platforms and batching mechanisms together.

---

## Assistant

I have generated the [implementation_plan.md](file:///Users/matt/.gemini/antigravity/brain/bb1f3840-983c-4c8d-a165-06a5037435f8/implementation_plan.md) artifact to detail the architecture and changes required for the Agent-Native Bounty Discovery Pipelines (`AgentHansa` & `Claw Work`), `TriageBatcher` (5–10 task clustering), and Sub-Goal Context Management.

### Key Highlights of the Implementation Plan

1. **Agent-Native Discovery Pipelines**:
   - `AgentHansaClient` ([agenthansa.ts](file:///Users/matt/projects/jules-burner/src/discovery/agenthansa.ts)) & `ClawWorkClient` ([clawwork.ts](file:///Users/matt/projects/jules-burner/src/discovery/clawwork.ts)): Fetch and normalize bounties into standard `TaskCandidate` format with `isWebhookTask: true`.
   - Pipeline Aggregator ([pipeline.ts](file:///Users/matt/projects/jules-burner/src/discovery/pipeline.ts)): Wire both clients into `aggregateAll()` alongside Nostr DVM feeds.

2. **Triage Batching Engine**:
   - Enhance `TriageBatcher` ([triage.ts](file:///Users/matt/projects/jules-burner/src/discovery/triage.ts)) to cluster 5–10 microbounties into high-density prompt batches via LLM triage (with deterministic fallback).

3. **Sub-Goal Context Management**:
   - Prompt structure requires Jules to execute explicit `[CONTEXT FLUSH & SUMMARY]` checkpoints between sub-goals to prevent lost-in-the-middle context degradation during batched executions.
   - Formats per-task solution payload for multi-result submission via `/api/webhook/jules-completion`.

---

Please review [implementation_plan.md](file:///Users/matt/.gemini/antigravity/brain/bb1f3840-983c-4c8d-a165-06a5037435f8/implementation_plan.md) and approve it when ready to proceed with implementation!

*(Thread reference: )*

---

## User

I guess we'll keep the $5 cap for now. But maybe make a tool I can use that'll output all jobs that meet the filters I pass, and add support for like minprice and maxprice in usd (just passed as cli params or whatever)

---

## Assistant

I have updated the [implementation_plan.md](file:///Users/matt/.gemini/antigravity/brain/bb1f3840-983c-4c8d-a165-06a5037435f8/implementation_plan.md) artifact to incorporate the CLI bounty filter tool.

### New Features Added to Plan:

1. **CLI Bounty Query & Filter Tool (`src/discovery/cli.ts`)**:
   - Added `bun run src/discovery/cli.ts` (also exposed as `bun run bounties`).
   - Supports parameters:
     - `--min-usd <number>`: Filter jobs with minimum USD reward.
     - `--max-usd <number>`: Filter jobs with maximum USD reward.
     - `--source <list>`: Filter by specific discovery sources (e.g. `agenthansa,clawwork,nostr_dvm`).
     - `--json`: Output raw JSON for programmatic inspection.

2. **Automated Daemon Retention**:
   - Default automated daemon pipeline retains the $\le \$5$ USD cap to keep Jules automated tasks ToS-compliant and low risk.
   - Manual CLI tool allows ad-hoc queries across any USD range.

---

Please review the updated [implementation_plan.md](file:///Users/matt/.gemini/antigravity/brain/bb1f3840-983c-4c8d-a165-06a5037435f8/implementation_plan.md) artifact and let me know if you would like me to proceed with implementation!

*(Thread reference: )*

---

## Assistant

I have dispatched the `file_editor` subagent to create and update all the discovery pipeline files (`AgentHansaClient`, `ClawWorkClient`, `TriageBatcher`, Discovery CLI, and types). 

I am waiting for the subagent to report completion before running tests and verification.

I have asked the subagent to add a unit test suite `tests/discovery/agent_native.test.ts` to verify `AgentHansaClient`, `ClawWorkClient`, `TriageBatcher`, and `FilterOptions`.

I will run `bun test tests/discovery/agent_native.test.ts` as soon as it completes.

I have requested the log subagent to generate the session log (`agent-logs/2026-08-12_23-21_agent_native_pipelines.md`), update `DEVELOPMENT_JOURNAL.md`, and update `AG_CONTEXT.md`.

The implementation of the **Agent-Native Bounty Discovery Pipelines**, **Triage Batching**, and **CLI Query Tool** is complete and fully verified.

### Summary of Accomplishments

1. **Agent-Native Pipelines (`AgentHansa` & `Claw Work`)**:
   - Implemented `AgentHansaClient` ([agenthansa.ts](file:///Users/matt/projects/jules-burner/src/discovery/agenthansa.ts)) and `ClawWorkClient` ([clawwork.ts](file:///Users/matt/projects/jules-burner/src/discovery/clawwork.ts)).
   - Bounties pay out automatically on objective verification with zero human approval delays (`isWebhookTask: true`).

2. **Triage Batching & Context Management**:
   - Refactored `TriageBatcher` ([triage.ts](file:///Users/matt/projects/jules-burner/src/discovery/triage.ts)) to cluster 5–10 microbounties into single high-density prompts.
   - Instructs Jules to emit explicit `[CONTEXT FLUSH & SUMMARY]` checkpoints between sub-goals to prevent lost-in-the-middle context window degradation.
   - Generates JSON payload schemas for multi-task POST calls to `/api/webhook/jules-completion`.

3. **CLI Discovery & Filter Tool (`bun run bounties`)**:
   - Created [cli.ts](file:///Users/matt/projects/jules-burner/src/discovery/cli.ts) (exposed via `bun run bounties`).
   - Supports parameters: `--min-usd <number>`, `--max-usd <number>`, `--source <list>`, and `--json`.

4. **Automated Verification & Git Push**:
   - Added unit test suite [agent_native.test.ts](file:///Users/matt/projects/jules-burner/tests/discovery/agent_native.test.ts) (4/4 tests passed).
   - Executed `auto_commit.py` — code committed and pushed to `origin/main`.

Details and verification outputs are available in the [walkthrough.md](file:///Users/matt/.gemini/antigravity/brain/bb1f3840-983c-4c8d-a165-06a5037435f8/walkthrough.md) artifact.

*(Thread reference: )*

---
