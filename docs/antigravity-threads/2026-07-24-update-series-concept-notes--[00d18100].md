---
title: "Update Series Concept Notes"
date: "2026-07-24"
conversation_id: "00d18100-ddc5-4ad0-99a5-c7d6a0760549"
source: "antigravity"
---

# Update Series Concept Notes

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
<truncated 23860 bytes>
ybe they even say "yeah, we couldn't possibly do that" but quickly someone else goes: "Oh, yeah we did that whole backstory about Trevor's parents being vampires" or like "oh, we already did that in season 13" or something. Basically the idea is: the show is so fucking ridiculous and stupid that EVEN the writers can't keep track of all the dumb shit they've done, and NOTHING is really too stupid for the show.

ASSISTANT: I have added your recurring bit idea to the concept note:

### Summary of Changes
* **Added Section 5:** Added the **"Nothing is Too Stupid" (The Forgotten Lore)** recurring bit under the standout scene ideas in the [TV Series Concept - "On Spec" (behind the scenes of soap opera).md](file:///Users/matt/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/Personal/Ideas/TV%20Series%20Concept%20-%20%22On%20Spec%22%20%28behind%20the%20scenes%20of%20soap%20opera%29.md) note.
* **The Bit:** Captures a self-conscious writer pitching an absurd out-of-the-box fix (like magic powers), only for a veteran writer to dig through the show's massive history and reveal that even more preposterous elements (like Trevor's vampire parents) are already canon.

USER: new recurring bit:
almost every writer is a weirdo and they have things they continually go back to. Sometimes they try and shoehorn in their bizarre ideas about the world into the show under the guise of it being "entertaining" and "absurd".
But then eventually other people on the show realize: "why the fuck does Ron keep having us do scenes where we're in the hot tub" or "Why is this character always making comments about Irish people out of nowhere"

---

## Assistant

