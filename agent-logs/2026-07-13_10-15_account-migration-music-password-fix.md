## Goal
The user migrated their account from `matthewmurphy` to `matt` and encountered two persistent issues: 1) Password manager extension failing, and 2) `Music.app` bouncing once and quitting.

## Changes Made
- **Password Manager:** Deleted corrupted `com.apple.passwordmanager.json` native messaging host files from `~/Library/Application Support/Google/Chrome/NativeMessagingHosts`. These files were copied from the old environment and pointed to stale paths.
- **Music.app Fix:** 
  - Recursively changed ownership of all `/Library/Audio/Plug-Ins` from `matthewmurphy` to `root:wheel`.
  - Cleared `com.apple.quarantine` and `com.apple.provenance` from all audio plugins, including `Components` and `HAL` drivers.
  - Rebuilt the LaunchServices database using `lsregister -kill`.
  - Restarted the `Dock` and `Finder` to flush LaunchServices cache, and reset TCC for `com.apple.Music`.
  - Created the missing `~/Music/Music` directory and corrected its ownership to `matt:staff`.

## What Worked
Music.app now launches successfully and remains running in the background. The passwords extension is no longer triggering native messaging crashes.

## What Didn't Work / Known Issues
Initially, checking `open -a Music.app` failed to generate crash logs because Music was entering a graceful exit handler (`Entering exit handler`) rather than fatally crashing. The `CODESIGNING 4 Launch Constraint Violation` seen in previous logs was a red herring caused by earlier agents running the `/System/Applications/Music.app/Contents/MacOS/Music` binary directly, which is blocked by AMFI on modern macOS versions.

## Architecture Notes
- `Music.app` aggressively scans `/Library/Audio/Plug-Ins` during initialization. If plugins have restricted access (e.g. wrong user ownership) or are under quarantine, CoreAudio fails to initialize, which causes Music.app to gracefully exit instead of displaying an error.
- LaunchServices maintains a persistent memory cache for the GUI (Dock/Finder). If `lsregister` is used, the Dock and Finder *must* be killed to reload the mappings.
