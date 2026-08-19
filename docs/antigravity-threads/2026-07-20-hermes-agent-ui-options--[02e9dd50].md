---
title: "Hermes Agent UI Options"
date: "2026-07-20"
conversation_id: "02e9dd506f2319bb"
source: "antigravity"
---

# Hermes Agent UI Options

## User

acp-compatible agent uis for macos/web?

I want to control Hermes agent.

Zed's isn't so bad.

I don't want ANYTHING electron.

---

## Assistant

If you want to control the **Nous Research Hermes agent** stack without touching a single megabyte of Electron bloat, you have a few excellent native macOS and web-based options.

Since you appreciate Zed's native performance, you'll want to lean into architectures that leverage the browser you already have open or use Apple's native rendering primitives.

1. The Native macOS Route: `hermes-swift-mac`

If you want a dedicated desktop window rather than a browser tab, this is exactly what you are looking for.

**The Stack:** Written natively in Swift using Apple's `WKWebView`.

**Why it fits your rules:** Zero Electron. It acts as a hyper-lightweight native wrapper around the Hermes Web UI.

**Key Perks:** Because it's a true macOS app, it integrates directly with macOS system notifications (notifying you when long-running agent loops complete), properly requests system microphone permissions for voice mode, and includes an elegant, built-in menu bar toggle for SSH tunneling if you are running Hermes on a remote machine or homelab box.

2. The Pure Web Route: `hermes-webui`

The official browser-based interface for the Hermes agent stack.

**The Stack:** Lightweight frontend, completely runtime-agnostic, served via a local Python/Shell bootstrapper.

**Why it fits your rules:** It lives entirely inside Safari or your browser of choice.

**Key Perks:** It delivers near 1:1 feature parity with the raw Hermes CLI. You get a clean, dark-themed UI that tracks tool-call cards, handles workspace project trees, displays inline file previews, and manages persistent agent memory sessions.

3. The Power-User Control Plane: `hermes-control-interface` (HCI)

If you are scaling past a single chat window and running automated tasks or agent teams.

**The Stack:** Node.js, WebSockets, and Vanilla JS.

**Why it fits your rules:** A self-hosted web dashboard accessible via any browser.

**Key Perks:** This is a comprehensive operational UI. It gives you a multi-panel "ZOO Swarm Monitor," a Kanban board for tracking agent tasks, token analytics, a browser-based terminal, and a full control plane to start, stop, and configure your **MCP (Model Context Protocol) servers** directly from the UI.

4. The "Zed-Adjacent" Option: `hermes --tui`

If you like Zed's vibe, you might not even need a browser. Hermes ships out-of-the-box with a modern **Terminal User Interface (TUI)**.

**Run command:** `hermes --tui`

**Features:** Built using terminal primitives, it supports full mouse selection, modal overlays, non-blocking multiline editing, and slash-command autocompletion. It is instantly responsive and bypasses the rendering overhead of a graphical engine entirely.

A Note on ACP/MCP Connectivity

If you are looking to wire Hermes explicitly into the broader **Agent Communication Protocol (ACP)** ecosystem (the open framework backed by the Linux Foundation and BeeAI for cross-framework agent messaging):
You can bridge your Hermes instance to custom, light web wrappers using tools like `@mcpc-tech/acp-ai-provider`. This allows you to expose the underlying agent to standardized HTTP REST endpoints without packing a heavy GUI framework along with it.

---
