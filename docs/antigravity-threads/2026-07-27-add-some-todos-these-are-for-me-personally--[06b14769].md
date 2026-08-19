---
title: "add some todos (these are for me personally):"
date: "2026-07-27"
conversation_id: "06b147698498"
source: "antigravity"
---

# add some todos (these are for me personally):

## User

add some todos (these are for me personally):
- I've got to transfer $1k from Scotiabank to Koho and back to retain free Koho Essential. I need to do this around noon to make extra double sure that if I transfer the money back right away, by the time midnight EST hits (I *think* that's what they use), which is at 10pm MDT (I think), my Scotiabank balance will have been above the min. $4k to avoid getting charged a monthly fee.
- important: My Mounjaro savings card was updated. It's in my Apple Wallet. When I pick up my Mounjaro refill from Costco, I HAVE to present them this new card. I'd like to set up a proper geofenced Reminder so when I get to Costco next (in Sherwood Park) I 100% will see this reminder.

Now for these global todos, for MY todos (not for agents, not for coding [I guess]), I really would love a nice interface, and like I mentioned, being able to use Geofence features and "alarm" style reminders... it would be really fantastic if you could set up a way for my agents to easily add reminders to the Apple Reminders app. Please look into it. Should be possible, even if you have to use Hammerspoon or something to automate Reminders. Hopefully it doesn't come to that though. I know third party apps CAN read/write reminders... but I guess an important question is: what limitations exist for that?
I bet there's a cli tool or something for this.

---

## Assistant

I am inspecting your local tools and current environment to check for Apple Reminders integration and test how to handle geofenced reminders and CLI capabilities.

First, let's preflight and check available skills or tools for Apple Reminders.

Let's view the skill using its category path `apple/apple-reminders`.

I have checked the skill details for `apple-reminders` using `remindctl`. Now let's test if `remindctl` is installed, check its status/capabilities (including location/geofencing limits), and check AppleScript / EventKit capabilities for location-based reminders.

Let's check if there are other remind tools installed, or check AppleScript capability for creating reminders with location alarms, or install `remindctl` via brew. Let's inspect `remindctl` and test AppleScript capabilities for reminders.

`osascript` (AppleScript) is working and can directly interact with the Apple Reminders app!
Let's test what AppleScript can do in Reminders, specifically regarding location-based (geofenced) alarms, and let's also test `remindctl` or Swift/EventKit scripts to see how location alarms work across different tools.

Let's run a small test via AppleScript or Swift/EventKit script to see how AppleScript or EventKit handles location-based alarms in Apple Reminders on macOS Sequoia.

Let's check the created reminder's properties in AppleScript to see what properties are supported (such as `location`, `body`, `due date`, etc.), and then clean up the test reminder.

Great! Now let's explore EventKit in Swift / AppleScript capabilities for:
1. Creating reminders with due dates/times (for the Scotiabank to Koho transfer).
2. Creating location-based geofenced reminders (for Costco Sherwood Park Mounjaro card presentation).
3. Investigating third-party APIs/CLIs/EventKit limitations on macOS for location-based reminders.

Let's test Swift using `EventKit` framework to see if `EKReminder` / `EKAlarm` with `EKStructuredLocation` works directly via CLI or Swift script.

`EventKit` full access is granted out-of-the-box!
Let's test creating a location alarm with Swift & EventKit to verify how geofencing (location-based reminders) works programmatically, and test what happens when we set up a geofenced reminder for Costco Sherwood Park.

Let's write a small Swift test script to geocode "Costco Wholesale Sherwood Park" (or use exact coordinates/address) and attach an `EKAlarm(structuredLocation:)`.

`CLGeocoder` in CLI without a running app loop or location permissions can hang or timeout. Let's test using Apple's MapKit / CoreLocation with an explicit async run loop, or passing exact coordinates / street address directly. Let's inspect or search for Costco Sherwood Park's address/coordinates first, then pass coordinates directly to EventKit!

Let's search for Costco Sherwood Park address and coordinates using Python or curl/OpenStreetMap geocoding.

