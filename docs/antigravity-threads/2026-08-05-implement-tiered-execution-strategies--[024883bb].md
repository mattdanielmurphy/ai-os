---
title: "Implement Tiered Execution Strategies"
date: "2026-08-05"
conversation_id: "024883bb-4b76-4dd1-8f6a-b11d3f05940d"
source: "antigravity"
---

# Implement Tiered Execution Strategies

## User

Update `/Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/src/discovery/ranker.ts` using `write_to_file`:

Enforce strict tiered execution strategies based on bounty values:
- Bounties < $25: 'single_pass'
- Bounties $25 - $100: 'staged_2pass' (Stage 1 Plan/Repro -> Stage 2 Implement)
- Bounties > $100: 'staged_4pass' (Stage 1 Research -> Stage 2 Fix -> Stage 3 Audit -> Stage 4 Staging Gate)

Contents of `src/discovery/ranker.ts`:
```typescript
import type { TaskCandidate, ScoredTaskCandidate, ExecutionStrategy } from './types';

export class YieldRiskRanker {
  score(task: TaskCandidate): ScoredTaskCandidate {
    let score = 50; // base score
    let strategy: ExecutionStrategy = 'single_pass';

    const bounty = task.bountyAmount || 0;

    if (bounty >= 100) {
      strategy = 'staged_4pass';
      score += 40; // High reward potential, carefully staged
    } else if (bounty >= 25) {
      strategy = 'staged_2pass';
      score += 25;
    } else {
      strategy = 'single_pass';
      if (task.complexity === 'low') score += 10;
    }
    
    return {
      ...task,
      executionStrategy: strategy,
      stage: task.stage || 1,
      score: Math.min(100, Math.max(0, score))
    };
  }
}
```

---

## Assistant

Created At: 2026-08-05T17:51:49-06:00
Completed At: 2026-08-05T17:51:50-06:00
Created file file:///Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/src/discovery/ranker.ts with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T17:51:53-06:00
Completed At: 2026-08-05T17:51:56-06:00
Message sent to "b5975665-c0ec-416e-ad2f-f24a34652c81".

The file `/Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/src/discovery/ranker.ts` has been updated with the tiered execution strategies.

---
