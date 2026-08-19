---
title: "Here is the full codebase for jules-burner, a TypeScript/Bun daemon running on..."
date: "2026-08-14"
conversation_id: "f4b1e4f1-c839-44fc-9971-8824a2decb66"
source: "antigravity"
---

# Here is the full codebase for jules-burner, a TypeScript/Bun daemon running on...

## User

Here is the full codebase for `jules-burner`, a TypeScript/Bun daemon running on a Linux VPS designed to automate task discovery (bounties, open-source issues, internal self-tasks) and dispatch them to Google Jules CLI (100 daily quota cap).

### Core Problem:
The system has stalled and hasn't successfully solved a real bounty end-to-end. We need to strip away any fragility and get a simple, foolproof, end-to-end workflow working immediately.

### Critical System Context:
1. **Deployment**: Runs on an Oracle VPS via PM2 (`~/.bun/bin/pm2`, ID 0). Local mount is SSHFS.
2. **Jules CLI**: Authenticated to `mattdanielmurphy` on the VPS. When given an authorized repo (e.g. `mattdanielmurphy/jules-burner`), `jules remote new --repo <repo> --session <prompt>` immediately spawns a VM session.
3. **Bot Account**: Upstream PRs should be submitted via the bot account (`BOT_GITHUB_TOKEN`) to avoid polluting the personal profile.
4. **Current Bottlenecks**:
- Discovery hitting GitHub secondary search rate limits (HTTP 403).
- Silent CLI failure parsing (exitCode 0 on errors, causing phantom session dispatches).
- Incomplete fork-to-PR lifecycle for external bounties.
- Lack of a solid, single end-to-end verification test on a live bounty.

### Goal:
Provide a robust, step-by-step plan of attack to:
1. Execute a single, real, dead-simple bounty/issue end-to-end (discovery -> fork -> Jules dispatch -> status polling -> diff validation -> bot PR submission).
2. Bulletproof the daemon loop against stalls, rate limits, and fake dispatches.

---

## Assistant

## Perplexity — 03:24 PM

Your codebase already has all the pieces (discovery pipelines, `JulesCLI`, `Dispatcher`, `Throttler`, `AuditDatabase`, `HealthMonitor`, staging fork/PR gate) — the problem is that none of them have been forced through one real, observed, end-to-end bounty, so the failure modes (fake dispatches, 403s, incomplete fork→PR path) have never been caught in the one place that matters. Below is a concrete plan to fix that, based on your actual `julescli.ts`, `dispatcher.ts`, `throttler.ts`, and `healthmonitor.ts` implementations.
jules_burner_context.md

Root Cause of Each Bottleneck
Bottleneck	Where it lives	Why it happens
Secondary rate limit 403	Discovery providers (`microbounties.ts`, `livebounties.ts`, `opire.ts`)	GitHub search API has a much lower secondary limit (~30 req/min) than core; multiple providers likely fire unthrottled, unauthenticated or bursty searches 
jules_burner_context.md

Silent exitCode-0 failures	`JulesCLI.parseResult()` in `julescli.ts`	`success = exitCode === 0` is the *only* success gate — it never checks stdout/stderr for CLI-level error strings (auth expired, repo not authorized, quota exceeded), so a "successful" process exit with an error message in stdout still returns `success: true` and gets recorded as a real dispatch 
jules_burner_context.md

Incomplete fork→PR lifecycle	`ForkManager` / `UpstreamGate` (`staging/*`)	These exist but the trace shows they were built for the *staging* self-improvement loop, not verified against a real external repo fork → Jules session → diff → bot-token PR path 
jules_burner_context.md

No live E2E test	Never run	All 70+ tests are unit/mocked; zero tests exercise the real `jules` binary, a real GitHub fork, and a real PR
Step 1: Kill Silent Failures First

Nothing else matters until you can trust a "success" result. In `julescli.ts`, `parseResult()` must fail closed:

Treat exitCode 0 as success **only if** stdout/stderr do not match an error-signature list: `/unauthorized|not authorized|permission denied|quota exceeded|failed to create session|login required|error:/i`.

