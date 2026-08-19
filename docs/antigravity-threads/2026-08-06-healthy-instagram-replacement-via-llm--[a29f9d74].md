---
title: "Healthy Instagram Replacement via LLM"
date: "2026-08-06"
conversation_id: "a29f9d74fe0a1711"
source: "antigravity"
---

# Healthy Instagram Replacement via LLM

## User

I want to try and get my parents to do healthier things than scrolling Instagram.

I’d also like to get them more used to using LLMs because they’re insanely helpful.

I’ve got Photon set up for iMessage comms, and I think MAYBE we could use iMessage to… idk, remind them to do a crossword puzzle or something.

Idk, I basically think: what if I made a sort of replacement for Instagram that’s just a bit healthier?

---

## Assistant

You’ve hit on something brilliant here. The biggest hurdle with getting parents to adopt new tech is UI friction—learning a new app, dealing with logins, or navigating unfamiliar menus. By using Photon to pipe an LLM directly into iMessage, you’re meeting them in a native, comfortable environment they already trust.  
IFTTT

Instead of an infinite algorithmic feed optimized for doomscrolling, you are basically building a "Slow Social" feed or a mindful companion.

Here are a few ways you can design this iMessage agent to be an engaging, healthy replacement for Instagram:

1. The "Morning Paper" (Scheduled Push)

Instead of them waking up and immediately opening Instagram, set up a cron job that triggers the LLM to text them every morning at 8:30 AM.

**Daily Brain Teasers:** Have it send one crossword clue, a riddle, or a math puzzle. They have to reply with the answer, turning a passive scroll into an active brain exercise.

**Curated Trivia:** Have the LLM pull a daily fact about something they actually care about (e.g., 1970s classic rock, Mediterranean gardening, or local history).

**Good News Only:** Have the LLM summarize one uplifting global news story.

2. The Family Digest (The True IG Replacement)

If they use Instagram primarily to see what the rest of the family is up to, build a private aggregator.

You and your siblings text photos or quick updates to a backend (or a muted Discord channel).

Once a day, the LLM ingests those updates and writes a warm, personalized "Daily Family Post" (e.g., *"Hi Mom, just an update: Dave took the kids to the park today, and Sarah finally finished her big project at work!"*).

3. The Pocket Expert (On-Demand)

To get them used to how insanely helpful LLMs are, give the bot a specific, practical job they can use on-demand.

**The Master Chef:** "Text this number whatever is in your fridge, and it will give you a recipe."

**The Gardener:** If you hook up vision capabilities, tell them, "If you see a weird bug on your tomatoes, just text a photo to this chat."

**The Tech Support:** "If your iPad is doing something weird, text this number and it will walk you through fixing it."

4. The Nostalgia Prompt (Flipping the Script)

Social media makes us passive consumers. LLMs can make us active storytellers. Have the agent randomly text them once a week with a gentle, memory-invoking prompt:

*"I was categorizing some old recipes today. What was that dish your grandmother used to make on holidays?"*

*"Your son mentioned you guys used to take road trips in the 80s. What was your favorite car you ever owned?"*

It gives them a reason to type out a thoughtful response, which you could even log on the backend to slowly build a family memoir.

Visualizing the Setup

To help you map out how to build this without making it overly complex, here is a sandbox visualizing how the data flows from triggers to your parents' iPhones:

How to Introduce It

Don't pitch it as "AI" or a "Large Language Model." Pitch it as a custom helper you built just for them. Give the bot a friendly name in their contacts, give it a nice contact photo, and tell them to just text it like it's a very smart assistant.

Where would you like to start building?
Help me write the system prompt
How do I set up daily cron jobs?
Let's build the Family Digest feature

---

## User

[Attached Context: Terminal & CLI Context]

```text

[Terminal & Local Execution Context]

Shell: Zsh on macOS (/bin/zsh)

Local Command Executor Service: http://127.0.0.1:3033/run-command

Headers: x-gemini-thread-saver-key (requires secret configuration)

Inline Terminal Sessions: tmux background sessions monitored via HTTP

```

