---
title: "Jules Burner Project Planning"
date: "2026-08-05"
conversation_id: "56725915-6305-4246-b379-93370c8b3da6"
source: "antigravity"
---

# Jules Burner Project Planning

## User

Please write the following multi-step plan files and project context file for jules-burner. Create the parent directory /Users/matt/projects/jules-burner/plans/jules-burner-self-improving if needed.

File 1: /Users/matt/projects/jules-burner/AG_CONTEXT.md
Content:
```markdown
# AG_CONTEXT - Jules Quota Burner (JQB)

## Architectural & System Context
- **Project Purpose**: Automated, local, ToS-compliant dispatch daemon designed to harvest compute value from Google Jules daily quota (100 tasks/day on a single Google AI Pro account).
- **Core Strategy**: High-density task discovery (Algora micro-bounties, open-source spec/doc generation, internal self-improvement), automated staging fork validation, strict 100% self-auditing telemetry, and iterative self-improvement loops.
- **Tech Stack**: Bun, TypeScript, `@google/jules` CLI wrapper, SQLite telemetry store, GitHub GraphQL / REST APIs.
- **Safety Firewall**: Staging fork isolation (`staging-*`), CI gate checks before upstream submission, rate limiting with jitter (3-7 min intervals), strict ToS compliance (no unauthorized scraping, mining, or public issue spam).

## Operational Rules
- All file edits must be performed via `flash_lite` subagent delegation per system rules.
- Single account mode: Max 100 tasks/day cap strictly enforced in dispatch state.
- Every Jules session MUST emit structured telemetry to `data/audit.db` and trigger failure pattern classification.
```

File 2: /Users/matt/projects/jules-burner/plans/jules-burner-self-improving/status.json
Content:
```json
{
  "plan_name": "jules-burner-self-improving",
  "status": "IN_PROGRESS",
  "current_step": 1,
  "steps": [
    {
      "id": 1,
      "file": "01-architecture-and-safety-guardrails.md",
      "title": "Architecture & Safety Guardrails Setup",
      "status": "TODO"
    },
    {
      "id": 2,
      "file": "02-task-discovery-and-monetization-engine.md",
      "title": "Task Discovery & Legal Monetization Engine",
      "status": "TODO"
    },
    {
      "id": 3,
      "file": 
<truncated 10416 bytes>
les populate correctly and friction analyzer generates valid summary stats.
```

File 8: /Users/matt/projects/jules-burner/plans/jules-burner-self-improving/06-self-improvement-and-prompt-auto-tuner.md
Content:
```markdown
# Step 6: Self-Improvement Loop, Quota Reinvestment & Auto-Tuning

## Objective
Establish a continuous self-improvement mechanism that uses initial quota to self-audit, tune prompt strategies, repair system bugs, and iteratively eliminate friction.

## Target Files
- `src/self_improve/tuner.ts` [NEW]
- `src/self_improve/quota_allocator.ts` [NEW]
- `src/self_improve/prompt_patcher.ts` [NEW]
- `src/self_improve/self_repair.ts` [NEW]

## Implementation Instructions

### 1. Quota Reinvestment Allocator (`src/self_improve/quota_allocator.ts`)
- Manage daily quota split (100 tasks/day total):
  - **Early Phase (Days 1-7)**: Reinvest 60% quota (60 tasks/day) into self-auditing, prompt tuning, internal unit test building, and `jules-burner` self-repair. 40% to external monetization.
  - **Mature Phase (Day 8+)**: Shift to 80% external monetization, 20% ongoing self-audit & refinement.

### 2. Prompt Auto-Tuning & Patching (`src/self_improve/prompt_patcher.ts`)
- Read daily friction logs from telemetry database.
- Identify recurrent prompt failure modes (e.g., Jules failing to install dependencies before building).
- Auto-inject negative prompts and directive rules into `src/daemon/prompter.ts` (e.g., "Always run `bun install` before testing").

### 3. Self-Repair Pipeline (`src/self_improve/self_repair.ts`)
- Dispatch Jules tasks against `jules-burner` repo itself to fix identified bugs, improve test coverage, or add missing miner integrations.
- Validate self-repair PRs via local test suites before merging into master.

## Verification
- Test auto-tuner against simulated friction logs; confirm that negative prompt directives are correctly generated and injected into prompt templates.
```

---

## Assistant

Created At: 2026-08-05T00:47:52-06:00
Completed At: 2026-08-05T00:47:52-06:00

				The command exited with code 0.
				Stdout:
				
				Stderr:

Created At: 2026-08-05T00:47:55-06:00
Completed At: 2026-08-05T00:47:55-06:00
Created file file:///Users/matt/projects/jules-burner/AG_CONTEXT.md with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T00:47:57-06:00
Completed At: 2026-08-05T00:47:57-06:00
Created file file:///Users/matt/projects/jules-burner/plans/jules-burner-self-improving/status.json with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T00:47:59-06:00
Completed At: 2026-08-05T00:47:59-06:00
Created file file:///Users/matt/projects/jules-burner/plans/jules-burner-self-improving/01-architecture-and-safety-guardrails.md with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T00:48:02-06:00
Completed At: 2026-08-05T00:48:02-06:00
Created file file:///Users/matt/projects/jules-burner/plans/jules-burner-self-improving/02-task-discovery-and-monetization-engine.md with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T00:48:04-06:00
Completed At: 2026-08-05T00:48:04-06:00
Created file file:///Users/matt/projects/jules-burner/plans/jules-burner-self-improving/03-jules-dispatch-daemon-and-single-account-throttler.md with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T00:48:05-06:00
Completed At: 2026-08-05T00:48:05-06:00
Created file file:///Users/matt/projects/jules-burner/plans/jules-burner-self-improving/04-staging-ci-cd-and-pr-validation-gate.md with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T00:48:07-06:00
Completed At: 2026-08-05T00:48:07-06:00
Created file file:///Users/matt/projects/jules-burner/plans/jules-burner-self-improving/05-self-auditing-telemetry-and-friction-tracker.md with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T00:48:09-06:00
Completed At: 2026-08-05T00:48:09-06:00
Created file file:///Users/matt/projects/jules-burner/plans/jules-burner-self-improving/06-self-improvement-and-prompt-auto-tuner.md with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T00:48:10-06:00
Completed At: 2026-08-05T00:48:10-06:00
Message sent to "a93da981-9838-4c2e-8c21-0c32bbc1192c".

OK. I have created the requested files for the `jules-burner` project, including the context file and the full set of multi-step plan files in `/Users/matt/projects/jules-burner/plans/jules-burner-self-improving/`.

---
