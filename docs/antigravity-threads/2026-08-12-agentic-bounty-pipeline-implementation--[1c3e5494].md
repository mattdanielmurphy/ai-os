---
title: "Agentic Bounty Pipeline Implementation"
date: "2026-08-12"
conversation_id: "1c3e5494-f96e-4610-bda5-8e39c5b194a6"
source: "antigravity"
---

# Agentic Bounty Pipeline Implementation

## User

<USER_REQUEST>
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
3. **Context Management:** The batched
<truncated 729 bytes>
s a [Workflow]:
<SKILL>The user mentioned the (planner) skill. Here are its contents:
Run high-reasoning planning using the `planner` skill instructions, bundling codebase context via repomix.

1. **Sanity Check**: Analyze the user's request against the current active project directory. If the request appears completely unrelated to the current project (e.g., asking about a music app while inside the `ai-os` repository), STOP and ask the user to confirm they are in the correct project folder before proceeding.
2. Confirm `repomix` is installed and on `PATH` (`which repomix`); no separate sync step is required since it reads the live directory directly.
3. Run `python3 ~/projects/ai-os/scripts/generate_planner_prompt.py "<insert user request here>"` — this generates both `./tmp/context.md` and `./tmp/planner_prompt.txt`.
4. Invoke `proxima:ask_perplexity` by passing the exact contents of `./tmp/planner_prompt.txt` into the `message` parameter (NOT `prompt`). By default, DO NOT call the `new_conversation` tool — you should RESUME the existing thread when following up on a plan or iterating, unless the script output explicitly tells you the context is bloated and requires a reset. You MUST strictly obey the `ACTION REQUIRED` directive printed at the end of the script output regarding `new_conversation` and whether to attach `context.md` via the `files` parameter.

**CRITICAL FALLBACK RULE**: If `generate_planner_prompt.py` or `proxima:ask_perplexity` fails for *any* reason, you MUST IMMEDIATELY STOP. Do NOT attempt to fall back to manual planning or proceed on your own. Explicitly inform the user of the exact error and wait for their instructions.

5. Format the output into `implementation_plan.md`.</SKILL>
</ADDITIONAL_METADATA>

---

## Assistant

I encountered an issue while trying to generate the implementation plan. 

Following the mandatory `/planner` workflow, I successfully gathered the context for `src/discovery/pipeline.ts`, `src/discovery/miner.ts`, and `src/discovery/triage.ts`, and passed it along with your prompt to `proxima:ask_perplexity`. 

However, Perplexity **refused to fulfill the request due to a safety/policy block**. It analyzed the `jules-burner` codebase and incorrectly flagged the architecture as a malicious prompt injection/C2 exfiltration scheme designed to hijack a third-party AI agent (Jules) for farming micro-bounties without authorization. 

Per the strict `/planner` rules, if `proxima:ask_perplexity` fails for any reason, I am strictly forbidden from attempting to do the planning work locally or bypassing this step. I must stop and inform you. 

How would you like to proceed? We can either try to adjust the prompt to clarify to the model that this is an authorized use of your own personal quota, or if you prefer, I can bypass the `/planner` skill (if you explicitly authorize it) and write the `implementation_plan.md` artifact myself based on the provided context.

---
