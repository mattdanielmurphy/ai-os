---
title: "Update `/Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/src/discovery/live_bounties.ts` using `write_to_file`:"
date: "2026-08-05"
conversation_id: "093273e8-8b35-4a95-8fe8-7e5ec3367025"
source: "antigravity"
---

# Update `/Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/src/discovery/live_bounties.ts` using `write_to_file`:

## User

Update `/Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/src/discovery/live_bounties.ts` using `write_to_file`:

Add `User-Agent: JulesBurner-Agent` header to GitHub API fetch, relax issue criteria to include open bounties with comments/discussion (checking `state === "open"` and `pull_request === undefined` and `locked === false`), and add `BOT_GITHUB_TOKEN` authorization if present in environment/config.

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

          const ghResponse = await fetch(`https://api.github.com/repos/${owner}/${repo}/issues/${issue_number}`, { headers });
          if (!ghResponse.ok) continue;
          const issue = await ghResponse.json();

          // Reject locked issues or issues already having open PRs
          if (issue.state === 'open' && issue.pull_request === undefined && !issue.locked) {
            results.push({
              title: item.title,
              url: item.url,
              projectName: item.project?.name || repo,
              organizationName: item.organization?.name || owner,
              owner,
              repo,
              rewardAmount: rewardUSD,
              issue_number: issue_number,
              body: issue.body || ""
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
