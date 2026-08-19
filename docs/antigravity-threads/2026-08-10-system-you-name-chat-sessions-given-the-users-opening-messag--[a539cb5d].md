---
title: "SYSTEM: You name chat sessions. Given the user's opening message, writ"
date: "2026-08-10"
conversation_id: "a539cb5d-c89a-4d0b-880b-3fbb6357331d"
source: "antigravity"
---

# SYSTEM: You name chat sessions. Given the user's opening message, writ

## User

SYSTEM: You name chat sessions. Given the user's opening message, write a title that lets them find this conversation again in a list.

Rules:
- 3 to 7 words, sentence case (capitalize only the first word and proper nouns).
- Name what the user wants DONE, not that they asked a question.
- Keep technical terms, filenames, numbers, and error codes exact.
- Drop filler words: the, this, my, a, an.
- No trailing punctuation, no quotes, no tool names, no 'Title:' prefix.
- Never answer the message. Name it.
- Always produce something, even for a bare greeting.
- Write the title in the same language as the user's message.
Good: {"title": "Fix login button on mobile"}
Good: {"title": "Postgres connection pool exhaustion"}
Good: {"title": "Friendly greeting"}
Too vague: {"title": "Code changes"}
Too long: {"title": "Investigate and fix the issue where the login button does not respond on mobile devices"}

Reply with JSON only: {"title": "..."}

USER: [Workspace::v1: /Users/matt/projects/music-cross-linker]
If I type `http://localhost:3011/https://music.apple.com/ca/album/belladonna/1844719636`
then the Apple Music link it gives me is `https://music.apple.com/us/album/desert-rose/1844719636?i=1844719654&uo=4`
I mean, first of all, I pasted an album and it links to a song called desert rose ON that album. we want to link to the album.
second, it's a US link when I pasted a Canadian link.
Third, I PASTED the fucking link so why wouldn't it use MY link for Apple Music?! (that should be the case for all platforms; if I paste a YouTube link, just embed that video... don't show Youtube search results either; if I paste Spotify link, use that for Spotify).

---

## Assistant

{"title": "Fix Apple Music album link matching"}

---
