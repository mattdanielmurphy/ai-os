---
title: "livebench userscript doesn't work. probably trying to inject too early"
date: "2026-07-27"
conversation_id: "c25d4c565ec2"
source: "antigravity"
---

# livebench userscript doesn't work. probably trying to inject too early

## User

livebench userscript doesn't work. probably trying to inject too early before everything is loaded fully

---

## Assistant

I will inspect the workspace files in `/Users/matt/projects/userscript-bundler` to locate the `livebench` userscript.
I will search for occurrences of "livebench" in the workspace to locate the source code or metadata for the userscript.
I will list the contents of the `userscripts` directory to find the userscript files.
I will list the contents of `userscripts/gemini-enhancements` to see if the livebench userscript resides there.
I will search case-insensitively for "livebench" across the entire repository.
I will view the `script_manifest.json` file to check the list of configured userscripts and find where the livebench script is defined.
I will run a command to search for any files containing "livebench" under `~/projects/` to locate the correct repository or file.
I am waiting for the file search to complete so we can locate the livebench userscript.
I found the userscript at `/Users/matt/projects/ai-os/userscripts/livebench-frontier.js`. I will view its contents to understand how it's currently injecting and what could be causing the early injection issue.
I will view the `modern-web-guidance` skill file to ensure we are using modern web development best practices for monitoring dynamic page updates in userscripts.
I will search the `modern-web-guidance` tool for best practices on observing dynamic DOM content in frontend scripts.
I will check `~/projects/ai-os/docs/MAC_ENVIRONMENT.md` to find out how Node.js and fnm/nvm are configured in this environment.
I will check where `npx` is located by running zsh as a interactive login shell to load the profile/rc files.
I will run the modern web guidance search using the interactive login shell where `npx` is available in the path.
I will search the `userscripts` directory to see if there are any existing helper patterns or userscripts using `MutationObserver` or selectors to wait for elements.
I will update `/Users/matt/projects/ai-os/userscripts/livebench-frontier.js` to wrap the performance peak calculation and styling in a `MutationObserver` and run it on page changes. I will also make the cell text parser resilient to pre-existing delta spans when recalculating.
I will search the `ai-os` repository for references to `livebench-frontier` to verify if it needs to be compiled or bundled, or if it runs as a standalone script.
I will list the contents of the main `ai-os` project directory to check for configuration files and build scripts.
I will list the contents of `/Users/matt/projects/ai-os/userscripts` to see what files exist in that directory and if there is a build or manifest file.
I will read the `package.json` file in `ai-os` to check if there are any build or packaging scripts defined for userscripts.
I will view `package.json` in the active workspace (`userscript-bundler`) to see its dependencies and configured scripts.
I will view `CLAUDE.md` in the `ai-os` project to see if there are any specific guidelines or information regarding userscripts or livebench.
I will run the project's preflight script to ensure all local rules, quotas, and git settings are properly synced.
I will run the project's auto-commit tool in the `ai-os` directory to package, commit, and push the userscript fix.
I will check the status of the `userscript-bundler` repository to make sure everything is clean there.
I have fixed the early injection issue in the LiveBench userscript at [/Users/matt/projects/ai-os/userscripts/livebench-frontier.js](file:///Users/matt/projects/ai-os/userscripts/livebench-frontier.js).

### Summary of Changes:
1. **MutationObserver Integration**: Wrapped the styling and peak calculation logic in a `MutationObserver` that watches the page for dynamic content updates (like data table rendering or tab switching).
2. **Infinite Loop Prevention**: The observer is temporarily disconnected before updating the DOM (adding `.delta-value` spans and styling cells) and reconnected immediately afterward to prevent self-triggering loops.
3. **Robust Re-Runs (Clone & Strip)**: 
   - Before evaluating column metrics, it clones cells and strips any existing `.delta-value` spans. This ensures that repeated run-cycles do not read previously appended text and break number parsing.
   - It removes old delta spans from the live DOM before appending new ones.
4. **Execution Triggers**: Hooks into both direct execution (if the DOM is already ready) and `DOMContentLoaded` listeners.
5. **Git Synchronization**: Ran the pre-flight check and committed/pushed the changes automatically to the remote repository.

---
