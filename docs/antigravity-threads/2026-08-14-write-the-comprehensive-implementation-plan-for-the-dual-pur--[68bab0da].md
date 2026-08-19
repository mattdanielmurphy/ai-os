---
title: "Write the comprehensive implementation plan for the Dual-Purpose Jules Burner System to /Users/matt/.gemini/antigravity/brain/eb52f7fb-8d62-42c4-889f-f1d88b3f9e03/implementation_plan.md."
date: "2026-08-14"
conversation_id: "68bab0da-e209-45e1-ba2a-9048459bc267"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Write the comprehensive implementation plan for the Dual-Purpose Jules Burner System to /Users/matt/.gemini/antigravity/brain/eb52f7fb-8d62-42c4-889f-f1d88b3f9e03/implementation_plan.md.

Include the following sections clearly structured:
# Dual-Purpose Jules Compute Engine: Rapid Bounty Sniper & Autonomous Maintenance Fleet

## Overview & Architectural Strategy
1. **Subsystem 1: High-Frequency Bounty Sniper Daemon** (Nostr DVM kind 5000-5999 real-time WebSocket, ClawWork/AgentHansa pollers, Algora/GH issue monitors, with atomic SQLite TTL lock/claiming to eliminate race conditions and snipe microbounties in <5s).
2. **Subsystem 2: Safe Jules Internal Maintenance & Optimization Fleet** (Repo scratch/garbage cleaner with strict allowlists, and `agent-logs/` pattern analyzer with SQLite FTS5 index to discover recurring agent bottlenecks/conflicts and draft PR proposals for `ai-os` system rules/directives).
3. **Subsystem 3: Strict Sandboxing & Mac Environment Firewall** (Zero local write execution on Matt's Mac; all Jules tasks execute in remote Google cloud VM / ephemeral VPS runners. Modifications land ONLY on staging branches / draft PRs via GitHub, with automated schema/linter gating).
4. **Subsystem 4: Cross-Project Opportunity Scout** (Periodically indexes all local/remote repos via `AG_CONTEXT.md` capabilities, scoring external microbounties against existing reusable modules).

## User Review Required
- Highlight the safe boundary model (Staging PRs only, no unattended local mutations on Mac).
- Highlight the cron schedule & quota partitioning (e.g. 50 tasks for high-speed sniper, 50 tasks for internal maintenance/scout).

## Data Structures & State Management
- Define schema additions in `data/audit.db` or new SQLite tables: `locks` (ttl, owner, heartbeat), `bounty_sniper_queue`, `maintenance_tasks`, `rule_improvement_proposals`.

## API & Interface Contracts
- `BountySourceAdapter` (Nostr, Algora, ClawWork)
- `MaintenanceJobRunner` (ScratchCleaner, LogPatternAnalyzer)
- `SafetyFirewall` (StagingBranchValidator, DiffBoundaryGuard)
- `OpportunityScout` (RepoCapabilityIndex, BountyMatcher)

## Logic Flow & Algorithms
- Real-time sniper lifecycle (Event -> Atomic Lock -> Jules Prompt Injection -> Webhook Settlement).
- Scheduled Maintenance lifecycle (Schedule -> Local read-only scan -> Jules task generation -> Git PR staging branch -> Review notification).

## Implementation Steps
List file modifications and new modules in `src/`:
1. `src/adapters/` (Nostr, Algora, ClawWork source adapters)
2. `src/maintenance/` (`ScratchCleaner.ts`, `LogPatternAnalyzer.ts`)
3. `src/scout/` (`OpportunityScout.ts`)
4. `src/security/` (`SafetyFirewall.ts`)
5. `src/daemon.ts` and `src/index.ts` (Dual-mode scheduler loop & quota budget partitioning).

Set ArtifactMetadata appropriately with user_facing: true and request_feedback: true.

</span>



<span title="Responded at 2:24am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The comprehensive implementation plan for the Dual-Purpose Jules Burner System has been created and saved as an artifact. You can review it here: [implementation_plan.md](file:///Users/matt/.gemini/antigravity/brain/68bab0da-e209-45e1-ba2a-9048459bc267/implementation_plan.md) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/68bab0da-e209-45e1-ba2a-9048459bc267/implementation_plan.md).
I have notified the parent agent of its completion. Please review the document, particularly the safety boundary model and resource allocation, and let me know if any changes are required.

</span>



</span>

</span>