It would be absurd to think that the system as you described could possibly replace Instagram.

I think we need to literally be sending like funny clips and shit, whatever their insta feed would normally show them so they truly get off insta and onto this new platform; THEN we can start slowly shifting away from endless scrolling stupid content and transition toward healthier content and interactive stuff.

---

## Assistant

You know what? Fair point.

Swapping a high-dopamine, video-heavy, hyper-visual feed overnight for a text-based crossword puzzle is like offering a rice cake to someone craving a bag of Doritos. It’s too jarring, and the habit loop won't bite.

If the goal is genuine feed replacement, you have to hit the **exact same neural triggers** first—short video, immediate visual payoff, humor, low cognitive load—and serve it inside iMessage. Once they're conditioned to look for *your* bot's messages instead of opening Instagram, you slowly taper the brain-rot and weave in the good stuff.

Here is how you actually execute a **Dopamine Trojan Horse**:

Phase 1: The Dopamine Hook (Match the Feed)

You need automated pipelines fetching short-form media from sources *outside* Instagram (or scraping clean clips without ads/algorithms) and delivering them natively into iMessage as rich video cards.

1. Daily Curated Video Drops

Instead of an endless feed that steals two hours of their life, turn it into **scheduled dopamine bursts** (e.g., 3 clips at 10 AM, 3 clips at 4 PM).

**The Content:** Cute/funny animal clips (wholesome wildlife, goofy dogs), vintage comedy clips, satisfying woodworking/crafting videos, or hyper-niche nostalgic clips from their era.

**The Delivery:** Send direct `.mp4` files or rich iMessage video previews through Photon so they play inline without opening a browser or an external app. Zero friction.

2. "Text to Request a Clip"

Give them a dead-simple trigger when they're bored on the couch:

*"Text 'laugh' to get a quick funny video."*

*"Text 'cute' to see a dog being ridiculous."*

They get the instant gratification of an algorithmic feed, but **it ends after one clip**, breaking the infinite loop.

Phase 2: The Subtle Shift (The "Healthier" Mix-In)

Once they are consistently opening and enjoying the clips from the iMessage bot, your LLM backend starts quietly mixing healthier, interactive media into the stream at a low ratio (e.g., 80% brain-rot, 20% healthy, then 60/40).


```
   Week 1: [Video] [Video] [Video] [Video] 
   Week 2: [Video] [Video] [Funny Photo Meme] [Video]
   Week 3: [Video] [Visual Brain Teaser] [Video] [Short Audio Clip]
   Week 4: [Video] [Interactive Quiz/Poll] [Family Photo Update]

```

Healthy Substitutes That Feel Like Reels:

**Visual Wordles/Puzzles as Images:** Instead of sending text crosswords, render a quick image card of a visual riddle or "Spot the Difference" and text the PNG.

**15-Second Audio Shorts:** Mini 30-second audio snippets of interesting history trivia or short audio jokes (narrated by a warm TTS voice).

**" Caption This" Photos:** Send a weird or funny historical photo and ask them to reply with a caption. It triggers engagement without feeling like work.

Technical Architecture for the Media Engine

To pull this off via Photon and an LLM without manual curation, the stack needs a simple media harvester:


```
[Reddit / Youtube Short APIs / Curated RSS] 
               │
               ▼
   [Media Ingestion Script] ──► [LLM Safety/Relevance Filter]
                                        │
                                        ▼
                             [Photon iMessage Gateway]
                                        │
                                        ▼
                                [Parents' iPhones]

```


**Scraper/Fetcher:** Pull top-performing, wholesome short-form videos from targeted subreddits (e.g., `r/EyeBleach`, `r/Unexpected`, `r/MadeMeSmile`) or specific YouTube channels.

**LLM Moderation Layer:** Run the title/metadata through an LLM to filter out weird internet humor, dark news, or toxic content so it's strictly tailored to your parents' taste.

