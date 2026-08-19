---
title: "TV Series Concept Development"
date: "2026-07-24"
conversation_id: "08566917-7bb0-4da5-b41f-14c122f89fa5"
source: "antigravity"
---

# TV Series Concept Development

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
<truncated 26651 bytes>
he Novice Writer looks genuinely moved. He nods slowly, beginning to respect the man.)*

**CUT TO:**

### INT. ON-SET MONITOR - NEXT DAY

A garish monitor screen playing raw, multi-camera footage. The lighting is harsh; the set looks like a cheap suburban living room.

**ON SCREEN:**  
*(A mother and father are screaming at a panicked, sweat-drenched PRIEST.)*

**FATHER**  
*(Veins popping in his neck)*  
Stay away from him, you sick freak! We know what you did to our boy!

*(Their 17-year-old SON steps between them with completely unearned, dramatic intensity.)*

**SON**  
*(Staring intensely into his parents' eyes)*  
Stop it! Mom, Dad... it wasn't him. It was *me*. I love Father Thomas.

*(Dead silence on set. The son turns, gazes tenderly at the middle-aged priest, takes his hand, and plants a passionate kiss on his lips. The priest looks visibly confused but accepts it. They walk off-camera hand-in-hand as the mother silently mouths 'Oh my God'.)*

**CUT TO:**

### INT. CONTROL ROOM - CONTINUOUS

The Novice Writer and Veteran Writer stand side-by-side watching the playback. The Novice's mouth is slightly open in absolute horror, completely unable to process what he just watched.

The Veteran takes a slow sip of stale coffee, doesn't even blink, and checks his clipboard.

**VETERAN WRITER**  
*(Deadpan, totally business-as-usual)*  
Great. That covers the 4:00 PM slot. Let's write the focus group apology for Thursday.
 Add a new idea:
- some character clearly should die, because they've been terminally ill for 3 years or something on the show, but the producers keep telling the writers they can't kill them off

---

## Assistant

Created At: 2026-07-23T19:11:00-06:00
Completed At: 2026-07-23T19:11:00-06:00
Your current permission grants (listed in the order they are checked) are:
- command(*): allowed
- execute_url(*): allowed
- read_url(*): allowed
- mcp(*): allowed
- escalate_admin(*): allowed
- command(du): allowed
- command(cp): allowed
- command(find): allowed
- command(pnpm run): allowed
- command(pnpm install): allowed
- command(npx): allowed
- command(grep): allowed
- command(sed): allowed
- command(pnpm approve-builds): allowed
- command(mv): allowed
- command(pnpm add): allowed
- command(which): allowed
- command(compress-html): allowed
- command(ls): allowed
- command(head): allowed
- command(python3 /Users/matthewmurphy/projects/ai-os/scripts/precision_edit.py --help): allowed
- command(/Users/matthewmurphy/projects/ai-os/scripts/ingest_codebase): allowed
- command(python /Users/matthewmurphy/projects/ai-os/scripts/get_last_cost.py --agent agy): allowed
- command(echo): allowed
- command(pnpm build): allowed
- command(curl -X POST http://127.0.0.1:8000/api/generate -H "Content-Type: application/json" -d '{"brief": "test", "palette": "test"}'): allowed
- command(cat <<'EOF' >test_model.py): allowed
- command(python test_model.py): allowed
- command(cat <<'EOF_SAFE' >requirements.txt): allowed
- command(source venv/bin/activate): allowed
- command(pip install -r requirements.txt): allowed
- command(git commit): allowed
- command(git add): allowed
- command(git status): allowed
- command(git diff): allowed
- read_file(/Users/matt/Library/LaunchAgents): allowed
- read_file(/Users/matt/Documents/Scripts/macOS/energy_monitor.sh): allowed
- write_file(/Users/matt/Documents/Scripts/macOS/energy_monitor.sh): allowed
- mcp(chrome-devtools/list_pages): allowed
- mcp(chrome-devtools/evaluate_script): allowed
- mcp(chrome-devtools/new_page): allowed
- execute_url(localhost): allowed
- read_url(github.com): allowed
- command(ps): allowed
- command(head): allowed
- command(killall chronod): allowed
- command(pkill): allowed
- command(grep): 
<truncated 2402 bytes>
ravity-cli/builtin): allowed
- write_file(/Users/matt/.gemini/antigravity-cli/builtin): denied
- read_file(/Users/matt/.gemini/antigravity-cli/conversations): ask
- write_file(/Users/matt/.gemini/antigravity-cli/conversations): denied
- read_file(/Users/matt/.gemini/config/mcp_config.json): ask
- write_file(/Users/matt/.gemini/config/mcp_config.json): ask
- read_file(/Users/matt/.gemini/config/skills): allowed
- write_file(/Users/matt/.gemini/config/skills): ask
- read_file(/Users/matt/.gemini/config/plugins): allowed
- write_file(/Users/matt/.gemini/config/plugins): ask
- read_file(/Users/matt/.gemini/config/agents): allowed
- write_file(/Users/matt/.gemini/config/agents): ask
- read_file(/Users/matt/.gemini/config/hooks.json): ask
- write_file(/Users/matt/.gemini/config/hooks.json): ask
- read_file(/Users/matt/.gemini/config/sidecars): allowed
- write_file(/Users/matt/.gemini/config/sidecars): ask
- read_file(/Users/matt/.gemini/config/projects): allowed
- write_file(/Users/matt/.gemini/config/projects): denied
- read_file(/Users/matt/.gemini/config/config.json): denied
- write_file(/Users/matt/.gemini/config/config.json): denied
- read_file(.env): ask
- write_file(.env): ask
- read_file(.env.local): ask
- write_file(.env.local): ask
- read_file(.env.production): ask
- write_file(.env.production): ask
- read_file(.env.development): ask
- write_file(.env.development): ask
- read_file(.env.staging): ask
- write_file(.env.staging): ask
- read_file(.npmrc): ask
- write_file(.npmrc): ask
- read_file(.pypirc): ask
- write_file(.pypirc): ask
- read_file(.netrc): ask
- write_file(.netrc): ask
- read_file(.git-credentials): ask
- write_file(.git-credentials): ask
- read_file(.vscode): ask
- write_file(.vscode): ask
- read_file(.cache): ask
- write_file(.cache): ask
- read_file(.git): ask
- write_file(.git): ask
- read_file(/Users/matt/.gemini/antigravity-cli): denied
- write_file(/Users/matt/.gemini/antigravity-cli): denied
- read_file(/Users/matt/.gemini/config): denied
- write_file(/Users/matt/.gemini/config): denied

Created At: 2026-07-23T19:11:01-06:00
Completed At: 2026-07-23T19:11:01-06:00
File Path: `file:///Users/matt/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/Personal/Ideas/TV%20Series%20Concept%20-%20%22On%20Spec%22%20%28behind%20the%20scenes%20of%20soap%20opera%29.md`
Total Lines: 100
Total Bytes: 5544
Showing lines 1 to 100
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
<truncated 2501 bytes>
  
64: *(Sincere, deeply philosophical)*  
65: You think I don't like Chekhov? I love Chekhov. But Chekhov doesn't pay my mortgage, and Chekhov isn't what a single mother working a 12-hour night shift wants to analyze at 8:00 PM. She doesn't want existential dread, kid. She wants... human truth. Raw, unfiltered emotion. What we do here... it touches people's actual lives.
66: 
67: *(The Novice Writer looks genuinely moved. He nods slowly, beginning to respect the man.)*
68: 
69: **CUT TO:**
70: 
71: ### INT. ON-SET MONITOR - NEXT DAY
72: 
73: A garish monitor screen playing raw, multi-camera footage. The lighting is harsh; the set looks like a cheap suburban living room.
74: 
75: **ON SCREEN:**  
76: *(A mother and father are screaming at a panicked, sweat-drenched PRIEST.)*
77: 
78: **FATHER**  
79: *(Veins popping in his neck)*  
80: Stay away from him, you sick freak! We know what you did to our boy!
81: 
82: *(Their 17-year-old SON steps between them with completely unearned, dramatic intensity.)*
83: 
84: **SON**  
85: *(Staring intensely into his parents' eyes)*  
86: Stop it! Mom, Dad... it wasn't him. It was *me*. I love Father Thomas.
87: 
88: *(Dead silence on set. The son turns, gazes tenderly at the middle-aged priest, takes his hand, and plants a passionate kiss on his lips. The priest looks visibly confused but accepts it. They walk off-camera hand-in-hand as the mother silently mouths 'Oh my God'.)*
89: 
90: **CUT TO:**
91: 
92: ### INT. CONTROL ROOM - CONTINUOUS
93: 
94: The Novice Writer and Veteran Writer stand side-by-side watching the playback. The Novice's mouth is slightly open in absolute horror, completely unable to process what he just watched.
95: 
96: The Veteran takes a slow sip of stale coffee, doesn't even blink, and checks his clipboard.
97: 
98: **VETERAN WRITER**  
99: *(Deadpan, totally business-as-usual)*  
100: Great. That covers the 4:00 PM slot. Let's write the focus group apology for Thursday.
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-23T19:11:03-06:00
Completed At: 2026-07-23T19:11:03-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/Ideas/TV Series Concept - "On Spec" (behind the scenes of soap opera).md. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -44,6 +44,12 @@
 * **Recurring Bit:** *Parks & Rec*-style emergency focus groups behind one-way mirrors.
 * Seeing both the absurdity of the common audience's demands (*"Why didn't the doctor use magic?"*) and the genuine emotional attachment viewers form with the archetypes.
 
+### 4. The Immortal Terminally Ill Character
+* **Setup:** A long-running character has been written as having a "highly aggressive, incurable, terminally terminal stage-4 brain tumor" for three full years.
+* **The Conflict:** The writers keep drafting emotional deathbed send-offs and dramatic funerals to wrap up the narrative. However, show producers repeatedly order them to undo/delay it because the character’s actor pulls massive ratings in the Midwestern demographic, or the character's merchandising (like a branded teapot line) is still selling out.
+* **The Result:** The writers are forced to invent increasingly absurd medical miracles, "alternative clinic" trips to outer Mongolia, misdiagnosed twin twists, or simply ignore the biological reality of time entirely to keep a dying character running laps on screen.
+
+
 ---
 
 ## Core Themes
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

I have successfully added your new idea to the [TV Series Concept - "On Spec" (behind the scenes of soap opera).md](file:///Users/matt/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/Personal/Ideas/TV%20Series%20Concept%20-%20%22On%20Spec%22%20(behind%20the%20scenes%20of%20soap%20opera).md) note.

### What Was Added:
* **The Immortal Terminally Ill Character:** Added a new standout scene/setup under Section 4 where a character has had an "aggressive, incurable, terminally terminal stage-4 brain tumor" for three full years. The writers keep scripting their demise, but production vetoes it due to strong ratings and commercial tie-ins (like branded teapots), forcing the writers to conjure up increasingly preposterous medical justifications to keep them alive and functional.

---
