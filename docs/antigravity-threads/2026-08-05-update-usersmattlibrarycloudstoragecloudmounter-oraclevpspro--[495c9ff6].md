---
title: "Update `/Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/src/discovery/live_bounties.ts` using `write_to_file`:"
date: "2026-08-05"
conversation_id: "495c9ff6-ef9c-4375-845c-6c3a2ca096eb"
source: "antigravity"
---

# Update `/Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/src/discovery/live_bounties.ts` using `write_to_file`:

## User

Update `/Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/src/discovery/live_bounties.ts` using `write_to_file`:

Enhance bounty discovery to search BOTH Opire API AND live GitHub bounties via GitHub Search API (`q=bounty+is:issue+is:open`).

```typescript
import { config } from "../config";

export async function getLiveBounties() {
  const results: any[] = [];
  const seenUrls = new Set<string>();

  const token = process.env.BOT_GITHUB_TOKEN || process.env.PERSONAL_GITHUB_TOKEN || config.BOT_GITHUB_TOKEN || config.PERSONAL_GITHUB_TOKEN;
  const headers: Record<string, string> = {
    "User-Agent": "JulesBurner-Agent/1.0",
    "Accept": "application/vnd.github.v3+json",
  };
  if (token) {
    headers["Authorization"] = `token ${token}`;
  }

  // 1. Fetch GitHub issue search for active bounties
  try {
    const searchUrl = "https://api.github.com/search/issues?q=bounty+is:issue+is:open+no:assignee&sort=created&order=desc&per_page=15";
    const res = await fetch(searchUrl, { headers });
    if (res.ok) {
      const data = await res.json();
      for (const issue of data.items || []) {
        if (issue.locked || issue.pull_request) continue;
        if (seenUrls.has(issue.html_url)) continue;

        // Skip own repos or internal test repos
        if (issue.html_url.includes("mattdanielmurphy/")) continue;

        results.push({
          title: issue.title,
          url: issue.html_url,
          rewardAmount: 50, // default bounty score weight
          issue_number: String(issue.number),
          body: issue.body || ""
        });
        seenUrls.add(issue.html_url);
        if (results.length >= 10) break;
      }
    }
  } catch (e) {
    console.error("Error searching GitHub bounties:", e);
  }

  // 2. Fetch from Opire
  try {
    const response = await fetch("https://api.opire.dev/rewards");
    if (response.ok) {
      const opireData = await response.json();
      for (const item of opireData) {
        const rewardUSD = (item.pendingPrice?.value || 0) / 100;
        if (rewardUSD >= 5 && rewardUSD <= 1000) {
          if (seenUrls.has(item.url)) continue;
          results.push({
            title: item.title,
            url: item.url,
            rewardAmount: rewardUSD,
            issue_number: item.id || "opire",
            body: item.title
          });
          seenUrls.add(item.url);
          if (results.length >= 15) break;
        }
      }
    }
  } catch (error) {
    console.error("Error fetching from Opire:", error);
  }
  
  console.log(`Fetched ${results.length} verified live bounties`);
  return results;
}

if (import.meta.main) {
  const bounties = await getLiveBounties();
  console.log(JSON.stringify(bounties, null, 2));
}
```

---
