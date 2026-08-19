---
title: "Rethinking AI Project Architecture"
date: "2026-07-20"
conversation_id: "d51d181cadd7b217"
source: "antigravity"
---

# Rethinking AI Project Architecture

## User

[2026-07-20 00:30 MDT-6] [context to this point is 0] I've been bouncing all over the place with my ai-os project and it's frankly fucking exhausting and dispiriting.

Anyway, I've just found reason to switch my project YET AGAIN.

I can't use hermes-webui because if I want to stop the agent and tell it something, I have to "cancel" the prompt, in which case, the next agent doesn't seem to have the context of the original thread because the previous message was "cancelled".

Which is fucking insane.




I've realized this: I think I just need a REALLY solid claude code UI, right?

Then I can set up my own custom triage model, then run either Hermes or `agy` without needing to fork anything (I'm already using litellm)... right?

---

## Assistant

That behavior is incredibly frustrating. Having a "cancel" function break the thread chain or drop historical context defeats the entire purpose of building an interactive agent loop—especially when you need to step in, redirect the execution, and keep moving. You shouldn't have to fight the core architectural design of a heavy UI framework just to run model steering.

Your instinct to strip things down is spot on. Decoupling the interface from the specific model runtime using a lightweight triage layer and a clean UI wrapper is a far more robust path.

Why Your Realization is the Right Pivot

**Zero Upstream Fighting:** By using `litellm` as your universal interface, you can treat models (whether it's Hermes, a local model via Ollama, or an API) as hot-swappable endpoints. You stop inheriting the UX assumptions or bugs of giant WebUI forks.

**Granular State Control:** When you write your own triage and execution logic, *you* own the array of messages. If a user interrupts or cancels a turn, you choose exactly how the history is mutated before the next prompt hits the orchestration layer.

**Deterministic Triage:** A dedicated, lightweight script handling model routing means you can tune how and when tasks get pushed to specific agents without breaking the frontend interface.

Choosing the Right UI Layer

Since you just want a reliable wrapper that won't get in your way or mangle the context, you have a few clean paths:

**The TUI / CLI Approach:** If you prefer keyboard efficiency, building or using a clean terminal/TUI wrapper (using tools like `ratatui` or a simple Python `textual` app) gives you absolute control over text streaming and interruption signals (`Ctrl+C`) without handling heavy state syncs.

**Lightweight Native Webview (Tauri / Wails):** If you want a dedicated side panel or desktop view, a minimal Tauri or Wails setup running a basic, highly responsive chat view lets you bind standard UI events directly to your backend proxy loop.

**Minimalist Open WebUI / Pipes:** If you don't want to build a frontend from scratch, you can look at minimal integration extensions (like the Claude Code Open WebUI Pipe concepts) or simple chat frontends that give you raw markdown streams and custom backend hooks, handling the message array yourself.

**The Core Architecture:**
`[Minimal UI Layer]` ↔ `[Your Custom Triage / Context Orchestrator]` ↔ `[LiteLLM Proxy]` ↔ `[Target Agents / Models]`

This keeps your frontend dumb, fast, and stable, while keeping your agent logic completely modular.

What does your current triage layout look like in your head—are you planning a simple router that evaluates intent first, or do you want a persistent state machine passing code tokens back and forth?

---
