---
title: "Find Mac Applications via Terminal"
date: "2026-08-13"
source: "gemini.google.com"
conversation_id: "cf856de9-52bd-537b-b569-934c7ad4a66a"
url: ""
---

# Find Mac Applications via Terminal

> [!NOTE]
> Archived Gemini Thread: [Find Mac Applications via Terminal]() | Date: 2026-08-13

## User
macos application browser

<!-- /gemini-message -->

---

<!-- gemini-message index=2 role=assistant timestamp="2026-07-12 21:53" -->

---

## Gemini
If you are looking to search or inspect the installed applications on your Mac via the terminal (or need a lightweight command to find out where an app is located), you can use the built-in `mdfind` utility or list the standard directories.

Per your system discovery preference, if you need to gather a quick list of all installed apps in your main application directories and copy it straight to your clipboard, you can run this command:

Bash

```
(ls -1 /Applications && ls -1 ~/Applications 2>/dev/null) | pbcopy

```


If you are looking for something else—such as a specific open-source app, an API definition for an asset browser inside an app project, or a terminal-based file/application launcher—let me know what you are building or trying to find!

<!-- /gemini-message -->

---