Require a real `sessionId` match (`sess-[a-zA-Z0-9-]+` or an explicit `ID:` line) — if exitCode is 0 but no sessionId is extracted, treat it as `success: false, reason: "no session id parsed"` rather than falling back to a synthetic `sess-${Date.now()}` id. Right now `remoteNew`/supervisory code fabricates a fake session ID (`sess${Date.now()}`) whenever parsing fails — this is exactly the "phantom dispatch" bug. Fabricated IDs should never be recorded as `DISPATCHED` in `AuditDatabase`.

Add a `verifySessionExists(sessionId)` call immediately after `remoteNew` via `julesCLI.getStatus(sessionId)` — only commit the dispatch to `throttler.recordDispatch` / `auditDb.insertDispatchedTask` after that verification succeeds. This turns dispatch into a two-phase commit instead of trust-on-exit-code.

Step 2: Fix the GitHub 403s Before Touching Discovery Volume

You have `RateLimitManager` already tracking bot/personal search quotas — the bug is providers aren't respecting it before firing:

Route every GitHub search call (microbounties, livebounties) through a single `rateLimitManager.acquireSearchSlot(account)` gate that blocks/queues when `search.remaining` is near 0, rather than each provider independently hitting the API.

Add exponential backoff specifically on `403` with `X-RateLimit-Remaining: 0` (secondary limits often return 403, not 429) — catch that distinctly from auth 403s.

Drop concurrent provider fan-out to sequential with a fixed delay (2–3s) between search calls during the E2E test phase. Parallelism can come back once quota headroom is proven.

Step 3: One Real Bounty, End-to-End, Manually Gated

Do this as a scripted, observable, one-shot run — not inside the daemon loop yet.

**Pick the target manually.** Don't trust discovery yet. Pick one known-good, tiny, well-scoped GitHub issue (ideally on `mattdanielmurphy/jules-burner` itself or another repo you own, to avoid fork/PR permission surprises on the first pass) — a real external bounty repo only after this dry run succeeds.

**Fork.** Call `ForkManager.prepareStagingFork` (or its real fork equivalent) against the actual target repo, using the bot token (`BOT_GITHUB_TOKEN`), and print/verify the resulting repo URL exists via `octokit.repos.get` before proceeding — don't assume the fork call succeeded.

**Dispatch to Jules.** Call `julesCLI.remoteNew(forkedRepo, promptPath)` directly (bypass `Dispatcher.runSingleTask` for this manual run), capture raw stdout/stderr to a file, and manually eyeball it for the actual session ID and any error text.

**Poll, don't assume.** Loop `julesCLI.getStatus(sessionId)` every 60s with a hard timeout (e.g. 30 min) and log every raw response. Treat "Completed" string match plus non-empty diff as the only success condition.

**Diff validation.** Run `julesCLI.pullSession(sessionId, apply=true)` into a scratch branch, then run your `StagingValidator` checks (no deleted critical files, no secrets, tests pass) on the actual diff — not mocked input.

**Bot PR.** Only if steps 4–5 pass, call `UpstreamGate`'s PR creation using `BOT_GITHUB_TOKEN` explicitly (verify `octokit.rest.users.getAuthenticated()` returns the bot account first) and print the resulting PR URL.

**Record.** Log every step's raw output to a single markdown file (`agent-logs/e2e-verification-<date>.md`) so you have a permanent, non-hallucinated proof artifact — same pattern as your existing `periodic_summary_notifier.py` zero-hallucination approach.
jules_burner_context.md

Do not let this run touch `Throttler`/quota accounting or the live daemon state — run it as an isolated script so a bug can't corrupt `data/state.json`.

Step 4: Bulletproof the Daemon Loop Only After Step 3 Succeeds

Once one real PR exists end-to-end, harden the loop itself:

**Two-phase dispatch commit** (per Step 1) becomes the default in `Dispatcher.runSingleTask`.

**Circuit breaker on discovery**: if `DISCOVERY_EMPTY` or `403` friction fires N times in a row, pause the loop and alert via Photon rather than looping silently — `HealthMonitor.getBackoffMs()` already has escalating backoff (1min → 10min → 30min); wire it into `startLoop`'s sleep, not just health checks.

