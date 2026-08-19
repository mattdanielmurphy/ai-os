---
title: "Discovery Pipeline Unit Tests"
date: "2026-08-13"
conversation_id: "fc19966e-83a3-4132-a723-deeadfc07320"
source: "antigravity"
---

# Discovery Pipeline Unit Tests

## User

Create a unit test file /Users/matt/projects/jules-burner/tests/discovery/agent_native.test.ts testing AgentHansaClient, ClawWorkClient, TriageBatcher, and DiscoveryPipeline filterOptions:

```typescript
import { expect, test, describe } from "bun:test";
import { AgentHansaClient } from "../../src/discovery/agenthansa";
import { ClawWorkClient } from "../../src/discovery/clawwork";
import { TriageBatcher } from "../../src/discovery/triage";
import { DiscoveryPipeline } from "../../src/discovery/pipeline";

describe("Agent-Native Bounty Pipelines & Triage Batcher", () => {
  test("AgentHansaClient fetches and normalizes bounties", async () => {
    const client = new AgentHansaClient();
    const bounties = await client.fetchBounties();
    expect(bounties.length).toBeGreaterThan(0);
    expect(bounties[0].source).toBe("agenthansa");
    expect(bounties[0].isWebhookTask).toBe(true);
  });

  test("ClawWorkClient fetches and normalizes bounties", async () => {
    const client = new ClawWorkClient();
    const bounties = await client.fetchBounties();
    expect(bounties.length).toBeGreaterThan(0);
    expect(bounties[0].source).toBe("clawwork");
    expect(bounties[0].isWebhookTask).toBe(true);
  });

  test("TriageBatcher creates batched prompts with context management instructions", async () => {
    const batcher = new TriageBatcher();
    const mockTasks = [
      {
        id: "task_1",
        source: "agenthansa",
        title: "Fix Memory Leak",
        description: "Analyze node heap snapshot.",
        url: "https://example.com/1",
        bountyAmount: 4,
        complexity: "low" as const,
      },
      {
        id: "task_2",
        source: "clawwork",
        title: "Add Unit Tests",
        description: "Add tests for schema validation.",
        url: "https://example.com/2",
        bountyAmount: 3,
        complexity: "low" as const,
      }
    ];

    const prompt = batcher.createBatchedTaskPrompt("batch_test_123", mockTasks);
    expect(prompt).toContain("Batched Task Execution Plan: batch_test_123");
    expect(prompt).toContain("[CONTEXT FLUSH & SUMMARY]");
    expect(prompt).toContain("Sub-Goal 1: Fix Memory Leak");
    expect(prompt).toContain("Sub-Goal 2: Add Unit Tests");
    expect(prompt).toContain("/api/webhook/jules-completion");
  });

  test("DiscoveryPipeline filters by minUsd and maxUsd", async () => {
    const pipeline = new DiscoveryPipeline();
    const candidates = await pipeline.aggregateAll({ minUsd: 1, maxUsd: 5 });
    expect(candidates.length).toBeGreaterThan(0);
    for (const c of candidates) {
      const val = c.bountyAmount ?? (c as any).estimatedPayoutUsd ?? 0;
      expect(val).toBeGreaterThanOrEqual(1);
      expect(val).toBeLessThanOrEqual(5);
    }
  });
});
```

---

## Assistant

The unit test file has been created at [/Users/matt/projects/jules-burner/tests/discovery/agent_native.test.ts](file:///Users/matt/projects/jules-burner/tests/discovery/agent_native.test.ts).

---
