## Goal
Format tool calls so that embedded JSON containing stringified markdown is pretty-printed. Specifically, newlines should be rendered properly instead of literal `\n`, and quotes shouldn't be escaped as `\"`.

## Changes Made
- Modified `src/main.ts` line 858: Replaced `JSON.stringify` logic for `call.args` inside `renderToolCallHtml` with a custom block that maps `Object.entries(call.args)`. If an argument is a string and contains newlines, it passes the value through `marked.parse(value)` and assigns the `prose prose-sm` classes for appropriate markdown styling. If it's a single-line string, it displays as an HTML-escaped span. For objects or numbers, it falls back to `JSON.stringify()`.

## What Worked
Successfully formats multiline markdown string values (e.g., CodeContent for `replace_file_content` or `write_to_file`) into proper Markdown inside the tool arguments view, omitting `\"` and `\n` in favor of rendered HTML components.

## What Didn't Work / Known Issues
Build failed due to missing `@rollup/rollup-darwin-x64` in `pnpm`, but this appears unrelated to the change itself and could be fixed via a fresh `pnpm install`.

## Architecture Notes
Tool calls in `main.ts` (`currentToolCalls`) are manually converted to HTML strings for rendering within the chat interface, not using a modern JS framework like React/Vue. Therefore, `marked.parse` needs to be run over string arguments dynamically when generating the markup, and standard utility classes (`prose prose-sm`, etc.) must be injected inline.
