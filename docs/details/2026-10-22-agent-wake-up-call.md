# Agent wake-up phone call

Thread: Agent wake-up phone call (2026-10-22). Matt's ask: "How can I get a wake-up call from Sonnet without
paying API prices? ... I have a Max anthropic plan, I swear I thought it said it came with $100 in API credit per
month?" Plus: do most of the morning check-in as a call, funny character voices (maybe celebrities) with a
voicemail if he misses it.

## 10:45 Proposal: Twilio + his own Deepgram tester, Sonnet paid by Max credits

**Asked:** cheapest real phone call from a Claude agent; tie into the morning check-in; record the voices idea.
**Did:** read the official Anthropic doc, Twilio and Deepgram pricing pages, and his repo. Built nothing.

---

### Max includes API credit

He was right. Anthropic's doc [API credits for Max and Team plans](https://platform.claude.com/docs/en/about-claude/api-credits-for-subscribers)
(and the [help-center article](https://support.claude.com/en/articles/17154008)): Max 5x = $100 USD/month, Max 20x =
$200 USD/month, refreshed each billing cycle, no rollover. Covers the Claude API, Agent SDK, Managed Agents and the
Console playground. Does not cover Claude Code or extra usage in the apps. Nothing is ever charged to the Claude
plan; when the balance hits zero, API calls simply stop until next month.

To claim: claude.ai > Settings > Billing > "API credits" > link a Console organization (create one at
platform.claude.com first if needed). One plan links to one org, and you can't change it yourself later, so link
the org he actually wants to build in. Must have been on Max 7+ days (he has).

A 5-minute Sonnet call is a few cents of API; a month of them is well under $5, so the credit covers it with room
to spare. This answers "without paying API prices": Sonnet on the API is already paid for.

Rejected: routing the call's LLM through `claude -p` on the Max subscription to avoid the API entirely. Anthropic's
Feb 2026 policy says subscription OAuth is for Claude Code and claude.ai only; headless local experiments are
tolerated, products aren't, and the latency would be bad for voice anyway. With free credit there's no reason.

---

### He already built the voice half

`tools/voice-agent-tester/` (Oct 13, "Morning Call Voice Tester & Persona Playground", `morning-call.test`,
port 3344) is a working browser workbench on the [Deepgram Voice Agent API](https://developers.deepgram.com/docs/voice-agent):
one WebSocket does speech-to-text, the LLM turn and text-to-speech, with barge-in, tuned turn-taking, a 138-voice
catalog and four personas in `presets.json` (drill_sergeant, victorian_butler, wall_street_boss,
temporal_dispatcher). Its README already names the production plan: Twilio Media Streams bridged to that same
Deepgram WebSocket. So the "character on the phone" piece exists; only the phone leg and the trigger are missing.

Deepgram's `think.provider` accepts `type: "anthropic"` with his own key
([LLM models doc](https://developers.deepgram.com/docs/voice-agent-llm-models)), so the brain is Sonnet paid by the
Max credit. The tester currently defaults to a Gemini model; that's one line to change.

---

### Cheapest stack and cost

| Piece | Service | Price | Notes |
|---|---|---|---|
| Phone leg | [Twilio Programmable Voice](https://www.twilio.com/en-us/voice/pricing/ca) | $0.014/min outbound to Canada, $1.15/mo for a Canadian number, free trial | Twilio has an official outbound Deepgram guide |
| Voice agent (STT+TTS+turns) | [Deepgram Voice Agent](https://deepgram.com/pricing) | $0.065/min on the "Custom, BYO LLM" tier; $200 signup credit that never expires | he already uses it |
| Brain | [Claude API, Sonnet](https://platform.claude.com/docs/en/about-claude/pricing) | a few cents per call | covered by the Max credit |

A 5-minute call ≈ $0.33 Deepgram + $0.07 Twilio ≈ $0.40, about $12/month daily; the $200 Deepgram credit alone
covers 1.5 years of that. Only real new monthly cost: the $1.15 number plus pennies of Twilio minutes.

Alternatives checked and set aside:
- [Vapi](https://vapi.ai) ($0.05/min platform + providers, BYO LLM ok), [Retell](https://www.retellai.com)
  ($0.07–0.31/min), [Bland](https://www.bland.ai) ($0.11–0.14/min, closed stack, no BYO LLM),
  [ElevenLabs Agents](https://elevenlabs.io/agents) ($0.08–0.10/min hosting + LLM + telephony). All are a second
  copy of what his Deepgram tester does, mostly pricier, and he'd have to redo his persona tuning. ElevenLabs is
  the one to revisit if he wants its voices; Deepgram's own voices are fine to start.
- Zero-cost "no telephony" routes: an iOS Shortcuts automation at the alarm's stop time can run immediately and
  speak text or open the check-in chat, but it isn't a ringing call from someone else, which is the whole point
  ("you'll actually be excited to see a call coming in"). A Mac can't FaceTime his own iPhone from his own Apple ID.
  Telegram bots can't place calls (his README already found that).

---

### Smallest working step

One afternoon, no new repo yet, all inside ai-os:

1. He links the Console org (Settings > Billing) and makes one API key; signs up for Twilio (trial number, verify
   his own phone) and grabs his Deepgram key. Keys go in `tools/voice-agent-tester/.env`
   (`ANTHROPIC_API_KEY`, `DEEPGRAM_API_KEY`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM`).
2. Add `call.ts` next to `server.ts`, following Deepgram's
   [outbound telephony guide](https://developers.deepgram.com/docs/outbound-telephony-agent) and Twilio's
   [outbound voice-agent post](https://www.twilio.com/en-us/blog/partners/integrations/building-an-outbound-voice-agent-with-twilio-and-deepgram):
   Twilio REST places the call with `<Connect><Stream>` to a WebSocket on his Mac; the server shuttles μ-law audio
   between Twilio and the Deepgram agent, reusing `buildDeepgramSettings` with a preset. Public URL: the Mac is
   already on Tailscale Funnel (mac-connector, port 443); add a second funnel port (8443 or 10000) for this.
3. First test: `bun call.ts --preset drill_sergeant --say "Good morning, this is a test"` rings his phone.

Step 2 (after the first call works): `daily.py call --date D`, run by the `morning-checkin` scheduled task after
`send`, dials at wake time with the day's `data/checkin-<date>.md` prompt as the agent's system prompt, so the
talk half of the check-in happens on the phone; the end of the call points him at the page link that was texted.
Needs the task to fire at wake time (it currently runs early to build the page); either a second scheduled run or
a launchd job on the Mac at the alarm time. Voicemail: Twilio's answering-machine detection (in the Deepgram guide)
detects no-answer, and the agent leaves a short in-character message via TTS, then hangs up; a missed call also
re-dials once after 5 minutes.

Ask before building: 👍 on the reply = build step 1 in ai-os (`tools/voice-agent-tester`), moving it to its own
private repo only if it grows past that folder.

---

### Funny voices and voicemail

Recorded in `IDEAS.md`. Cloning Snoop Dogg or any real celebrity is out: ElevenLabs and Deepgram ToS both forbid
cloning a voice you don't have rights to, and personality-rights law applies even for private use with a cloned
voice bought from a service. Original characters give the same effect and he already has four; proposal: Sonnet
invents a new character each morning (name, job, one running gag) from a small bible, picks a Deepgram voice +
speed/expressivity to match, and the iMessage that goes out with the page link names who called ("Missed call from
Reginald, your Victorian butler") so the missed-voicemail sting works.

---

### Untested and risks

- Nothing built or run; prices read from vendor pages today, Twilio trial limits (can only call verified numbers;
  trial preamble on calls) apply until he adds a card ($20 minimum).
- Call quality through Tailscale Funnel on a laptop that sleeps: the Mac must be awake at wake time (lid-closed
  keep-awake is already set up; nightly restart at 04:30 must finish before the call).
- Deepgram tester currently takes the Deepgram key from the browser, not `.env`; step 1 moves it server-side.

**Undo:** nothing to undo; delete the IDEAS entry and this file.
