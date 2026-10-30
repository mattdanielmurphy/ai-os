# Morning check-in as a phone call (Pipecat spike)
<!-- readthrough project=code -->

## 13:50 Spike result and recommendation

You asked whether your morning check-in can be a call, ideally FaceTime Audio, on Pipecat. Built only a throwaway test; nothing is live.

---

### Recommendation: Twilio first

| Route | Places a call by itself? | Audio | Cost | Verdict |
|---|---|---|---|---|
| FaceTime Audio | Only with a hack: no API, Mac prompts before dialing, needs a second Apple ID, a virtual audio device and an awake Mac | Best | Free | Rejected: fails on the mornings that matter, and automating it may break Apple's terms |
| Twilio into Pipecat | Yes, Pipecat has an official guide | Phone quality, 8 kHz | About US$0.35 for 15 minutes | Pick this |
| CallKit app | Yes, looks like a real call | Best | US$99 a year Apple developer fee, plus an app to build | Later, only if phone audio bothers you |
| WebRTC link | No: a notification, not a ring | Best | Low | Rejected: doesn't get you out of bed |

---

### What the spike tested

Real Speechify voice (Marian) and real Deepgram speech-to-text inside Pipecat, with a simulated 200-second room recording. Not tested: a real phone call, a real microphone, or a Claude conversation.

- **Latency:** first voice audio arrives in 0.22 seconds, every line. Claude's reply time will add to this and wasn't measured.
- **Silence:** with the mic open, breaths and a cough caused no false turn, but quiet muttering did. With the mic off during scripted phases there were no false turns, and speech-to-text heard you correctly right after 178 seconds off.
- **Timeout:** Pipecat's default ends a pipeline after 300 idle seconds, which would kill a long meditation. Read from the code, not tested; turn it off or keep it fed.
- **Pronunciation:** back-transcribed lines were right, except course codes read as numbers ("CMPUT 201" became "two hundred and one"). A small word list fixes those. Transcription can't judge the feel; only your ears can.
- **Design this implies:** breathing and meditation are pre-rendered audio played into the call with the mic off, so timing is exact and Pipecat only handles the check-in.

---

### Cost for a 15-minute morning

Twilio: 15 × (US$0.014 + $0.0044) = $0.28, plus the $1.15 a month number. Speech-to-text comes from your Deepgram credit, Speechify from your existing plan (exact rate not checked), and Claude is cents from your Max API credit. Roughly US$10 a month.

---

### Blockers

Needs a new Twilio account (paid, so asking first). No Anthropic API key is set yet; the Max credit has to be claimed. The Deepgram key in your ai-os `.env` has a stray character and returns 401 until it's removed; the spike stripped it in memory, and the file wasn't changed.

## 14:10 Free options for the call

You rejected Deepgram for voice and want Groq speech-to-text and a free Twilio replacement. The voice was already Speechify, so nothing changes there. Groq swaps in for speech-to-text, but it transcribes after you stop talking, so replies start slightly later. Telegram is the free candidate: a second user account can place a real ringing call, though bots can't, and it needs a spare number. Twilio's trial credit is a free way to test a real phone call, not a lasting answer.