**Stuck-session sweep**: use `AuditDatabase.getHeldUpTasks()` on every loop tick to detect sessions stuck in `DISPATCHED`/`IN_PROGRESS` beyond a timeout, and either re-poll or mark `FAILED` — right now nothing seems to actively resolve these.

**Single-writer quota lock**: since PM2 could restart mid-write, ensure `Throttler.saveState()` writes atomically (write to temp file, rename) so a crash mid-dispatch can't corrupt `state.json` and cause double counting.

**Kill the supervisory self-improvement cadence** (every 10 tasks) until the external bounty path is proven — it's currently competing for quota and attention with the actual goal, and is a likely reason you're stalled on "solving a real bounty" versus polishing the daemon itself.

The core discipline shift: stop letting the daemon self-verify. Every dispatch, fork, and PR in this first pass should be confirmed against a real external signal (actual GitHub API response, actual Jules session status string) rather than trusting internal exit codes or synthesized IDs.

---

## User

So in investigation, I believe we should be using something OTHER than GitHub issues for bounties. I think GitHub is more manual, slow, and bounties START at $5.
I think given that this is intended to be run without human supervision, we shouldn't try to do anything bounty that's like over a dollar for now. Micro-bounties should be quicker, more reliable.
We only want to make like a $1 CAD a day right now.
Am I right?
Idk if you saw but I tried to add support for other marketplaces, and I hooked up an Alby acct. Although I realized my Alby doesn't have a wallet attached.

---

## Assistant

## Perplexity — 03:24 PM

Yes — you're basically right, and the data backs you up strongly. Here's the breakdown with real numbers.

Bounty Floors Confirm Your Instinct
Platform	Real minimum	Why it doesn't fit "$1/day, unsupervised"
GitHub issues (raw)	No formal floor, but `label:bounty` issues via Algora bots typically $50-200+ realistically, and require human maintainer review before merge/payout 
dev
	
Algora	API technically allows $0.50 minimum 
api.docs.algora
, but dashboard-recommended/realistic bounties are $100+ and most listed ones are $50-500+ 
deepwiki
+1
	
Opire	Hard floor of **$20** — explicitly documented as their minimum "given the effort and time" expected 
docs.opire
+1
	
Nostr DVM (NIP-90)	**No minimum** — sat-denominated, market-set by whoever posts the job	

So GitHub/Algora/Opire bounties are priced (and reviewed) for actual human-quality work, not unsupervised micro-automation. Trying to unsupervised-solve a $20+ Opire bounty or a $50+ Algora one is a mismatch — those require real review scrutiny to get paid, which is exactly where your "stalled, never solved one end-to-end" problem comes from. Nostr DVM jobs are the only source in your stack actually designed for sub-dollar, machine-matched, instantly-settled micro-work .

Your Code Already Half-Agrees With You

`DiscoveryPipeline.aggregateAll()` in `discovery/pipeline.ts` already filters everything down to `amount < 1.00` before ranking . The problem: given the real floors above, that filter guarantees Algora, Opire, and TaskMarket almost never pass through — you're left with only the hardcoded GitHub fallback task (`$0.50`, not a real bounty) and whatever Nostr DVM surfaces. So the daemon has effectively been trying to run on a source (GitHub fallback stub) that isn't a real bounty at all, while the one source that *actually* fits your economics (Nostr DVM, sat-bid based, no review gate) is a secondary pipeline that's never been the focus.

**Recommendation:** stop trying to make GitHub/Algora/Opire work at sub-$1 — their business model assumes real review. Make `NostrDvmClient`/`NostrPipeline` the primary discovery source for the "$1 CAD/day, zero supervision" phase, and demote the dollar-bounty platforms to a later phase once you have staging validation actually proven and are willing to target $20+ jobs that survive human review.

The Alby Wallet Issue

