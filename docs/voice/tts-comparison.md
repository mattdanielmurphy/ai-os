# TTS comparison (rebuilt 2026-10-29)

The Oct 22–24 table wasn't saved anywhere searchable (only a ranked-list summary in the Oct 24 relay thread), so this is rebuilt from the [Artificial Analysis TTS leaderboard](https://artificialanalysis.ai/text-to-speech/leaderboard), fetched 2026-10-29. Elo = blind listener preference. Latency isn't in the leaderboard table; the Oct 24 check found AA's latency numbers unreliable, so it's left out.

| Rank | Model (maker) | Elo | $ / 1M chars |
|---|---|---|---|
| 1 | Eleven v4 Turbo (ElevenLabs) | 1336 | $40 |
| 2 | Eleven v4 (ElevenLabs) | 1334 | $80 |
| 3 | Qwen-Audio-3.1-TTS-Plus (Alibaba) | 1305 | $19.3 |
| 4 | Sonic 3.6 (Cartesia) | 1296 | $49 |
| 5 | Gemini 3.8 Flash TTS (Google) | 1283 | $16.5 |
| 6 | Fish Audio Drama 3 | 1278 | $15 |
| 8 | Realtime TTS-2 (Inworld) | 1267 | $20.8 |
| 10 | Gemini 3.8 Flash-Lite TTS (Google) | 1259 | $11 |
| **11** | **Simba 3.2 (Speechify) — what we use** | **1249** | **$6.6 list; $6–10 billed** |
| 16 | Realtime TTS-2 Flash (Inworld) | 1217 | $10.4 |
| 64 | Flux TTS (Deepgram; Aura-2 not listed) | 1055 | $45 |

Takeaway: Simba 3.2 is the cheapest model in the top 15 by far, about 85 Elo below the leader at ~1/6 the price.

## Speechify ongoing cost

Plans ([speechify.ai/pricing](https://speechify.ai/pricing)): Free $0 = 500K chars/month (pauses after); Starter $10 = 1.9M; Pro $99 = 13.5M. Simba 3.2 overage $10/1M on Starter.

Our plan isn't recorded in the repo (key lives in `.env`, not read); check the Speechify dashboard. No usage log exists, so this is an estimate:

- Reels: 4 so far, ~0.5–3K narrated chars each, plus rebuilds → under 50K/month.
- Read-aloud if moved to Speechify: ~30 replies/day × ~600 chars ≈ 540K/month.

Estimate: **$0 on Free for reels alone; ~$10/month (Starter) once read-aloud uses it.** Heavy use (3× that) still fits Starter's 1.9M.
