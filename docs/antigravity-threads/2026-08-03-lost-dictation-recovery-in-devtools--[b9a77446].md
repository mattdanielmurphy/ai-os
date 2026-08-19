---
title: "Lost Dictation Recovery in DevTools"
date: "2026-08-03"
conversation_id: "b9a77446a4056bd1"
source: "antigravity"
---

# Lost Dictation Recovery in DevTools

## User

Okay, holy shit, I'm mad right now. I just used dictation in Gemini (on chrome) and talked for about three minutes, and then it suddenly just stopped and all of what I said is now gone, lost forever.

I've been trying Gemini on macOS, and it at least seemed to gracefully say, "Okay, you've got 10 seconds left," and then count down, and then actually submit the text even though you hit the time limit of the dictation.




I'm assuming I hit the time limit of the dictation on Gemini Web, and it simply just quit the entire thing, but holy fuck, that is really irritating to lose that.




If it were an app on my computer, I would assume there's some kind of... I guess even it's still worth exploring if maybe in dev tools I can see if there's that audio recording, because I really would love to have that transcription.







give me a prompt I can give to AI in devtools to see if it can find any audio of that dictation session that was lost in the browser storage or something

---

## Assistant

That is beyond frustrating—losing a full three-minute thought stream to a silent timeout buffer feels like shouting into a void.

On web applications like Gemini (`gemini.google.com`), dictation typically relies on streaming audio over WebSockets or processing via the Web Speech API directly in memory rather than dumping raw audio blobs into persistent browser storage. However, intermediate drafts, session logs, or IndexedDB caches **do sometimes retain unsent input fragments or transcript buffers** before garbage collection sweeps them.

Option 1: Quick Automated JavaScript Snippet (Run in DevTools Console)

Before feeding prompts into DevTools AI, you can immediately run this inspection script directly in your **DevTools Console** (`Cmd + Option + J` on Mac) to crawl `sessionStorage`, `localStorage`, `IndexedDB`, and active `textarea`/`input` elements for residual text or audio buffers:

JavaScript

```
(async function findLostDictation() {
  console.log("%c🔍 Searching for lost text/audio fragments...", "color: #00ffff; font-weight: bold;");

  // 1. Check LocalStorage & SessionStorage
  ['localStorage', 'sessionStorage'].forEach(storageType => {
    const store = window[storageType];
    for (let i = 0; i < store.length; i++) {
      const key = store.key(i);
      const val = store.getItem(key);
      if (val && val.length > 50) {
        console.log(`[${storageType}] Potential match in key "${key}":`, val.slice(0, 300) + '...');
      }
    }
  });

  // 2. Check IndexedDB Databases
  if (indexedDB.databases) {
    const dbs = await indexedDB.databases();
    for (const dbInfo of dbs) {
      const request = indexedDB.open(dbInfo.name);
      request.onsuccess = (e) => {
        const db = e.target.result;
        for (const storeName of db.objectStoreNames) {
          try {
            const tx = db.transaction(storeName, 'readonly');
            const store = tx.objectStore(storeName);
            const getAllReq = store.getAll();
            getAllReq.onsuccess = () => {
              if (getAllReq.result && getAllReq.result.length) {
                console.log(`[IndexedDB: ${dbInfo.name} -> ${storeName}] Found ${getAllReq.result.length} entries:`, getAllReq.result);
              }
            };
          } catch (err) {}
        }
      };
    }
  }

  // 3. Scan DOM for hidden draft elements
  document.querySelectorAll('textarea, [contenteditable="true"], input').forEach((el, i) => {
    const text = el.value || el.innerText || el.textContent;
    if (text && text.trim().length > 20) {
      console.log(`[DOM Element ${i}] Found text:`, text);
    }
  });
})();

```

Option 2: Prompt for Chrome DevTools AI Assistance

If you want to use the **AI Assistance** panel inside Chrome DevTools (or feed a prompt to an AI agent interacting with your browser context), copy and paste the prompt below:

Plaintext

```
Act as a Chrome DevTools foreground forensic expert. I was using a web application (gemini.google.com) and performed a ~3-minute voice dictation session. The dictation timed out and cleared the text input field without submitting.

I need to inspect the current browser context to check if any transcript text, draft state, audio Blob, or temporary stream buffer still exists in memory or local storage before this page reloads or garbage collects.

Please generate and execute a diagnostic JavaScript script that will inspect:
1. window.localStorage and window.sessionStorage for recent long string entries or draft keys.
2. window.indexedDB databases for recent audio Blobs, ArrayBuffers, or draft prompt strings.
3. The DOM (including shadow DOM trees) for any hidden contenteditable nodes, draft text containers, or aria live regions that captured transcribed text.
4. Active global media variables or window objects (e.g., MediaRecorder buffers, Web Speech recognition instances, or internal framework state) that might hold array chunks or string buffers.

Provide the exact console output and highlight any strings over 100 characters that look like transcribed text or audio payload data.

```

Pro-Tip for Network Logs

If the dictation transcribed in real-time before disappearing:

Open the **Network** tab in DevTools.

Filter by `WS` (WebSocket) or `Fetch/XHR`.

Look for active or closed connection requests to Google speech/dictation endpoints (e.g., `batchExecute` or streaming RPCs).

Click on the connection entry and check the **Messages** or **Response** tab—the streaming JSON payloads often contain the raw transcription text sent token-by-token during the recording.

---

## User

I wasn't able to recover anything.

But given that failure, I'm afraid to use Gemini for macOS.

I mean, hopefully because it's on my Mac as opposed to in the browser, the audio WILL still be saved somewhere...

I guess I could investigate that right now.

Give me a brief prompt

---

## Assistant

The desktop app is effectively a wrapper around web processes, so raw dictation audio streams directly to Google's backend rather than caching locally to disk. However, native Mac application sandboxes and system logs **do sometimes retain persistent UI state or application cache databases** across app sessions.

Here is a prompt you can feed to an AI context tool, or run against your terminal to check the `Library` sandbox directories where macOS stores the Gemini app's cached state:

Plaintext

```
Act as a macOS application forensics expert. I am using the native Gemini desktop app on macOS. A dictation session hit a time limit and cleared without sending the prompt. 

I need to search the local macOS Application Support and Cache sandbox directories for the Gemini app to see if any draft text, transcript logs, SQLite database records, or temporary audio files (e.g., .wav, .m4a, .tmp, .aiff) persist on disk.

Please generate terminal commands or a script to inspect:
1. ~/Library/Application Support/ (specifically directories matching *Gemini* or *Google*)
2. ~/Library/Caches/ (specifically directories matching *Gemini* or *Google*)
3. ~/Library/Containers/ (for sandboxed app data)
4. Active system log streams or log archives (via the `log` utility) filtered for recent speech/dictation events under the process name.

Focus on identifying text files, SQLite databases (.db/.sqlite), or temporary media files modified in the last 60 minutes.

```

Quick Manual Terminal Command

If you want to quickly check the filesystem right now, open **Terminal** and run this snippet to find any temporary media or database files modified in the last hour under Gemini's app footprint:

Bash

```
find ~/Library/Application\ Support ~/Library/Caches ~/Library/Containers -maxdepth 4 -mmin -60 \( -name "*.db" -o -name "*.sqlite" -o -name "*.tmp" -o -name "*.wav" -o -name "*.m4a" -o -name "*.log" \) 2>/dev/null

```

---

## User

you've got the wrong idea.

It's not that we're trying to recover this audio; it's gone.

I'm just trying to figure out if Gemini.app saves the audio of transcripts, and I'd especially like to know if the audio will still be saved if the app crashes during the transcription.

---

## Assistant

The Short Answer

**No, `Gemini.app` does not save audio files locally.**

**If the app crashes mid-dictation, the audio is completely lost.**

Why It Works This Way