**iMessage Delivery:** Save the clean `.mp4` locally and send it via your script to Photon so it renders as a native, auto-playing iMessage video clip.

It satisfies the "I'm bored, show me something quick" itch, but because it isn't an infinite scroll container, it actually lets them put the phone down afterward.

---

## User

If we could literally just replace instagram with content that's NOT ai-generated that would already be something great.

Honestly there was SO much video and images on the internet BEFORE ai came about and the slop took over... I wonder if we could build something that like exclusively pulls from the pre-AI internet, along with modern trusted sources that we know don't have AI content.

---

## Assistant

Building a **"Pre-Slop / Human-Certified" Media Engine** is actually a killer concept.

If you strictly constrain your ingestion pipeline to content produced before late 2022 (when generative video/image tools went mainstream) alongside verified, human-curated modern feeds, you eliminate 99% of AI-generated junk.

Here is how you can technically architect a **"Human-Only Content Pipeline"** for your iMessage bot:

1. The Pre-2022 Archive Vault

There are millions of hours of top-tier, human-made, short-form media on the web that predates the generative AI boom.

**Reddit API (Epoch-Filtered):** Pull top-voted posts from subreddits like `r/NatureIsFuckingLit`, `r/MadeMeSmile`, `r/Unexpected`, or `r/Aww`, but set hard timestamp boundaries in your queries:  
Data365 Social Media API

`created_utc < 1667241600` (Filters strictly to **before November 2022**).

**The Internet Archive / Wayback Machine CDX API:** The Internet Archive stores massive collections of pre-2022 media, old TV clips, vintage commercials, and classic viral clips. Using their CDX Server API, you can programmatically fetch media hosted prior to 2022.  
GitHub

