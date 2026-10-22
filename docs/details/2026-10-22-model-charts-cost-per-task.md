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

## 22:45 Email revised: link + chart code offer

Matt asked (via coordinator) to add https://www.mattmurphy.ca/projects/model-charts and say AA is welcome to use his 3D chart code. The original card text wasn't saved anywhere I could find, so I rewrote the email from the handoff's points (cost-per-task in free API; else weekly read with attribution or pay per call).

---

### Repo is private

model-charts on GitHub is private, so the email offers to send the code on request instead of linking it. Making it public would be Matt's call.

---

### No general contact address

AA's site only lists media@ and critpt@ addresses. No general/API inbox found, so the To field is left for Matt (their site contact form or media@ are the options).

---

### Mail not opened

claude-control returned "hammerspoon unreachable", so I didn't open Mail (opening apps needs clearance). Draft also saved at model-charts/tmp/aa-email.txt (gitignored).

## 22:50 Note on the public model-charts page

Matt sent the AA email and asked for a note on the page saying the chart isn't cost per task (so not very useful) and he's waiting on AA.

---

### Note under description

Added an optional `note` field to projects in mattmurphy.ca `src/data/projects.js`, rendered under the description in `src/pages/projects/[slug].js` as a muted paragraph with a thin left rule (existing `--muted` / `--card-border` vars, no new colours). Reusable for any project. Text: cost is price per 1M tokens, not cost per task; asked Artificial Analysis, waiting to hear back. Build passed and the static page contains the text. Pushed to main (Vercel deploys).

Undo: delete the `note:` line in projects.js.

---

### Follow-up

When AA replies, remove the note and implement per their answer (handoff 2026-10-22_relay-from-coordinator-session-cold.md).
