# Apple Music won't launch: evidence brief

Prepared 2026-10-20 for the follow-up fix thread. Prep only: nothing was changed, killed or disabled, and Music was not launched.

## TL;DR

- **Most likely cause: Supercharge 2's "Prevent Music app from opening" is switched on.** `defaults read com.sindresorhus.Supercharge` shows `preventMusicLaunch = 1`. Supercharge is running (login item).
- **The logs match that exactly.** The last logged launch (2026-10-16 13:37:29) ran for 0.45 s, connected to WindowServer, checked in with LaunchServices, and 20 ms later was ended by **SIGTERM** (`termination reported by launchd (2, 15, 15)`). No crash report. That's the "bounces once, no error" symptom: something outside Music terminated it, it didn't crash.
- **That's why the account migration didn't fix it.** The migration rsync copied every non-`com.apple.*` preference, so `com.sindresorhus.Supercharge.plist`, with the setting still on, came over to the new `matt` account.
- **The timeline fits.** Supercharge was installed 2026-04-25 (first real launch 2026-05-03, per its prefs), and Music first failed on 2026-05-15.
- **The May "code signing corruption" theory was a red herring.** That crash (`Launch Constraint Violation`) happened only because Music's binary was run directly from zsh in Warp. macOS 15 launch constraints kill first-party apps that aren't launched by launchd. Music's signature verifies fine today.

## Suggested first test for the fix thread (cheap and reversible)

