---
title: "Update Discovery Types File"
date: "2026-08-05"
conversation_id: "80ab8606-4256-4396-99b2-f5ed13fcb7de"
source: "antigravity"
---

# Update Discovery Types File

## User

Update `/Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/src/discovery/types.ts` using `write_to_file`:

Add executionStrategy and stage tracking types:

```typescript
export type ExecutionStrategy = 'single_pass' | 'staged_2pass' | 'staged_4pass';

export type TaskCandidate = {
  id: string;
  source: string;
  title: string;
  description: string;
  url: string;
  bountyAmount?: number;
  complexity: 'low' | 'medium' | 'high';
  executionStrategy?: ExecutionStrategy;
  stage?: number; // 1: Research/Plan, 2: Fix, 3: Audit, 4: CI/Review
};

export type TaskSource = 'micro_bounties' | 'asset_specs' | 'self_tasks';

export type ScoredTaskCandidate = TaskCandidate & {
  score: number;
};

export type PipelineOptions = {
  dryRun?: boolean;
};
```

---

## Assistant

Created At: 2026-08-05T17:49:40-06:00
Completed At: 2026-08-05T17:49:41-06:00
Created file file:///Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/src/discovery/types.ts with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T17:49:44-06:00
Completed At: 2026-08-05T17:49:45-06:00
Message sent to "b5975665-c0ec-416e-ad2f-f24a34652c81".

I have successfully updated [`/Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/src/discovery/types.ts`](file:///Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/src/discovery/types.ts) with the new `ExecutionStrategy` and the updated `TaskCandidate` type definitions.

Created At: 2026-08-05T17:49:48-06:00
Completed At: 2026-08-05T17:49:49-06:00
Message sent to "b5975665-c0ec-416e-ad2f-f24a34652c81".

The update to `src/discovery/types.ts` is complete.

---
