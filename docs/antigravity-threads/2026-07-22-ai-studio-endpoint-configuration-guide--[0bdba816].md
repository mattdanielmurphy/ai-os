---
title: "AI Studio Endpoint Configuration Guide"
date: "2026-07-22"
conversation_id: "0bdba8165c9082b9"
source: "antigravity"
---

# AI Studio Endpoint Configuration Guide

## User

what would I make these for gemini via aistudio endpoint?

---

## Assistant

To connect Google AI Studio using its OpenAI-compatible endpoint, fill out the fields as follows:

Endpoint Settings

**Endpoint name:** `Google AI Studio` *(or any label you prefer)*

**Endpoint URL:** `[https://generativelanguage.googleapis.com/v1beta/openai/](https://generativelanguage.googleapis.com/v1beta/openai/)`

**API key:** Your API key from Google AI Studio *(typically starts with `AIza...`)*

**Model name:** `gemini-2.5-flash` *(or `gemini-2.5-pro`, `gemini-1.5-flash`)*

**Model alias (optional):** `Gemini 2.5 Flash` *(or any display name you'd like in the app UI)*

**Note:** If your client app automatically appends `/chat/completions` to the base URL, keeping the trailing slash on `[https://generativelanguage.googleapis.com/v1beta/openai/](https://generativelanguage.googleapis.com/v1beta/openai/)` ensures it routes correctly to Google's official OpenAI-compatible endpoint.

---
