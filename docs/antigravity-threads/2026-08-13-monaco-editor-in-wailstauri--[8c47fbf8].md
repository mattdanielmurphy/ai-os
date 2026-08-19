---
title: "Monaco Editor in Wails/Tauri"
date: "2026-08-13"
conversation_id: "8c47fbf8-42fe-5bb9-8504-7d406d99af94"
source: "antigravity"
---

# Monaco Editor in Wails/Tauri

## USER_EXPLICIT (2026-08-13T18:54:11.021052)

is there a project that uses Monaco editor in Wails/Tauri?

<!-- /gemini-message -->

---

<!-- gemini-message index=2 role=assistant timestamp="2026-07-13 17:38" -->

---
## MODEL (2026-08-13T18:54:11.021056)

Yes, there are several open-source projects that successfully pair the Monaco Editor (the editor engine behind VS Code) with either **Wails** (Go-based) or **Tauri** (Rust-based) backends.  
GitHub

Because both Wails and Tauri use the operating system’s native webview to render the frontend, integrating Monaco is highly feasible.  
GitHub

Projects Using Monaco Editor with Wails (Go)
1. **monaco-notepad** (by Jun-Murakami)

A programmer's notepad designed specifically around the Monaco Editor.  
GitHub

**The Stack:** Go (Wails) + React.

**Key Features:** It functions as a local file editor that can also convert files to cloud notes synced via Google Drive. It relies heavily on Monaco for theme switching, auto-saving, and syntax highlighting.  
GitHub
+ 1

**Repository:** Jun-Murakami/monaco-notepad  
GitHub

2. **XenSQL** (by Bare7a)

A local-first, fast SQL workbench.

**The Stack:** Go (Wails v3) + React & TypeScript.  
GitHub

**Key Features:** Uses Monaco Editor to drive a full, IDE-like SQL writing experience complete with custom dark/light themes and multi-statement script execution.  
GitHub

**Repository:** Bare7a/XenSQL  
GitHub

3. **GoNavi** (by Syngnat)

A modern, high-performance database client.  
GitHub

**The Stack:** Go (Wails v2) + React, TypeScript, and Ant Design 5.  
GitHub

**Key Features:** Utilizes Monaco Editor as its SQL editing core, supporting multi-tab query workflows.  
GitHub

**Repository:** Syngnat/GoNavi  
GitHub

Projects Using Monaco Editor with Tauri (Rust)
1. **Mark-us-Down** (by col000r)

A fast, lightweight Markdown editor with a live preview.  
GitHub

**The Stack:** Rust (Tauri 2) + React & Vite.  
GitHub

**Key Features:** Employs Monaco Editor to handle syntax highlighting for the Markdown editor pane while maintaining rapid, native performance compared to heavy Electron alternatives.  
GitHub

**Repository:** col000r/Mark-us-Down  
GitHub

2. **montauri-editor** (by TimSusa)

A dedicated, lightweight cross-platform text editor.  
GitHub

**The Stack:** Rust (Tauri) + HTML/CSS/JS.  
GitHub

**Key Features:** Built specifically to demonstrate and utilize Monaco Editor directly inside a minimalist Tauri-wrapped container.

**Repository:** TimSusa/montauri-editor  
GitHub

Pro-Tip for Integrating Monaco in these Frameworks

When bundling Monaco Editor in a Wails or Tauri project, the biggest hurdle is usually the **Web Workers** that Monaco uses for language services (like CSS, HTML, and TypeScript validation).

If you use a bundler like **Vite** (which is default for many Tauri/Wails templates), you will want to use the official Vite plugin:

Bash

```
npm install vite-plugin-monaco-editor --save-dev

```


And configure your `vite.config.ts` to prevent the bundler from getting tripped up by the webview environment's asset loading restrictions.

<!-- /gemini-message -->

---

<!-- gemini-message index=3 role=user timestamp="2026-07-13 17:39" -->

---
## USER_EXPLICIT (2026-08-13T18:54:11.021057)

What's the editor closest to the features of VSCode that's made in either Tauri or Wails (slightly preferred) and is still in active development or is really robust?

Crucially all the vscode keybindings must remain.

<!-- /gemini-message -->

---

<!-- gemini-message index=4 role=assistant timestamp="2026-07-13 17:39" -->

---
## MODEL (2026-08-13T18:54:11.021058)

If you want an editor that strictly retains **all of VS Code’s default keybindings** while being built on a lightweight, native-webview framework (like Tauri or Wails), there is one clear, standout project that fits this exact description: **SideX**.  
GitHub

The Standout: **SideX** (Tauri + Rust Backend)

**SideX** is literally **VS Code rebuilt on Tauri**.  
GitHub

Rather than building a brand new editor from scratch and attempting to mimic VS Code, the developers of SideX took VS Code's open-source core (`Code - OSS`) and mapped its entire Electron-based architecture directly onto Tauri and Rust:  
GitHub

**Frontend:** It uses a direct port of VS Code's TypeScript workbench. Because the UI layer remains identical to VS Code, **every single default VS Code keybinding, shortcut, and command palette interaction works out of the box.**  
GitHub

**Editor Core:** It relies on the native Monaco Editor (which is the exact text engine inside VS Code).

**Backend:** Replaces Node.js with a highly optimized Rust backend. It handles file I/O, terminal PTY, search indexing, and Git integration natively in Rust.  
GitHub

Current Status (as of Mid-2026)

SideX is under active, heavy development. It was launched in early 2026 to significant developer interest, with commits actively rolling in.

**What's highly robust:** Standard editing, file trees, file watching, the integrated terminal (mapped via Rust’s `portable-pty`), Git diffing, and core configurations.  
GitHub

**What is still in progress:** The full-featured extension host (though they are actively implementing support to load extensions via Open VSX).

Why Wails Projects Don't Quite Fit This Spec (Yet)

While Wails is fantastic for desktop applications (and there are great text editors built on it, like *monaco-notepad*), you will run into major limitations if you want "closest to VS Code features" out of them:

**Feature Gap:** Most Wails-based editors are single-file text editors or SQL-centric workbenches (like XenSQL). They do not possess a multi-file sidebar explorer, workspaces, split-panes, or full command-palette search.

**Keybinding Porting:** Implementing the vast list of VS Code shortcuts manually in a custom Wails editor is a massive undertaking that most indie devs skip, usually only implementing basic shortcuts (like `Cmd/Ctrl + P` for file search, or `Cmd/Ctrl + F` for find).

Because SideX actually ports the VS Code TypeScript workbench over to Tauri, it is the only project in this class where you won't have to manually re-map your muscle memory.  
GitHub

Want instructions on how to build and run SideX locally?
Yes

<!-- /gemini-message -->

---