1. Hold **Shift** while clicking Music. Supercharge's own help text says Shift bypasses the block. If Music opens, the cause is confirmed.
2. To fix it: Supercharge → Settings → turn off "Prevent Music app from opening" (there's also a "Prevent Music from showing in Dock recents" sub-option). If Matt still wants Play/Pause to not open Music, keep the setting on and use Shift whenever he really wants Music.
3. A fallback check if needed: quit Supercharge, then launch Music normally.

## Evidence

### System
- macOS 15.7.8 (24G824), Mac14,10, SIP enabled, Gatekeeper assessments **disabled** (`spctl --status`; not relevant to a first-party app, but worth knowing).
- `/System/Applications/Music.app` is version 1.5.6, and `codesign --verify --strict` passes.
- LaunchServices has one registration for `/System/Applications/Music.app`, plus a **Safari web app** at `~/Applications/Apple Music.app` (`com.apple.Safari.WebApp.8CC1…`, created 2026-08-06). Spotlight or Raycast searches for "Apple Music" may open that web app instead of Music.app, so name the real app when testing.

### Crash/diagnostic reports
- No Music-related `.ips`/`.crash` files in `~/Library/Logs/DiagnosticReports` or `/Library/Logs/DiagnosticReports` (Retired included). That's consistent with SIGTERM, which doesn't produce a crash report.

### Unified log (`/usr/bin/log show --last 7d`; note that `log` is shadowed in Matt's zsh, so use the full path)
Only one Music app launch was logged in 7 days (2026-10-13 → 10-20):

```
13:37:29.245 runningboardd  LS launch com.apple.Music (originator CoreServicesUIAgent)
13:37:29.270 runningboardd  Now tracking process … Music :70984
13:37:29.275 loginwindow    App: Music, ready
13:37:29.668 Music[70984]   SkyLight server port …          (only 2 lines from Music itself)
13:37:29.698 launchservicesd CHECKIN … 70984 com.apple.Music
13:37:29.718 runningboardd  … :70984] termination reported by launchd (2, 15, 15)   ← SIGTERM
13:37:29.724 loginwindow    App: Music, quit
```

The kill lands right after the LaunchServices check-in. That's when an app watching `NSWorkspace.didLaunchApplication` would see Music and terminate it. The log doesn't name the sender of the signal.

Music's background pieces are fine: `MusicCacheExtension`, `AMPDeviceDiscoveryAgent` and `mediaremoted` run normally.

### Supercharge (strings from the app binary)
> Prevent Music app from opening. Stops the Music app from opening when you don't want to. For example, when Play/Pause is pressed on your keyboard or AirPods. This also prevents the Music app from launching normally. You can hold Shift to allow launching it. Optionally launch another app instead (for example, Spotify).

Pref keys present: `preventMusicLaunch = 1`. Version 1.26.0-macos15. The plist was last written 2026-10-20 13:28.

### Other things checked (nothing Music-related found)
- **Hammerspoon** (`~/.hammerspoon`): nothing kills or quits Music.
- **Keyboard Maestro**: the only Music macro is an inactive "Copy Link" menu macro, and the only force-quit macros target Lunar and Session.
- **Login items**: Alfred 5, Yoink, Keyboard Maestro Engine, Blip, Shottr, Raycast, Rectangle, **Supercharge 2**, Hammerspoon, DarkModeBuddy, CodexBar, TypeWhisper, Amphetamine, SoundSource, AirFidelity, Flux, rcmd, AlDente, Claude, Paletro, TypedRecall, Bartender 5.
- **User LaunchAgents**: about 37 entries, almost all `com.matt.agent.*` dev services, plus loopbackd, maestral, puma-dev, mutagen, nginx, postgres, Pieces. None mention Music.
- **/Library/LaunchAgents**: Little Snitch, Arturia, Adobe ARMDC, Jump Connect, Rogue Amoeba arkaudiod, Zoom.
- **/Library/LaunchDaemons**: Little Snitch, Arturia, Adobe, AlDente helper, iStat, Docker, QSpace, **CleanMyMac5 Agent**, Microsoft AutoUpdate, Jump Connect, `com.user.networkswitch`, Zoom.
- **Droppy** (`iordv.Droppy`, running, `appleMusicTracked = 1`) reads now-playing through a MediaRemote perl adapter. It's a weak suspect only.

## History of earlier attempts (all before this brief)

| Date | Where | What was tried / concluded |
|---|---|---|
| 2026-05-15 | Gemini thread "who sells drizzilicious in ft sask?" (`70b3ba686605cb8c`) | First report. Reset the audio service, `killall Music …Extension`, Option-launch for a new library, wiped Music caches/containers/prefs (`defaults delete com.apple.Music`), `lsregister -kill -r`, `killall mediaremoted`, wiped `com.apple.security.*` prefs, logged out. Ran the binary from zsh, which gave `SIGKILL (Code Signature Invalid)` / `Launch Constraint Violation`. Gemini blamed dyld/SSV corruption and suggested `update_dyld_shared_cache` / a macOS reinstall; Matt declined. |
| 2026-05-23 | Gemini thread (`aa884281c732e323`) | "I restarted eventually and Music.app launched again. But some time later... failing to launch again." Gemini repeated the AMFI/code-signing theory. |
| 2026-06-02 | Gemini thread "restore ipad air…" (`8ccf5b427967b0bc`) | Music still dead. Also AlDente's helper and Jump Desktop Connect break on every reboot. Gemini suggested cache/pref resets and an in-place reinstall. |
| 2026-06-07 | Gemini thread (`2ccfef3bac7fa7d6`) | LaunchServices rebuild and a codesign check suggested. Matt couldn't add local albums without Music. |
| 2026-07-04 → 07-10 | Gemini `b689d8fbef33802f`, Antigravity "System Audit Migration Bridge" (`d8887a58…`), Claude desktop `20260710_153927_4ab627` | Migrated `matthewmurphy` → new `matt` account, with Music.app not launching as one of the stated reasons. See below. |

Search with `python3 ~/projects/ai-os/scripts/threads.py search "<words>"`. Nothing relevant turned up in the Obsidian vault or the ai-os journals.

## What the account migration carried over
From `/Users/Shared/MigrationBridge/MIGRATION_STATUS.md` and `migrate_app_settings.sh`:
- `rsync -a --exclude="com.apple.*"` of `~/Library/Preferences` and `~/Library/Containers`. **All third-party prefs came along, Supercharge's included.**
- Shell config, `.ssh`, `.gitconfig`, `.tmux.conf`; custom `com.matthewmurphy.*` LaunchAgents with paths rewritten; Raycast via `.rayconfig`; CloudMounter app support; selected Apple prefs (trackpad, symbolichotkeys, Dock/Finder, `.GlobalPreferences`).
- TCC was left behind on purpose (fresh permissions). Everything was `chown`ed to `matt:staff`.
- The old `/Users/matthewmurphy` no longer exists.

## Hypotheses, ranked by evidence

1. **Supercharge "Prevent Music app from opening" is on (very likely).** The pref is set, the app is running, and the symptom matches: an external SIGTERM right after check-in with no crash report. The dates line up (installed 3 weeks before the first failure), and the migration copied the pref. The temporary "fix" after a restart in May would fit if Supercharge hadn't been relaunched or the toggle was off then. Test: Shift-launch.
2. **Another app terminates Music on launch (unlikely).** Droppy (MediaRemote tracking), CleanMyMac5's agent, AirFidelity, rcmd. No prefs or config point at Music except Droppy's tracking flag. Check only if hypothesis 1 fails: with Supercharge quit, launch Music and look for the same `(2, 15, 15)`.
3. **Corrupted Music library or prefs (unlikely).** That would show up as a crash or hang, not a SIGTERM. Option-launch to a fresh library was already tried in May without success.
4. **System volume / code-signing / dyld corruption (ruled out).** The signature verifies, and the only launch-constraint crash came from running the binary from a shell, which macOS 15 blocks by design. No reinstall is needed.

Separate issue, not this bug: AlDente and Jump Desktop helpers dying at reboot was the other reason for the migration. `/Library/LaunchAgents/com.p5sys.jump.connect.agent.plist` was rewritten 2026-10-19. Not investigated here.

## Raw evidence (local, gitignored)
`~/projects/ai-os/tmp/music/`: `log_7d.txt` (7-day filtered log), `log_oct16_window.txt` (every process ±1.5 s around the launch), thread dumps for each thread listed above, `km.xml` (Keyboard Maestro macros export).
