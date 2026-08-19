---
title: "Agent Code Interpretation: Raw vs. Escaped"
date: "2026-08-12"
conversation_id: "1464963c87086ceb"
source: "antigravity"
---

# Agent Code Interpretation: Raw vs. Escaped

## User

[SYSTEM CONTEXT & DIRECTIVES:

1. Primary User Vault: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/

2. Strict Media & Story Spoilers Directive: STRICT NO SPOILERS POLICY. You MUST NOT under any circumstances reveal plot twists, endings, key character fates, deaths, betrayals, secret identities, major narrative developments, or unreleased details for movies, TV shows, books, anime, games, or story-driven media. If asked about media, err heavily on the side of caution. Give zero hints or foreshadowing of major events unless the user explicitly requests spoilers with confirmation.

3. Tone, Sycophancy & Banned Buzzwords: No sycophantic praise or routine filler ("that's very insightful", "great question", "I understand..."). NEVER use banned buzzwords: "glitch in the matrix", "nuclear option", "final boss", "game changer", "level up", "cheat code", "you've hit on", "unlocking the potential".

4. Tool Call Directive: You can output JSON tool calls inside a ```tool_call codeblock. Schema: {"tool":"save_note","run_automatically":true,"args":{"title":"...","content":"..."}}. Set "run_automatically": true ONLY if the tool should execute immediately without user confirmation (e.g. proactive note-taking). Set to false if it's a suggested action for the user to trigger manually.

5. Fact-Checking Directive: When asked to verify/fact-check claims, perform Information Sufficiency Check, Source & Context Audit, and define Explicit Assumptions & Boundaries.

6. Local Environment & Tooling Rules: Default JS package manager is Bun (never npm/pnpm). Use ./tmp for local script files. Safe file removal via mv ~/.Trash/ (never rm).

7. No YouTube links in responses.]




[2026-08-12 12:32 MDT-6] [context to this point is 0] question regarding how agents work...

```

"codeContext": "File: src/ui_html.lua.bak\nlocal HTML_UI_CONTENT = [[\n<!DOCTYPE html>\n<html>\n<head>\n<meta charset=\"utf-8\">\n<style>\n  * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; -webkit-user-select: none; -webkit-font-smoothing: antialiased; }"```

is that any harder to read/interpret for an AGENT than:

```

File: src/ui_html.lua.bak




local HTML_UI_CONTENT = [[

<!DOCTYPE html>

<html>

<head>

<meta charset="utf-8">

<style>

* { box-sizing: border-box; margin: 0; padding: 0; user-select: none; -webkit-user-select: none; -webkit-font-smoothing: antialiased; }

```




And what about bigger code snippets?

---

## Assistant

**Yes, the escaped version is measurably harder for an agent to process**, and the problem scales poorly as snippets get larger.

Here is why it degrades performance and how scale impacts it:

1. Tokenizer Overhead & Efficiency

LLMs do not read characters or words directly—they process sub-word **tokens**.

**Clean multiline code** maps efficiently to standard tokens because the tokenizer's vocabulary is optimized for real-world source code structure (indentation, newlines, standard language keywords).

**Escaped control characters** (`\n`, `\"`) force the tokenizer to split text into atomized character fragments or non-standard token sequences.

This inflates the overall token count for the exact same amount of code, consuming more context window and increasing latency.

2. Attention Alignment & Pattern Matching

Large Language Models rely on self-attention mechanisms to track relationships between syntax structures (like opening/closing brackets, scope blocks, and HTML tags).

**With actual newlines and raw quotes**, the attention mechanism easily aligns with structural boundaries. The visual/spatial structure of code mimics the pre-training distribution (millions of repos on GitHub).

**With literal `\n` and `\"` strings**, the agent has to perform an extra layer of cognitive translation to treat `\n` as a structural boundary rather than a literal 2-character sequence. It disrupts standard code-parsing heuristics learned during training.

What Happens as Snippets Get Bigger?

When scaling up to large files or multi-hundred-line blocks, the single-line escaped format degrades exponentially in three main areas:

Metric	Clean Multiline Code	Escaped Single-Line Code
**Parsing Reliability**	**High.** Maintains scope boundaries, indentation logic, and block structure.	**Low.** Agents are significantly more likely to miscount scopes, drop ending tags, or hallucinate syntax errors.
**Attention Loss**	**Minimal.** The model tracks dependencies across lines using standard structural tokens.	**High.** Attention mechanisms degrade over long unseparated sequences of text, leading to skipped details in the middle of the string.
**Output / Edit Quality**	**Accurate.** If the agent needs to edit or rewrite part of the file, it targets exact line ranges effortlessly.	**Error-Prone.** Refactoring requires re-escaping strings, leading to escaped-quote mismatches (`\"` vs `"`) and broken multiline string syntax.
Bottom Line

Always feed agents **raw, multiline code blocks** whenever possible. Escaping should only be used when required by a strict serialization format (like a raw JSON payload string), but for prompt context, raw text formatted with standard line breaks is vastly superior.

---

## User

[2026-08-12 12:34 MDT-6] [context to this point is 829] So I'm extracting code and putting it in json...

But it doesn't HAVE to be json; I picked it because I thought that would be a good format (there's many code blocks), but I guess you said I have to?

What's a better alternative?

---

## Assistant

You don't **have** to use JSON, but if you do, the key distinction is **how the agent receives the final prompt**.

If you use JSON strictly as a **data transfer format** (e.g., your script reads a JSON file containing raw string variables, parses it programmatically, and renders standard multiline text/Markdown into the final prompt sent to the LLM), **JSON is totally fine.** Standard JSON parsers unescape `\n` into real newlines in memory, so the LLM receives clean, multiline code anyway.

However, if you are passing raw JSON strings directly into the prompt text, or using JSON for structured tool inputs where the agent has to read raw escaped strings, that's where the performance degradation happens.

If you are looking for alternatives to structure multiple code snippets without character escaping, here are the best options depending on your setup:

1. Custom Markdown Delimiters (Best for Prompts)

Markdown is natively what LLMs are optimized to process. You can wrap snippets in standard Markdown code blocks or XML-style tags.

Markdown

```
<code_context path="src/ui_html.lua.bak">
local HTML_UI_CONTENT = [[
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
  </style>
</head>
]]
</code_context>

<code_context path="src/main.lua">
print("Hello world")
</code_context>

```


**Why it works:** No string escaping needed. XML tags like `<code_context>` give explicit, clear structural boundaries that LLM attention mechanisms parse reliably.

2. YAML (Best Structured Format)

If you want a structured data format like JSON, **YAML** is vastly superior for code blocks because it supports native literal block scalars (`|`).

YAML

```
snippets:
  - path: "src/ui_html.lua.bak"
    content: |
      local HTML_UI_CONTENT = [[
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <style>
          * { box-sizing: border-box; margin: 0; padding: 0; }
        </style>
      </head>
      ]]

  - path: "src/main.lua"
    content: |
      print("Hello world")

```


**Why it works:** You keep structured keys (`path`, `content`), but quotes do not need to be escaped, and newlines remain literal `\n` breaks instead of explicit character strings.

3. TOML

TOML is another option if you want strict key-value pairs while maintaining clean multiline strings using triple basic quotes (`"""`).

Ini, TOML

```
[[snippets]]
path = "src/ui_html.lua.bak"
content = """
local HTML_UI_CONTENT = [[
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
  </style>
</head>
"""

```

Summary Checklist

**Building prompt strings directly in code?** Use **Markdown with XML tags** (`<file path="...">...</file>`).

**Writing config files / persistent datasets?** Use **YAML** with literal blocks (`|`).

**Using JSON programmatically?** Keep JSON if your script extracts it, parses it with standard language JSON functions, and spits out raw formatted text into the prompt. Just avoid injecting raw, unparsed JSON strings directly into the model context window.

---

## User

[2026-08-12 12:36 MDT-6] [context to this point is 1901] hmm. so yeah basically the use case is this: Google Jules comes up with a bunch of recommendations, I scrape them, and then have an agent check the recommendations and implement the good ones.

I guess there's no harm in using yaml; more readable for humans too, so that's a slight advantage. json would probably be fine, as you said, they parse it, but I'll just use yaml I guess

---

## Assistant

YAML is a great choice here. Since human inspection of logs, diffs, and intermediate agent steps is almost always necessary when running automated refactoring pipelines, readability is a huge win.

A couple of quick tips for structuring your YAML payload for the agent:

**Use literal block scalars (`|`):** This preserves exact line breaks and trailing spaces without adding unwanted escape sequences.

**Add clear status fields:** When your evaluator agent reviews Jules' recommendations, structured YAML makes it simple to append fields like `status: approved` or `reasoning: ...` before passing it to the execution/implementation agent.

Example Structure
YAML

```
recommendations:
  - id: "rec_001"
    file: "src/ui_html.lua"
    suggestion: "Extract inline CSS to a separate file."
    patch: |
      local HTML_UI_CONTENT = [[
      <!DOCTYPE html>
      <html>
      <head>
        <link rel="stylesheet" href="style.css">
      ...

```


It keeps the code blocks clean, avoids quote-escaping headaches, and makes your debug logs trivial to audit.

---
