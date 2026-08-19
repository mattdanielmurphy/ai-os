---
title: "Update `/Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/src/discovery/live_bounties.ts` using `write_to_file` tool:"
date: "2026-08-05"
conversation_id: "ba921aef-895b-4516-a0ec-7f10b7d1686e"
source: "antigravity"
---

# Update `/Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/src/discovery/live_bounties.ts` using `write_to_file` tool:

## User

Update `/Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/src/discovery/live_bounties.ts` using `write_to_file` tool:

Change the price check filter in `getLiveBounties()` from:
`if (rewardUSD >= 5 && rewardUSD <= 50)`
to:
`if (rewardUSD >= 5 && rewardUSD <= 1000)`

Also update `item.url.split("/")` logic to cleanly extract issue_number and handle repository details, and ensure fallback for item.pendingPrice values.

Contents of `src/discovery/live_bounties.ts`:
```typescript
import { config } from "../config";

export async function getLiveBounties() {
  const results: any[] = [];
  const seenUrls = new Set<string>();

  try {
    const response = await fetch("https://api.opire.dev/rewards");
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const opireData = await response.json();

    for (const item of opireData) {
      const rewardUSD = (item.pendingPrice?.value || 0) / 100;
      if (rewardUSD >= 5 && rewardUSD <= 1000) {
        if (seenUrls.has(item.url)) continue;

        try {
          const urlParts = item.url.split("/");
          const owner = urlParts[3];
          const repo = urlParts[4];
          const issue_number = urlParts[6];

          if (!owner || !repo || !issue_number) continue;

          const ghResponse = await fetch(`https://api.github.com/repos/${owner}/${repo}/issues/${issue_number}`);
          if (!ghResponse.ok) continue;
          const issue = await ghResponse.json();

          if (issue.state === 'open' && issue.pull_request === undefined) {
            results.push({
              title: item.title,
              url: item.url,
              projectName: item.project?.name || repo,
              organizationName: item.organization?.name || owner,
              owner,
              repo,
              rewardAmount: rewardUSD,
              issue_number: issue_number
            });
            seenUrls.add(item.url);
          }
        } catch (e) {
          console.error(`Error verifying issue ${item.url}:`, e);
        }
      }
      if (results.length >= 10) break;
    }
    console.log(`Fetched ${results.length} verified live bounties from Opire`);
  } catch (error) {
    console.error("Error fetching from Opire:", error);
  }
  
  return results;
}

if (import.meta.main) {
  const bounties = await getLiveBounties();
  console.log(JSON.stringify(bounties, null, 2));
}
```

---
