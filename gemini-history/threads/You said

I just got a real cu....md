[2026-07-02 22:50] User:
I just got a real curiosity in my head.

If I were to just blindly give an LLM ALL the context of my entire Mac, excluding system files, generated files, things like node_modules and .git folders, etc... Not even photos... Basically just like documents. All the human-created text on my Mac... how many tokens is that?

I want you to help me craft a simple oneliner that uses code2prompt to find out the answer.




Now, with code2prompt, you just pass in a directory (I'll pass ~) along with --include "file1pattern" --include "file2pattern*" --exclude "node_modules" etc, and it will return one text stream of all the files.

Now, we can happily discard this text stream. All I care about is the token count.

I often pipe the output to pbcopy, which leaves behind the token count. Can you maybe just pipe it to nowhere so it has that effect? I'd rather not have the output go straight to my terminal.

---

[2026-07-02 22:50] Assistant:
To get the token count without cluttering your terminal or overwriting your clipboard, you can redirect the standard output (`stdout`) to `/dev/null`.

When `code2prompt` runs, it prints its processing status and the final token count to standard error (`stderr`), while the actual aggregated text goes to `stdout`. Redirecting `stdout` leaves only the token metrics visible in your terminal.

Here is the one-liner to scan your home directory while filtering out system clutter, dependency folders, and non-text media:

Bash

```
code2prompt ~ --exclude "**/node_modules/**" --exclude "**/.git/**" --exclude "**/Library/**" --exclude "**/.Trash/**" --exclude "**/*.png" --exclude "**/*.jpg" --exclude "**/*.jpeg" --exclude "**/*.mp4" --exclude "**/*.mov" > /dev/null

```

How it breaks down:

**`~`**: Starts the scan from your user home directory.

**`--exclude "/node_modules/" --exclude "/.git/"`**: Skips heavy developer dependency and history folders anywhere they appear.

**`--exclude "/Library/" --exclude "/.Trash/"`**: Ignores macOS system application support files, caches, and deleted items.

**`--exclude "/*.png" ...`**: Filters out common image and video formats that aren't plain text.

**`> /dev/null`**: Discards the massive stream of text, leaving only the `code2prompt` summary table (which includes the token count) printed on your screen.

Depending on how many files you have, this might take a minute or two to crawl the drive, but it will give you the exact number you're looking for.