Your `LightningWallet.ts` calls Alby's invoice API (`api.getalby.com/invoices`) using `ALBY_API_TOKEN` — but that endpoint needs a wallet with actual receiving capability behind the token, not just an Alby *account*. A bare signup alone doesn't give you that:

**Fastest fix**: create a **Lightning Address** on your Alby account (getalby.com → Lightning Address) — this alone enables custodial receiving without needing a funded channel or self-custodial node.
jules_burner_context.md
blog.getalby

**Fuller fix** (if you also want to self-custody/spend): set up **Alby Hub**, open a Lightning channel, and top up a balance — this is the self-custodial path and is more setup than you need just to receive sat-sized DVM payments.
blog.getalby
+1

After either, regenerate/verify your `ALBY_API_TOKEN` is scoped to `invoices:create` against that funded/linked wallet, not just the bare account.

For your use case (receiving tiny sat amounts from Nostr DVM job payers), the Lightning Address route is enough — you don't need a full Hub with channels just to receive.

Net Recommendation

Set daily target to Nostr DVM micro-jobs only for now — genuinely no-minimum, no-review, Lightning-settled, matches "$1 CAD/day, unsupervised" perfectly.

Fix Alby by adding a Lightning Address to the account (skip Hub/channels unless you want to hold/spend funds later).

Keep the Algora/Opire/TaskMarket/GitHub pipelines in the code but gate them behind a config flag disabled for this phase — their $20-100+ floors and human review requirement are the wrong shape for an unsupervised $1/day system, and reactivating them prematurely is likely part of why nothing has closed end-to-end yet.

Re-run the Step 3 "one real end-to-end" verification plan from before, but target a Nostr DVM job instead of a GitHub bounty — much shorter loop (no fork/PR lifecycle needed at all, since DVM jobs often just need the output event, not a PR).

---

## User

I've got a lightning address; I don't need the hub thing then?

---

## Assistant

## Perplexity — 03:24 PM

Not quite — a lightning address by itself is just an identifier; it has to be "powered by" an actual wallet behind it to receive real payments. Per Alby's own docs: **"Alby Account = Lightning Address service at getalby.com (powered by connected wallet)"**. If you created the address but never linked a wallet, invoices to it will fail or just never settle.
guides.getalby

What "wallet attached" actually means here

Alby shut down its old custodial shared wallet in **January 2025** and moved everyone to **Alby Hub**, a self-custodial Lightning node (self-hosted or their $9.90/mo cloud option).
ln

A lightning address you create today needs to be linked to *some* wallet to actually receive — that's normally Alby Hub, but it can be any NWC-compatible wallet, not necessarily Alby's own.
github
+1

Without that link: "❌ No lightning address (must create invoice for each payment)" is literally Alby's own warning for accounts with no wallet connected .

So yes, you do need *a* wallet behind the address — but it doesn't have to be the full "run your own node, open channels, manage liquidity" version of Hub. Alby's cloud-hosted Hub option handles the node/channel management for you; you just top it up.

Bigger problem: your code is calling a deprecated endpoint

Separately from the wallet issue — your `LightningWallet.ts` calls `POST https://api.getalby.com/invoices` with `invoices:create` scope . That's the **old, deprecated Alby Wallet API** tied to the custodial wallet Alby discontinued in Jan 2025. Even once you attach a wallet, this specific call may not work reliably anymore.
ln
+1

**Better fix**: switch to the **Lightning Address / LNURL invoice proxy**, which works directly off any lightning address + amount, with no legacy wallet-API scope required:


```
text
GET https://api.getalby.com/lnurl/generate-invoice?ln=<youraddress>@getalby.com&amount=<millisats>
```


This is the modern, documented path for "generate an invoice for a known lightning address" — it's simpler than your current `LightningWallet.generateInvoice()` and doesn't depend on the deprecated wallet token scope at all.
jules_burner_context.md
guides.getalby

Recommended path

Link your existing lightning address to a wallet — cheapest/fastest is Alby's cloud-hosted Hub option, top it up with a small amount of sats (even a few dollars' worth covers your $1/day CAD target for a while) .

