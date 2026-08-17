---
name: _link-youtube-highlights
description: "Formats and generates YouTube video URLs with highlight reel timestamp parameters for automated segment skipping in Matt's YouTube userscript."
---

# Link YouTube Highlights

Whenever recommending, referencing, or summarizing a YouTube video for Matt, format the YouTube URL with the `highlights` query parameter. Matt's YouTube Master userscript automatically intercepts these parameters on page load, generates scrubber heatmap markers, jumps to the first highlight segment, and automatically skips non-highlight portions during playback.

## URL Syntax & Formats

The primary URL parameter is `highlights` (aliases `reel` or `segments` are also supported).

### 1. Integer Seconds Interval (Recommended & Most Compact)
Format: `&highlights=start-end,start-end,...`
```markdown
https://www.youtube.com/watch?v=VIDEO_ID&highlights=42-85,120-150,300-360
```

### 2. Labelled Segments (Recommended for Summaries)
Format: `&highlights=start-end:Title,start-end:Title` (use `+` or `%20` for spaces)
```markdown
https://www.youtube.com/watch?v=VIDEO_ID&highlights=42-85:The+Core+Problem,120-150:Architecture+Demo,300-360:Key+Takeaway
```
*Note: The userscript displays these segment titles in the floating HUD and above the scrubber.*

### 3. Timestamp Notation (`MM:SS` or `HH:MM:SS`)
Format: `&highlights=MM:SS-MM:SS,MM:SS-MM:SS`
```markdown
https://www.youtube.com/watch?v=VIDEO_ID&highlights=0:42-1:25:Intro,2:00-2:30:Demo,5:15-6:00:Conclusion
```

### 4. Human Duration Notation
Format: `&highlights=1m20s-2m30s,5m-6m15s`
```markdown
https://www.youtube.com/watch?v=VIDEO_ID&highlights=1m20s-2m30s:Overview,5m-6m15s:Walkthrough
```

### 5. URL-Encoded JSON Array
Format: `&highlights=[{"start":42,"end":85,"title":"..."}]`
```markdown
https://www.youtube.com/watch?v=VIDEO_ID&highlights=%5B%7B%22start%22%3A42%2C%22end%22%3A85%2C%22title%22%3A%22Core+Problem%22%7D%5D
```

## Sharing with Others (Standalone Web Player)

When sharing a highlight reel with users who do NOT have Matt's userscript installed, format the link pointing to Matt's deployed web player:
```markdown
https://yt-highlight-reel.vercel.app/?v=VIDEO_ID&highlights=42-85:Intro,120-150:Solution
```
The web player automatically embeds the video, renders scrubber heatmaps, navigates soundbites, and handles automated skipping in any browser without needing extensions.

---

## Agent Curation Best Practices

When curating highlight timestamps from a transcript or video:
1. **Continuous Thoughts**: Ensure each segment starts at the beginning of a complete sentence and ends after the thought is fully expressed (never cut mid-sentence).
2. **Target Cumulative Duration**: ~3 to 5 minutes total (or ~10–15% of the total runtime) unless otherwise requested.
3. **Cut Fluff**: Exclude sponsor reads, intros/outros, repetitive filler, and low-signal banter.
4. **Descriptive Labels**: Add concise 2–4 word title descriptors to each segment (e.g. `:Benchmark+Results`, `:Root+Cause`).
