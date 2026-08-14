---
title: "not a hyphenated Hugging Face-style name?"
date: "2026-08-13"
source: "gemini.google.com"
conversation_id: "614d9b85-b389-5405-8a9e-29ceec147f03"
url: ""
---

# not a hyphenated Hugging Face-style name?

> [!NOTE]
> Archived Gemini Thread: [not a hyphenated Hugging Face-style name?]() | Date: 2026-08-13

## User

not a hyphenated Hugging Face-style name?

---

## Gemini

Correct. When using Ollama, the model tag structure is specific and does not follow the typical repository naming conventions seen on platforms like Hugging Face.


Ollama uses a family:version format.



* Hugging Face style (Example): qwen2.5-7b-instruct (Often used in local inference tools that bridge to HF repositories).

* Ollama style (Correct): qwen2.5:7b-instruct (The colon acts as the separator for the specific variant).


If you try to pull using the hyphenated version (qwen2.5-7b-instruct), Ollama looks for a repository path that doesn't match its internal library, resulting in the "file does not exist" error you encountered. Always ensure the colon is placed between the family name (e.g., qwen2.5) and the specific size/variant (e.g., 7b or 7b-instruct).

---

## User

Having a hell of a time getting a local model to do tool calls reliably

---

## Gemini

It's an incredibly frustrating bottleneck. Local tool calling is notorious for breaking because small models require absolute precision, and standard API wrappers often mangle the formatting they expect.


When you drop down to the 7B–14B parameter range, the margin for error vanishes. A single misplaced comma, an extra markdown code block, or a slightly malformed JSON payload will cause the harness to fail at parsing the tool call entirely.


The trick to stabilizing this setup usually comes down to three things:


1. Match the Model to Ollama's Native Tool Logic
While many models claim tool-calling capabilities, Ollama handles some much better out of the box than others because of how its internal templates are structured.



* The Safest Bet: llama3.1:8b or llama3.2:3b. Meta’s instruct variants have deeply baked-in, rigid XML/JSON structures for tools that Ollama supports natively.

* The Alternative: mistral-nemo (12B). Mistral models are historically excellent at function calling and follow system prompts regarding tool execution tightly.

* The Qwen Quirk: As you might have run into, qwen2.5-coder:7b often chokes on tool parsing inside certain harnesses unless you switch to the standard qwen2.5:7b instruct model, or vice-versa, depending on how the harness writes its system prompt.


2. Bypass the Harness Grammar (The Strict JSON Fix)
If the harness allows you to pass raw options or edit the system prompt template, you want to force the model's sampling to be incredibly rigid.



* Set temperature to 0. Anything higher introduces creativity where you absolutely do not want it.

* If the harness supports it, enforce a JSON schema or format constraint directly via the Ollama API configuration ("format": "json"). This forces the local model's logits to only output valid JSON, stopping it from rambling with conversational text before or after the tool call.


3. Simplify the Tools
Small models struggle with complex tool definitions. If your harness is feeding the model a massive schema with 6 different tools and complex nested properties, a 7B model will lose the plot.



* Strip the tool definitions down to the bare minimum.

* Keep property descriptions short and clear.

* If a tool takes arguments, try to make them flat strings or integers rather than nested objects.


Are you seeing the model fail by completely ignoring the tools and just talking, or is it trying to call them but spitting out mangled, unparseable syntax?

---

