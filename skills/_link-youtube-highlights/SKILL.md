---
name: _link-youtube-highlights
description: "Formats and generates YouTube video URLs with highlight reel timestamp parameters for automated segment skipping in Matt's YouTube userscript."
---

# Link YouTube Highlights

Whenever recommending, referencing, or summarizing a YouTube video for Matt, format the YouTube URL with the `highlights` query parameter. Matt's YouTube Master userscript automatically intercepts these parameters on page load, generates scrubber heatmap markers, jumps to the first highlight segment, and automatically skips non-highlight portions during playback.

## URL Syntax & Formats

The primary URL parameter is `highlights` (aliases `reel` or `segments` are also supported).

### Integer Seconds / Timestamp Intervals with Labels (Standard)
Format: `&highlights=start-end:Title,start-end:Title` (use `+` for spaces)
```markdown
[https://www.youtube.com/watch?v=VIDEO_ID&highlights=0:42-1:25:Core+Problem,2:00-2:30:Demo](https://www.youtube.com/watch?v=VIDEO_ID&highlights=0:42-1:25:Core+Problem,2:00-2:30:Demo)
```

### Sharing with Others (Standalone Web Player)
When sharing with folks who don't have Matt's userscript installed:
```markdown
[https://yt.mattmurphy.ca/?v=VIDEO_ID&highlights=0:42-1:25:Core+Problem,2:00-2:30:Demo](https://yt.mattmurphy.ca/?v=VIDEO_ID&highlights=0:42-1:25:Core+Problem,2:00-2:30:Demo)
```

---

## Agent Curation Best Practices

1. **Payoff Over Setup:**
- Skip conversational preambles, general intros, and generic background.
- Start the clip where the speaker states the *problem, metric, or technique*, and end it after the *solution/rule-of-thumb* is fully stated.

2. **The "+15s Cliffhanger Check":**
- Always inspect the 15–30 seconds immediately following a planned `end` timestamp.
- If the speaker introduces a catch, counter-example, or crucial caveat (*"but the real issue is..."*, *"here is why that fails..."*), extend the segment through the resolution.

3. **Continuous Thoughts & Natural Boundaries:**
- Never cut mid-sentence. Start at the first word of the premise and close after the final concluding phrase.

4. **Descriptive Labels:**
- Use concise 2–4 word title descriptors (e.g., `:Shelf+Depth+Trap`, `:Waterproof+Liners`).