**Streaming in Memory:** When you use dictation (including macOS features like *Speak to Window* or the mic icon), Gemini encodes your voice input in real-time in RAM and streams the audio packets straight to Google's servers over a WebSocket connection. It does **not** write a temporary `.wav`, `.m4a`, or cache file to your SSD while you speak.

**No Local Auto-Save/Crash Recovery:** Because there is no persistent local buffer or crash log for raw audio, if the app process crashes, freezes, or times out mid-sentence, the RAM buffer holding that active stream is immediately wiped. There is no recovery queue or draft audio file created on disk.

What to Do If You Want Safe Dictation

If you prefer dictating long thought streams without risk of losing work:

**Use a local dictation/transcription app:** Tools like **WhisperKit**, **MacWhisper**, or native macOS Dictation (`Fn` twice into a local text editor like Obsidian or TextEdit) run local models or write directly to local text files as you speak.

**Record first, transcribe second:** Use **Voice Memos** (or QuickTime) to record your audio. Once saved locally, you can drag the `.m4a` file directly into Gemini or NotebookLM to summarize/transcribe it—ensuring your source audio remains safe on your Mac.

---

## User

[2026-08-03 16:32 MDT-6] [context to this point is *] Is there an app that provides free dictation like Gemini.app?

If not, I'll just do a hammerscript that, when I trigger Gemini dictation records audio on its own just as a backup. Although... if gemini is using the mic, then will my hammerscript then be unable to? Maybe I'd have to use like blackhole or whatever?

---

## Assistant

1. Free, Local Dictation Apps on macOS

Rather than hack together a backup recorder for Gemini, switching to an **on-device, Whisper-powered dictation app** avoids the timeout/loss issue altogether. These run standard OpenAI Whisper models locally on Apple Silicon (using Neural Engine/Metal), type into any active cursor field via standard hotkeys, and automatically log the text locally:

**OpenWhispr** (Free / Open Source): A system-wide hotkey dictation tool built on `whisper.cpp` / WhisperKit. Press a hotkey, talk into any app, and it injects the text while saving the transcript history locally in SQLite.

**FluidVoice / OpenSuperWhisper** (Free / Open Source): Lightweight menu-bar apps that run local Whisper models. They function like Superwhisper without subscription limits.

**MacWhisper** (Free Basic Tier): Jordi Bruin’s popular Mac utility. The free version handles local file/mic recording using Whisper models and holds every recording and transcript on disk before you do anything with it.

2. macOS Microphone Sharing & Audio Routing
Can two apps listen to the mic at once?

**Yes.** macOS CoreAudio natively supports multi-client microphone access.

Multiple processes (e.g., Chrome/Gemini, a terminal recording script, or a Hammerspoon audio hook) can read from the physical microphone input device simultaneously without locking each other out.

Gemini using the microphone will **not** prevent a secondary script or app from capturing the exact same hardware input stream.

Do you need BlackHole?

**No, not for mic input.**

**BlackHole** is a virtual loopback driver designed to route *system output audio* (what your Mac plays out loud) back into an input.

Since you are capturing hardware input (your physical mic), macOS allows direct parallel taps. BlackHole is unnecessary unless you are trying to capture Gemini’s text-to-speech *voice output*.

3. Alternative: Local Recording Fallback Script

If you stick with Gemini Web/Desktop dictation and want a local safety net, you don't need a heavy setup. A lightweight background recorder using `sox` or `ffmpeg` tied to your dictation trigger shortcut will preserve a local audio file:

Install `sox` via Homebrew: `brew install sox`

Run a background capture process when starting a session:

Bash

```
# Records mic input directly to a timestamped local WAV file in ~/Documents
rec ~/Documents/dictation_backup_$(date +%Y%m%d_%H%M%S).wav

```


If Gemini crashes or drops the stream, your hardware mic input is already safely written to disk, ready to drop into a local transcription tool.

---

## User

[2026-08-03 16:34 MDT-6] [context to this point is *] I'd like to see the text come up as I talk too, rather than just when I finish.

