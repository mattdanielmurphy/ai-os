---
title: "Please perform the following batched edits to implement the live bounty pipeline and dual-token separation:"
date: "2026-08-06"
conversation_id: "fbef5594-ace3-41cb-aaef-6296e8200f5c"
source: "antigravity"
---

# Please perform the following batched edits to implement the live bounty pipeline and dual-token separation:

## User

Please perform the following batched edits to implement the live bounty pipeline and dual-token separation:

1. Update `/Users/matt/projects/jules-burner/src/config.ts`:
```typescript
import { z } from "zod";

const envSchema = z.object({
  BOT_GITHUB_TOKEN: z.string().optional(),
  PERSONAL_GITHUB_TOKEN: z.string().optional(),
  GITHUB_TOKEN: z.string().optional(),
  JULES_CLI_PATH: z.string().default("jules"),
  DATABASE_PATH: z.string().default("data/audit.db"),
});

const env = envSchema.parse(process.env);

export const config = {
  DAILY_TASK_LIMIT: 100,
  MIN_JITTER_SECONDS: 180,
  MAX_JITTER_SECONDS: 420,
  STAGING_ORG_OR_USER: "ZephyrAethes",
  BOT_GITHUB_TOKEN: env.BOT_GITHUB_TOKEN || env.GITHUB_TOKEN || "",
  PERSONAL_GITHUB_TOKEN: env.PERSONAL_GITHUB_TOKEN || env.GITHUB_TOKEN || "",
  GITHUB_TOKEN: env.BOT_GITHUB_TOKEN || env.GITHUB_TOKEN || "",
  JULES_CLI_PATH: env.JULES_CLI_PATH,
  DATABASE_PATH: env.DATABASE_PATH,
};
```

2. Update `/Users/matt/projects/jules-burner/src/discovery/types.ts`:
```typescript
export type TaskCandidate = {
  id: string;
  source: string;
  title: string;
  description: string;
  url: string;
  repo?: string;
  bountyAmount?: number;
  complexity: 'low' | 'medium' | 'high';
};

export type TaskSource = 'micro_bounties' | 'asset_specs' | 'self_tasks';

export type ScoredTaskCandidate = TaskCandidate & {
  score: number;
};

export type PipelineOptions = {
  dryRun?: boolean;
};
```

3. Replace `/Users/matt/projects/jules-burner/src/discovery/pipelines/micro_bounties.ts`:
```typescript
import type { TaskCandidate } from '../types';
import { Octokit } from '@octokit/rest';
import { config } from '../../config';

export class MicroBountiesPipeline {
  private octokit: Octokit;

  constructor() {
    this.octokit = new Octokit({
      auth: config.BOT_GITHUB_TOKEN || config.GITHUB_TOKEN || undefined,
    });
  }

  async fetch(): Promise<TaskCandidate[]> {
    try {
      // Query GitHub API for open bounties / easy-win issues
      const q = 'is:issue is:open 
<truncated 4879 bytes>
s.stagingRepo.split("/")[0];

        const createRes = await this.botOctokit.pulls.create({
          owner,
          repo,
          title: params.title,
          head: `${headOwner}:${params.branch}`,
          base: "main",
          body: prBody,
        });

        return {
          submitted: true,
          prUrl: createRes.data.html_url,
          prBody,
        };
      } catch (err: any) {
        return {
          submitted: false,
          reason: `GitHub API Error (Bot Account ZephyrAethes): ${err.message}`,
        };
      }
    }

    return {
      submitted: true,
      prUrl: `https://github.com/${params.upstreamRepo}/pull/1`,
      prBody,
    };
  }
}
```

8. Create `/Users/matt/projects/jules-burner/tests/test_live_bounty.test.ts`:
```typescript
import { describe, expect, it } from 'bun:test';
import { MicroBountiesPipeline } from '../src/discovery/pipelines/micro_bounties';
import { YieldRiskRanker } from '../src/discovery/ranker';
import { UpstreamPRGate } from '../src/staging/upstream_pr';
import { config } from '../src/config';

describe('Live Bounty E2E Pipeline', () => {
  it('mines live micro-bounty candidates without mock data', async () => {
    const pipeline = new MicroBountiesPipeline();
    const ranker = new YieldRiskRanker();

    const candidates = await pipeline.fetch();
    expect(candidates.length).toBeGreaterThan(0);

    const first = candidates[0];
    expect(first.source).toBe('micro_bounties');
    expect(first.title.length).toBeGreaterThan(0);
    expect(first.complexity).toBe('low');

    const scored = ranker.score(first);
    expect(scored.score).toBeGreaterThanOrEqual(80); // Micro-bounties low complexity score 100 max
  });

  it('verifies bot account token configuration for external PRs', () => {
    expect(config.STAGING_ORG_OR_USER).toBe('ZephyrAethes');
    const gate = new UpstreamPRGate();
    expect(gate).toBeDefined();
  });
});
```

---
