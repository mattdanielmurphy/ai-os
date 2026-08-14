---
title: "any way to get gemini-cli thread exported somehow? I've run "
date: "2026-08-13"
source: "gemini.google.com"
conversation_id: "0cea2a96-b320-5295-87d9-11459b1e4549"
url: ""
---

# any way to get gemini-cli thread exported somehow? I've run 

> [!NOTE]
> Archived Gemini Thread: [any way to get gemini-cli thread exported somehow? I've run ]() | Date: 2026-08-13

## User

any way to get gemini-cli thread exported somehow? I've run out of tokens (and for some reason only ONE of my accounts will work with gemini-cli now)

---

## Gemini

If you are still in the active terminal session where you ran out of tokens, you have a built-in slash command that will handle this directly.


1. The Direct Command (If the session is still open)
Run this command straight inside the CLI prompt:


/chat share thread.md

(You can also use thread.json if you prefer structured data over Markdown).


If you've already closed the terminal or it crashed because of the token limit, the CLI automatically saves conversation states by project directory hashes. You can check for a saved state using:


/chat list

If your session is listed, you can spin it back up with /chat resume <tag> and then run the share command.



2. The File System Backup (If you've closed the terminal)
If the session is dead and you can't resume it through the interactive prompt, gemini-cli caches raw session states directly on your local disk.


On macOS, you can find the raw files here:


cd ~/.gemini/tmp/

Inside this folder, you will see subdirectories named after project hashes. Dig into the most recent one, and you'll find JSON files containing the exact history of your prompts and responses. You can grab the text or use a quick script to clean up the JSON payload.



3. Fixing the Account/Token Lockout
Since you mentioned only one account is working and you hit the token wall, you can easily pivot to an API Key instead of relying on the standard web OAuth browser login.


Using an API key from Google AI Studio completely bypasses the default daily browser OAuth limits (which cap out at 1,000 requests/day).



* Go to Google AI Studio and generate a free API key on the account you want to use.

* In your terminal, swap the authentication method by setting the environment variable before launching:


export GEMINI_API_KEY="your_actual_api_key_here"
gemini

If you ever need to forcefully clear out old session states or reset the token count tracking locally, you can use /chat clear or pass the --fresh flag when initializing the CLI to spin up a completely clean pipeline.

---