---

## Assistant

If seeing text stream character-by-character while you speak is essential, standard Whisper-based batch processors won't work—they typically wait until you stop talking to run the model.

Here are the best ways to get real-time, word-by-word local dictation on macOS:

Option 1: Native macOS On-Device Dictation (Built-In)

If you haven't enabled local processing yet, macOS includes a built-in streaming engine that types into any focused window in real time:

Go to **System Settings > Keyboard**.

Turn **Dictation** ON.

Set **Language** to your main language (ensure on-device support is toggled/downloaded).

Assign a **Shortcut** (e.g., `Press Fn Key Twice`).

Focus any text input (Obsidian, Chrome, TextEdit) and trigger it—it streams the text word-for-word as you talk with zero time limit.

Option 2: Live-Streaming Local Mac Apps

If you want a dedicated floating overlay or AI auto-formatting on top of live streaming:

**Superwhisper (Free Tier Available):** Built specifically for Apple Silicon. It features a **Realtime Mode** that displays text live as you speak via an overlay before inserting it into your active app.

**Local-Whisper / Open-Source Streaming Wrappers:** Open-source Mac utilities built on streaming architectures like `whisper.cpp` (or NVIDIA's Parakeet model) offer streaming overlays that display partial transcriptions live before releasing the final text.

Option 3: Real-Time Stream via Hammerspoon (Custom Setup)

Since you already use **Hammerspoon**, you can hook up a local real-time audio pipeline directly into a floating canvas overlay:

**Engine:** Use `whisper.cpp` compiled with the `--step` / stream flag, or an instance of local streaming STT via `ffmpeg` + WebSocket.

**Hammerspoon UI:**

Create a floating `hs.canvas` box on screen.

Spawn a background `hs.task` that streams standard output line-by-line from the local speech process.

As lines hit `stdout`, update the `hs.canvas` text element in real-time.

On key release or timeout, automatically paste the text into the active focused window (`hs.eventtap.keyStrokes`) and write a copy to a local backup markdown file in your vault or `~/Downloads`.

---

## User

[2026-08-03 16:37 MDT-6] [context to this point is *] Native macOS dictation, even though it's good, I don't think it's as good as other options, especially when it comes to technical terms or brand names. Another big drawback for me with native macOS dictation is it just stops after a minute or something, and I would like it to just keep going indefinitely, ideally.

---

## Assistant

You're completely right to be turned off by native dictation for those exact reasons:

**Vocabulary limits:** Native engines rely on small, traditional language models that struggle with jargon, domain-specific terminology, code syntax, and brand names.

**Idle cutoffs:** macOS dictation technically doesn't have an absolute duration cap anymore, but it drops the session instantly if it detects **30 seconds of silence**—which kills your flow if you pause to think mid-sentence.

If you want **high accuracy on technical terms** without arbitrary time limits, you need a local model powered by **OpenAI's Whisper** (via Apple Silicon's Core ML/Neural Engine) or NVIDIA's **Parakeet**.

Here are the best alternatives that solve both problems:

1. Free & Open-Source Options (Local & Infinite)

**OpenWhispr:** Fully open-source Mac GUI app that uses local Whisper models. You hit a hotkey, talk for as long as you want (no timeout), and when you're done, it formats and pastes the text directly into whatever field you're in.