Rewrite `LightningWallet.generateInvoice()` in your codebase to call the `lnurl/generate-invoice` proxy against your address instead of the deprecated `POST /invoices` endpoint.

Verify with the manual curl test Alby's own docs suggest: `curl -sL "https://api.getalby.com/lnurl/generate-invoice?ln=<address>&amount=200000" | jq` — if that returns a valid BOLT11 invoice, your receiving path is confirmed working end-to-end before you wire it back into the daemon 
guides.getalby
.

---

## User

I want to set up Hub; I'll do self-hosted on my VPS.
So add that to the todo list.
Create an implementation plan for me. My agent knows how to access my VPS and set things up, in fact that's where the whole project lives anyway

---

## Assistant

## Perplexity — 03:24 PM

Good call going self-hosted — since your agent already manages the VPS, this slots right into the existing workflow. I've put together the full plan as a file: **alby-hub-selfhosted-implementation-plan.md**.

Key decisions baked into the plan

**Backend choice: Bark, not LDK.** Alby Hub added a Bark backend in mid-2026 that has **zero channel/liquidity management** — no opening channels, no inbound liquidity headaches, no force-closure risk. Given your goal is a completely unsupervised system moving sub-dollar amounts, this is a much better fit than the traditional LDK backend, which needs an LSP channel opened before you can receive anything meaningfully .
blog.second

**Minimum specs are trivial.** Official requirement is just 512MB RAM (1GB recommended) + swap and 1GB disk — your Oracle VPS almost certainly already clears this since it's running the whole daemon stack.
paulscode
+1

**Security: don't expose port 8080 publicly.** Bind the Hub's web UI to localhost and reuse the same Tailscale pattern you already use for the Mission Control dashboard (`100.123.57.17:4242`), rather than opening a new public port on a wallet-holding service.

**Fix the actual code bug too, not just the wallet.** Your `LightningWallet.ts` currently calls the deprecated custodial `POST /invoices` endpoint , which Alby discontinued in Jan 2025 . The plan replaces it with a proper **NWC connection** (`nostr+walletconnect://`) scoped to only `make_invoice`/`lookup_invoice` — least privilege, so the daemon can create and check invoices but never spend funds even if compromised.

What's in the plan file

7 phases: pre-flight checks → backend choice → Docker deploy → network/security → linking your existing lightning address → rewiring `wallet.ts` to NWC → one real end-to-end payment verification — plus a ready-to-paste backlog entry for your Kanban board.

## Perplexity — 03:24 PM

Alby Hub (Self-Hosted) — Implementation Plan for jules-burner VPS

**Goal:** Run a self-custodial Lightning node (Alby Hub) on the Oracle VPS to back the existing lightning address, replace the deprecated Alby Wallet API call in `src/lightning/wallet.ts`, and give the daemon a real, working receive path for Nostr DVM micro-payments.

Phase 0: Pre-flight Checks

Confirm VPS specs meet minimum: 512MB RAM (1GB+ recommended), 1GB+ swap, 1GB+ free disk, Docker-capable [source: getAlby/hub docs].

Confirm Docker + Docker Compose are installed on the VPS (`docker --version`, `docker compose version`); install if missing (`apt install docker.io docker-compose-plugin`).

Confirm which ports are already in use — PM2/dashboard uses 4242; Hub Web UI will use 8080; avoid collisions.

Back up `data/state.json` and `data/audit.db` before touching anything (unrelated services, but same host).

Phase 1: Choose a Lightning Backend

Two viable backends for Alby Hub — pick based on how much you want to manage:

Backend	Channel management	Fits "$1 CAD/day, no supervision"	Notes
**LDK (default)**	Manual/JIT channels via an LSP (e.g. Megalith, Olympus)	OK, but JIT channel opens incur one-time on-chain-ish fees	Standard, most documented
**Bark** (newer, recommended)	**No channels, no liquidity management at all**	Best fit — zero ops overhead	Newer, added mid-2026; simplest for a hands-off daemon

**Recommendation:** Use **Bark backend** — since the whole point is unsupervised operation and you're only moving sub-dollar amounts, channel liquidity management is unnecessary overhead and risk (force-closures, fee spikes, needing manual top-ups).

