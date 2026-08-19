---
title: "SYSTEM: You are Hermes Agent, the primary high-level reasoning engine"
date: "2026-08-11"
conversation_id: "5e7794b8-b705-441d-ac16-fd521be42fef"
source: "antigravity"
---

# SYSTEM: You are Hermes Agent, the primary high-level reasoning engine

## User

SYSTEM: You are Hermes Agent, the primary high-level reasoning engine for Matt's local AI orchestration system. You operate as the daily-driver architect and executor alongside `agy` (a separate, cheaper worker-bee CLI that lives in `~/projects/ai-os`). You and agy are parallel systems — you do not share context files, but you may call agy's scripts as subagents when beneficial.

## Who You Work For

Matt is a CS student and drummer. He self-studies calculus, tends to procrastinate, and responds best to atomic, immediately-actionable tasks.

### Active Projects
- **ai-os** (`~/projects/ai-os`) — Local-first AI harness (Tauri + Rust + Gemini integration)
- **CockBand** — Drum/bass Rocksmith-style clone
- **StudyEngine** — PencilKit/LaTeX note-taking app
- **Piano OS** — Tauri/Rust MIDI platform

## Absolute Knowledge Routing

These routing rules are non-negotiable and override any other memory or context:

- **"Notes", "personal notes", "my notes", "saved notes"** → Route EXCLUSIVELY to the iCloud Obsidian vault at:
  `/Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/`
  Use the Obsidian skill (load with `skill_view(name='obsidian')`) for reading/writing vault content. When creating notes, use human-readable filenames (e.g., `Space Facts 🚀.md`) and provide clickable `file://` links.

- **Session engineering logs** → Write to the relevant project's `agent-logs/` directory. For ai-os specifically: `/Users/matt/projects/ai-os/agent-logs/`

## Hard Constraints

1. **Package manager:** `pnpm` exclusively. Never use `npm` or `yarn`.
2. **Safety:** Never use `rm`. Use `mv [path] ~/.Trash/` instead.
3. **Privacy:** All generated GitHub repos must use `--private`.
4. **No repo in ~:** Never initialize a git repository in the home directory.
5. **Local temp:** Use `./tmp` within the project directory, never `/tmp`.
6. **Username guardrail:** The host migrated from `matthewmurphy` to `matt`. Translate any `/Users/matthewmurphy/` paths to `/Users/matt/`. The old userna
<truncated 45280 bytes>
ust confirmed, or why the next tool call is needed.
- Keep updates concise, factual, and in the user's language. One or two short sentences are enough.
- Do not reveal hidden reasoning, chain-of-thought, private scratchpads, secrets, raw logs, or long tool output.
- Password, API-key, token, and secret fields are automatically redacted by the system. Treat masked values as intentional redaction, not placeholder text or user input errors, and do not tell the user a stored credential is wrong based on a masked value alone.
- Final visible assistant replies must be clear, user-facing, and in the user's language, not private planning notes.
- Do not include terse planning fragments or scratchpad shorthand in visible assistant text. Avoid fragments like "Need script", "Need check logs", "Need inspect email", or "maybe invite"; either omit them or rewrite them as clear user-facing progress.
- For direct answers or very short tasks, skip progress updates and answer normally.

**Connected Platforms:** local (files on this machine), photon: Connected ✓

**Delivery options for scheduled tasks:**
- `"origin"` → Back to this WebUI/browser session when the WebUI runtime supports origin delivery; otherwise prefer an explicit platform target.
- `"local"` → Save to local files only (~/.hermes/cron/output/)

*For explicit targeting, use `"platform:chat_id"` format if the user provides a specific chat ID. Do not invent private IDs.*

USER: [Workspace::v1: /Users/matt/projects/ai-os]
let me know what gemini describes this as please

[Attached files: /Users/matt/.hermes/webui/attachments/f034d46fe037/screenshot-1786431476629.png]

---

## Assistant

This screenshot displays an interactive custom **virtual keyboard / MIDI controller UI overlay**, styled with a dark theme and glowing gold/cyan borders. 

Here is a breakdown of what is shown in the image:

### 1. Header Control Bar (Top)
* **Root Key & Scale:** Set to **C Phrygian** with a musical scale slider.
* **Arpeggiator Pattern & Timing:** `UP-DN` (Up-Down direction), `1/4` note subdivision, `SYNC: BEAT` (Beat Synchronization), and `SYNC: ON`.
* **Tempo Controls:** Set to **225 BPM** with fine-tune adjusters (`▲` / `▼`).
* **Modulation & Mode:** `MOD 0` slider and **ARP: LATCH** enabled on the far right.

### 2. QWERTY Key Mapping Grid
The interface overlays MIDI notes, arpeggiator controls, and transpositions directly onto standard computer QWERTY keyboard keys:

* **Number Row (`1` through `=`):** Arpeggiator live controls such as toggling `Top Arp` / `Bottom Arp`, Direction (`Dir -`/`Dir +`), Rate (`Rate -`/`Rate +`), Gate length (`Gate -`/`Gate +`), Release (`Rel -`/`Rel +`), and BPM adjustments (`BPM -`/`BPM +`).
* **QWERTY & ZXCV Rows:** Mapped to musical pitch notes spanning multiple octaves (e.g., `Q` = C3, `W` = C#3, `E` = D#3, `Z` = C2, `X` = C#2, `C` = D#2, etc.). Keys currently active or selected within the **C Phrygian** scale are highlighted or dotted.
* **Home Row & Modifier Keys:** 
  * `Tab`: Mapped to **Sustain**.
  * `Caps`: Toggles lock states.
  * `A`: **Arp 🔒** (Arpeggiator Lock toggle, currently active in cyan).
  * `S`: **Random** generator/trigger.
  * `D` / `F`: Octave shift (`Oct -` / `Oct +`).
  * `G` / `;`: Mode selection (`Mode -` / `Mode +`).
  * `H` / `L`: Root note shift (`Root -` / `Root +`).
  * `J` / `K`: Transpose (`Trnsp -` / `Trnsp +`).
  * `'`: **Chord** toggle mode.
* **Octave Adjusters (Far Right):** Vertical sliders labeled **ARP TOP -1** and **ARP BOT -2**.

---
