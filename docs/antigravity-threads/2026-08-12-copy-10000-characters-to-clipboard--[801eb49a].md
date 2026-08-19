---
title: "Copy 10,000 Characters to Clipboard"
date: "2026-08-12"
conversation_id: "801eb49ab8f1343b"
source: "antigravity"
---

# Copy 10,000 Characters to Clipboard

## User

give me some code to copy 10,000 characters to my clipboard. Doesn't matter what they are. They just can't be spaces.

---

## Assistant

Here is a Bun one-liner that generates 10,000 characters and copies them directly to your clipboard (works natively on macOS using `pbcopy`):

Bash

```
bun -e 'process.stdout.write("A".repeat(10000))' | pbcopy

```


If you prefer a standalone Python script that works cross-platform:

Python

```
import subprocess

# Generate 10,000 non-space characters
data = "x" * 10000

# Copy to clipboard via macOS pbcopy
process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
process.communicate(input=data.encode('utf-8'))

print("10,000 characters copied to clipboard.")

```


Or a quick JavaScript/Node snippet if you want to run it via Node/Bun or browser console:

JavaScript

```
// Copies 'X' repeated 10,000 times directly in a browser console
copy('X'.repeat(10000));

```

---