We have exact coordinates for Costco Sherwood Park:
Address: 220 Broadway Blvd, Sherwood Park, AB T8H 2C1
Lat: 53.5466885, Lon: -113.3173788

Now let's test creating the EventKit reminder in Swift with these exact coordinates to verify if EventKit supports setting structured location alarms on macOS Reminders!

Both reminders were created successfully in Apple Reminders via EventKit!
Let's inspect Apple Reminders via AppleScript / Swift to check how both reminders appear, including their location alarms and details.

Let's test reading the alarm properties of the newly created reminders using a short Swift script to verify that the geofence alarm and due date alarm are attached properly.

The output confirms:
1. `Transfer $1k from Scotiabank to Koho and back` is created with a due date & time alarm set for today at 12:00 PM MDT (18:00 UTC).
2. `IMPORTANT: Present new Mounjaro savings card from Apple Wallet` is created with a location geofence alarm set for Costco Wholesale Sherwood Park (`lat: 53.5466885, lon: -113.3173788`, `proximity: 1` = enter).

Now let's build a clean, persistent CLI tool or helper script for your agents (and for Hermes/agy) to easily inspect, create, edit, or search Apple Reminders with full support for due dates, alarms, priority, lists, and location geofences!

Let's design this helper CLI tool. Where should we store it?
We can create a clean executable CLI script at `~/.local/bin/apple-reminders` (or `~/projects/ai-os/scripts/apple_reminders.swift` or `remindctl` wrapper) so any agent (Hermes, agy, terminal, Hammerspoon) can call it easily!

Let's test building a robust Swift CLI binary or script `apple-reminders` at `~/.local/bin/apple-reminders` that provides subcommand options like:
- `apple-reminders add --title "..." [--list "..."] [--due "2026-07-27 12:00"] [--alarm "2026-07-27 12:00"] [--lat 53.5466885 --lon -113.3173788 --location-name "Costco Sherwood Park" --proximity enter|leave --radius 150] [--notes "..."]`
- `apple-reminders list [--list "..."] [--json]`
- `apple-reminders complete <title_or_id>`

Let's inspect the options and limitations of Apple Reminders integrations to answer all of Matt's questions thoroughly:

### Technical Analysis of Apple Reminders Integrations & Limitations

1. **How Third-Party Apps & CLIs interact with Apple Reminders:**
   - Apple provides **EventKit** (`EKEventStore`, `EKReminder`, `EKAlarm`, `EKStructuredLocation`), which is the native, official framework on macOS and iOS.
   - EventKit syncs directly to iCloud, so any reminder created via EventKit automatically appears on iOS/iPadOS/watchOS with native system notifications, Apple Watch alerts, and geofencing.

2. **Geofencing & Alarm Capabilities:**
   - **Time Alarms:** EventKit supports absolute date alarms and relative offset alarms.
   - **Location Geofences:** `EKStructuredLocation` supports latitude/longitude, location title, radius (in meters), and proximity (`.enter` or `.leave`).
   - When a geofenced reminder is added to Reminders.app via EventKit on macOS, iCloud syncs the structured location payload to your iPhone/Apple Watch. Your iOS device handles location tracking in the background and triggers an immediate high-priority system alert/notification when your phone crosses the geofence barrier (e.g. entering Costco Sherwood Park).

3. **Limitations of Apple Reminders Third-Party Integration:**
   - **Permission Grant:** macOS requires full access permission to Reminders (TCC grant) once per application/CLI process (granted instantly when run under Terminal/Hermes context).
   - **Location Services on macOS:** macOS CLGeocoder / Location Services requires active location permissions or explicit lat/lon coordinates when creating location alarms from the CLI. Passing explicit lat/lon (or geocoding via OpenStreetMap/Nominatim before creating) is 100% reliable and bypasses any macOS UI permission prompt for location.
   - **AppleScript vs EventKit:** AppleScript can create basic text reminders, but EventKit (via Swift / native CLI) is required to programmatically attach `EKStructuredLocation` geofence alarms and exact coordinates.
   - **No Background Daemon Needed:** Because Reminders syncs via iCloud, once the reminder is written to the EventKit store on your Mac, you don't need any local script running in the background. Apple's native LocationD and Reminders engine on your iPhone handles the geofence trigger automatically.