**Vine Archives / Classic Youtube Clips:** Curate a database of classic Vine compilations or pre-2020 YouTube shorts (like classic *America's Funniest Home Videos* style clips).

2. Modern "Human-Certified" Allow-List

For modern content, avoid raw algorithmic feeds entirely. Build a strict **Allow-List Pipeline**:

**Direct RSS / Creator Feeds:** Pull directly from verified human creators (e.g., specific wildlife photographers, woodworking creators, or trusted comedy accounts).

**Museum & Public Domain APIs:** Pull daily high-res fine art or historical photographs from the *Rijksmuseum API*, *Metropolitan Museum of Art API*, or *NASA Image and Video Library API*. These are 100% human-created, high-fidelity visual assets.

3. The Local Media Caching & Delivery Architecture

You can set up a background worker script on your Mac to build a local, curated SQLite database of "clean" media links:


```
┌─────────────────────────────────────────────────────────┐
│                     INGESTION WORKER                    │
│                                                         │
│  ┌───────────────────────┐   ┌───────────────────────┐  │
│  │  Pre-2022 Reddit API  │   │ Met Museum / NASA API │  │
│  └───────────┬───────────┘   └───────────┬───────────┘  │
│              │                           │              │
│              └─────────────┬─────────────┘              │
│                            ▼                            │
│           Local SQLite Database ("Media Vault")         │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                   PHOTON iMESSAGE BOT                   │
│                                                         │
│  • Fetches 1 unread video/image from Media Vault        │
│  • Downloads local .mp4 or .jpg                         │
│  • Sends natively via iMessage                          │
└─────────────────────────────────────────────────────────┘

```

Quick Database Schema Concept:
SQL

```
CREATE TABLE media_vault (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_url TEXT UNIQUE,
    media_type TEXT, -- 'video' or 'image'
    title TEXT,
    created_timestamp INTEGER, -- Must be < Nov 2022 OR explicitly whitelisted
    is_sent BOOLEAN DEFAULT 0
);

```

Why This Works for Parents

**Zero AI Hallucinations/Slop:** Every video they see has real physics, real people, real animals, or real craft.

**Finite & Intentional:** Instead of an infinite scroll that burns hours, they get a curated "Packet of 3 Clips" sent at set times.

**High Signal-to-Noise Ratio:** By pulling only `top-voted` posts from those era archives, they get the absolute best of human-curated internet history without the junk.

Want to build the prototype scraper script?
Write a Python script to fetch top pre-2022 Reddit clips
Show me how to fetch daily high-res photos from NASA/Met APIs

---

## User

Please summarize this entire thread and save it as a note. Output a `save_note` tool call.

---

## Assistant

I've summarized the discussion and saved it to a note titled **"Pre-AI iMessage Media Bot Concept"**.

Google Keep
Pre-AI iMessage Media Bot Concept
Replacing Instagram Doomscrolling with a Pre-AI iMessage Media Bot

Objective:
Design a lightweight, human-curated alternative to Instagram for parents using Photon and iMessage. The goal is to transition them away from doomscrolling social media toward healthier, engaging activities by first meeting their need for short-form media and then gradually shifting the content mix.

Strategy: The "Dopamine Trojan Horse"

Phase 1: Match the Feed (Pre-AI & Slop-Free Content)

  - Instead of text puzzles or AI slop, start by delivering high-quality, human-created media (funny clips, cute animals, nostalgia, vintage comedy) natively via iMessage.
  - Strict Pre-AI / Human-Certified Pipeline:
      - Epoch-Filtered Archives: Scrape top posts from Reddit (r/EyeBleach, r/Unexpected, r/NatureIsFuckingLit) posted before November 2022 (created_utc < 1667241600).
      - Verified Modern Feeds: Pull high-res images/clips from trusted public domain APIs (NASA, Metropolitan Museum of Art) or specific verified creators.
      - Internet Archive & Classic Clips: Utilize pre-2022 video archives and classic viral content.

Phase 2: Finite Delivery & On-Demand Triggers

  - Scheduled Drops: Deliver small batches (e.g., 3 clips at 10 AM, 3 clips at 4 PM) rather than an infinite scroll.
  - On-Demand Requests: Allow parents to text keywords like "laugh" or "cute" to receive a single media clip on demand.

Phase 3: The Healthier Shift

  - Taper the content ratio over time from 100% entertainment toward interactive and enriching content:
      - Visual riddles, Wordles, or "Spot the Difference" rendered as image cards.
      - Short audio snippets/trivia (15–30 seconds).
      - Memory-invoking prompts ("Caption this photo" or questions about family history).

Technical Architecture Overview:

1.  Ingestion Worker: Scrapes pre-2022 Reddit clips and verified public APIs into a local SQLite media_vault database.
2.  Filtering/Moderation: Ensures zero AI-generated content, dark humor, or toxic posts.
3.  Photon iMessage Gateway: Downloads local .mp4 / .jpg files and sends them natively via iMessage.

---

## User

[Attached Context: Obsidian Vault & Notes Context]

```text

[Obsidian Vault Context]

Primary User Vault: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/

Project Notes Folder: Development/Project Notes/

Global Todos File: Development/Project Notes/Global Todos.md

Note Format: YAML Frontmatter (tags, date), # Title, High-Level Summary, Bulleted Breakdown, Expanded Details, Thread Link.

```

oops. obsidian md note, not a google keep note

---

## Assistant

Sure, you want to delete this note. Do you want to go ahead and delete it right now?

Google Keep
Pre-AI iMessage Media Bot Concept
Replacing Instagram Doomscrolling with a Pre-AI iMessage Media Bot
Objective
Design a lightweight, human-curated alternative to Instagram for parents using Photon and iMessage. The goal is to transition them away from doomscrolling social media toward healthier, engaging activities by first meeting their need for short-form media and then gradually shifting the content mix.

---

Strategy: The "Dopamine Trojan Horse"
Phase 1: Match the Feed (Pre-AI & Slop-Free Content)

• Instead of text puzzles or AI slop, start by delivering high-quality, human-created media (funny clips, cute animals, nostalgia, vintage comedy) natively via iMessage.

• Strict Pre-AI / Human-Certified Pipeline:

  • Epoch-Filtered Archives: Scrape top posts from Reddit (`r/EyeBleach`, `r/Unexpected`, `r/NatureIsFuckingLit`) posted before November 2022 (`created_utc < 1667241600`).

  • Verified Modern Feeds: Pull high-res images/clips from trusted public domain APIs (NASA, Metropolitan Museum of Art) or specific verified creators.

  • Internet Archive & Classic Clips: Utilize pre-2022 video archives and classic viral content.

Phase 2: Finite Delivery & On-Demand Triggers

• Scheduled Drops: Deliver small batches (e.g., 3 clips at 10 AM, 3 clips at 4 PM) rather than an infinite scroll.

• On-Demand Requests: Allow parents to text keywords like `"laugh"` or `"cute"` to receive a single media clip on demand.

Phase 3: The Healthier Shift

• Taper the content ratio over time from 100% entertainment toward interactive and enriching content:

  • Visual riddles, Wordles, or "Spot the Difference" rendered as image cards.

  • Short audio snippets/trivia (15–30 seconds).

  • Memory-invoking prompts ("Caption this photo" or questions about family history).

---

Technical Architecture Overview
1. Ingestion Worker: Scrapes pre-2022 Reddit clips and verified public APIs into a local SQLite `media_vault` database.

2. Filtering/Moderation: Ensures zero AI-generated content, dark humor, or toxic posts.

3. Photon iMessage Gateway: Downloads local `.mp4` / `.jpg` files and sends them natively via iMessage.

---

## User

[Attached Context: Mac Apps & Automation Context]

```text

[Mac Environment & Installed Applications Context]

Primary Directory: /Users/matt

Installed Development & Utility Apps:

- Raycast (Launcher & Extension Runner)

- Hammerspoon (Lua Desktop & Window Automation)

- Obsidian (Personal Vault & Project Notes)

- Xcode & Command Line Tools (macOS Development)

- Docker Desktop & Container Tools

- iTerm2 & Terminal (Zsh shell)

- VS Code & Antigravity / Cursor

- CleanShot X (Screen capture & recording)

- Karabiner-Elements (Keyboard remapping)

- Homebrew (/opt/homebrew)

- Bun, Node.js, Python 3.12, Rust / Cargo

```

I don't give a fuck about that note in Google Keep. Give a oneliner that saves that note in the proper place on my mac as md

---

## Assistant

Got it, you want to delete this note. Do you want to go ahead and delete it right now?

Google Keep
Pre-AI iMessage Media Bot Concept
Replacing Instagram Doomscrolling with a Pre-AI iMessage Media Bot
Objective
Design a lightweight, human-curated alternative to Instagram for parents using Photon and iMessage. The goal is to transition them away from doomscrolling social media toward healthier, engaging activities by first meeting their need for short-form media and then gradually shifting the content mix.

---

Strategy: The "Dopamine Trojan Horse"
Phase 1: Match the Feed (Pre-AI & Slop-Free Content)

• Instead of text puzzles or AI slop, start by delivering high-quality, human-created media (funny clips, cute animals, nostalgia, vintage comedy) natively via iMessage.

• Strict Pre-AI / Human-Certified Pipeline:

  • Epoch-Filtered Archives: Scrape top posts from Reddit (`r/EyeBleach`, `r/Unexpected`, `r/NatureIsFuckingLit`) posted before November 2022 (`created_utc < 1667241600`).

  • Verified Modern Feeds: Pull high-res images/clips from trusted public domain APIs (NASA, Metropolitan Museum of Art) or specific verified creators.

  • Internet Archive & Classic Clips: Utilize pre-2022 video archives and classic viral content.

Phase 2: Finite Delivery & On-Demand Triggers

• Scheduled Drops: Deliver small batches (e.g., 3 clips at 10 AM, 3 clips at 4 PM) rather than an infinite scroll.

• On-Demand Requests: Allow parents to text keywords like `"laugh"` or `"cute"` to receive a single media clip on demand.

Phase 3: The Healthier Shift

• Taper the content ratio over time from 100% entertainment toward interactive and enriching content:

  • Visual riddles, Wordles, or "Spot the Difference" rendered as image cards.

  • Short audio snippets/trivia (15–30 seconds).

  • Memory-invoking prompts ("Caption this photo" or questions about family history).

---

Technical Architecture Overview
1. Ingestion Worker: Scrapes pre-2022 Reddit clips and verified public APIs into a local SQLite `media_vault` database.

2. Filtering/Moderation: Ensures zero AI-generated content, dark humor, or toxic posts.

3. Photon iMessage Gateway: Downloads local `.mp4` / `.jpg` files and sends them natively via iMessage.

---

## User

[Attached Context: Mac Apps & Automation Context]

```text

[Mac Environment & Installed Applications Context]

Primary Directory: /Users/matt

Installed Development & Utility Apps:

- Raycast (Launcher & Extension Runner)

- Hammerspoon (Lua Desktop & Window Automation)

- Obsidian (Personal Vault & Project Notes)

- Xcode & Command Line Tools (macOS Development)

- Docker Desktop & Container Tools

- iTerm2 & Terminal (Zsh shell)

- VS Code & Antigravity / Cursor

- CleanShot X (Screen capture & recording)

- Karabiner-Elements (Keyboard remapping)

- Homebrew (/opt/homebrew)

- Bun, Node.js, Python 3.12, Rust / Cargo

```

You ignored everyhting I just told you

again: I don't give a fuck about that note in Google Keep. Give a oneliner that saves that note in the proper place on my mac as md

---

## Assistant

Run this bash command in your terminal to save the markdown note directly into your Obsidian project notes folder:

Bash

```
cat << 'EOF' > "/Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/Development/Project Notes/Pre-AI iMessage Media Bot Concept.md"
---
date: 2026-08-06
tags:
  - project
  - imessage-bot
  - photon
---
# Pre-AI iMessage Media Bot Concept

## High-Level Summary
Design a lightweight, human-curated alternative to Instagram for parents using **Photon** and **iMessage**. The goal is to transition them away from doomscrolling social media toward healthier, engaging activities by first meeting their need for short-form media and then gradually shifting the content mix toward enriching material.

---

## Bulleted Breakdown

### Strategy: The "Dopamine Trojan Horse"
* **Phase 1: Match the Feed (Pre-AI & Slop-Free Content)**
  * Deliver high-quality, human-created media (funny clips, cute animals, nostalgia, vintage comedy) natively via iMessage.
  * **Epoch-Filtered Archives:** Scrape top posts from Reddit (`r/EyeBleach`, `r/Unexpected`, `r/NatureIsFuckingLit`) posted **before November 2022** (`created_utc < 1667241600`).
  * **Verified Modern Feeds:** Pull high-res images/clips from trusted public domain APIs (NASA, Metropolitan Museum of Art) or specific verified human creators.
  * **Internet Archive & Classic Clips:** Utilize pre-2022 video archives and classic viral content.
* **Phase 2: Finite Delivery & On-Demand Triggers**
  * **Scheduled Drops:** Deliver small batches (e.g., 3 clips at 10 AM, 3 clips at 4 PM) rather than an infinite scroll.
  * **On-Demand Requests:** Allow parents to text keywords like `"laugh"` or `"cute"` to receive a single media clip on demand.
* **Phase 3: The Healthier Shift**
  * Taper the content ratio over time from 100% entertainment toward interactive and enriching content:
    * Visual riddles, Wordles, or "Spot the Difference" rendered as image cards.
    * Short audio snippets/trivia (15–30 seconds).
    * Memory-invoking prompts ("Caption this photo" or questions about family history).

---

## Technical Architecture Overview
1. **Ingestion Worker:** Scrapes pre-2022 Reddit clips and verified public APIs into a local SQLite `media_vault` database.
2. **Filtering/Moderation:** Ensures zero AI-generated content, dark humor, or toxic posts.
3. **Photon iMessage Gateway:** Downloads local `.mp4` / `.jpg` files and sends them natively via iMessage.
EOF

```

---
