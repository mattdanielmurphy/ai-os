# Chrome tabs piling up (2026-10-27)

## 07:30 Research: what to do about Chrome tab pile-up

**Asked (via coordinator):** a solution for Chrome tabs piling up (mass-wake risk, RAM). Ideas: Claude closes tabs it's nearly sure you're done with, sorts by date and groups them; experiment with display styles; can an extension replace Chrome's vertical tab bar? Project freeze is on, so research and options only, no build.

### What I found on your Mac

- 70 tabs across 3 Chrome windows right now. 16 GB RAM, 29% free.
- Chrome 156 (new enough for native vertical tabs).
- **Auto Tab Discard is already installed**, so idle tabs can already be unloaded from RAM. Memory Saver is on Chrome's default setting.
- Nothing about tabs in ai-os IDEAS.md yet.

---

### Chrome now has native vertical tabs

Chrome shipped vertical tabs to stable in April 2026 ([TechCrunch](https://techcrunch.com/2026/04/07/chrome-is-finally-getting-vertical-tabs/), [Hongkiat](https://www.hongkiat.com/blog/chrome-vertical-tabs-reading-mode/), [Chrome Unboxed](https://chromeunboxed.com/google-is-officially-rolling-out-native-vertical-tabs-to-the-stable-version-of-chrome/)). Turn it on by right-clicking the tab strip and choosing **Show Tabs Vertically**. It works with tab groups.

---

### Extensions cannot replace the tab bar

No extension can remove or redraw Chrome's real tab strip. The closest an extension gets is the **side panel** (`chrome.sidePanel`), which can show its own tab list (grouped by date, by site, whatever) beside the page, while the real tabs stay where they are. That's how Tabs Outliner / "vertical tabs" extensions worked before Chrome shipped its own. So custom display styles are possible, but only as a side panel next to Chrome's own list. With native vertical tabs collapsed to icons, that's close to a replacement in practice.

What an extension *can* do: read every tab with its last-used time (`tab.lastAccessed`), close, move and group tabs (`chrome.tabs`, `chrome.tabGroups`), discard them to free RAM, and save a list before closing.

---

### Mass wake and RAM

Discarded tabs (Memory Saver, Auto Tab Discard) use almost no RAM and only reload when you click them. The real risk is a restart restoring lots of tabs at once; fewer open tabs is the only full fix, which is why auto-closing with a record matters more than discarding.

---

### Option 1: zero build, today

Turn on vertical tabs, set Memory Saver to Maximum (Settings > Performance), and keep Auto Tab Discard. Fixes RAM, doesn't stop the pile.

---

### Option 2: Tab Wrangler (existing, open source)

[Tab Wrangler](https://github.com/tabwrangler/tabwrangler) closes tabs you haven't touched for a set time (you pick, e.g. 1 day), never closes pinned or audio-playing tabs or a minimum count you set, and keeps every closed tab in a searchable list (its "corral") so anything can be reopened. That meets the "never close without a recoverable record" safety rule. No Claude judgment, just time-based. Nothing to build.

Rejected as main pick: OneTab (manual, one big dump), The Great Suspender (old one was malware; forks only suspend, don't close), Arc/Dia-style auto-archive browsers (would mean leaving Chrome; Arc is in maintenance mode).

---

### Option 3: Claude tidies your tabs (build after the freeze)

A small extension of your own plus a Claude pass:
- Extension exports open tabs (title, URL, last used, group) to a local file and can close/group on command.
- Once a day (or on demand), Claude reads that list and proposes: close (done with it), keep, or group (e.g. "Today / This week / Older", or by topic).
- Before closing anything it appends the tab to a closed-tabs archive (markdown, searchable by QMD), so nothing is lost.
- A side-panel view for trying display styles (by date, by site, by topic). Per the UI-options rule, that view would start as 3–4 separately made design options before any code.
Risk: Claude might close something you still wanted; the archive and a "suggest first, close later" first week cover that.

---

### Recommendation

Do Option 1 now (2 minutes, no build), try Option 2 for a week, and only build Option 3 if time-based closing feels too dumb. That respects the freeze.

Undo: all settings are toggles; Tab Wrangler uninstalls cleanly and its list can be exported first.