Created At: 2026-07-23T19:19:33-06:00
Completed At: 2026-07-23T19:19:33-06:00
File Path: `file:///Users/matt/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/Personal/Ideas/TV%20Series%20Concept%20-%20%22On%20Spec%22%20%28behind%20the%20scenes%20of%20soap%20opera%29.md`
Total Lines: 112
Total Bytes: 7280
Showing lines 1 to 112
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # Series Concept Note: "On Spec" (Working Title)
2: 
3: ## Logline
4: A satirical workplace comedy set in the frantic, high-volume writers' room of a 40-year-old daily soap opera, following an ambitious new writer who tries to "save" the show with art—only to be crushed by production deadlines, veteran hacks, and the bizarre reality of daytime TV.
5: 
6: ---
7: 
8: ## Core Premise & World
9: * **The Machine:** The room is tasked with pumping out 4–5 episodes a week, 52 weeks a year. Volume and deadlines trump artistic integrity every single time.
10: * **Format:** Single-camera workplace comedy / mockumentary style (in the vein of *30 Rock* or *The Office*).
11: 
12: ---
13: 
14: ## Main Character & Core Arc
15: * **The Idealist (Novice Writer):** Joined the show believing it’s just a stepping stone or a chance to elevate "low-brow" media. Struggles with perfectionism, writer's block, and artistic arrogance.
16: * **The Arc:** Moves from condescending snobbery → total burnout → realization of the raw discipline required to produce volume → ultimate appreciation for the comfort and companionship simple, trope-heavy stories provide real people.
17: 
18: ---
19: 
20: ## Key Character Dynamics
21: * **The Veteran Writers:**
22:   * Tactical "marathon runners" who can churn out 15 formatted pages before lunch.
23:   * They aren't untalented; they've mastered the mechanical craft of hitting beats under insane pressure.
24:   * Defensive 
<truncated 4297 bytes>
cere, deeply philosophical)*  
77: You think I don't like Chekhov? I love Chekhov. But Chekhov doesn't pay my mortgage, and Chekhov isn't what a single mother working a 12-hour night shift wants to analyze at 8:00 PM. She doesn't want existential dread, kid. She wants... human truth. Raw, unfiltered emotion. What we do here... it touches people's actual lives.
78: 
79: *(The Novice Writer looks genuinely moved. He nods slowly, beginning to respect the man.)*
80: 
81: **CUT TO:**
82: 
83: ### INT. ON-SET MONITOR - NEXT DAY
84: 
85: A garish monitor screen playing raw, multi-camera footage. The lighting is harsh; the set looks like a cheap suburban living room.
86: 
87: **ON SCREEN:**  
88: *(A mother and father are screaming at a panicked, sweat-drenched PRIEST.)*
89: 
90: **FATHER**  
91: *(Veins popping in his neck)*  
92: Stay away from him, you sick freak! We know what you did to our boy!
93: 
94: *(Their 17-year-old SON steps between them with completely unearned, dramatic intensity.)*
95: 
96: **SON**  
97: *(Staring intensely into his parents' eyes)*  
98: Stop it! Mom, Dad... it wasn't him. It was *me*. I love Father Thomas.
99: 
100: *(Dead silence on set. The son turns, gazes tenderly at the middle-aged priest, takes his hand, and plants a passionate kiss on his lips. The priest looks visibly confused but accepts it. They walk off-camera hand-in-hand as the mother silently mouths 'Oh my God'.)*
101: 
102: **CUT TO:**
103: 
104: ### INT. CONTROL ROOM - CONTINUOUS
105: 
106: The Novice Writer and Veteran Writer stand side-by-side watching the playback. The Novice's mouth is slightly open in absolute horror, completely unable to process what he just watched.
107: 
108: The Veteran takes a slow sip of stale coffee, doesn't even blink, and checks his clipboard.
109: 
110: **VETERAN WRITER**  
111: *(Deadpan, totally business-as-usual)*  
112: Great. That covers the 4:00 PM slot. Let's write the focus group apology for Thursday.
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-23T19:19:39-06:00
Completed At: 2026-07-23T19:19:39-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/Ideas/TV Series Concept - "On Spec" (behind the scenes of soap opera).md. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -54,7 +54,13 @@
 * **The Joke:** Another writer immediately scoffs: *"Magic powers? That's way too stupid, we couldn't possibly do that."* Then a veteran writer pauses, flips through a massive, dusty binder of show lore, and deadpans: *"Actually, we established in Season 13 that Trevor’s parents are vampires. So magic is already canon."*
 * **The Concept:** The show has been running so long and has accumulated so much ridiculous, low-budget melodrama that even the writers can't keep track of all the dumb shit they've done—and absolutely nothing is too stupid to make it to air.
 
-
+### 6. The Writer's Obsessive Tropes (The Weirdo In The Room)
+* **Setup/Recurring Bit:** Almost every writer in the room is a weirdo with specific, bizarre fixations or real-world opinions they continuously shoehorn into the script under the guise of "entertaining daytime drama" or "character flavor."
+* **The Realization:** Over time, the other writers (or actors) notice suspicious patterns in the scripts, leading to awkward interventions:
+  * *"Why the fuck does Ron keep writing scenes where characters resolve their emotional conflicts in a hot tub?"*
+  * *"Why does this character randomly make derogatory comments about Irish people out of nowhere in every episode written by Brenda?"*
+  * *"Is there a narrative reason Trevor has had to change his shirt on screen seven times this week, or is Gary just doing it again?"*
+* **The Concept:** The room is so busy hitting deadlines that these weird, highly personal obsessions and pet peeves slip through the edit, becoming permanent, baffling fixtures of the show's canon.
 
 ---
 
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

I have added the new recurring bit to your concept note:

### Summary of Changes
* **Added Section 6:** Added **"The Writer's Obsessive Tropes (The Weirdo In The Room)"** to the standout scene ideas in the [TV Series Concept - "On Spec" (behind the scenes of soap opera).md](file:///Users/matt/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/Personal/Ideas/TV%20Series%20Concept%20-%20%22On%20Spec%22%20%28behind%20the%20scenes%20of%20soap%20opera%29.md) note.
* **The Bit:** Details the eccentricities of the writing staff, who sneak their bizarre real-world fixations and random opinions (like hot tub scenes, out-of-nowhere anti-Irish commentary, or gratuitous shirt changes) into the script under the guise of daytime drama, only for the rest of the room to slowly notice the pattern and stage awkward interventions.

---