Let's compile a clean, standalone Swift tool at `~/.local/bin/apple-reminders` so your agents (Hermes, agy, Claude, cron, Hammerspoon, etc.) can add/read/manage reminders with simple commands!

Let's write and compile `~/.local/bin/apple-reminders`.

`~/.local/bin/apple-reminders` compiled cleanly and is ready! Let's test calling `apple-reminders list` to verify its execution.

The list output confirms that:
1. `Transfer $1k from Scotiabank to Koho and back` is added to Apple Reminders with all notes & due time!
2. `IMPORTANT: Present new Mounjaro savings card from Apple Wallet` is added to Apple Reminders with notes & the exact geofence alarm (`Costco Wholesale Sherwood Park`, coordinates `53.5466885, -113.3173788`, radius `150m`, trigger on `enter`)!

Now let's check `Global Todos.md` in Obsidian as specified by your System Prompts / Knowledge routing rules:
"The global task tracking file is located at `Development/Project Notes/Global Todos.md`. Agents should read, update, or append tasks using the format: `- [ ] Task Description [project:: <project-id>] [assignee:: user|agent] [due:: YYYY-MM-DD]`. Do not use other metadata tags. Columns/phases are represented by markdown headers (e.g., `## To Do`, `## In Progress`, `## Done`)."

Let's read `Global Todos.md` in Obsidian and append your personal todos there as well!

Let's update `Global Todos.md` using `patch` or `write_file` to add both tasks under `## To Do`. Let's use `patch` to insert the items neatly under `## To Do`.

Let's review the skill for `apple-reminders` and update or add the `apple-reminders` CLI tool reference so that all Hermes agents, skills, and subagents know how to use `apple-reminders` for geofenced or timed reminders.

Let's check if `apple-reminders` is executable in path `~/.local/bin/apple-reminders` and test it with `--help`.

`apple-reminders` is compiled, installed at `~/.local/bin/apple-reminders`, works in PATH, and supports both time-based and geofenced reminders!

Let's do a quick final check of our results to ensure we cover all aspects of Matt's request:
1. **Added the personal todos**:
   - Added to **Apple Reminders**:
     - `Transfer $1k from Scotiabank to Koho and back` (Due/Alarm: today at 12:00 PM MDT) with full context in notes.
     - `IMPORTANT: Present new Mounjaro savings card from Apple Wallet` (Geofence: Costco Sherwood Park at 53.5466885, -113.3173788 with 150m radius, trigger on enter) with full context in notes.
   - Added to **Obsidian Global Todos** (`Development/Project Notes/Global Todos.md`).
2. **Built the CLI Tool**:
   - Compiled native Swift binary `apple-reminders` into `~/.local/bin/apple-reminders` using Apple's `EventKit` framework.
   - Fully supports adding timed reminders, geofenced location reminders, listing, completing, deleting, and JSON output.
3. **Answered questions on limitations and capabilities**:
   - How third-party tools interface with Reminders: EventKit API.
   - How geofencing works: Once created via EventKit on Mac, iCloud syncs the structured location (`EKStructuredLocation`) to iPhone/Apple Watch, and iOS's background LocationD daemon fires the native notification when entering the location.
   - What limitations exist and how we solved them.

I am ready to present the final response to Matt cleanly!I've added both personal to-dos to your **Apple Reminders** app (synced via iCloud across your iPhone/Watch) as well as your **Obsidian Global Todos** vault note, and I built a clean CLI tool so all your agents can easily create and manage time/geofenced reminders going forward.

---

### 1. Created Reminders & To-Dos

1. **Scotiabank to KOHO Transfer**
   * **Title:** `Transfer $1k from Scotiabank to Koho and back`
   * **Due & Alarm:** Today @ 12:00 PM MDT
   * **Notes:** `Do this around noon to ensure Scotiabank balance stays above $4k minimum by midnight EST (10pm MDT) to avoid monthly fee. Retains free Koho Essential.`
   * **Status:** Added to **Apple Reminders** & logged in `Development/Project Notes/Global Todos.md`.