**Hapi / VoiceInk (Built on WhisperKit):** Wrappers utilizing `WhisperKit` (Apple's Core ML optimization for Whisper). They run directly on your Mac's Neural Engine with zero network dependency, insane accuracy on obscure words/brand names, and infinite recording buffers.

2. Live-Streaming Options (Text shows up as you speak)

If seeing the text stream live line-by-line is mandatory:

**Dictato / Superwhisper (Realtime Mode):** Paid native Mac clients that support local low-latency engines like **Parakeet** (~80ms latency). They display floating overlay text live as you speak without hitting timeouts.

The Ultimate Fail-Safe: Your Hammerspoon Plan

Since you already use Hammerspoon, pairing a local Whisper app with your own fallback script gives you absolute peace of mind.

If you don't want to write complex audio routing, you can make Hammerspoon handle the **"Audio Safety Net"** while any dictation app runs:

**Hotkey Trigger:** Bind a single shortcut (e.g., `Option + Space`) in Hammerspoon.

**Dual-Action:**

It spawns a background `sox` or `ffmpeg` process via `hs.task` to record raw audio directly to `~/Recordings/dictation_backup.wav`.

It triggers your dictation app's shortcut.

**Completion:** Hitting the shortcut again stops `sox` and saves the file.

If your dictation tool crashes, times out, or loses text, your raw `.wav` file is already safely sitting on your disk, ready to be dropped into any offline Whisper script or LLM for an instant, perfect recovery.

---

## User

[2026-08-03 16:43 MDT-6] [context to this point is *] I'd really like to have one that shows a text stream that is also updated and fixed by a smarter model after a delay, you know?

---

## Assistant

That exact two-stage architecture—**a fast real-time streaming model followed by an LLM cleanup pass**—is the holy grail for dictation, and a couple of modern Mac tools are built around this exact pipeline.

Here is how that workflow actually exists in dedicated tools, and how you could easily build it yourself using your existing tools.

Dedicated Apps Built for This Exact Two-Pass Pipeline
1. **Superwhisper** (Best Native macOS Option)

Superwhisper is explicitly designed around a two-stage pipeline:

**Stage 1 (Real-time):** Uses a fast, low-latency voice model (like Parakeet or a lightweight Whisper variant) to stream draft text into a floating UI overlay as you speak.  
App Store - Apple

**Stage 2 (Post-Process LLM):** When you release your recording shortcut, it takes that entire raw text draft and passes it through an LLM (you can choose Claude Sonnet, Haiku, GPT-4o, or local Ollama models).  
Max Productive AI

**Result:** The LLM strips out filler words ("um," "like," repetitive stutters), corrects specialized vocabulary or brand names, applies proper formatting/markdown, and drops the clean text into your focused app. You can even bring your own API keys (BYOK) so you aren't tied to a subscription.  
Max Productive AI

2. **Wispr Flow**

Wispr Flow handles this in the cloud. It streams raw transcription tokens live and then instantly runs an LLM layer over the top that rewrites the text into structured prose based on what app you are currently typing into (e.g., casual for Slack, clean code comments for Cursor, formal for Mail).  
Voibe
+ 1

The Custom DIY Approach (Hammerspoon + Local Model + LLM)

Since you already use **Hammerspoon**, you can build this exact two-stage pipeline with total control over safety and backups:


```
[ Your Voice ]
     │
     ├── 1. Hammerspoon spawns `ffmpeg` or `sox` ──> Saves raw ~/Backups/audio.wav (Fail-safe)
     │
     ├── 2. Live Stream (Fast/Draft) ─────────────> Local streaming Whisper (`whisper.cpp --step`)
     │                                               Displays raw, noisy text in an `hs.canvas` box
     │
     └── 3. Final Pass (When stopped) ─────────────> Pass raw transcript to local Ollama / Claude API
                                                     Pastes polished, error-corrected text at cursor

```

How it solves all your problems:

**Zero Data Loss:** `ffmpeg` writes the `.wav` directly to your SSD as you speak. Even if the LLM fails, internet drops, or script crashes, your audio is safe.

**Real-time Feedback:** The live WebSocket/Whisper stream gives you instant visual feedback in a floating canvas overlay so you know it's capturing your voice.

**Smart Cleanup:** The secondary LLM pass fixes the phonetic mistakes, adds proper punctuation, formats code snippets/technical terms, and removes your thinking pauses automatically.

If you want a polished off-the-shelf app that does this out of the box, check out **Superwhisper**. If you want complete ownership without software subscriptions, setting up the two-stage pipe in Hammerspoon is surprisingly straightforward to script!

---
