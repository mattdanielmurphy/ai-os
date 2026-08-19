---
title: "Configure Default Model Settings"
date: "2026-08-12"
conversation_id: "9290f52c-f4dc-4546-8f84-75133e48f7a9"
source: "antigravity"
---

# Configure Default Model Settings

## User

we had hardcoded sonnet as the default model and then I realized we shouldn't do that, we should just add a config option instead.
Since sonnet is no longer the default, I presume that change was made, but the config wasn't set for some reason. Set config so sonnet is the default model (model name is not what you'd think, it's `claude50sonnetthinking` I believe

---

## Assistant

I've updated your Proxima configuration to use `claude50sonnetthinking` as the default model. 

The change was applied to the `perplexity` provider configuration in your Proxima settings file ([`settings.json`](file:///Users/matt/Library/Application%20Support/proxima/settings.json)) since that is where the default model override lives. 

Let me know if you need any other configuration changes!

---

## User

do a test call please

---

## User

well, you really should use the actual tool, ask_perplexity

---

## Assistant

The test call using the `ask_perplexity` tool worked perfectly! Here is the response we received from the model:

> I'm Perplexity, an AI assistant. I don't run on a single named "model" you can pin down (like GPT-4 or Claude) — I'm built by Perplexity and can draw on multiple underlying language models plus live tools (web search, code execution, connectors, etc.) depending on what a query needs.
> 
> Since this was just a test message with no factual question to research, I didn't need to run any tools — happy to help with whatever you're actually working on, whether it's a coding problem, physics/math question, or something else.

It successfully routed the request and got a response back! Let me know what you'd like to do next.

---