Phase 2: Deploy Alby Hub on the VPS

```
bash
ssh -i ~/.ssh/Oracle-Minecraft-Server-SSH.key ubuntu@40.233.124.200
mkdir -p ~/albyhub && cd ~/albyhub
```


Create `docker-compose.yml` (Bark variant — no separate LSP/channel container needed):


```
text
services:
  albyhub:
    container_name: albyhub
    image: ghcr.io/getalby/hub:latest
    volumes:
      - ./albyhub-data:/data
    ports:
      - "127.0.0.1:8080:8080"   # bind to localhost only — see Phase 3
    environment:
      - WORK_DIR=/data
      - LN_BACKEND_TYPE=BARK
    stop_grace_period: 300s
    restart: unless-stopped
```


```
bash
docker compose up -d
docker compose logs -f   # watch until "listening on :8080"
```


If Bark isn't stable enough yet on your Hub version, fall back to LDK + JIT channels via an LSP (Megalith/Olympus) — no manual channel opening required either way.

Phase 3: Network & Security

**Do not expose port 8080 publicly.** Bind it to `127.0.0.1` (as above) and access the setup wizard/dashboard exactly the way you already access the jules-burner Mission Control dashboard — via **Tailscale** (same pattern as `100.123.57.17:4242`) or an SSH tunnel:


```
bash
ssh -L 8080:localhost:8080 -i ~/.ssh/Oracle-Minecraft-Server-SSH.key ubuntu@40.233.124.200
```


then open `http://localhost:8080` locally.

If you end up on the LDK backend, port `9735` (Lightning P2P) needs to be open to the public internet in the Oracle Cloud security list / VPS firewall (`ufw allow 9735/tcp`) — Bark backend does not need this.

Run through the Hub setup wizard once: set an unlock password, **write down and securely store the recovery phrase somewhere off the VPS** (password manager, not a file on the server).

Phase 4: Link Your Existing Lightning Address

In the Hub dashboard, go to the Alby Account link/connect flow and attach your existing `getalby.com` lightning address to this Hub instance as its backing wallet.

Confirm receive works: from the Hub UI, generate a small test invoice and pay it from any other wallet, or ask someone to send a few sats to your address — verify balance updates in the Hub dashboard.

Phase 5: Wire jules-burner to the Hub via NWC (Replace Deprecated API Call)

Your current `src/lightning/wallet.ts` calls the deprecated `POST https://api.getalby.com/invoices` endpoint. Replace it with a **Nostr Wallet Connect (NWC)** client pointed at this self-hosted Hub:

In the Hub dashboard, create a new NWC connection scoped to **`make_invoice` and `lookup_invoice` only** (least privilege — do not grant `pay_invoice` to the daemon).

Copy the resulting `nostr+walletconnect://...` connection string.

Add it to `.env` as an empty placeholder per your existing secrets protocol, then have yourself fill in the real value directly on the VPS:


```
text
ALBY_NWC_URL=
```


Rewrite `LightningWallet`:

Add `@getalby/sdk` (NWC client) as a dependency.

`generateInvoice(amountSats, memo)` → `nwcClient.makeInvoice({ amount: amountSats, description: memo })`.

`checkPaymentStatus(paymentHash)` → `nwcClient.lookupInvoice({ payment_hash: paymentHash })`, check `settled_at`.

Remove the old `ALBY_API_TOKEN` fetch calls entirely.

Phase 6: Integration & Health Checks

Add a Hub liveness check to `HealthMonitor` (same pattern as Jules CLI auth check) — call `nwcClient.getInfo()` on an interval; if it fails, flag `needsHumanIntervention` with a clear reason (e.g. "Alby Hub unreachable — check Docker container on VPS").

Wire `NostrPipeline`/`NostrDvmClient` job completions to call `LightningWallet.generateInvoice()` for payment requests, and log settlement into `AuditDatabase` so completed DVM jobs show real revenue in the dashboard.

