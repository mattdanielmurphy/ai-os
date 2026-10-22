# Model charts: cost per task

## 19:05 Swap per-1M price for cost per task

Asked (via coordinator): replace per-1M-token cost on model charts with cost per task, update weekly refresh, push live, save the rule.

---

### Free API lacks it

Artificial Analysis free API (`/api/v2/data/llms/models`) returns only `price_1m_*` pricing, speed, TTFT and evals. No cost per task, no tokens per task. Checked the live data/aa-api.json and the API reference page.

---

### Terms block scraping

AA Terms of Use (artificialanalysis.ai/docs/legal/Terms-of-Use.pdf): no scraping/automated queries of the Site, and no part of the Site may be copied, republished or displayed. The existing private CSV (17 Claude rows, scraped 2026-10-20) was already kept off the public site for this reason. A weekly scraper + public cost per task would break both clauses.

---

### What was done

- Private charts already default to cost per task (specs/default.json, ask.ts).
- Added CLAUDE.md in model-charts with the rule + the terms limit (commit d00fde5).
- Public charts NOT changed: they still use price per 1M tokens, because removing it with no replacement leaves them with no cost axis.

---

### Options for Matt

1. Ask AA for permission / commercial API (email; needs his OK to send).
2. Epoch AI Benchmarking Hub (CC BY per secondary sources, unverified): different metric (cost to reach a score), would be a rebuild.
3. Drop cost from public charts entirely (score vs speed only).

Undo: git revert d00fde5 in model-charts.
