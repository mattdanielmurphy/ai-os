---
title: "Troubleshooting Chrome Duplicate Entry"
date: "2026-08-14"
conversation_id: "f40b4f92-3cb6-4d79-87ec-b3baef74407c"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100%; max-width: 100%; min-width: 0; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 2.5rem 1.25rem; scrollbar-width: thin;">

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Yep, fix it.

</span>



<span title="Responded at 5:51am" style="display: block; width: fit-content; max-width: 90%; min-width: 0; margin-right: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

I am cleaning up the duplicate bundle and rebuilding your macOS LaunchServices cache now. I will let you know as soon as it completes.

Still rebuilding the LaunchServices database. Waiting a few seconds for it to finish...

LaunchServices is actively reindexing the system domains. Waiting for it to finish...

The fix has been completed:

1. **Updated `rcmd` Configuration**:
   Changed the `c:` shortcut binding in [`~/.config/rcmd/config.yaml`](file:///Users/matt/.config/rcmd/config.yaml#L13) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.config/rcmd/config.yaml%3A13) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.config/rcmd/config.yaml) to point cleanly to `/Applications/Google Chrome.app`.
2. **Removed Stale App Bundle**:
   Safely moved `/Applications/Google Chrome Fixed.app` to your Trash (`~/.Trash/`).
3. **Rebuilt macOS LaunchServices**:
   Rebuilt the system LaunchServices database (`lsregister`) across local, system, and user domains to flush cached app associations.

Applications and window switchers will now only recognize and launch the official **Google Chrome**.

---

Current Thread: [thread.md](file:///Users/matt/.gemini/antigravity/brain/f40b4f92-3cb6-4d79-87ec-b3baef74407c/thread.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/f40b4f92-3cb6-4d79-87ec-b3baef74407c/thread.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/f40b4f92-3cb6-4d79-87ec-b3baef74407c/thread.md)

**Thread Metrics:**

| Total Tokens | Cache Expiry | Financial Rotation | Perplexity Quota |
| :--- | :--- | :--- | :--- |
| ~47k | 12:50am | ~47k / ~376k 🟢 | 90, 20 🔬, 8 📤 |

</span>



</span>

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Can you figure out why I have Google Chrome and "Google Chrome fixed"? Two separate applications and when i delete google chrome fixed it replaces itself. And when I launch Chrome, it says it's Google Chrome fixed. Or like, when other applications show me a list of active applications, it says Google Chrome fixed instead of Google Chrome.

</span>



<span title="Responded at 5:48am" style="display: block; width: fit-content; max-width: 90%; min-width: 0; margin-right: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

Here is what is happening on your system:

---

### 1. Where "Google Chrome Fixed" Came From
On **July 15, 2026**, a terminal command was executed to create an untracked copy of Chrome:
```bash
rsync -a /Applications/Google\ Chrome.app/ /Applications/Google\ Chrome\ Fixed.app/
```
Both bundles ended up living simultaneously inside `/Applications/`:
- `/Applications/Google Chrome.app` (currently updated to version `151.0.7922.138`)
- `/Applications/Google Chrome Fixed.app` (older copy at version `150.0.7871.182`)

---

### 2. Why It Appears as "Google Chrome Fixed" in Other Apps
Two things are causing other apps to show and launch the fixed version:

1. **`rcmd` App Configuration**:
   In your `rcmd` config ([`~/.config/rcmd/config.yaml`](file:///Users/matt/.config/rcmd/config.yaml#L15) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.config/rcmd/config.yaml%3A15) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.config/rcmd/config.yaml)), the shortcut **Right-Command + C** is explicitly configured to launch `/Applications/Google Chrome Fixed.app`:
   ```yaml
   c: {app: /Applications/Google Chrome Fixed.app, launchIfNotRunning: true, whenAlreadyFocusedAction: FollowGlobal}
   ```
2. **macOS LaunchServices Database**:
   Both apps share the identical macOS bundle identifier (`com.google.Chrome`). When two apps share the same bundle ID, macOS registers both paths in its internal LaunchServices database (`lsregister`), causing window switchers, process monitors, and app menus to display the cached label (`Google Chrome fixed`).

---

### 3. Why It Seemed to "Replace Itself"
- **GoogleUpdater (Auto-Update)**: Chrome's background updater regularly updates `/Applications/Google Chrome.app`, but `/Applications/Google Chrome Fixed.app` remained pinned to the older build.
- **Shortcuts & Launchers**: Launching via `rcmd` or stale app shortcuts would re-open or trigger the secondary app bundle.

---

### Recommended Fix

If you'd like, I can apply this fix right away:

1. **Update `rcmd` config**: Change the `c:` mapping in [`~/.config/rcmd/config.yaml`](file:///Users/matt/.config/rcmd/config.yaml) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.config/rcmd/config.yaml) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.config/rcmd/config.yaml) from `Google Chrome Fixed.app` to `/Applications/Google Chrome.app`.
2. **Move to Trash**: Safely move `/Applications/Google Chrome Fixed.app` to `~/.Trash/`.
3. **Rebuild LaunchServices**: Reset the LaunchServices database so macOS completely purges the "Google Chrome fixed" registration:
   ```bash
   /System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -kill -r -domain local -domain system -domain user
   ```

Let me know if you would like me to execute these steps!

---

Current Thread: [thread.md](file:///Users/matt/.gemini/antigravity/brain/f40b4f92-3cb6-4d79-87ec-b3baef74407c/thread.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/f40b4f92-3cb6-4d79-87ec-b3baef74407c/thread.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/f40b4f92-3cb6-4d79-87ec-b3baef74407c/thread.md)

**Thread Metrics:**

| Total Tokens | Cache Expiry | Financial Rotation | Perplexity Quota |
| :--- | :--- | :--- | :--- |
| ~42k | 12:50am | ~42k / ~376k 🟢 | 90, 20 🔬, 8 📤 |

</span>



</span>

</span>