Add a cron or PM2-adjacent job to back up `~/albyhub/albyhub-data` off the VPS periodically (rclone to the same remote you already use for the SSHFS mount) — losing this directory loses wallet funds.

Phase 7: One Real End-to-End Verification

Post or accept one real, tiny Nostr DVM job.

Confirm the daemon calls `generateInvoice`, gets a valid BOLT11 string back from the Hub (not a mock/fallback).

Confirm the payer settles it and `checkPaymentStatus` correctly reports `settled: true`.

Log this as your first real proof-of-revenue entry in `agent-logs/`.

Backlog / Todo Entry

Add to `agent-logs/KANBANBOARD.md` (or wherever the active backlog lives):

**[BACKLOG] Self-host Alby Hub on VPS for lightning receive path**

Deploy Alby Hub (Bark backend) via Docker Compose on Oracle VPS

Bind Web UI to localhost, access via Tailscale/SSH tunnel only

Link existing lightning address to the Hub

Replace deprecated `POST /invoices` call in `src/lightning/wallet.ts` with NWC (`make_invoice`/`lookup_invoice` scoped only)

Add Hub liveness check to `HealthMonitor`

Back up `albyhub-data` off-VPS on a schedule

Run one real end-to-end DVM job payment as verification

## Perplexity — 03:24 PM

Alby Hub (Self-Hosted) — Implementation Plan for jules-burner VPS

**Goal:** Run a self-custodial Lightning node (Alby Hub) on the Oracle VPS to back the existing lightning address, replace the deprecated Alby Wallet API call in `src/lightning/wallet.ts`, and give the daemon a real, working receive path for Nostr DVM micro-payments.

Phase 0: Pre-flight Checks

Confirm VPS specs meet minimum: 512MB RAM (1GB+ recommended), 1GB+ swap, 1GB+ free disk, Docker-capable [source: getAlby/hub docs].

Confirm Docker + Docker Compose are installed on the VPS (`docker --version`, `docker compose version`); install if missing (`apt install docker.io docker-compose-plugin`).

Confirm which ports are already in use — PM2/dashboard uses 4242; Hub Web UI will use 8080; avoid collisions.

Back up `data/state.json` and `data/audit.db` before touching anything (unrelated services, but same host).

Phase 1: Choose a Lightning Backend

Two viable backends for Alby Hub — pick based on how much you want to manage:

Backend	Channel management	Fits "$1 CAD/day, no supervision"	Notes
**LDK (default)**	Manual/JIT channels via an LSP (e.g. Megalith, Olympus)	OK, but JIT channel opens incur one-time on-chain-ish fees	Standard, most documented
**Bark** (newer, recommended)	**No channels, no liquidity management at all**	Best fit — zero ops overhead	Newer, added mid-2026; simplest for a hands-off daemon

**Recommendation:** Use **Bark backend** — since the whole point is unsupervised operation and you're only moving sub-dollar amounts, channel liquidity management is unnecessary overhead and risk (force-closures, fee spikes, needing manual top-ups).

Phase 2: Deploy Alby Hub on the VPS

```
bash
ssh -i ~/.ssh/Oracle-Minecraft-Server-SSH.key ubuntu@40.233.124.200
mkdir -p ~/albyhub && cd ~/albyhub
```


Create `docker-compose.yml` (Bark variant — no separate LSP/channel container needed):


```
text
services:
  albyhub:
    container_name: albyhub
    image: ghcr.io/getalby/hub:latest
    volumes:
      - ./albyhub-data:/data
    ports:
      - "127.0.0.1:8080:8080"   # bind to localhost only — see Phase 3
    environment:
      - WORK_DIR=/data
      - LN_BACKEND_TYPE=BARK
    stop_grace_period: 300s
    restart: unless-stopped
```


```
bash
docker compose up -d
docker compose logs -f   # watch until "listening on :8080"
```


If Bark isn't stable enough yet on your Hub version, fall back to LDK + JIT channels via an LSP (Megalith/Olympus) — no manual channel opening required either way.

Phase 3: Network & Security

