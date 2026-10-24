## 23:05 Usage per active hour

Asked: CA$ and tokens per active hour, per day, split by model/project, today vs 7-day avg, did the rate drop after the Sonnet default (Oct 23 19:24Z).

### Definition used
Active time = merged timeline of every user/assistant event across all sessions (Mountain time); gaps over 10 min count as idle; parallel sessions don't double-count. Rejected: counting only Matt's prompts (misses long agent runs he started).

### Cost method
Tokens from `~/.claude/projects` logs, deduped by request id, priced from CodexBar's pricing cache (1h cache writes at 2x input), USD to CAD at CodexBar's rate (1.413). Matches CodexBar's own daily totals to the cent for Oct 17-23.

### Result
7 days before switch: CA$26.58/h, 44.1 Mtok/h (44 h). Since switch: CA$20.70/h, 49.7 Mtok/h (4.5 h). Opus still 77% of spend since the switch. Only 4.5 h of data: suggestive, not proof.

### CodexBar menu
CodexBar is closed third-party; its menu can't take a chart without forking. Built a page instead: http://pages.test/usage-rate/ (local only, not deployed: personal data). Data refresh: `scripts/usage_rate_refresh.sh`.

### Undo
Delete `scripts/usage_rate*.{py,sh}` and `~/projects/pages/site/usage-rate`.
