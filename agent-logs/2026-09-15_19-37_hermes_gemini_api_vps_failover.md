# Session Log: Hermes Gemini API Setup & Mac-to-VPS Failover

## Summary
Configured Hermes Agent on both Mac and Oracle VPS (oracle-vps) to use the official Google Gemini API (gemini-3.8-flash) as the primary orchestrator. Established a dynamic triage and cost-reduction protocol delegating heavy coding tasks to agymcp:agy (Antigravity subscription quota) and deep planning to query_aios.js. Configured a Caddy reverse proxy on the VPS to provide a single, seamless entrypoint for iPhone PWA with automatic failover between Mac and VPS.

## Key Changes
1. Mac Hermes Configuration:
   - Safely set GEMINI_API_KEY and GOOGLE_API_KEY in ~/.hermes/.env.
   - Updated ~/.hermes/config.yaml to use model.provider: gemini, model.default: gemini-3.8-flash, and agent.reasoning_effort: low.
   - Added aliases flash, flash-low, flash-med, flash-high.
   - Updated ~/.hermes/SOUL.md with three-tier triage: Tier 1 direct Gemini Flash, Tier 2 agy code delegation, Tier 3 query_aios planning.
   - Restarted hermes-webui and hermes-gateway via la restart.
2. Oracle VPS Setup:
   - Provisioned Hermes Agent and Hermes WebUI on oracle-vps.
   - Synchronized config.yaml, SOUL.md, and Gemini API keys.
   - Bootstrapped WebUI under PM2 on 127.0.0.1:8788.
3. Caddy Failover Proxy:
   - Configured :8787 on oracle-vps to reverse proxy to 100.106.59.25:8787 (Mac) with health check fallback to 127.0.0.1:8788 (VPS local).
   - Tested and verified live failover and automatic recovery.
4. Project Board:
   - Marked task completed in PROJECT_BOARD.md.
