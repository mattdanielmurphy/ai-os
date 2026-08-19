---
title: "Refactor Latency Statistics Module"
date: "2026-08-17"
conversation_id: "09fb33cb-b582-412d-8f62-93cabff4743b"
source: "antigravity"
---

# Refactor Latency Statistics Module

## User

Rewrite /Users/matt/projects/yt-highlight-reel/api/lib/latencyStats.js completely:
1. Do NOT import '@upstash/redis' or use CommonJS require. Use pure ES modules (`export class LatencyStats`, `export const latencyStats = new LatencyStats()`).
2. Read `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN` using `process.env` (with `.env.local` fallback if needed).
3. If redis URL and token exist, read via `fetch(\`\${redisUrl}/get/latency:\${key}\`, { headers: { Authorization: \`Bearer \${redisToken}\` } })` and write via `fetch(\`\${redisUrl}/set/latency:\${key}/\${encodeURIComponent(JSON.stringify(newEma))}\`, { headers: { Authorization: \`Bearer \${redisToken}\` } })`.
4. Catch all fetch errors gracefully and fallback to `this.ema` in-memory Map.
5. Provide methods:
  - `record(stage, model, promptTokens, completionTokens, wallMs, reasoningTokens = 0)`
  - `estimateWallMs(stage, model, expectedCompletionTokens = 400)`

---

## Assistant

The file `/Users/matt/projects/yt-highlight-reel/api/lib/latencyStats.js` has been completely rewritten to use pure ES modules, native `fetch` for Redis communication, and `process.env` for configuration. The in-memory `this.ema` map now serves as the fallback for any fetch errors.

---
