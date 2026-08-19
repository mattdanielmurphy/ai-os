---
title: "Deck Volume vs. Mixer Volume"
date: "2026-08-13"
conversation_id: "1fda931b-3bba-5b88-802f-77b07c496b26"
source: "antigravity"
---

# Deck Volume vs. Mixer Volume

## USER_EXPLICIT (2026-08-13T18:54:09.573727)

[2026-07-12 21:04 MDT-6] [context to this point is 0] I see "gain" but I really just want volume for deck 1... why is it missing?

<!-- /gemini-message -->

---

<!-- gemini-message index=2 role=assistant timestamp="2026-07-12 21:04" -->

---
## MODEL (2026-08-13T18:54:09.573730)

It is missing because you currently have the **Target** drop-down menu set to "Deck 1". In djay Pro's MIDI mapping architecture, specific deck settings handle platter and tone controls (like Gain, EQs, and Tempo), while the actual channel faders belong to the central audio routing.

To find the channel volume, look at the column or dropdown next to the action list and change your **Target** from **Deck 1** to **Mixer**. Once you switch the target to Mixer, you will see options like **Volume (Ch. 1)** or **Line Volume** appear in the action list.

<!-- /gemini-message -->

---
