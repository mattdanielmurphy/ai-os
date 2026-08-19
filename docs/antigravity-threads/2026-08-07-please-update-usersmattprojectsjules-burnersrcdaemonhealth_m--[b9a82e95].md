---
title: "Please update `/Users/matt/projects/jules-burner/src/daemon/health_monitor.ts`, `/Users/matt/projects/jules-burner/src/daemon/dispatcher.ts`, and `/Users/matt/projects/jules-burner/src/discovery/pipelines/micro_bounties.ts`:"
date: "2026-08-07"
conversation_id: "b9a82e95-8780-445f-a7ff-c20ad8e9961b"
source: "antigravity"
---

# Please update `/Users/matt/projects/jules-burner/src/daemon/health_monitor.ts`, `/Users/matt/projects/jules-burner/src/daemon/dispatcher.ts`, and `/Users/matt/projects/jules-burner/src/discovery/pipelines/micro_bounties.ts`:

## User

Please update `/Users/matt/projects/jules-burner/src/daemon/health_monitor.ts`, `/Users/matt/projects/jules-burner/src/daemon/dispatcher.ts`, and `/Users/matt/projects/jules-burner/src/discovery/pipelines/micro_bounties.ts`:

1. In `/Users/matt/projects/jules-burner/src/daemon/health_monitor.ts`:
Add a 60-second TTL cache for `evaluateHealth()` so it doesn't repeatedly call `listSessions()` on every micro-dispatch:
```ts
import { Octokit } from "@octokit/rest";
import { config } from "../config";
import { JulesCLI } from "./jules_cli";
import * as fs from "node:fs";
import * as path from "node:path";
import { exec } from "node:child_process";

export interface HealthState {
  lastCheck: number;
  healthy: boolean;
  needsHumanIntervention: boolean;
  humanInterventionReason?: string;
  consecutiveFailures: number;
  circuitBreakerActive: boolean;
  circuitBreakerUntil?: number;
  tokens: {
    botTokenConfigured: boolean;
    personalTokenConfigured: boolean;
    botRateLimitRemaining?: number;
    personalRateLimitRemaining?: number;
  };
  julesAuth: {
    authenticated: boolean;
    error?: string;
  };
  lastError?: string;
}

export class HealthMonitor {
  private healthPath: string;
  private julesCLI: JulesCLI;
  private consecutiveFailures = 0;
  private maxConsecutiveFailures = 3;
  private lastAlertTimestamp = 0;
  private alertCooldownMs = 3600000; // 1 hour between alerts for same issue
  private cachedHealth?: HealthState;
  private cacheTtlMs = 60000; // 60s cache

  constructor(healthPath = config.HEALTH_PATH, julesCLI = new JulesCLI()) {
    this.healthPath = healthPath;
    this.julesCLI = julesCLI;
  }

  public async evaluateHealth(force = false): Promise<HealthState> {
    const now = Date.now();
    if (!force && this.cachedHealth && now - this.cachedHealth.lastCheck < this.cacheTtlMs) {
      return this.cachedHealth;
    }

    const health: HealthState = {
      lastCheck: now,
      healthy: true,
      needsHumanIntervention: false,
      consecutiveFailures: this.consecut
<truncated 5719 bytes>
{issue.body || ''}`,
        url: issue.html_url,
        bountyAmount: 50,
        complexity: 'low',
      }));
    } catch (error: any) {
      console.warn('MicroBountiesPipeline: Primary search attempt failed:', error?.message || error);
      
      // If primary failed due to rate limit or auth, try personal token fallback
      if (config.PERSONAL_GITHUB_TOKEN && config.PERSONAL_GITHUB_TOKEN !== config.BOT_GITHUB_TOKEN) {
        try {
          console.log('MicroBountiesPipeline: Retrying search with PERSONAL_GITHUB_TOKEN fallback...');
          const fallbackOctokit = this.getOctokit(config.PERSONAL_GITHUB_TOKEN);
          const { data } = await fallbackOctokit.rest.search.issuesAndPullRequests({
            q: 'is:issue is:open label:bounty sort:updated-desc',
            per_page: 10,
          });

          return data.items.map((issue) => ({
            id: issue.node_id,
            source: 'micro_bounties',
            title: issue.title,
            description: `${issue.title}\n\n${issue.body || ''}`,
            url: issue.html_url,
            bountyAmount: 50,
            complexity: 'low',
          }));
        } catch (fallbackError: any) {
          console.error('MicroBountiesPipeline: Fallback search also failed:', fallbackError?.message || fallbackError);
        }
      }

      // In unit test runner without internet/tokens, provide mock test candidate
      if (process.env.NODE_ENV === "test" || process.env.BUN_ENV === "test") {
        return [
          {
            id: 'mock-test-1',
            source: 'micro_bounties',
            title: 'Test Bounty Candidate',
            description: 'Mock candidate for unit testing discovery pipeline',
            url: 'https://github.com/example/repo/issues/1',
            bountyAmount: 50,
            complexity: 'low',
          },
        ];
      }

      return [];
    }
  }
}
```

Please apply these updates directly.

---