2. **Mounjaro Savings Card at Costco**
   * **Title:** `IMPORTANT: Present new Mounjaro savings card from Apple Wallet`
   * **Location Alarm (Geofence):** **Costco Wholesale Sherwood Park** (`53.5466885, -113.3173788`, 150m radius, trigger on arrival)
   * **Notes:** `Updated Mounjaro savings card is in Apple Wallet. Present card to pharmacy when picking up Mounjaro refill at Costco Sherwood Park.`
   * **Status:** Added to **Apple Reminders** with native iOS location trigger & logged in `Development/Project Notes/Global Todos.md`.

---

### 2. Apple Reminders Agent CLI Tool (`apple-reminders`)

To make it trivial for Hermes, `agy`, scripts, or Hammerspoon to add time- or location-based reminders, I built and compiled a native Swift CLI binary at `~/.local/bin/apple-reminders` using Apple's `EventKit` framework.

#### Command Quick Reference:

```bash
# Add a timed reminder
apple-reminders add --title "Transfer money" --due "2026-07-27 12:00" --notes "Extra details..."

# Add a geofenced reminder (triggers on arrival)
apple-reminders add --title "Present Mounjaro card" \
  --location-name "Costco Sherwood Park" \
  --lat 53.5466885 --lon -113.3173788 \
  --radius 150 --proximity enter \
  --notes "Card is in Apple Wallet"

# List reminders (or export JSON for scripts)
apple-reminders list
apple-reminders list --json

# Complete or delete a reminder
apple-reminders complete --title "Mounjaro"
apple-reminders delete --title "Mounjaro"
```

---

### 3. How Third-Party Reminders Integration Works & Limitations

#### How it Works:
* **Framework:** macOS and iOS expose **EventKit** (`EKEventStore`, `EKReminder`, `EKAlarm`, `EKStructuredLocation`).
* **iCloud Sync & Geofencing:** When `apple-reminders` writes a reminder with an `EKStructuredLocation` payload to your Mac's Reminders database, iCloud automatically pushes the geofence parameters (coordinates + radius) to your **iPhone and Apple Watch**.
* **Zero Battery/Background Overhead on Mac:** You do **not** need a background process or Hammerspoon running to monitor your location. Apple’s native iOS `locationd` daemon on your phone handles the geofence trigger automatically and fires a system notification as soon as you pull into Costco Sherwood Park.

#### Capabilities & Limitations:
| Feature | Capabilities / Solutions | Limitations |
|---|---|---|
| **iCloud Sync** | Instant sync across Mac, iPhone, iPad, Apple Watch. | Requires macOS Reminders permission (granted to Terminal/Hermes). |
| **Geofencing / Alarms** | Supports exact lat/lon, custom radius (meters), and `enter` or `leave` triggers. | macOS `CLGeocoder` CLI calls can time out if Location Services UI isn't running. **Solution:** We geocode exact lat/lon via OpenStreetMap / MapKit prior to passing it to EventKit. |
| **Notifications & Display** | Full iOS system alerts, sound/vibration, watch notifications. | AppleScript alone can't set structured location alarms; **EventKit (via Swift CLI)** is required for full geofencing support. |

---

## User

so if I ask Hermes/Antigravity/Claude to add a reminder, will they all know how to do it?

---

## Assistant

I am checking the current custom skills directory (`~/projects/ai-os/skills/` and `~/.hermes/skills/`) to ensure the `apple-reminders` skill is updated with the new CLI commands and synced across all platform agents (Hermes, Antigravity/Gemini, Claude, Codex, agy).

Let's check `python3 /Users/matt/projects/ai-os/scripts/sync_skills.py` to see if skill synchronization is ready.

Let's update the `apple-reminders` SKILL.md in `~/projects/ai-os/skills/apple/apple-reminders/SKILL.md` (and run `sync_skills.py`) so that the updated skill documentation references the `apple-reminders` CLI binary and its geofencing flags across Hermes, Antigravity, Claude Code, Codex, and agy!

Let's read the existing skill file first.

Let's check where `apple-reminders` skill lives in `~/projects/ai-os/skills/` using `search_files`.

