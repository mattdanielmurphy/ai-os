---
title: "Agentic Harnesses with GUI"
date: "2026-08-07"
conversation_id: "5be8d8037669e20f"
source: "antigravity"
---

# Agentic Harnesses with GUI

## User

[Attached Context: Terminal & CLI Context]

```text

[Terminal & Local Execution Context]

Shell: Zsh on macOS (/bin/zsh)

Local Command Executor Service: http://127.0.0.1:3033/run-command

Headers: x-gemini-thread-saver-key (requires secret configuration)

Inline Terminal Sessions: tmux background sessions monitored via HTTP

```

What are the best custom minimalist agentic harnesses that have a robust GUI of some kind that isn't electron (web app is fine!)—the one exception is if it is a vscode fork or extension—and is ideally open source? I also need it to support agy as a provider. Needs to be solid, decently robust.

Does this exist?

Most important thing is it is a GUI wrapper for antigravity-cli. Does that exist?

---

## Assistant

Yes, this exists. Depending on how strictly you define "wrapper" versus "companion," there are a few robust options in the current ecosystem (as of August 2026) that avoid Electron and match your criteria for the `agy` (Antigravity CLI) provider.

1. The VS Code Extension: "Antigravity for VS Code"

Since you explicitly noted VS Code extensions as an exception, this is the most direct 1:1 GUI wrapper available for `agy`.

**What it is:** A community extension published by `lyadhgod` that embeds the Antigravity CLI directly into the editor.  
Visual Studio

**Features:** It provides a Material 3 Expressive chat panel, a slash-command navigator, interactive sessions, and native Google sign-in. It serves as the VS Code UI counterpart to the CLI, functioning similarly to the Claude Code marketplace extension.  
Visual Studio

2. The Open-Source Native App: Antigravity Manager

If you prefer a local-first, multi-agent desktop harness built outside of Electron, this open-source project uses a Tauri v2, React, and Rust stack.

**What it is:** A self-hosted desktop app (also known as Antigravity Tools) that acts as a proxy gateway and manager for Antigravity tools.  
SourceForge

**Features:** While it functions more as an account manager and token router rather than a pure conversational chat UI, it manages `agy` environments natively. It handles token proxying, multi-account rotation, and quota dashboards. The Tauri foundation keeps the application lightweight and cross-platform.  
LobeHub
+ 1

3. The Official Sibling: Antigravity 2.0 IDE

While this is a proprietary Google product and a full GUI application, it is built to operate in exact tandem with the CLI.

**The Connection:** Both the CLI and the GUI run on the exact same core agent engine, sharing all settings, permissions, and security configurations bidirectionally.  
Google Antigravity

**The Workflow:** If you are working in `agy` and a task becomes too complex for the terminal, you can type `/export`. This seamlessly pushes your active CLI session into the Antigravity 2.0 visual desktop environment to continue working with visual orchestration and project management.  
Google Antigravity

4. The Domain-Specific Open Source Tool: Open Design

If your agentic needs lean toward UI/UX, this is an open-source, local-first design agent.

**What it is:** A desktop app that wires Antigravity into a structured design workflow.  
Open Design

**Features:** It leverages the native multimodal capabilities of the Gemini 3.x models to read screenshots, reason about layout, and use an integrated browser to verify the UI it builds.  
Open Design

If you want a pure chat and agent UI wrapper for your daily coding, the VS Code extension is exactly what you are looking for. If you want to manage underlying `agy` processes in an open-source, non-Electron desktop environment, the Tauri-based Antigravity Manager is the closest architectural match.

---
