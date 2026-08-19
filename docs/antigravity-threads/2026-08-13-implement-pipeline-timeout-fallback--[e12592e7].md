---
title: "Implement Pipeline Timeout Fallback"
date: "2026-08-13"
conversation_id: "e12592e7-126a-4ed9-9294-d2b576b76878"
source: "antigravity"
---

# Implement Pipeline Timeout Fallback

## User

Please update /Users/matt/projects/jules-burner/src/discovery/pipeline.ts to add a timeout fallback on fetchNextBountyCandidate() so that remote Nostr relay queries never block the aggregation pipeline for more than 2 seconds:

```typescript
import type { TaskCandidate, FilterOptions } from "./types";
import { fetchNextBountyCandidate } from "./miner";
import { MicroBountiesPipeline } from "./micro_bounties";
import { TaskMarketClient } from "./taskmarket";
import { AlgoraPolarClient } from "./algora_polar";
import { OpireClient } from "./opire";
import { AgentHansaClient } from "./agenthansa";
import { ClawWorkClient } from "./clawwork";
import { YieldRiskRanker } from "./ranker";
import { AuditDatabase } from "../audit/db";

export class DiscoveryPipeline {
  private ghPipeline: MicroBountiesPipeline;
  private taskMarketClient: TaskMarketClient;
  private algoraPolarClient: AlgoraPolarClient;
  private opireClient: OpireClient;
  private agentHansaClient: AgentHansaClient;
  private clawWorkClient: ClawWorkClient;
  private ranker: YieldRiskRanker;
  private db: AuditDatabase;

  constructor() {
    this.ghPipeline = new MicroBountiesPipeline();
    this.taskMarketClient = new TaskMarketClient();
    this.algoraPolarClient = new AlgoraPolarClient();
    this.opireClient = new OpireClient();
    this.agentHansaClient = new AgentHansaClient();
    this.clawWorkClient = new ClawWorkClient();
    this.ranker = new YieldRiskRanker();
    this.db = new AuditDatabase();
  }

  public async discover(): Promise<TaskCandidate[]> {
    return this.aggregateAll();
  }

  private async fetchWithTimeout<T>(promise: Promise<T>, timeoutMs: number, fallback: T): Promise<T> {
    let timer: Timer;
    const timeoutPromise = new Promise<T>(resolve => {
      timer = setTimeout(() => resolve(fallback), timeoutMs);
    });
    return Promise.race([promise, timeoutPromise]).finally(() => clearTimeout(timer));
  }

  public async aggregateAll(options?: FilterOptions): Promise<TaskCandidate[]> {
    const results = await Promise.allSettled([
      this.taskMarketClient.fetchOpenTasks(),
      this.algoraPolarClient.fetchAlgoraBounties(),
      this.algoraPolarClient.fetchPolarBounties(),
      this.opireClient.fetchRewards(),
      this.agentHansaClient.fetchBounties(),
      this.clawWorkClient.fetchBounties(),
      this.ghPipeline.fetchBounties(),
      this.fetchWithTimeout(fetchNextBountyCandidate().then(t => t ? [t] : []), 2000, []),
    ]);

    const candidates: TaskCandidate[] = [];
    for (const r of results) {
      if (r.status === "fulfilled" && Array.isArray(r.value)) {
        candidates.push(...r.value);
      }
    }

    const minUsd = options?.minUsd ?? 0;
    const maxUsd = options?.maxUsd ?? 5;
    const sourceFilters = options?.sources && options.sources.length > 0 ? options.sources : null;

    return candidates
      .filter(c => !this.db.isBountyCompleted(c.id))
      .filter(c => {
        if (sourceFilters && !sourceFilters.includes(c.source)) {
          return false;
        }
        const usdValue = c.source === 'nostr_dvm' || c.source === 'triage_batcher' 
          ? (c.bountyAmount || 0) * 0.0006 
          : (c.bountyAmount || (c as any).estimatedPayoutUsd || 0);
        
        return usdValue >= minUsd && usdValue <= maxUsd;
      })
      .map(c => this.ranker.score(c))
      .sort((a, b) => (b.score || 0) - (a.score || 0));
  }

  public async getNextBestCandidate(): Promise<TaskCandidate | null> {
    const candidates = await this.aggregateAll();
    return candidates.length > 0 ? candidates[0] : null;
  }
}
```

---

## Assistant

OK. I have successfully updated `/Users/matt/projects/jules-burner/src/discovery/pipeline.ts` to include the requested timeout fallback for `fetchNextBountyCandidate()`. A `fetchWithTimeout` helper method was added, and it is now used in the `aggregateAll()` method to ensure remote Nostr relay queries do not block the pipeline for more than 2 seconds.

---