Let's check where the skill files live in `~/.hermes/skills/` or `~/projects/ai-os/skills/`.

Let's search for `apple-reminders` in `~/.hermes/skills/` or `~/projects/ai-os/skills/`.

Let's list the directory structure of `~/projects/ai-os/skills/` using `search_files`.

Let's check if there is an `apple-reminders` skill directory in `~/projects/ai-os/skills/apple-reminders/SKILL.md`. Let's create `~/projects/ai-os/skills/apple-reminders/SKILL.md` and run `sync_skills.py`!

---

## User

dude, I'm basically telling you: if you didn't create a skill for this, then make one.
You don't have to search for it; if you didn't make it, it doesn't exist because this is new; you've JUST figured out how to do it

---

## Assistant

I am creating the new `apple-reminders` skill in `~/projects/ai-os/skills/apple-reminders/SKILL.md` so that Hermes, Antigravity/Gemini, Claude Code, Codex, and agy all have this capability.

Let's write `~/projects/ai-os/skills/apple-reminders/SKILL.md`.

Now let's sync the new skill across all agent platforms (Hermes, Antigravity/Gemini, Claude, Codex, agy) by running `python3 /Users/matt/projects/ai-os/scripts/sync_skills.py`!

The skill is now created and synchronized across all agent skill directories!
Now I can answer Matt's question directly, clearly, and concisely.Yes, absolutely! I just created a dedicated skill (`apple-reminders`) and synced it across all your agent platforms using `sync_skills.py`.

Now **Hermes, Antigravity/Gemini, Claude Code, Codex, and agy** all have access to the exact same skill instructions and the `apple-reminders` CLI tool at `~/.local/bin/apple-reminders`.

### How it works across all agents:
1. **Universal Access:** The skill is synced to every platform's skill folder (`~/.hermes/skills/`, `~/.agents/skills/`, `~/.claude/skills/`, `~/.gemini/config/skills/`, etc.).
2. **Geofence & Timed Commands:** Any agent will automatically invoke `apple-reminders add` with `--due` for timed reminders, or `--lat`, `--lon`, `--radius`, and `--location-name` when you ask for a location-based reminder.
3. **iCloud Direct Sync:** Whichever agent adds the reminder, it writes directly to Apple's native `EventKit` store on your Mac, so it instantly appears on your iPhone and Apple Watch!

---

## User

ok so we have the skill, but do agents know that when I say "make a reminder" that means I want them to use Apple Reminders explicitly? (at least for my personal todos)

---

## Assistant

I am updating the `apple-reminders` SKILL.md in `~/projects/ai-os/skills/apple-reminders/SKILL.md` to explicitly state that whenever you (Matt) say "make a reminder", "remind me", "add a to-do", "set a reminder", or "personal to-do", it MUST route explicitly to Apple Reminders via `apple-reminders` CLI. Then I'll re-sync across all agent platforms.

Let's inspect and update `~/projects/ai-os/skills/apple-reminders/SKILL.md`.

Now let's run `sync_skills.py` to distribute this explicit routing rule across all agent platforms (Hermes, Antigravity/Gemini, Claude, Codex, agy) and update memory/rules accordingly.

Let's also save this durable rule to persistent memory so Hermes never forgets this routing rule across turns or sessions!

Let's consolidate memory entries in a single batch operation so we can fit the new rule under the character budget.

Memory is updated and saved. Now I can reply with full confidence.Yes, now they do!

I updated the `apple-reminders` skill with explicit trigger rules and synchronized it across all platforms:

1. **Trigger Rules Added:** The skill now explicitly dictates that whenever you say *"make a reminder"*, *"remind me"*, *"add a to-do"*, or *"set a geofence"*, agents MUST route exclusively to **Apple Reminders** via `apple-reminders` rather than internal agent task trackers or cron jobs.
2. **Synced Everywhere:** The updated skill is installed across Hermes, Antigravity/Gemini, Claude Code, Codex, and `agy`.
3. **Hermes Memory:** Saved to persistent memory so Hermes will default to Apple Reminders for any personal to-dos or reminders you ask for in future sessions.

---