**Do not expose port 8080 publicly.** Bind it to `127.0.0.1` (as above) and access the setup wizard/dashboard exactly the way you already access the jules-burner Mission Control dashboard — via **Tailscale** (same pattern as `100.123.57.17:4242`) or an SSH tunnel:


```
bash
ssh -L 8080:localhost:8080 -i ~/.ssh/Oracle-Minecraft-Server-SSH.key ubuntu@40.233.124.200
```


then open `http://localhost:8080` locally.

If you end up on the LDK backend, port `9735` (Lightning P2P) needs to be open to the public internet in the Oracle Cloud security list / VPS firewall (`ufw allow 9735/tcp`) — Bark backend does not need this.

Run through the Hub setup wizard once: set an unlock password, **write down and securely store the recovery phrase somewhere off the VPS** (password manager, not a file on the server).

Phase 4: Link Your Existing Lightning Address

In the Hub dashboard, go to the Alby Account link/connect flow and attach your existing `getalby.com` lightning address to this Hub instance as its backing wallet.

Confirm receive works: from the Hub UI, generate a small test invoice and pay it from any other wallet, or ask someone to send a few sats to your address — verify balance updates in the Hub dashboard.

Phase 5: Wire jules-burner to the Hub via NWC (Replace Deprecated API Call)

Your current `src/lightning/wallet.ts` calls the deprecated `POST https://api.getalby.com/invoices` endpoint. Replace it with a **Nostr Wallet Connect (NWC)** client pointed at this self-hosted Hub:

In the Hub dashboard, create a new NWC connection scoped to **`make_invoice` and `lookup_invoice` only** (least privilege — do not grant `pay_invoice` to the daemon).

Copy the resulting `nostr+walletconnect://...` connection string.

Add it to `.env` as an empty placeholder per your existing secrets protocol, then have yourself fill in the real value directly on the VPS:


```
text
ALBY_NWC_URL=
```


Rewrite `LightningWallet`:

Add `@getalby/sdk` (NWC client) as a dependency.

`generateInvoice(amountSats, memo)` → `nwcClient.makeInvoice({ amount: amountSats, description: memo })`.

`checkPaymentStatus(paymentHash)` → `nwcClient.lookupInvoice({ payment_hash: paymentHash })`, check `settled_at`.

Remove the old `ALBY_API_TOKEN` fetch calls entirely.

Phase 6: Integration & Health Checks

Add a Hub liveness check to `HealthMonitor` (same pattern as Jules CLI auth check) — call `nwcClient.getInfo()` on an interval; if it fails, flag `needsHumanIntervention` with a clear reason (e.g. "Alby Hub unreachable — check Docker container on VPS").

Wire `NostrPipeline`/`NostrDvmClient` job completions to call `LightningWallet.generateInvoice()` for payment requests, and log settlement into `AuditDatabase` so completed DVM jobs show real revenue in the dashboard.

Add a cron or PM2-adjacent job to back up `~/albyhub/albyhub-data` off the VPS periodically (rclone to the same remote you already use for the SSHFS mount) — losing this directory loses wallet funds.

Phase 7: One Real End-to-End Verification

Post or accept one real, tiny Nostr DVM job.

Confirm the daemon calls `generateInvoice`, gets a valid BOLT11 string back from the Hub (not a mock/fallback).

Confirm the payer settles it and `checkPaymentStatus` correctly reports `settled: true`.

Log this as your first real proof-of-revenue entry in `agent-logs/`.

Backlog / Todo Entry

Add to `agent-logs/KANBANBOARD.md` (or wherever the active backlog lives):

**[BACKLOG] Self-host Alby Hub on VPS for lightning receive path**

Deploy Alby Hub (Bark backend) via Docker Compose on Oracle VPS

Bind Web UI to localhost, access via Tailscale/SSH tunnel only

Link existing lightning address to the Hub

Replace deprecated `POST /invoices` call in `src/lightning/wallet.ts` with NWC (`make_invoice`/`lookup_invoice` scoped only)

Add Hub liveness check to `HealthMonitor`

Back up `albyhub-data` off-VPS on a schedule

Run one real end-to-end DVM job payment as verification

---
