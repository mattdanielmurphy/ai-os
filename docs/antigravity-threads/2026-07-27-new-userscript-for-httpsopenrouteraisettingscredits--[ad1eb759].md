---
title: "new userscript for https://openrouter.ai/settings/credits:"
date: "2026-07-27"
conversation_id: "ad1eb7595813"
source: "antigravity"
---

# new userscript for https://openrouter.ai/settings/credits:

## User

new userscript for https://openrouter.ai/settings/credits:
(function() {
  // Select the input container using its unique class list
  const container = document.querySelector('.flex.h-10.items-center.overflow-hidden.rounded-md.border.border-input');
  
  if (container && !document.getElementById('service-fee-reminder')) {
    // Create the reminder element
    const reminder = document.createElement('div');
    reminder.id = 'service-fee-reminder';
    reminder.textContent = '💡 Reminder: Flat $0.80 service fee. Adding small amounts (like $5) is less cost-effective!';
    
    // Style the reminder to fit the UI
    Object.assign(reminder.style, {
      fontSize: '12px',
      color: '#d97706', // Amber/Orange color for warning
      marginTop: '6px',
      fontWeight: '500',
      fontFamily: 'inherit'
    });

    // Insert it immediately after the input container
    container.parentNode.insertBefore(reminder, container.nextSibling);
  }
})();

Of course the container is summoned by me pressing `<button type="button" class="inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-button font-medium cursor-pointer transition-colors focus-visible:outline-none focus-visible:border-focus-border focus-visible:shadow-focus disabled:pointer-events-none disabled:opacity-50 [&amp;_svg]:pointer-events-none [&amp;_svg]:size-4 [&amp;_svg]:shrink-0 bg-primary text-primary-foreground hover:bg-accent-hover active:bg-primary/80 h-10 px-4 py-2 relative w-full">Add Credits</button>`, so you can't just look for it and try to inject on LOAD. You have to watch for DOM changes.

---

## Assistant

Let me check the project structure first to understand conventions.

Let me look at existing userscripts that already use MutationObserver, and the bundler structure

Let me check the bundler and script manifest to see the conventions for standalone `.user.js` files:

Let me check the bundler to understand the standalone compilation format

Now I have the full picture. Let me create the userscript with the MutationObserver pattern and register it.

Now register it in the manifest:

Now let me run the bundler to compile it:

The bundler compiled successfully — your new script was picked up as script 20/21. Let me verify the file looks right

Done. Here's what the script does differently from your original:

**Key change — DOM watcher instead of one-shot:**
- A `MutationObserver` watches `document.body` with `{ childList: true, subtree: true }` so when the "Add Credits" button dynamically inserts the credit input modal, the observer fires and injects the reminder
- Still does an initial `injectReminder()` call on load in case the modal is already open
- Guarded by `document.getElementById('or-service-fee-reminder')` so it never duplicates, even during rapid mutations

**Other tweaks from your snippet:**
- Changed the reminder `id` from `service-fee-reminder` to `or-service-fee-reminder` — avoids potential collisions with other plugins
- Registered in `script_manifest.json` and compiled into the bundle via the bundler

**To install:**
**Option A** (via the bundle): The bundler wrapped it into `userscript_bundle.js` — if you already have the loader userscript in Tampermonkey with `@require file:///.../userscript_bundle.js`, it'll auto-activate on `https://openrouter.ai/settings/credits`.

**Option B** (standalone): Copy the file into Tampermonkey as a new script — it's fully self-contained (`@grant none`), no external deps. The file is at `file:///Users/matt/projects/userscript-bundler/userscripts/openrouter-credit-reminder.user.js`.

---
