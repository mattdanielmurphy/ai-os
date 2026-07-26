# Agy Argument Ordering Pitfall — Session Reproduction

## The Bug

When calling agy in print mode, `-p` consumes the **next positional argument** as the prompt text. If you accidentally put a flag there, agy treats the flag name as your prompt.

## Symptom

```bash
# WRONG — --dangerously-skip-permissions gets read as the prompt
agy -p --dangerously-skip-permissions "investigate this issue"
```

agy responds with "You have passed the --dangerously-skip-permissions flag" or discusses its permission configuration — because it read `--dangerously-skip-permissions` as the prompt text, and `"investigate this issue"` as an unknown positional argument that got ignored.

## Correct Invocation

```bash
# RIGHT — prompt text immediately after -p, flags after the prompt
agy -p "investigate this issue" --dangerously-skip-permissions --print-timeout 5m
```

## Shell Quoting Guide

**Always use single-quoted strings.** Single quotes prevent ALL bash interpretation — backticks, $ signs, other special chars pass through verbatim.

```bash
# Safe: backticks inside single quotes are literal
agy -p '`matthewmurphy` paths need fixing' --dangerously-skip-permissions --print-timeout 5m

# Long prompts span multiple lines in single quotes naturally
agy -p 'First paragraph of context.

Second paragraph with more detail.
Final instruction line.' --dangerously-skip-permissions --print-timeout 5m
```

If the prompt itself contains a single quote character (e.g., "it's"), use double quotes for the outer string instead — but this is the only exception.

## What NOT to Do

- ❌ Write prompt to a file and read with `$(cat file)` — backticks and $ signs inside the file get interpreted by bash
- ❌ Use Python subprocess wrappers — triggers Hermes permission prompts
- ❌ Pipe stdin into agy — agy doesn't read stdin for the prompt text
- ❌ Use heredocs (`cat << 'EOF'`)

## Lesson

The simplest invocation is always the right one. Single-quoted string, direct terminal command. Fix quoting issues by escaping or rephrasing, never by adding layers.