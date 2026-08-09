# Userscripts Directory

**Path:** `/Users/matt/projects/userscript-bundler/userscripts`

This directory is the source folder for all browser userscripts that are watched and bundled by the `userscript-bundler` project. It contains important synchronization and enhancement scripts (e.g. `ai-os-context-sync.user.js`, `gemini.js`, `youtube-master.user.js`).

## ⚠️ The Gemini userscript in ai-os is a GENERATED file — DO NOT EDIT

`~/projects/ai-os/userscripts/gemini-DO-NOT-EDIT.js` is **NOT a source file**. It is a **symlink** to a **generated** file:

```
~/projects/ai-os/userscripts/gemini-DO-NOT-EDIT.js
    └── (symlink) → ~/projects/userscript-bundler/compiled/gemini-enhancements.user.js   [GENERATED]
```

### Where the real source lives

The source of truth for the Gemini enhancements userscript is the **numbered modules** in the bundler project:

```
~/projects/userscript-bundler/userscripts/gemini-enhancements/
    00-bootstrap.js
    01-shared.js
    02-token-usage.js
    03-timestamps.js
    04-sidebar-dates.js
    05-prompt-tools.js
    06-archive.js
    07-terminal.js
    08-model-optimizer.js
    09-page-observer.js
    10-tool-calls.js
```

### How to make changes (the ONLY correct way)

1. **Edit the source modules** in `~/projects/userscript-bundler/userscripts/gemini-enhancements/`.
2. **Rebuild** the compiled output:
   ```bash
   cd ~/projects/userscript-bundler && node bundler.cjs
   ```
   (An auto-watcher LaunchAgent `com.matt.agent.userscript-bundler` also rebuilds automatically on file changes.)
3. The compiled `gemini-enhancements.user.js` is regenerated **read-only** and carries a `GENERATED FILE — DO NOT EDIT` banner. The ai-os symlink picks up the new content automatically.

### Why it's impossible to edit by mistake

- The generated file is **read-only** (`chmod 0444`) after every build.
- It carries a prominent **GENERATED FILE — DO NOT EDIT** banner naming its source modules and rebuild command.
- The ai-os filename is literally `gemini-DO-NOT-EDIT.js`.

### How ai-os consumes it

`tauri-gui/src-tauri/src/main.rs` reads the symlink path and injects it as an initialization script into the `gemini_main` webview window. After changing the userscript you must **rebuild the Tauri app** for the change to take effect in the webview:

```bash
cd ~/projects/ai-os/tauri-gui && bun run build-macos
```
